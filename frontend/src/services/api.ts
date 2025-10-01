import axios from 'axios';
import { Topic, Assessment, AssessmentResult, Stats } from '../types';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Topics
  getTopics: async (): Promise<Topic[]> => {
    const response = await api.get('/topics');
    return response.data;
  },

  addTopic: async (name: string, category: string, difficulty: number): Promise<string> => {
    const response = await api.post('/topics', { name, category, difficulty });
    return response.data.message;
  },

  // Assessment
  generateAssessment: async (count: number): Promise<Assessment> => {
    const response = await api.post('/generate-assessment', { count });
    return response.data;
  },

  verifyCode: async (question: string, code: string): Promise<string> => {
    const response = await api.post('/verify-code', { question, code });
    return response.data.verification;
  },

  submitAssessment: async (setId: string, results: AssessmentResult[]): Promise<string> => {
    const response = await api.post('/submit-assessment', { 
      set_id: setId, 
      results 
    });
    return response.data.message;
  },

  // Stats
  getStats: async (): Promise<Stats> => {
    const response = await api.get('/stats');
    return response.data;
  },

  getAssessmentHistory: async (): Promise<any[]> => {
    const response = await api.get('/assessment-history');
    return response.data;
  },
};

export default apiService;