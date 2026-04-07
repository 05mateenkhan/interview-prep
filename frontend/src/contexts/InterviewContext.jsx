import { createContext, useContext, useState, useCallback } from 'react';
import { interviewApi } from '../services/api';

const InterviewContext = createContext(null);

export function InterviewProvider({ children }) {
  const [session, setSession] = useState(null);
  const [options, setOptions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadOptions = useCallback(async () => {
    try {
      setLoading(true);
      const data = await interviewApi.getOptions();
      setOptions(data);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const startSession = useCallback(async ({ role, topic, difficulty, maxQuestions }) => {
    try {
      setLoading(true);
      setError(null);
      const data = await interviewApi.startSession({ role, topic, difficulty, maxQuestions });
      setSession({
        sessionId: data.session_id,
        role: data.role,
        topic: data.topic,
        difficulty: data.difficulty,
        currentQuestion: data.question,
        questionNumber: data.question_number,
        maxQuestions: maxQuestions,
        answers: [],
      });
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const submitAnswer = useCallback(async ({ answer }) => {
    if (!session?.sessionId) throw new Error('No active session');

    try {
      setLoading(true);
      setError(null);
      const data = await interviewApi.submitAnswer({ sessionId: session.sessionId, answer });

      setSession((prev) => ({
        ...prev,
        currentQuestion: data.next_question,
        questionNumber: data.session_complete ? prev.questionNumber : prev.questionNumber + 1,
        answers: [
          ...prev.answers,
          {
            question: prev.currentQuestion,
            answer,
            feedback: data.feedback,
            idealAnswer: data.ideal_answer,
            score: data.score,
            missingConcepts: data.missing_concepts,
          },
        ],
      }));

      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [session]);

  const submitAudioAnswer = useCallback(async ({ audioFile }) => {
    if (!session?.sessionId) throw new Error('No active session');

    try {
      setLoading(true);
      setError(null);
      const data = await interviewApi.submitAudioAnswer({
        sessionId: session.sessionId,
        audioFile,
      });

      setSession((prev) => ({
        ...prev,
        currentQuestion: data.next_question,
        questionNumber: data.session_complete ? prev.questionNumber : prev.questionNumber + 1,
        answers: [
          ...prev.answers,
          {
            question: prev.currentQuestion,
            answer: data.transcribed_text,
            feedback: data.feedback,
            idealAnswer: data.ideal_answer,
            score: data.score,
            missingConcepts: data.missing_concepts,
          },
        ],
      }));

      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [session]);

  const getSummary = useCallback(async () => {
    if (!session?.sessionId) return null;
    return interviewApi.getSummary(session.sessionId);
  }, [session]);

  const getFeedback = useCallback(async () => {
    if (!session?.sessionId) return null;
    return interviewApi.getFeedback(session.sessionId);
  }, [session]);

  const clearSession = useCallback(() => {
    setSession(null);
    setError(null);
  }, []);

  const value = {
    session,
    options,
    loading,
    error,
    loadOptions,
    startSession,
    submitAnswer,
    submitAudioAnswer,
    getSummary,
    getFeedback,
    clearSession,
  };

  return (
    <InterviewContext.Provider value={value}>
      {children}
    </InterviewContext.Provider>
  );
}

export function useInterview() {
  const context = useContext(InterviewContext);
  if (!context) {
    throw new Error('useInterview must be used within an InterviewProvider');
  }
  return context;
}

export default InterviewContext;