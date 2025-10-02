import axios from 'axios';
import { Topic, Assessment, AssessmentResult, Stats, AssessmentFilters } from '../types';
import { authService } from './auth';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    try {
      const authHeaders = authService.getAuthHeaders();
      Object.assign(config.headers, authHeaders);
    } catch (error) {
      // If not authenticated, let the request proceed without auth headers
      // The backend will return 401 if auth is required
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token is invalid or expired, redirect to login
      await authService.logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const apiService = {
  // Topics
  getTopics: async (): Promise<Topic[]> => {
    const response = await api.get('/topics');
    return response.data;
  },

  addTopic: async (topic_name: string, category: string, base_score: number): Promise<string> => {
    const response = await api.post('/topics', { topic_name, category, base_score });
    return response.data.message;
  },

  getCategories: async (): Promise<string[]> => {
    const response = await api.get('/categories');
    return response.data;
  },

  // Assessment
  generateAssessment: async (count: number, filters?: AssessmentFilters): Promise<Assessment> => {
    const response = await api.post('/generate-assessment', { count, ...filters });
    return response.data;
  },

  generateAssessmentAdvanced: async (
    count: number, 
    sortBy: string, 
    sortOrder: string
  ): Promise<Assessment & { sort_info: { sort_by: string; sort_order: string; description: string } }> => {
    const response = await api.post('/generate-assessment-advanced', { 
      count, 
      sort_by: sortBy, 
      sort_order: sortOrder 
    });
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