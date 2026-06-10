import { useState, useEffect, useRef } from 'react';
import Button from '../components/Button';
import LoadingSpinner from '../components/LoadingSpinner';
import { useInterview } from '../contexts/InterviewContext';
import './Summary.css';

export default function Summary({ onNewSession }) {
  const { getSummaryV2, clearSession } = useInterview();
  const [summary, setSummary] = useState(null);
  const [loadingData, setLoadingData] = useState(true);
  const dataLoaded = useRef(false);

  useEffect(() => {
    // Prevent duplicate calls in React 18 Strict Mode
    if (dataLoaded.current) return;
    dataLoaded.current = true;

    async function loadData() {
      try {
        setLoadingData(true);
        const summaryData = await getSummaryV2();
        setSummary(summaryData);
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingData(false);
      }
    }
    loadData();
  }, [getSummaryV2]);

  const handleNewSession = () => {
    clearSession();
    onNewSession();
  };

  const getScoreColor = (value) => {
    if (value >= 80) return 'var(--success)';
    if (value >= 60) return 'var(--warning)';
    return 'var(--error)';
  };

  const getScoreClass = (value) => {
    if (value >= 80) return 'color-success';
    if (value >= 60) return 'color-warning';
    return 'color-error';
  };

  const getPerformanceLevel = (score) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Needs Work';
    return 'Keep Practicing';
  };

  // Calculate circle progress
  const score = summary?.overall_score || 0;
  const circumference = 2 * Math.PI * 70;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  if (loadingData || !summary) {
    return (
      <div className="summary page">
        <LoadingSpinner text="Generating your interview feedback..." />
      </div>
    );
  }

  return (
    <div className="summary page">
      <div className="summary">
        {/* Header */}
        <div className="summary-header">
          <div className="celebration-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
            </svg>
          </div>
          <h1>Interview Complete!</h1>
          <p className="summary-subtitle">
            Here's your detailed performance analysis
          </p>
        </div>

        {/* Score Section */}
        <div className="score-section">
          <div className="score-circle">
            <svg viewBox="0 0 160 160">
              <circle className="score-circle-bg" cx="80" cy="80" r="70" />
              <circle
                className="score-circle-progress"
                cx="80"
                cy="80"
                r="70"
                stroke={getScoreColor(score)}
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
              />
            </svg>
            <div className="score-circle-text">
              <span className="score-value" style={{ color: getScoreColor(score) }}>
                {Math.round(score)}
              </span>
              <span className="score-label">out of 100</span>
            </div>
          </div>

          <div className="score-details">
            <div className="session-meta">
              <div className="meta-badge">
                <strong>Role:</strong> {summary.role || 'N/A'}
              </div>
              <div className="meta-badge">
                <strong>Topic:</strong> {summary.topic || 'N/A'}
              </div>
              <div className="meta-badge">
                <strong>Difficulty:</strong> {summary.difficulty || 'N/A'}
              </div>
            </div>

            <div className="performance-summary">
              <div className="perf-card">
                <div className="perf-value" style={{ color: getScoreColor(score) }}>
                  {getPerformanceLevel(score)}
                </div>
                <div className="perf-label">Performance</div>
              </div>
              <div className="perf-card">
                <div className="perf-value">
                  {summary.strengths?.length || 0}
                </div>
                <div className="perf-label">Strengths</div>
              </div>
              <div className="perf-card">
                <div className="perf-value">
                  {summary.weaknesses?.length || 0}
                </div>
                <div className="perf-label">Areas to Improve</div>
              </div>
            </div>
          </div>
        </div>

        {/* Feedback Grid */}
        <div className="feedback-grid">
          {/* Strengths */}
          {summary.strengths && summary.strengths.length > 0 && (
            <div className="feedback-card strengths">
              <h3>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                </svg>
                Your Strengths
              </h3>
              <ul>
                {summary.strengths.map((strength, index) => (
                  <li key={index}>{strength}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Weaknesses */}
          {summary.weaknesses && summary.weaknesses.length > 0 && (
            <div className="feedback-card weaknesses">
              <h3>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
                </svg>
                Areas to Improve
              </h3>
              <ul>
                {summary.weaknesses.map((weakness, index) => (
                  <li key={index}>{weakness}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommendations */}
          {summary.recommendations && summary.recommendations.length > 0 && (
            <div className="feedback-card recommendations">
              <h3>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7z" />
                </svg>
                Recommendations
              </h3>
              <ul>
                {summary.recommendations.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Next Steps */}
        {summary.next_steps && summary.next_steps.length > 0 && (
          <div className="next-steps">
            <h3>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M13.5.67s.74 2.65.74 4.8c0 2.06-1.35 3.73-3.41 3.73-2.07 0-3.63-1.67-3.63-3.73l.03-.36C5.21 7.51 4 10.62 4 14c0 4.42 3.58 8 8 8s8-3.58 8-8C20 8.61 17.41 3.8 13.5.67zM11.71 19c-1.78 0-3.22-1.4-3.22-3.14 0-1.62 1.05-2.76 2.81-3.12 1.77-.36 3.6-1.21 4.62-2.58.39 1.29.59 2.65.59 4.04 0 2.65-2.15 4.8-4.8 4.8z" />
              </svg>
              Next Steps to Improve
            </h3>
            <ol>
              {summary.next_steps.map((step, index) => (
                <li key={index}>{step}</li>
              ))}
            </ol>
          </div>
        )}

        {/* Question Breakdown */}
        {summary.question_evaluations && summary.question_evaluations.length > 0 && (
          <div className="breakdown">
            <h2>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9h-4v4h-2v-4H9V9h4V5h2v4h4v2z" />
              </svg>
              Question-by-Question Breakdown
            </h2>
            <div className="questions-list">
              {summary.question_evaluations.map((item, index) => (
                <div key={index} className="question-item">
                  <div className="question-item-header">
                    <span className="question-num">Q{item.question_id}</span>
                    <div className="question-score-badge">
                      <span
                        className="question-score"
                        style={{ color: getScoreColor(item.score) }}
                      >
                        {Math.round(item.score)}%
                      </span>
                      <div className="question-score-bar">
                        <div
                          className="question-score-fill"
                          style={{
                            width: `${item.score}%`,
                            background: getScoreColor(item.score),
                          }}
                        />
                      </div>
                    </div>
                  </div>
                  <div className="question-body">
                    <p className="question-text">{item.question}</p>
                    <div className="answer-block">
                      <strong>Your Answer</strong>
                      <p>{item.user_answer || 'No answer provided'}</p>
                    </div>
                    <div className="feedback-block">
                      <strong>Feedback</strong>
                      <p>{item.feedback}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="summary-actions">
          <Button variant="primary" size="lg" onClick={handleNewSession}>
            Start New Interview
          </Button>
        </div>
      </div>
    </div>
  );
}