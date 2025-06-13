"use client"

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import './History.css';

interface Question {
  question: string;
  answer: string;
  content_id: string;
  created_at: string;
}

interface HistoryProps {
  studentId: string;
}

const History: React.FC<HistoryProps> = ({ studentId }) => {
  const { token } = useAuth();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStudentQuestions();
  }, [studentId]);

  const fetchStudentQuestions = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/auth/student/${studentId}/questions`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch questions');
      }

      const data = await response.json();
      setQuestions(data.questions);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch questions');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="history-loading">
        <div className="spinner"></div>
        <p>Loading chat history...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="history-error">
        <p>{error}</p>
        <button onClick={fetchStudentQuestions} className="retry-button">
          Retry
        </button>
      </div>
    );
  }

  if (!questions.length) {
    return (
      <div className="history-empty">
        <p>No chat history found for this student</p>
      </div>
    );
  }

  return (
    <div className="history-container">
      <div className="history-header">
        <h2>Chat History</h2>
      </div>
      <div className="history-content">
        {questions.map((question, index) => (
          <div key={index} className="chat-item">
            <div className="message user-message">
              <div className="message-content">
                <p className="message-text">{question.question}</p>
                <p className="message-meta">{new Date(question.created_at).toLocaleString()}</p>
              </div>
            </div>
            <div className="message ai-message">
              <div className="message-content">
                <p className="message-text">{question.answer}</p>
                <p className="message-meta">{new Date(question.created_at).toLocaleString()}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default History;
