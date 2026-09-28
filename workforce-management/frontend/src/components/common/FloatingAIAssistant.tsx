import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, X, Send, Maximize2, Bot, User, BookOpen } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { AIAssistantOrb } from '../3d/AIAssistantOrb';
import { chatbotService } from '../../services/chatbotService';
import { ChatMessageResponse } from '../../types/chatbot';
import { useAuth } from '../../context/AuthContext';

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: string[];
}

export const FloatingAIAssistant: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [inputMessage, setInputMessage] = useState<string>('');
  const [isThinking, setIsThinking] = useState<boolean>(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([
    'What is the standard casual leave policy?',
    'How do I request a shift swap?',
    'Explain the attendance anomaly detection rules.',
    'What are the core employee benefits?',
  ]);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      content: `Hello ${user?.name?.split(' ')[0] || 'there'}! I am your AI Workforce Assistant powered by real-time HR policies and enterprise RAG. How can I assist you today?`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [isMobile, setIsMobile] = useState<boolean>(() => {
    if (typeof window !== 'undefined') return window.innerWidth < 768;
    return false;
  });

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    if (isOpen) {
      chatbotService
        .getSuggestions()
        .then((res) => {
          if (res.suggestions && res.suggestions.length > 0) {
            setSuggestions(res.suggestions.slice(0, 4));
          }
        })
        .catch(() => {});
    }
  }, [isOpen]);

  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  const handleSend = async (textToSend?: string) => {
    const query = (textToSend || inputMessage).trim();
    if (!query || isThinking) return;

    const userMsg: ChatMessage = {
      id: `u-${Date.now()}`,
      sender: 'user',
      content: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputMessage('');
    setIsThinking(true);

    try {
      const response: ChatMessageResponse = await chatbotService.sendMessage(query, conversationId || undefined);
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      const assistantMsg: ChatMessage = {
        id: `a-${Date.now()}`,
        sender: 'assistant',
        content: response.answer || (response as any)?.message || 'I have analyzed your request against enterprise records. How else can I assist you?',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        sources: response.sources?.map((s) => (typeof s === 'string' ? s : s.title || s.document_name || 'HR Policy')),
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      const errorMsg: ChatMessage = {
        id: `err-${Date.now()}`,
        sender: 'assistant',
        content: "I'm having trouble connecting to the workforce intelligence engine right now. Please verify backend services or try again shortly.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsThinking(false);
    }
  };

  return (
    <>
      {/* Floating Trigger Button */}
      {!isOpen && (
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0, opacity: 0 }}
          whileHover={{ scale: 1.08 }}
          whileTap={{ scale: 0.95 }}
          style={{
            position: 'fixed',
            bottom: isMobile ? '76px' : '24px',
            right: isMobile ? '16px' : '24px',
            zIndex: 990,
            display: 'flex',
            alignItems: 'center',
            gap: '0.6rem',
          }}
        >
          {/* Subtle pulse label (hidden on mobile to save space) */}
          {!isMobile && (
            <div
              onClick={() => setIsOpen(true)}
              style={{
                padding: '0.4rem 0.8rem',
                borderRadius: 'var(--radius-full)',
                background: 'var(--bg-card-solid)',
                border: '1px solid var(--border-glass)',
                boxShadow: 'var(--shadow-lg)',
                color: '#FFFFFF',
                fontSize: '0.78rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                backdropFilter: 'blur(12px)',
              }}
            >
              <Sparkles size={14} color="var(--primary)" />
              <span>AI Assistant</span>
            </div>
          )}

          {/* 3D Orb Button */}
          <button
            onClick={() => setIsOpen(true)}
            aria-label="Open AI Workforce Assistant"
            style={{
              width: isMobile ? '50px' : '56px',
              height: isMobile ? '50px' : '56px',
              borderRadius: '50%',
              background: 'var(--gradient-primary)',
              border: '2px solid rgba(255, 255, 255, 0.25)',
              boxShadow: '0 8px 25px rgba(99, 102, 241, 0.45)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              overflow: 'hidden',
              padding: 0,
            }}
          >
            <AIAssistantOrb size={isMobile ? 46 : 52} isThinking={false} />
          </button>
        </motion.div>
      )}

      {/* Expandable Chatbot Drawer */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: isMobile ? '100%' : 30, scale: isMobile ? 1 : 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: isMobile ? '100%' : 20, scale: isMobile ? 1 : 0.95 }}
            transition={{ duration: 0.25, ease: 'easeOut' }}
            style={{
              position: 'fixed',
              bottom: isMobile ? 0 : '24px',
              right: isMobile ? 0 : '24px',
              top: isMobile ? 0 : 'auto',
              left: isMobile ? 0 : 'auto',
              width: isMobile ? '100%' : '390px',
              maxWidth: isMobile ? '100vw' : 'calc(100vw - 32px)',
              height: isMobile ? '100%' : '560px',
              maxHeight: isMobile ? '100vh' : 'calc(100vh - 48px)',
              backgroundColor: 'var(--bg-card-solid)',
              border: isMobile ? 'none' : '1px solid var(--border-glass)',
              borderRadius: isMobile ? 0 : 'var(--radius-xl)',
              boxShadow: '0 20px 45px rgba(0, 0, 0, 0.6), 0 0 30px rgba(99, 102, 241, 0.2)',
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
              zIndex: 2000,
              backdropFilter: 'blur(20px)',
            }}
          >
            {/* Header */}
            <div
              style={{
                padding: '0.9rem 1.1rem',
                borderBottom: '1px solid var(--border-subtle)',
                background: 'rgba(255, 255, 255, 0.02)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                <div style={{ width: '38px', height: '38px', borderRadius: '50%', overflow: 'hidden' }}>
                  <AIAssistantOrb size={38} isThinking={isThinking} />
                </div>
                <div>
                  <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#FFFFFF' }}>
                    AI Workforce Assistant
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                    <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--success)' }} />
                    <span>RAG Knowledge Active</span>
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                <button
                  onClick={() => {
                    setIsOpen(false);
                    navigate('/ai-assistant');
                  }}
                  className="btn btn-ghost btn-icon"
                  style={{ width: '30px', height: '30px' }}
                  title="Expand to Full Page"
                >
                  <Maximize2 size={15} />
                </button>
                <button
                  onClick={() => setIsOpen(false)}
                  className="btn btn-ghost btn-icon"
                  style={{ width: '30px', height: '30px' }}
                  title="Close Assistant"
                >
                  <X size={16} />
                </button>
              </div>
            </div>

            {/* Messages Body */}
            <div
              style={{
                flex: 1,
                overflowY: 'auto',
                padding: '1rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.85rem',
              }}
            >
              {messages.map((m) => {
                const isUser = m.sender === 'user';
                return (
                  <div
                    key={m.id}
                    style={{
                      display: 'flex',
                      flexDirection: isUser ? 'row-reverse' : 'row',
                      gap: '0.6rem',
                      alignItems: 'flex-start',
                    }}
                  >
                    <div
                      style={{
                        width: '28px',
                        height: '28px',
                        borderRadius: '50%',
                        background: isUser ? 'var(--gradient-accent)' : 'rgba(99, 102, 241, 0.2)',
                        color: isUser ? '#0B0F19' : 'var(--primary)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                        fontSize: '0.75rem',
                        fontWeight: 700,
                      }}
                    >
                      {isUser ? <User size={14} /> : <Bot size={14} />}
                    </div>

                    <div
                      style={{
                        maxWidth: '82%',
                        padding: '0.7rem 0.95rem',
                        borderRadius: isUser ? '14px 14px 4px 14px' : '14px 14px 14px 4px',
                        background: isUser ? 'var(--primary)' : 'rgba(255, 255, 255, 0.05)',
                        border: isUser ? 'none' : '1px solid var(--border-subtle)',
                        color: isUser ? '#FFFFFF' : 'var(--text-main)',
                        fontSize: '0.82rem',
                        lineHeight: 1.45,
                        boxShadow: 'var(--shadow-sm)',
                      }}
                    >
                      <div style={{ whiteSpace: 'pre-wrap' }}>{m.content}</div>

                      {/* RAG Sources Accordion */}
                      {m.sources && m.sources.length > 0 && (
                        <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '0.3rem', marginBottom: '0.25rem' }}>
                            <BookOpen size={11} />
                            <span>Verified Policy Citations:</span>
                          </div>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.3rem' }}>
                            {m.sources.map((src, i) => (
                              <span
                                key={i}
                                style={{
                                  fontSize: '0.68rem',
                                  padding: '0.1rem 0.4rem',
                                  borderRadius: '4px',
                                  background: 'rgba(99, 102, 241, 0.15)',
                                  color: 'var(--primary)',
                                  border: '1px solid rgba(99, 102, 241, 0.3)',
                                }}
                              >
                                {src}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      <div style={{ fontSize: '0.68rem', color: isUser ? 'rgba(255,255,255,0.7)' : 'var(--text-dim)', textAlign: 'right', marginTop: '0.25rem' }}>
                        {m.timestamp}
                      </div>
                    </div>
                  </div>
                );
              })}

              {isThinking && (
                <div style={{ display: 'flex', gap: '0.6rem', alignItems: 'center' }}>
                  <div
                    style={{
                      width: '28px',
                      height: '28px',
                      borderRadius: '50%',
                      background: 'rgba(99, 102, 241, 0.2)',
                      color: 'var(--primary)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Bot size={14} />
                  </div>
                  <div
                    style={{
                      padding: '0.6rem 0.9rem',
                      borderRadius: '14px 14px 14px 4px',
                      background: 'rgba(255, 255, 255, 0.05)',
                      border: '1px solid var(--border-subtle)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.4rem',
                      fontSize: '0.78rem',
                      color: 'var(--text-dim)',
                    }}
                  >
                    <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--primary)', animation: 'pulse 1s infinite' }} />
                    <span>Analyzing HR Knowledge Base...</span>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Quick Suggestions */}
            {messages.length < 4 && (
              <div
                style={{
                  padding: '0.5rem 0.75rem',
                  borderTop: '1px solid var(--border-subtle)',
                  background: 'rgba(0, 0, 0, 0.15)',
                  display: 'flex',
                  gap: '0.4rem',
                  overflowX: 'auto',
                }}
              >
                {suggestions.map((s, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(s)}
                    style={{
                      whiteSpace: 'nowrap',
                      padding: '0.3rem 0.6rem',
                      borderRadius: 'var(--radius-full)',
                      background: 'rgba(255, 255, 255, 0.04)',
                      border: '1px solid var(--border-subtle)',
                      color: 'var(--text-muted)',
                      fontSize: '0.72rem',
                      cursor: 'pointer',
                      flexShrink: 0,
                    }}
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}

            {/* Message Input Footer */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              style={{
                padding: '0.75rem 1rem',
                borderTop: '1px solid var(--border-subtle)',
                background: 'rgba(255, 255, 255, 0.01)',
                display: 'flex',
                gap: '0.5rem',
              }}
            >
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask about leave, attendance, payroll, policies..."
                className="form-control"
                style={{ flex: 1, height: '38px', fontSize: '0.82rem' }}
                disabled={isThinking}
              />
              <button
                type="submit"
                disabled={!inputMessage.trim() || isThinking}
                className="btn btn-primary"
                style={{ width: '38px', height: '38px', padding: 0 }}
                aria-label="Send message"
              >
                <Send size={16} />
              </button>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};
