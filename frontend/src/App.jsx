import { useState } from 'react';
import { InterviewProvider, useInterview } from './contexts/InterviewContext';
import Landing from './pages/Landing';
import Setup from './pages/Setup';
import Interview from './pages/Interview';
import Summary from './pages/Summary';
import './App.css';

function AppContent() {
  const [page, setPage] = useState('landing');
  const { session } = useInterview();

  const goToSetup = () => setPage('setup');
  const goToLanding = () => setPage('landing');
  const goToInterview = () => setPage('interview');
  const goToSummary = () => setPage('summary');

  return (
    <div className="app">
      <main className="container">
        {page === 'landing' && <Landing onStart={goToSetup} />}
        {page === 'setup' && <Setup onStart={goToInterview} />}
        {page === 'interview' && session && (
          <Interview onComplete={goToSummary} />
        )}
        {page === 'summary' && (
          <Summary onNewSession={goToLanding} />
        )}
      </main>
    </div>
  );
}

function App() {
  return (
    <InterviewProvider>
      <AppContent />
    </InterviewProvider>
  );
}

export default App;