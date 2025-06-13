"use client";

import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import './QuestionInterface.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  type: 'user' | 'ai';
}

interface QuestionInterfaceProps {
  uploadedContent: string | null;
  onContentUpload: (content: string) => void;
}

const QuestionInterface: React.FC<QuestionInterfaceProps> = (props) => {
  const { token } = useAuth();
  const { uploadedContent } = props;
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Load chat history when content is uploaded
  useEffect(() => {
    if (!uploadedContent || !token) return;
    
    const loadChatHistory = async () => {
      setLoadingHistory(true);
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/auth/student/${uploadedContent}/questions`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch chat history');
        }

        const data = await response.json();
        const historyMessages = data.questions.map((q: any) => ({
          id: q.content_id,
          role: 'user',
          type: 'user',
          content: q.question,
          timestamp: q.created_at
        })).concat(data.questions.map((q: any) => ({
          id: q.content_id + '_ai',
          role: 'assistant',
          type: 'ai',
          content: q.answer,
          timestamp: q.created_at
        })));

        setMessages(historyMessages);
      } catch (err) {
        console.error('Error loading chat history:', err);
      } finally {
        setLoadingHistory(false);
      }
    };

    loadChatHistory();
  }, [uploadedContent, token]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (!loadingHistory) {
      scrollToBottom();
    }
  }, [loadingHistory]);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        setError(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const formatTime = (date: string): string => {
    return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim() || !token || !uploadedContent || loading) {
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      type: "user",
      content: inputValue,
      timestamp: new Date().toISOString(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    const question = inputValue;
    setInputValue('');
    setError(null);
    
    await handleAskQuestion(question);
  };

  const handleAskQuestion = async (question: string) => {
    try {
      setLoading(true);

      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/content/${uploadedContent}/question`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ question })
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      const answer = data.data.answer;

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        type: "ai",
        content: answer,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (err) {
      console.error('Error asking question:', err);
      setError('Failed to get AI response. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>AI Chat</h2>
        <p>Upload content and ask your questions</p>
        {uploadedContent && (
          <div className="content-status">
            1 document loaded
          </div>
        )}
      </div>

      <div className="chat-messages">
        {loadingHistory ? (
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>Loading chat history...</p>
          </div>
        ) : messages.length === 0 ? (
          <div className="empty-state">
            <h3>Start chatting with AI!</h3>
            <p>Upload your content first and ask any questions about it.</p>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div key={message.id} className={`chat-message ${message.type}`}>
                <div className="avatar">
                  {message.type === "user" ? "🧑" : "🤖"}
                </div>
                <div className="bubble">
                  <div className="content">{message.content}</div>
                  <div className="timestamp">{formatTime(message.timestamp)}</div>
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="chat-message ai">
                <div className="avatar">🤖</div>
                <div className="bubble">
                  <div className="loading-indicator">
                    <span>AI is thinking</span>
                    <div className="loading-dots">
                      <div className="loading-dot"></div>
                      <div className="loading-dot"></div>
                      <div className="loading-dot"></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      <div className="chat-input-container">
        <div className="chat-input">
          {error && (
            <div className="error">{error}</div>
          )}
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your question..."
            disabled={loading || !uploadedContent}
            autoComplete="off"
          />
          <button 
            type="button" 
            onClick={handleSubmit}
            disabled={loading || !inputValue.trim() || !uploadedContent}
          >
            {loading ? '...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default QuestionInterface;