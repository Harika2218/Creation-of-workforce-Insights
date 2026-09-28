export interface CitationSource {
  title: string;
  source_type: 'policy_document' | 'database_record' | 'ai_prediction';
  section?: string;
  page?: number;
  document_name?: string;
  snippet?: string;
}

export interface ChatMessageRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatMessageResponse {
  answer: string;
  sources: CitationSource[];
  intent: string;
  conversation_id: string;
  grounded: boolean;
  timestamp: string;
  follow_up_suggestions: string[];
}

export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  intent?: string;
  sources?: CitationSource[];
}

export interface ConversationSummary {
  conversation_id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ConversationDetail {
  conversation_id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: ConversationMessage[];
}

export interface SourceDocumentItem {
  document_id: string;
  document_name: string;
  title: string;
  category: string;
  file_type: string;
  total_pages: number;
  chunk_count: number;
  indexed_at: string;
}

export interface SuggestedPromptsResponse {
  role: string;
  suggestions: string[];
}
