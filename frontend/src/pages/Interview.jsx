import { useState } from 'react';
import Button from '../components/Button';
import AudioRecorder from '../components/AudioRecorder';
import FeedbackCard from '../components/FeedbackCard';
import { useInterview } from '../hooks/useInterview';
import './Interview.css';

export default function Interview({ onComplete }) {
  const { session, error, submitAnswer, submitAudioAnswer } = useInterview();
  const [answer, setAnswer] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [mode, setMode] = useState('text');
  const [lastFeedback, setLastFeedback] = useState(null);
  const [showFeedback, setShowFeedback] = useState(false);

  const handleTextSubmit = async (e) => {
    e.preventDefault();
    if (!answer.trim()) return;

    setSubmitting(true);
    try {
      const result = await submitAnswer({ answer });
      setAnswer('');
      setLastFeedback(result);
      setShowFeedback(true);

      if (result.session_complete) {
        onComplete();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleAudioSubmit = async (audioBlob) => {
    setSubmitting(true);
    try {
      const file = new File([audioBlob], 'answer.webm', { type: 'audio/webm' });
      const result = await submitAudioAnswer({ audioFile: file });

      setLastFeedback(result);
      setShowFeedback(true);

      if (result.session_complete) {
        onComplete();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleNextQuestion = () => {
    setShowFeedback(false);
    setLastFeedback(null);
  };

  if (!session) {
    return (
      <div className="interview page">
        <p className="text-secondary">No active session</p>
      </div>
    );
  }

  return (
    <div className="interview page">
      {/* Progress bar */}
      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{
            width: `${(session.questionNumber / session.maxQuestions) * 100}%`,
          }}
        />
      </div>

      {/* Question header */}
      <div className="question-header">
        <span className="question-number">
          Question {session.questionNumber} of {session.maxQuestions}
        </span>
        <div className="question-meta">
          <span className="badge">{session.role}</span>
          <span className="badge">{session.topic}</span>
          <span className="badge">{session.difficulty}</span>
        </div>
      </div>

      {/* Question */}
      <div className="question-card">
        <h2>{session.currentQuestion}</h2>
      </div>

      {/* Feedback display */}
      {showFeedback && lastFeedback ? (
        <FeedbackCard
          feedback={lastFeedback.feedback}
          idealAnswer={lastFeedback.ideal_answer}
          missingConcepts={lastFeedback.missing_concepts}
          score={lastFeedback.score}
          onNext={!lastFeedback.session_complete ? handleNextQuestion : null}
        />
      ) : (
        <>
          {/* Mode toggle */}
          <div className="mode-toggle">
            <button
              className={`mode-btn ${mode === 'text' ? 'active' : ''}`}
              onClick={() => setMode('text')}
              disabled={submitting}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M2.5 4v3h5v12h3V7h5V4h-13zm19 5h-9v3h3v7h3v-7h3V9z" />
              </svg>
              Text
            </button>
            <button
              className={`mode-btn ${mode === 'voice' ? 'active' : ''}`}
              onClick={() => setMode('voice')}
              disabled={submitting}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1 1.93c-3.94-.49-7-3.85-7-7.93h2c0 3.31 2.69 6 6 6s6-2.69 6-6h2c0 4.08-3.06 7.44-7 7.93V19h4v2H8v-2h4v-3.07z" />
              </svg>
              Voice
            </button>
          </div>

          {/* Text input mode */}
          {mode === 'text' && (
            <form className="answer-form" onSubmit={handleTextSubmit}>
              {error && <p className="error-message">{error}</p>}

              <textarea
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                placeholder="Type your answer here..."
                rows={6}
                disabled={submitting}
              />

              <div className="answer-actions">
                <Button
                  type="submit"
                  variant="primary"
                  disabled={!answer.trim() || submitting}
                  loading={submitting}
                >
                  Submit Answer
                </Button>
              </div>
            </form>
          )}

          {/* Voice input mode */}
          {mode === 'voice' && (
            <div className="voice-section">
              {error && <p className="error-message">{error}</p>}
              <AudioRecorder
                onRecordingComplete={handleAudioSubmit}
                disabled={submitting}
              />
            </div>
          )}
        </>
      )}
    </div>
  );
}