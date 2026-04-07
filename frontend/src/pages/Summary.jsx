import { useState, useEffect } from 'react';
import Button from '../components/Button';
import LoadingSpinner from '../components/LoadingSpinner';
import ScoreDisplay from '../components/ScoreDisplay';
import { useInterview } from '../contexts/InterviewContext';
import './Summary.css';

export default function Summary({ onNewSession }) {
  const { session, loading, error, getSummary, getFeedback, clearSession } = useInterview();
  const [summary, setSummary] = useState(null);
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    async function loadData() {
      try {
        const summaryData = await getSummary();
        setSummary(summaryData);

        const feedbackData = await getFeedback();
        setFeedback(feedbackData);
      } catch (err) {
        console.error(err);
      }
    }
    loadData();
  }, [getSummary, getFeedback]);

  const handleNewSession = () => {
    clearSession();
    onNewSession();
  };

  if (loading || !summary) {
    return (
      <div className="summary page">
        <LoadingSpinner text="Loading summary..." />
      </div>
    );
  }

  const getScoreColor = (value) => {
    if (value >= 80) return 'var(--success)';
    if (value >= 60) return 'var(--warning)';
    return 'var(--error)';
  };

  return (
    <div className="summary page">
      <div className="summary-header">
        <div className="celebration-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="var(--accent)">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
          </svg>
        </div>
        <h1>Session Complete!</h1>
        <p className="summary-subtitle">
          Here's how you performed in your {summary.topic} interview
        </p>
      </div>

      {/* Overall stats */}
      <div className="summary-stats">
        <div className="stat-card">
          <span className="stat-value" style={{ color: getScoreColor(summary.average_score) }}>
            {summary.average_score}
          </span>
          <span className="stat-label">Average Score</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{summary.total_questions}</span>
          <span className="stat-label">Questions</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{summary.role}</span>
          <span className="stat-label">Role</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{summary.difficulty}</span>
          <span className="stat-label">Difficulty</span>
        </div>
      </div>

      {/* Overall feedback */}
      {feedback && (
        <div className="overall-feedback">
          <h3>Overall Feedback</h3>
          <p>{feedback.overall_feedback}</p>

          {feedback.areas_to_improve && feedback.areas_to_improve.length > 0 && (
            <div className="areas-to-improve">
              <h4>Areas to Improve</h4>
              <ul>
                {feedback.areas_to_improve.map((area, index) => (
                  <li key={index}>{area}</li>
                ))}
              </ul>
            </div>
          )}

          {feedback.overall_score !== undefined && (
            <div className="overall-score">
              <span className="score-label">Overall Score:</span>
              <span
                className="score-value"
                style={{ color: getScoreColor(feedback.overall_score * 10) }}
              >
                {feedback.overall_score}/10
              </span>
            </div>
          )}
        </div>
      )}

      {/* Question breakdown */}
      <div className="breakdown">
        <h3>Question Breakdown</h3>
        <div className="questions-list">
          {summary.breakdown?.map((item, index) => (
            <div key={index} className="question-item">
              <div className="question-item-header">
                <span className="question-num">Q{item.question_number}</span>
                {item.score !== null && (
                  <span
                    className="question-score"
                    style={{ color: getScoreColor(item.score) }}
                  >
                    {item.score}/100
                  </span>
                )}
              </div>
              <p className="question-text">{item.question}</p>
              <p className="answer-text">{item.student_answer}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="summary-actions">
        <Button variant="primary" size="lg" onClick={handleNewSession}>
          Start New Session
        </Button>
      </div>
    </div>
  );
}