# RAG HR POLICY ASSISTANT ARCHITECTURE DIAGRAM

**System:** AI-Powered Workforce Management Automation System (InnovateCorp HRvantage)  
**Document:** `docs/diagrams/rag_architecture.md`  

---

```mermaid
graph TD
    subgraph Client_Query ["1. Conversational Client (Voice / Text)"]
        UserQuery["Employee / Manager Query:
        'What is our bereavement leave policy and can I see EMP002's balance?'"]
        VoiceSTT["W3C Web Speech API Speech-to-Text"]
    end

    subgraph Defense_Gate ["2. Input Guardrails & Pre-Retrieval Auth Gate"]
        Guardrails["backend.ai.chatbot.guardrails.GuardrailEngine
        • Regex Prompt Injection Interceptor
        • Adversarial Pattern Detector
        • PII Sanitizer (Redacts Cards, External Phones)"]
        
        AuthGate["backend.ai.chatbot.authorization.AuthorizationGate
        • Enforces RBAC BEFORE Querying Database
        • Checks caller role vs target record
        • BLOCKS query for EMP002's balance with 403 Forbidden"]
    end

    subgraph Knowledge_Retrieval ["3. Knowledge Base & Scoped Retrieval"]
        DocCorpus["Official HR Policies (data/hr_policies/)
        • Leave Policy, Code of Conduct, Travel Guidelines"]
        
        ChunkIndex["Semantic Chunks (500 chars, 100 overlap)
        • Tagged with doc_id, section, effective date"]
        
        VectorSearch["Cosine Similarity Search
        • Retrieves Top 3 Chunks (Threshold >= 0.35)"]
        
        DBScopedLookup["Authorized Scoped DB Lookup
        • Only retrieves authenticated user's own data"]
    end

    subgraph Generation_Citations ["4. Grounded Generation & Citation Verification"]
        LLMEngine["Grounded LLM Generator
        • Instructed to rely exclusively on retrieved context
        • Rejects hallucination when context is absent"]
        
        CitationEngine["backend.ai.chatbot.citations.CitationEngine
        • Attaches precise clickable citations:
          [Source: HR-POL-02, Section 3.1 - Bereavement]"]
        
        ConversationHistory["Context Window (Last 6 turns)
        • Persisted in db.chatbot_conversations & messages"]
    end

    VoiceSTT --> UserQuery
    UserQuery --> Guardrails
    Guardrails -->|Safe Query| AuthGate
    Guardrails -->|Adversarial Payload| RejectAdversarial["Return Security Rejection"]

    AuthGate -->|Unauthorized Target (EMP002)| DenyAccess["Return HTTP 403 / Scope Denial"]
    AuthGate -->|Authorized Query| VectorSearch & DBScopedLookup

    DocCorpus --> ChunkIndex --> VectorSearch
    VectorSearch & DBScopedLookup --> LLMEngine
    LLMEngine --> CitationEngine --> ConversationHistory
    ConversationHistory --> VerifiedAnswer["Final Answer with Grounded Policy Citations"]
```
