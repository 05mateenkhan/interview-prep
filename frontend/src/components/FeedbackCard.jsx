import ScoreDisplay from './ScoreDisplay';
import './FeedbackCard.css';

export default function FeedbackCard({ feedback, idealAnswer, missingConcepts, score, onNext }) {
  return (
    <div className="feedback-card">
      <div className="feedback-header">
        <h3>Feedback</h3>
        <ScoreDisplay score={score} />
      </div>

      <div className="feedback-content">
        <div className="feedback-section">
          <h4>Your Feedback</h4>
          <p className="feedback-text">{feedback}</p>
        </div>

        {missingConcepts?.length > 0 && (
          <div className="feedback-section">
            <h4>Missing Concepts</h4>
            <ul className="missing-concepts">
              {missingConcepts.map((concept, index) => (
                <li key={index}>{concept}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="feedback-section">
          <h4>Ideal Answer</h4>
          <div className="ideal-answer">
            <p>{idealAnswer}</p>
          </div>
        </div>
      </div>

      {onNext && (
        <div className="feedback-actions">
          <button className="next-btn" onClick={onNext}>
            Next Question
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
}