import React, { useState, useEffect, useRef } from 'react';
import {
  Bot,
  Sparkles,
  Send,
  Plus,
  Trash2,
  FileText,
  Database,
  BrainCircuit,
  CheckCircle2,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Shield,
  BookOpen,
  MessageSquare,
  Clock,
  Layers,
  Mic,
  MicOff,
  Volume2
} from 'lucide-react';
import { AIAssistantOrb } from '../../components/3d';
import { useAuth } from '../../context/AuthContext';
import { chatbotService } from '../../services/chatbotService';
import {
  ChatMessageResponse,
  ConversationMessage,
  ConversationSummary,
  SourceDocumentItem,
  CitationSource,
} from '../../types/chatbot';

export const ChatbotPage: React.FC = () => {
  const { user } = useAuth();
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [sourcesList, setSourcesList] = useState<SourceDocumentItem[]>([]);
  const [activeTab, setActiveTab] = useState<'chat' | 'sources'>('chat');
  const [expandedSources, setExpandedSources] = useState<{ [key: number]: boolean }>({});
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const recognitionRef = useRef<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Detect Web Speech API support
    const SpeechRec = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRec) {
      setSpeechSupported(true);
      try {
        const recognition = new SpeechRec();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onresult = (event: any) => {
          if (event.results && event.results[0] && event.results[0][0]) {
            const transcript = event.results[0][0].transcript;
            setInputText(transcript);
          }
          setIsListening(false);
        };

        recognition.onerror = () => {
          setIsListening(false);
        };

        recognition.onend = () => {
          setIsListening(false);
        };

        recognitionRef.current = recognition;
      } catch (e) {
        setSpeechSupported(false);
      }
    }
  }, []);

  const toggleVoiceInput = () => {
    if (!speechSupported || !recognitionRef.current) return;
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch (err) {
        setIsListening(false);
      }
    }
  };

  const speakText = (text: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const cleanText = text.replace(/\[Source \d+\]/g, '').replace(/[*_#]/g, '');
      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  };

  useEffect(() => {
    loadConversations();
    loadSuggestions();
    loadSources();
  }, []);

  useEffect(() => {
    if (activeConversationId) {
      loadConversationHistory(activeConversationId);
    } else {
      setMessages([]);
    }
  }, [activeConversationId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversations = async () => {
    try {
      const data = await chatbotService.getConversations();
      setConversations(data);
      if (data.length > 0 && !activeConversationId) {
        setActiveConversationId(data[0].conversation_id);
      }
    } catch (err) {
      console.error('Failed to load conversations:', err);
    }
  };

  const loadSuggestions = async () => {
    try {
      const data = await chatbotService.getSuggestions();
      setSuggestions(data.suggestions);
    } catch (err) {
      console.error('Failed to load prompt suggestions:', err);
    }
  };

  const loadSources = async () => {
    try {
      const data = await chatbotService.getSources();
      setSourcesList(data);
    } catch (err) {
      console.error('Failed to load document sources:', err);
    }
  };

  const loadConversationHistory = async (convId: string) => {
    try {
      const detail = await chatbotService.getConversationDetail(convId);
      setMessages(detail.messages);
    } catch (err) {
      console.error('Failed to load conversation history:', err);
    }
  };

  const handleStartNewChat = async () => {
    try {
      const newConv = await chatbotService.createConversation();
      setConversations((prev) => [newConv, ...prev]);
      setActiveConversationId(newConv.conversation_id);
      setMessages([]);
    } catch (err) {
      console.error('Failed to create new conversation:', err);
    }
  };

  const handleDeleteConversation = async (convId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm('Delete this conversation history?')) return;
    try {
      await chatbotService.deleteConversation(convId);
      setConversations((prev) => prev.filter((c) => c.conversation_id !== convId));
      if (activeConversationId === convId) {
        setActiveConversationId(null);
        setMessages([]);
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    }
  };

  const handleSendMessage = async (textToSend?: string) => {
    const text = textToSend || inputText;
    if (!text.trim() || isLoading) return;

    const userMessage: ConversationMessage = {
      role: 'user',
      content: text.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response: ChatMessageResponse = await chatbotService.sendMessage(
        text.trim(),
        activeConversationId || undefined
      );

      if (!activeConversationId && response.conversation_id) {
        setActiveConversationId(response.conversation_id);
        loadConversations();
      }

      const assistantMessage: ConversationMessage = {
        role: 'assistant',
        content: response.answer,
        timestamp: response.timestamp,
        intent: response.intent,
        sources: response.sources,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      const errorMsg =
        err.response?.data?.detail || 'Failed to reach AI HR Assistant. Please check system status.';
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `⚠️ ${errorMsg}`,
          timestamp: new Date().toISOString(),
          sources: [],
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSourceExpand = (idx: number) => {
    setExpandedSources((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  return (
    <div style={{ display: 'flex', height: 'calc(100vh - 120px)', gap: '16px', position: 'relative' }}>
      {/* 1. Left Sidebar: Conversation Threads & Policy Sources */}
      <div
        style={{
          width: '280px',
          backgroundColor: 'var(--bg-card)',
          borderRadius: '12px',
          border: 'var(--border-glass)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          flexShrink: 0,
        }}
      >
        <div style={{ padding: '16px', borderBottom: 'var(--border-glass)' }}>
          <button
            onClick={handleStartNewChat}
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              padding: '10px 14px',
              backgroundColor: 'var(--color-primary)',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              fontWeight: 600,
              cursor: 'pointer',
              fontSize: '0.9rem',
              boxShadow: '0 2px 8px rgba(99, 102, 241, 0.25)',
            }}
          >
            <Plus size={16} /> New Conversation
          </button>

          <div style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
            <button
              onClick={() => setActiveTab('chat')}
              style={{
                flex: 1,
                padding: '6px',
                fontSize: '0.8rem',
                borderRadius: '6px',
                border: 'none',
                backgroundColor: activeTab === 'chat' ? 'var(--bg-hover)' : 'transparent',
                color: activeTab === 'chat' ? 'var(--color-primary)' : 'var(--text-muted)',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '4px',
              }}
            >
              <MessageSquare size={14} /> Chats ({conversations.length})
            </button>
            <button
              onClick={() => setActiveTab('sources')}
              style={{
                flex: 1,
                padding: '6px',
                fontSize: '0.8rem',
                borderRadius: '6px',
                border: 'none',
                backgroundColor: activeTab === 'sources' ? 'var(--bg-hover)' : 'transparent',
                color: activeTab === 'sources' ? 'var(--color-primary)' : 'var(--text-muted)',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '4px',
              }}
            >
              <BookOpen size={14} /> Policies ({sourcesList.length})
            </button>
          </div>
        </div>

        {/* Tab 1: Conversation History */}
        {activeTab === 'chat' ? (
          <div style={{ flex: 1, overflowY: 'auto', padding: '8px' }}>
            {conversations.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '32px 16px', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                <Clock size={28} style={{ opacity: 0.4, marginBottom: '8px' }} />
                <p>No conversation history yet.</p>
                <p style={{ fontSize: '0.75rem' }}>Start an inquiry to begin.</p>
              </div>
            ) : (
              conversations.map((c) => {
                const isActive = c.conversation_id === activeConversationId;
                return (
                  <div
                    key={c.conversation_id}
                    onClick={() => setActiveConversationId(c.conversation_id)}
                    style={{
                      padding: '10px 12px',
                      borderRadius: '8px',
                      marginBottom: '4px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      backgroundColor: isActive ? 'var(--bg-hover)' : 'transparent',
                      borderLeft: isActive ? '3px solid var(--color-primary)' : '3px solid transparent',
                      transition: 'background-color 0.2s',
                    }}
                  >
                    <div style={{ overflow: 'hidden', paddingRight: '8px' }}>
                      <p
                        style={{
                          margin: 0,
                          fontSize: '0.85rem',
                          fontWeight: isActive ? 600 : 400,
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          color: 'var(--text-main)',
                        }}
                      >
                        {c.title}
                      </p>
                      <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                        {new Date(c.updated_at).toLocaleDateString([], { month: 'short', day: 'numeric' })}
                      </span>
                    </div>
                    <button
                      onClick={(e) => handleDeleteConversation(c.conversation_id, e)}
                      title="Delete Conversation"
                      style={{
                        background: 'none',
                        border: 'none',
                        color: 'var(--text-muted)',
                        cursor: 'pointer',
                        padding: '4px',
                        borderRadius: '4px',
                        display: 'flex',
                      }}
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>
                );
              })
            )}
          </div>
        ) : (
          /* Tab 2: Indexed Policy Documents Catalog */
          <div style={{ flex: 1, overflowY: 'auto', padding: '12px' }}>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '8px' }}>
              Indexed in RAG Vector Store:
            </p>
            {sourcesList.map((doc) => (
              <div
                key={doc.document_id}
                style={{
                  padding: '8px 10px',
                  borderRadius: '6px',
                  backgroundColor: 'var(--bg-hover)',
                  marginBottom: '8px',
                  fontSize: '0.8rem',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 600 }}>
                  <FileText size={14} color="var(--color-primary)" />
                  <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {doc.title}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '0.7rem', marginTop: '4px' }}>
                  <span>{doc.category}</span>
                  <span>{doc.chunk_count} chunks</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 2. Main Chat Panel */}
      <div
        style={{
          flex: 1,
          backgroundColor: 'var(--bg-card)',
          borderRadius: '12px',
          border: 'var(--border-glass)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: '14px 20px',
            borderBottom: 'var(--border-glass)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            backgroundColor: 'var(--bg-hover)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ width: '42px', height: '42px', borderRadius: '50%', overflow: 'hidden' }}>
              <AIAssistantOrb size={42} isThinking={isLoading} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <h2 style={{ margin: 0, fontSize: '1.05rem', fontWeight: 700 }}>AI HR Assistant</h2>
                <span
                  style={{
                    fontSize: '0.7rem',
                    padding: '2px 8px',
                    borderRadius: '12px',
                    backgroundColor: 'rgba(16, 185, 129, 0.12)',
                    color: '#10b981',
                    fontWeight: 600,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                  }}
                >
                  <CheckCircle2 size={11} /> Grounded RAG
                </span>
              </div>
              <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Role: <strong>{user?.role}</strong> | Scoped: {user?.employee_id || user?.name}
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span
              style={{
                fontSize: '0.72rem',
                color: 'var(--text-muted)',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              <Shield size={13} color="var(--primary)" /> RBAC Protected
            </span>
          </div>
        </div>

        {/* Message Stream Area */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '20px' }}>
          {messages.length === 0 ? (
            /* Empty State: Suggested Prompts with 3D Holographic Orb */
            <div
              style={{
                maxWidth: '680px',
                margin: '20px auto',
                textAlign: 'center',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '16px' }}>
                <AIAssistantOrb size={130} isThinking={isLoading} />
              </div>
              <h3 style={{ margin: '0 0 8px', fontSize: '1.25rem', fontWeight: 700 }}>
                Welcome, {user?.name || 'Colleague'}!
              </h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '24px' }}>
                I am your intelligent HR assistant. I can answer questions about your leave balance,
                attendance, shifts, and salary records, or explain verified company policies with exact citations.
              </p>

              <div style={{ textAlign: 'left', marginBottom: '12px' }}>
                <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Suggested Questions for {user?.role}:
                </span>
              </div>

              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                  gap: '10px',
                }}
              >
                {suggestions.map((prompt, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(prompt)}
                    style={{
                      padding: '12px 14px',
                      borderRadius: '8px',
                      border: 'var(--border-glass)',
                      backgroundColor: 'var(--bg-hover)',
                      color: 'var(--text-main)',
                      fontSize: '0.85rem',
                      textAlign: 'left',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      transition: 'border-color 0.2s, transform 0.1s',
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.borderColor = 'var(--color-primary)')}
                    onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'var(--border-glass)')}
                  >
                    <span>{prompt}</span>
                    <Sparkles size={13} style={{ opacity: 0.5, flexShrink: 0, marginLeft: '6px' }} />
                  </button>
                ))}
              </div>
            </div>
          ) : (
            /* Chronological Message Stream */
            messages.map((m, idx) => {
              const isUser = m.role === 'user';
              return (
                <div
                  key={idx}
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: isUser ? 'flex-end' : 'flex-start',
                    marginBottom: '18px',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      gap: '10px',
                      maxWidth: '82%',
                      flexDirection: isUser ? 'row-reverse' : 'row',
                    }}
                  >
                    <div
                      style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '50%',
                        backgroundColor: isUser ? 'var(--color-primary)' : 'rgba(99, 102, 241, 0.15)',
                        color: isUser ? '#fff' : 'var(--color-primary)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                        fontSize: '0.8rem',
                        fontWeight: 700,
                      }}
                    >
                      {isUser ? 'ME' : <Bot size={18} />}
                    </div>

                    <div
                      style={{
                        padding: '12px 16px',
                        borderRadius: '12px',
                        backgroundColor: isUser ? 'var(--color-primary)' : 'var(--bg-hover)',
                        color: isUser ? '#fff' : 'var(--text-main)',
                        fontSize: '0.9rem',
                        lineHeight: 1.55,
                        boxShadow: '0 1px 4px rgba(0,0,0,0.05)',
                        border: isUser ? 'none' : 'var(--border-glass)',
                        whiteSpace: 'pre-wrap',
                      }}
                    >
                      {m.content}

                      {/* Expandable Citations Block for Assistant Answers */}
                      {!isUser && m.sources && m.sources.length > 0 && (
                        <div
                          style={{
                            marginTop: '12px',
                            paddingTop: '10px',
                            borderTop: '1px solid rgba(255, 255, 255, 0.08)',
                          }}
                        >
                          <button
                            onClick={() => toggleSourceExpand(idx)}
                            style={{
                              background: 'none',
                              border: 'none',
                              color: 'var(--color-primary)',
                              fontSize: '0.75rem',
                              fontWeight: 600,
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '4px',
                              padding: 0,
                              marginBottom: expandedSources[idx] ? '8px' : 0,
                            }}
                          >
                            <Layers size={13} />
                            <span>
                              {m.sources.length} Verified Source Reference{m.sources.length > 1 ? 's' : ''}
                            </span>
                            {expandedSources[idx] ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                          </button>

                          {/* Text-to-Speech Playback Button */}
                          <button
                            onClick={() => speakText(m.content)}
                            title="Listen to this response"
                            style={{
                              background: 'none',
                              border: 'none',
                              color: 'var(--text-muted)',
                              fontSize: '0.75rem',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '4px',
                              padding: '2px 0',
                              marginTop: '4px',
                            }}
                          >
                            <Volume2 size={13} /> Listen
                          </button>

                          {expandedSources[idx] && (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                              {m.sources.map((s, sIdx) => (
                                <div
                                  key={sIdx}
                                  style={{
                                    padding: '6px 10px',
                                    borderRadius: '6px',
                                    backgroundColor: 'rgba(0,0,0,0.15)',
                                    fontSize: '0.75rem',
                                  }}
                                >
                                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 600 }}>
                                    {s.source_type === 'policy_document' && <FileText size={12} color="#60a5fa" />}
                                    {s.source_type === 'database_record' && <Database size={12} color="#34d399" />}
                                    {s.source_type === 'ai_prediction' && <BrainCircuit size={12} color="#a78bfa" />}
                                    <span>{s.title}</span>
                                    {s.section && (
                                      <span style={{ opacity: 0.7 }}>
                                        ({s.section}{s.page ? `, Page ${s.page}` : ''})
                                      </span>
                                    )}
                                  </div>
                                  {s.snippet && (
                                    <p
                                      style={{
                                        margin: '4px 0 0',
                                        fontSize: '0.72rem',
                                        opacity: 0.8,
                                        fontStyle: 'italic',
                                      }}
                                    >
                                      "{s.snippet}"
                                    </p>
                                  )}
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>

                  <span
                    style={{
                      fontSize: '0.68rem',
                      color: 'var(--text-muted)',
                      marginTop: '4px',
                      paddingLeft: isUser ? 0 : '42px',
                      paddingRight: isUser ? '42px' : 0,
                    }}
                  >
                    {new Date(m.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              );
            })
          )}

          {/* Typing Indicator */}
          {isLoading && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  backgroundColor: 'rgba(99, 102, 241, 0.15)',
                  color: 'var(--color-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Bot size={18} />
              </div>
              <div
                style={{
                  padding: '10px 16px',
                  borderRadius: '12px',
                  backgroundColor: 'var(--bg-hover)',
                  color: 'var(--text-muted)',
                  fontSize: '0.85rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                <RefreshCw size={14} className="animate-spin" />
                <span>Checking company records and analyzing policy corpus...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar Footer */}
        <div style={{ padding: '14px 20px', borderTop: 'var(--border-glass)' }}>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            style={{ display: 'flex', gap: '10px', alignItems: 'center' }}
          >
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Ask an HR question (e.g., 'What is my leave balance?', 'What is the maternity leave policy?')..."
              disabled={isLoading}
              style={{
                flex: 1,
                padding: '12px 16px',
                borderRadius: '8px',
                border: 'var(--border-glass)',
                backgroundColor: 'var(--bg-hover)',
                color: 'var(--text-main)',
                fontSize: '0.9rem',
                outline: 'none',
              }}
              onFocus={(e) => (e.target.style.borderColor = 'var(--color-primary)')}
              onBlur={(e) => (e.target.style.borderColor = 'var(--border-glass)')}
            />
            <button
              type="button"
              onClick={toggleVoiceInput}
              disabled={isLoading || !speechSupported}
              title={speechSupported ? (isListening ? 'Stop listening' : 'Start voice input (Speech-to-Text)') : 'Voice input requires Web Speech API browser support'}
              style={{
                padding: '12px 14px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: isListening ? '#ef4444' : 'var(--bg-hover)',
                color: isListening ? '#fff' : (speechSupported ? 'var(--color-primary)' : 'var(--text-muted)'),
                cursor: speechSupported ? 'pointer' : 'not-allowed',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.9rem',
                transition: 'all 0.2s',
              }}
            >
              {isListening ? <MicOff size={16} className="animate-pulse" /> : <Mic size={16} />}
            </button>
            <button
              type="submit"
              disabled={isLoading || !inputText.trim()}
              style={{
                padding: '12px 18px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: 'var(--color-primary)',
                color: '#fff',
                fontWeight: 600,
                cursor: isLoading || !inputText.trim() ? 'not-allowed' : 'pointer',
                opacity: isLoading || !inputText.trim() ? 0.6 : 1,
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '0.9rem',
              }}
            >
              <Send size={16} /> Send
            </button>
          </form>

          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginTop: '8px',
              fontSize: '0.72rem',
              color: 'var(--text-muted)',
            }}
          >
            <span>Press Enter to send. Shift+Enter for new line.</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Shield size={12} color="#10b981" /> No automated adverse decisions • Strictly cited answers
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
