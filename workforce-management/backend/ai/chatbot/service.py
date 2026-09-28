"""
AI HR Chatbot Orchestration Service
-----------------------------------
Orchestrates the complete lifecycle:
  User Question -> Guardrails -> Intent Detection -> Authorization ->
  Data Retrieval -> RAG Retrieval -> Context Building -> LLM Execution ->
  Grounded Response -> Citations -> History Persistence.
"""

from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime, timezone

from database.mongodb import get_db
from backend.ai.chatbot.schemas import (
    ChatMessageResponse,
    CitationSource,
    ConversationSummary,
    ConversationDetail,
    ConversationMessage
)
from backend.ai.chatbot.guardrails import GuardrailEngine
from backend.ai.chatbot.intent_classifier import IntentClassifier
from backend.ai.chatbot.authorization import AuthorizationGate
from backend.ai.chatbot.retriever import ScopedDataRetriever
from backend.rag.retriever import RAGRetriever
from backend.ai.chatbot.context_builder import ContextBuilder
from backend.ai.chatbot.llm_service import get_llm_service
from backend.ai.chatbot.citations import CitationEngine
from backend.ai.chatbot.prompt_templates import get_suggested_prompts

class ChatbotService:
    """
    Central orchestration service for the AI HR Chatbot.
    """

    def __init__(self):
        self.db = get_db()
        self.data_retriever = ScopedDataRetriever()
        self.rag_retriever = RAGRetriever()
        self.llm_service = get_llm_service()
        self._ensure_indexes()

    def _ensure_indexes(self):
        try:
            self.db.chatbot_conversations.create_index("conversation_id", unique=True)
            self.db.chatbot_conversations.create_index("user_id")
            self.db.chatbot_messages.create_index("conversation_id")
            self.db.chatbot_messages.create_index("timestamp")
        except Exception:
            pass

    def process_chat_message(
        self,
        message: str,
        current_user: Dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> ChatMessageResponse:
        """
        Executes end-to-end grounded conversational response generation.
        """
        user_id = current_user.get("user_id", "USR_ANON")
        user_role = current_user.get("role", "EMPLOYEE")
        emp_id = current_user.get("employee_id")
        now_iso = datetime.now(timezone.utc).isoformat()

        # 1. Resolve or create conversation thread
        if not conversation_id:
            # Generate initial title from first few words
            words = message.strip().split()
            title = " ".join(words[:6]) + ("..." if len(words) > 6 else "")
            conversation_id = f"CONV_{uuid.uuid4().hex[:12].upper()}"
            self.db.chatbot_conversations.insert_one({
                "conversation_id": conversation_id,
                "user_id": user_id,
                "employee_id": emp_id,
                "title": title,
                "created_at": now_iso,
                "updated_at": now_iso,
                "message_count": 0
            })
        else:
            conv = self.db.chatbot_conversations.find_one({"conversation_id": conversation_id})
            if not conv:
                conversation_id = f"CONV_{uuid.uuid4().hex[:12].upper()}"
                self.db.chatbot_conversations.insert_one({
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                    "employee_id": emp_id,
                    "title": message[:30] + "...",
                    "created_at": now_iso,
                    "updated_at": now_iso,
                    "message_count": 0
                })

        # Save incoming user message
        self.db.chatbot_messages.insert_one({
            "message_id": f"MSG_{uuid.uuid4().hex[:10]}",
            "conversation_id": conversation_id,
            "role": "user",
            "content": message,
            "timestamp": now_iso,
            "sources": []
        })

        # 2. Input Security Guardrails
        is_safe, check_result = GuardrailEngine.check_query_safety(message)
        if not is_safe:
            denial_resp = ChatMessageResponse(
                answer=check_result,
                sources=[],
                intent="security_violation",
                conversation_id=conversation_id,
                grounded=True,
                timestamp=now_iso,
                follow_up_suggestions=get_suggested_prompts(user_role)[:3]
            )
            self._save_assistant_message(conversation_id, denial_resp)
            return denial_resp

        # 3. Retrieve recent history for follow-up resolution
        recent_msgs = list(self.db.chatbot_messages.find(
            {"conversation_id": conversation_id},
            {"_id": 0}
        ).sort("timestamp", -1).limit(4))
        recent_msgs.reverse()

        last_intent = None
        last_user_query = None
        for m in recent_msgs[:-1]:
            if m.get("role") == "user":
                last_user_query = m.get("content")
            elif m.get("role") == "assistant" and m.get("intent"):
                last_intent = m.get("intent")

        # Intent Detection & Query Rewriting
        intent_info = IntentClassifier.classify_intent(message)
        intent = intent_info["intent"]
        resource_type = intent_info["resource_type"]

        resolved_query = IntentClassifier.resolve_follow_up_context(
            message,
            last_user_query,
            last_intent
        )

        # 4. CRITICAL: Backend Authorization Gate BEFORE any retrieval
        is_authorized, denial_reason, scoped_params = AuthorizationGate.check_authorization(
            current_user=current_user,
            intent=intent,
            query=message
        )

        if not is_authorized:
            unauthorized_resp = ChatMessageResponse(
                answer=denial_reason or "Access Denied: You do not have permission to view the requested information.",
                sources=[],
                intent=intent,
                conversation_id=conversation_id,
                grounded=True,
                timestamp=now_iso,
                follow_up_suggestions=get_suggested_prompts(user_role)[:3]
            )
            self._save_assistant_message(conversation_id, unauthorized_resp)
            return unauthorized_resp

        # 5. Permitted Data Retrieval
        mongo_data = None
        ai_data = None
        rag_chunks = []

        if resource_type in ["mongodb", "multi_source"]:
            mongo_data = self.data_retriever.retrieve_mongodb_data(intent, scoped_params)

        if resource_type in ["ai_ml", "multi_source"]:
            ai_data = self.data_retriever.retrieve_ai_analytics(intent, scoped_params)

        if resource_type in ["rag_document", "multi_source"] or not (mongo_data or ai_data):
            rag_chunks = self.rag_retriever.retrieve(resolved_query, top_k=4)

        # 6. Build Grounded Context
        context, citations = ContextBuilder.build_context(
            mongo_data=mongo_data,
            rag_chunks=rag_chunks,
            ai_data=ai_data
        )

        # 7. LLM Response Generation
        history_turns = [{"role": m["role"], "content": m["content"]} for m in recent_msgs[:-1]]
        answer_text = self.llm_service.generate_response(
            query=resolved_query,
            context=context,
            conversation_history=history_turns
        )

        # 8. Output Safety Sanitization
        safe_answer = GuardrailEngine.verify_output_safety(answer_text)
        deduped_sources = CitationEngine.deduplicate_citations(citations)

        # Check if grounded
        grounded = "I don't have enough verified information" not in safe_answer

        response = ChatMessageResponse(
            answer=safe_answer,
            sources=deduped_sources,
            intent=intent,
            conversation_id=conversation_id,
            grounded=grounded,
            timestamp=now_iso,
            follow_up_suggestions=get_suggested_prompts(user_role)[:3]
        )

        # 9. Save message and update conversation stats
        self._save_assistant_message(conversation_id, response)
        return response

    def _save_assistant_message(self, conversation_id: str, response: ChatMessageResponse):
        now_iso = datetime.now(timezone.utc).isoformat()
        self.db.chatbot_messages.insert_one({
            "message_id": f"MSG_{uuid.uuid4().hex[:10]}",
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": response.answer,
            "timestamp": now_iso,
            "intent": response.intent,
            "sources": [s.model_dump() for s in response.sources]
        })
        self.db.chatbot_conversations.update_one(
            {"conversation_id": conversation_id},
            {
                "$set": {"updated_at": now_iso},
                "$inc": {"message_count": 2}
            }
        )

    # -------------------------------------------------------------
    # Conversation Management Endpoints
    # -------------------------------------------------------------
    def create_conversation(self, user_id: str, employee_id: Optional[str], title: Optional[str] = None) -> ConversationSummary:
        conv_id = f"CONV_{uuid.uuid4().hex[:12].upper()}"
        now_iso = datetime.now(timezone.utc).isoformat()
        doc = {
            "conversation_id": conv_id,
            "user_id": user_id,
            "employee_id": employee_id,
            "title": title or "New Conversation",
            "created_at": now_iso,
            "updated_at": now_iso,
            "message_count": 0
        }
        self.db.chatbot_conversations.insert_one(doc)
        return ConversationSummary(
            conversation_id=conv_id,
            user_id=user_id,
            title=doc["title"],
            created_at=now_iso,
            updated_at=now_iso,
            message_count=0
        )

    def get_user_conversations(self, user_id: str) -> List[ConversationSummary]:
        convs = list(self.db.chatbot_conversations.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("updated_at", -1))
        return [ConversationSummary(**c) for c in convs]

    def get_conversation_detail(self, conversation_id: str, user_id: str) -> Optional[ConversationDetail]:
        conv = self.db.chatbot_conversations.find_one(
            {"conversation_id": conversation_id, "user_id": user_id},
            {"_id": 0}
        )
        if not conv:
            return None

        msgs = list(self.db.chatbot_messages.find(
            {"conversation_id": conversation_id},
            {"_id": 0}
        ).sort("timestamp", 1))

        formatted_msgs = []
        for m in msgs:
            sources = [CitationSource(**s) for s in m.get("sources", [])]
            formatted_msgs.append(ConversationMessage(
                role=m["role"],
                content=m["content"],
                timestamp=m["timestamp"],
                intent=m.get("intent"),
                sources=sources
            ))

        return ConversationDetail(
            conversation_id=conv["conversation_id"],
            user_id=conv["user_id"],
            title=conv["title"],
            created_at=conv["created_at"],
            updated_at=conv["updated_at"],
            messages=formatted_msgs
        )

    def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        res = self.db.chatbot_conversations.delete_one({"conversation_id": conversation_id, "user_id": user_id})
        if res.deleted_count > 0:
            self.db.chatbot_messages.delete_many({"conversation_id": conversation_id})
            return True
        return False
