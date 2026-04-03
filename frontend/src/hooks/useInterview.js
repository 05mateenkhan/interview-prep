import { useState, useCallback } from 'react';
import { interviewApi } from '../services/api';

export function useInterview() {
  const [session, setSession] = useState(null);
  const [options, setOptions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load interview options (roles, topics, difficulties)
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

  // Start a new interview session
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

  // Submit text answer
  const submitAnswer = useCallback(async ({ answer }) => {
    if (!session?.sessionId) throw new Error('No active session');

    try {
      setLoading(true);
      setError(null);
      const data = await interviewApi.submitAnswer({ sessionId: session.sessionId, answer });

      // Update session state
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

  // Submit audio answer
  const submitAudioAnswer = useCallback(async ({ audioFile }) => {
    if (!session?.sessionId) throw new Error('No active session');

    try {
      setLoading(true);
      setError(null);
      const data = await interviewApi.submitAudioAnswer({
        sessionId: session.sessionId,
        audioFile,
      });

      // Update session state
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

  // Get session summary
  const getSummary = useCallback(async () => {
    if (!session?.sessionId) return null;
    return interviewApi.getSummary(session.sessionId);
  }, [session]);

  // Get overall feedback
  const getFeedback = useCallback(async () => {
    if (!session?.sessionId) return null;
    return interviewApi.getFeedback(session.sessionId);
  }, [session]);

  // Clear session
  const clearSession = useCallback(() => {
    setSession(null);
    setError(null);
  }, []);

  return {
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
}

export default useInterview;