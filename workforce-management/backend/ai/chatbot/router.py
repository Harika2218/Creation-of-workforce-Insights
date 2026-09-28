"""
FastAPI Router: AI HR Chatbot & RAG
-----------------------------------
Exposes conversational AI endpoints, conversation management,
document source introspection, and administrative RAG document indexing.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.auth.dependencies import get_current_user, require_role
from backend.ai.chatbot.schemas import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationSummary,
    ConversationDetail,
    DocumentIndexResponse,
    SourceDocumentItem,
    SuggestedPromptsResponse
)
from backend.ai.chatbot.service import ChatbotService
from backend.rag.indexing_service import IndexingService
from backend.rag.vector_store import MongoVectorStore
from backend.ai.chatbot.prompt_templates import get_suggested_prompts

router = APIRouter(prefix="/chatbot", tags=["AI HR Assistant & RAG"])

_chatbot_service = ChatbotService()
_indexing_service = IndexingService()
_vector_store = MongoVectorStore()

# -------------------------------------------------------------------
# 1. Chat Interaction Endpoint
# -------------------------------------------------------------------
@router.post("/chat", response_model=ChatMessageResponse, summary="Send message to AI HR Assistant")
async def send_chat_message(
    payload: ChatMessageRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Submits a natural language query to the AI HR Assistant.
    Enforces authorization, retrieves verified database / RAG context, and returns cited answer.
    """
    response = _chatbot_service.process_chat_message(
        message=payload.message,
        current_user=current_user,
        conversation_id=payload.conversation_id
    )
    return response

# -------------------------------------------------------------------
# 2. Conversation Management Endpoints
# -------------------------------------------------------------------
@router.post("/conversations", response_model=ConversationSummary, summary="Create a new conversation thread")
async def create_conversation(
    current_user: dict = Depends(get_current_user)
):
    """Initializes a new conversational session for the authenticated user."""
    conv = _chatbot_service.create_conversation(
        user_id=current_user.get("user_id"),
        employee_id=current_user.get("employee_id"),
        title="New HR Inquiry"
    )
    return conv

@router.get("/conversations", response_model=List[ConversationSummary], summary="List user's conversation threads")
async def list_conversations(
    current_user: dict = Depends(get_current_user)
):
    """Retrieves all conversation sessions belonging to the current user."""
    return _chatbot_service.get_user_conversations(user_id=current_user.get("user_id"))

@router.get("/conversations/{conversation_id}", response_model=ConversationDetail, summary="Get conversation history")
async def get_conversation_history(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Returns the message history for a specific conversation session."""
    conv = _chatbot_service.get_conversation_detail(
        conversation_id=conversation_id,
        user_id=current_user.get("user_id")
    )
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation '{conversation_id}' not found or access unauthorized."
        )
    return conv

@router.delete("/conversations/{conversation_id}", summary="Delete conversation thread")
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Deletes a conversation session and all its associated messages."""
    deleted = _chatbot_service.delete_conversation(
        conversation_id=conversation_id,
        user_id=current_user.get("user_id")
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation '{conversation_id}' could not be deleted or not found."
        )
    return {"status": "success", "message": f"Conversation {conversation_id} deleted successfully."}

# -------------------------------------------------------------------
# 3. Document Indexing (HR/Admin Only)
# -------------------------------------------------------------------
@router.post(
    "/documents/index",
    response_model=DocumentIndexResponse,
    dependencies=[Depends(require_role(["ADMIN", "HR"]))],
    summary="Index enterprise policy documents (HR/Admin Only)"
)
async def index_hr_documents():
    """
    Parses, chunks, embeds, and indexes all HR policy documents into MongoDB.
    Strictly restricted to Admin and HR users.
    """
    try:
        result = _indexing_service.index_directory()
        return DocumentIndexResponse(
            status="success",
            indexed_documents=result["indexed_documents"],
            indexed_chunks=result["indexed_chunks"],
            provider=result["provider"],
            message=f"Successfully indexed {result['indexed_documents']} policy documents ({result['indexed_chunks']} chunks) into vector store."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document indexing failed: {str(e)}"
        )

# -------------------------------------------------------------------
# 4. Sources & Prompt Suggestions
# -------------------------------------------------------------------
@router.get("/sources", response_model=List[SourceDocumentItem], summary="List indexed document sources")
async def get_indexed_sources(
    current_user: dict = Depends(get_current_user)
):
    """Returns the catalog of all indexed enterprise HR documents available to RAG."""
    sources = _vector_store.list_sources()
    return [
        SourceDocumentItem(
            document_id=s["document_id"],
            document_name=s["document_name"],
            title=s["title"],
            category=s.get("category", "HR Policy"),
            file_type=s.get("file_type", "MD"),
            total_pages=s.get("total_pages", 1),
            chunk_count=s.get("chunk_count", 0),
            indexed_at=s.get("indexed_at", "")
        )
        for s in sources
    ]

@router.get("/suggestions", response_model=SuggestedPromptsResponse, summary="Get role-specific prompt suggestions")
async def get_role_suggestions(
    current_user: dict = Depends(get_current_user)
):
    """Provides role-scoped suggested questions for quick-click interactions."""
    role = current_user.get("role", "EMPLOYEE")
    prompts = get_suggested_prompts(role)
    return SuggestedPromptsResponse(role=role, suggestions=prompts)
