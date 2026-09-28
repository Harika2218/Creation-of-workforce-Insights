/**
 * Frontend Service for AI HR Chatbot and RAG Endpoints
 */

import api from './api';
import {
  ChatMessageRequest,
  ChatMessageResponse,
  ConversationSummary,
  ConversationDetail,
  SourceDocumentItem,
  SuggestedPromptsResponse,
} from '../types/chatbot';

export const chatbotService = {
  sendMessage: async (message: string, conversationId?: string): Promise<ChatMessageResponse> => {
    const payload: ChatMessageRequest = {
      message,
      conversation_id: conversationId || undefined,
    };
    const res = await api.post<ChatMessageResponse>('/chatbot/chat', payload);
    return res.data;
  },

  createConversation: async (): Promise<ConversationSummary> => {
    const res = await api.post<ConversationSummary>('/chatbot/conversations');
    return res.data;
  },

  getConversations: async (): Promise<ConversationSummary[]> => {
    const res = await api.get<ConversationSummary[]>('/chatbot/conversations');
    return res.data;
  },

  getConversationDetail: async (conversationId: string): Promise<ConversationDetail> => {
    const res = await api.get<ConversationDetail>(`/chatbot/conversations/${conversationId}`);
    return res.data;
  },

  deleteConversation: async (conversationId: string): Promise<{ status: string; message: string }> => {
    const res = await api.delete<{ status: string; message: string }>(`/chatbot/conversations/${conversationId}`);
    return res.data;
  },

  getSources: async (): Promise<SourceDocumentItem[]> => {
    const res = await api.get<SourceDocumentItem[]>('/chatbot/sources');
    return res.data;
  },

  getSuggestions: async (): Promise<SuggestedPromptsResponse> => {
    const res = await api.get<SuggestedPromptsResponse>('/chatbot/suggestions');
    return res.data;
  },

  indexDocuments: async (): Promise<{ status: string; message: string }> => {
    const res = await api.post<{ status: string; message: string }>('/chatbot/documents/index');
    return res.data;
  },
};
