import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import './Analytics.css';

interface AnalyticsData {
  _id: string;
  student_id: string;
  total_contents_uploaded: number;
  total_questions_asked: number;
  total_answer_length: number;
}

const Analytics: React.FC = () => {
  const [studentId, setStudentId] = useState('');
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { token } = useAuth();
  
  const fetchAnalytics = async (studentId: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/analytics/student/${studentId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.message || 'Failed to fetch analytics');
      }

      const data = await response.json();
      setAnalyticsData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch analytics');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.MouseEvent | React.KeyboardEvent) => {
    e.preventDefault();
    if (!studentId.trim()) {
      setError('Please enter a valid student ID');
      return;
    }
    fetchAnalytics(studentId);
  };

  const averageAnswerLength = analyticsData?.total_questions_asked 
    ? (analyticsData.total_answer_length / analyticsData.total_questions_asked).toFixed(1)
    : '0';

  return (
    <div className="analytics-container">
      <div className="analytics-wrapper">
        <div className="header-section">
          <div className="header-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 3v5h5M6 17.5L12 12l6 5.5M21 3l-3.5 3.5L21 10"/>
            </svg>
          </div>
          <h1 className="main-title">Analytics Dashboard</h1>
          <p className="main-subtitle">
            Comprehensive insights into student learning patterns and engagement metrics
          </p>
        </div>

        <div className="search-section">
          <div className="search-container">
            <div className="search-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8"/>
                <path d="m21 21-4.35-4.35"/>
              </svg>
            </div>
            <input
              type="text"
              value={studentId}
              onChange={(e) => setStudentId(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSubmit(e)}
              placeholder="Enter Student ID"
              disabled={loading}
              className="search-input"
            />
            <button
              onClick={handleSubmit}
              disabled={loading || !studentId.trim()}
              className="search-button"
            >
              {loading ? (
                <div className="loading-container">
                  <div className="spinner"></div>
                  <span>Analyzing...</span>
                </div>
              ) : (
                'View Analytics'
              )}
            </button>
          </div>
        </div>

        {error && (
          <div className="error-section">
            <div className="error-message">
              <div className="error-icon">⚠️</div>
              <div className="error-content">
                <h3>Error</h3>
                <p>{error}</p>
              </div>
            </div>
          </div>
        )}

        {analyticsData && (
          <div className="results-section">
            <div className="metrics-grid">
              <div className="metric-card content-card">
                <div className="card-header">
                  <div className="card-icon content-icon">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                      <polyline points="14,2 14,8 20,8"/>
                    </svg>
                  </div>
                  <div className="card-value">
                    <div className="main-number">{analyticsData.total_contents_uploaded}</div>
                  </div>
                </div>
                <div className="card-info">
                  <h3>Content Uploaded</h3>
                  <p>Total documents and materials uploaded</p>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill content-progress"
                    style={{ width: `${Math.min(analyticsData.total_contents_uploaded * 2, 100)}%` }}
                  ></div>
                </div>
              </div>

              <div className="metric-card questions-card">
                <div className="card-header">
                  <div className="card-icon questions-icon">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                    </svg>
                  </div>
                  <div className="card-value">
                    <div className="main-number">{analyticsData.total_questions_asked}</div>
                  </div>
                </div>
                <div className="card-info">
                  <h3>Questions Asked</h3>
                  <p>Total inquiries and interactions</p>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill questions-progress"
                    style={{ width: `${Math.min(analyticsData.total_questions_asked / 2, 100)}%` }}
                  ></div>
                </div>
              </div>

              <div className="metric-card quality-card">
                <div className="card-header">
                  <div className="card-icon quality-icon">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="22,12 18,12 15,21 9,3 6,12 2,12"/>
                    </svg>
                  </div>
                  <div className="card-value">
                    <div className="main-number">{averageAnswerLength}</div>
                  </div>
                </div>
                <div className="card-info">
                  <h3>Answer Quality</h3>
                  <p>Average response length per question</p>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill quality-progress"
                    style={{ width: `${Math.min(parseFloat(averageAnswerLength) / 5, 100)}%` }}
                  ></div>
                </div>
              </div>
            </div>

            <div className="details-section">
              <div className="details-header">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="22,12 18,12 15,21 9,3 6,12 2,12"/>
                </svg>
                <h2>Detailed Statistics</h2>
              </div>
              
              <div className="details-grid">
                <div className="detail-item">
                  <div className="detail-icon user-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                      <circle cx="12" cy="7" r="4"/>
                    </svg>
                  </div>
                  <div className="detail-label">Student ID</div>
                  <div className="detail-value">{analyticsData.student_id}</div>
                </div>
                
                <div className="detail-item">
                  <div className="detail-icon chars-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                      <polyline points="14,2 14,8 20,8"/>
                    </svg>
                  </div>
                  <div className="detail-label">Total Characters</div>
                  <div className="detail-value">{analyticsData.total_answer_length.toLocaleString()}</div>
                </div>
                
                <div className="detail-item">
                  <div className="detail-icon engagement-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M3 3v5h5M6 17.5L12 12l6 5.5M21 3l-3.5 3.5L21 10"/>
                    </svg>
                  </div>
                  <div className="detail-label">Engagement Score</div>
                  <div className="detail-value">
                    {Math.round((analyticsData.total_questions_asked / analyticsData.total_contents_uploaded) * 10) / 10}
                  </div>
                </div>
                
                <div className="detail-item">
                  <div className="detail-icon activity-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="22,12 18,12 15,21 9,3 6,12 2,12"/>
                    </svg>
                  </div>
                  <div className="detail-label">Activity Level</div>
                  <div className="detail-value">
                    {analyticsData.total_questions_asked > 100 ? 'High' : analyticsData.total_questions_asked > 50 ? 'Medium' : 'Low'}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Analytics;