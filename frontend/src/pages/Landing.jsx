import Button from '../components/Button';
import './Landing.css';

export default function Landing({ onStart }) {
  return (
    <div className="landing page">
      <div className="landing-hero">
        <div className="logo">
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
            <rect width="48" height="48" rx="12" fill="var(--accent)" />
            <path
              d="M14 32V16h6l6 10 6-10h6v16h-5v-10l-5 8h-4l-5-8v10h-5z"
              fill="white"
            />
          </svg>
        </div>
        <h1>PrepIQ</h1>
        <p className="tagline">Master your next interview with AI-powered practice</p>
      </div>

      <div className="features">
        <div className="feature">
          <div className="feature-icon">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
              <path d="M10 2a8 8 0 100 16 8 8 0 000-16zm1 11H9V9h2v4zm0-5H9V5h2v3z" />
            </svg>
          </div>
          <h3>Real Questions</h3>
          <p>Practice with actual interview questions from top companies</p>
        </div>

        <div className="feature">
          <div className="feature-icon">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
              <path d="M10 2a8 8 0 100 16 8 8 0 000-16zm-1 13V5h2v10H9z" />
            </svg>
          </div>
          <h3>Instant Feedback</h3>
          <p>Get detailed feedback and scores on your answers</p>
        </div>

        <div className="feature">
          <div className="feature-icon">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
              <path d="M10 2a6 6 0 00-6 6v2H3a1 1 0 00-1 1v6a1 1 0 001 1h1v2a1 1 0 001 1h6a1 1 0 001-1v-2h1a1 1 0 001-1v-6a1 1 0 00-1-1h-1V8a6 6 0 00-6-6z" />
            </svg>
          </div>
          <h3>Voice Answers</h3>
          <p>Practice speaking your answers just like the real interview</p>
        </div>
      </div>

      <Button variant="primary" size="lg" onClick={onStart}>
        Start Practice
      </Button>

      <p className="powered-by">Powered by AI • Local processing • Private</p>
    </div>
  );
}