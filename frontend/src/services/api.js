const API_BASE = 'http://localhost:8000';

// Helper for fetch with error handling
async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;

  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// Interview API
export const interviewApi = {
  // Get available options for dropdowns
  getOptions: () => fetchAPI('/interview/options'),

  // Start a new interview session
  startSession: ({ role, topic, difficulty, maxQuestions }) =>
    fetchAPI('/interview/start', {
      method: 'POST',
      body: JSON.stringify({
        role,
        topic,
        difficulty,
        max_questions: maxQuestions,
      }),
    }),

  // Submit text answer
  submitAnswer: ({ sessionId, answer }) =>
    fetchAPI('/interview/submit', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        answer,
      }),
    }),

  // Submit audio answer
  submitAudioAnswer: async ({ sessionId, audioFile }) => {
    const formData = new FormData();
    formData.append('file', audioFile);
    formData.append('session_id', sessionId);

    const response = await fetch(`${API_BASE}/submit-audio-answer`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  },

  // Get session summary
  getSummary: (sessionId) => fetchAPI(`/interview/summary/${sessionId}`),

  // Get overall feedback
  getFeedback: (sessionId) => fetchAPI(`/interview/feedback/${sessionId}`),
};

// Resume API
export const resumeApi = {
  // Analyze resume PDF
  analyzeResume: async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/resume/analyze`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  },
};

export default { interviewApi, resumeApi };