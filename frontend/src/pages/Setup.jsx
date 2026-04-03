import { useState, useEffect } from 'react';
import Button from '../components/Button';
import LoadingSpinner from '../components/LoadingSpinner';
import { useInterview } from '../hooks/useInterview';
import './Setup.css';

export default function Setup({ onStart }) {
  const { options, loading, error, loadOptions, startSession } = useInterview();

  const [role, setRole] = useState('');
  const [topic, setTopic] = useState('');
  const [difficulty, setDifficulty] = useState('Medium');
  const [maxQuestions, setMaxQuestions] = useState(5);
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    loadOptions();
  }, [loadOptions]);

  const handleStart = async () => {
    if (!role || !topic) return;
    setStarting(true);
    try {
      await startSession({ role, topic, difficulty, maxQuestions });
      onStart();
    } catch (err) {
      console.error(err);
    } finally {
      setStarting(false);
    }
  };

  if (loading && !options) {
    return (
      <div className="setup page">
        <LoadingSpinner text="Loading options..." />
      </div>
    );
  }

  const topics = options?.topics?.[role] || [];

  return (
    <div className="setup page">
      <div className="setup-header">
        <button className="back-btn" onClick={onStart}>
          <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" />
          </svg>
          Back
        </button>
        <h2>Configure Interview</h2>
      </div>

      {error && <p className="error-message">{error}</p>}

      <div className="setup-form">
        <div className="form-group">
          <label htmlFor="role">Role</label>
          <select
            id="role"
            value={role}
            onChange={(e) => {
              setRole(e.target.value);
              setTopic('');
            }}
          >
            <option value="">Select a role</option>
            {options?.roles?.map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="topic">Topic</label>
          <select
            id="topic"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            disabled={!role}
          >
            <option value="">Select a topic</option>
            {topics.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="difficulty">Difficulty</label>
          <select
            id="difficulty"
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
          >
            {options?.difficulties?.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="questions">Number of Questions</label>
          <div className="questions-slider">
            <input
              type="range"
              id="questions"
              min="1"
              max="10"
              value={maxQuestions}
              onChange={(e) => setMaxQuestions(Number(e.target.value))}
            />
            <span className="questions-value">{maxQuestions}</span>
          </div>
        </div>

        <Button
          variant="primary"
          size="lg"
          disabled={!role || !topic}
          loading={starting}
          onClick={handleStart}
        >
          Start Interview
        </Button>
      </div>
    </div>
  );
}