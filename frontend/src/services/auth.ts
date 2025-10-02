import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

export interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}

export interface Profile {
  preferences: {
    default_difficulty: number;
    preferred_categories: string[];
    question_types: string[];
  };
  stats: {
    total_assessments: number;
    total_topics: number;
    avg_success_rate: number;
  };
}

class AuthService {
  private token: string | null = null;
  private user: User | null = null;

  constructor() {
    // Load token from localStorage on initialization
    this.token = localStorage.getItem('auth_token');
    const savedUser = localStorage.getItem('auth_user');
    this.user = savedUser ? JSON.parse(savedUser) : null;
  }

  isAuthenticated(): boolean {
    return !!this.token && !!this.user;
  }

  getToken(): string | null {
    return this.token;
  }

  getUser(): User | null {
    return this.user;
  }

  async loginWithGoogle(googleToken: string): Promise<AuthResponse> {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/google`, {
        token: googleToken
      });

      const { token, user } = response.data;
      
      // Store token and user info
      this.token = token;
      this.user = user;
      localStorage.setItem('auth_token', token);
      localStorage.setItem('auth_user', JSON.stringify(user));

      return { token, user };
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Authentication failed');
    }
  }

  async verifyToken(): Promise<boolean> {
    if (!this.token) return false;

    try {
      const response = await axios.get(`${API_BASE_URL}/auth/verify`, {
        headers: {
          Authorization: `Bearer ${this.token}`
        }
      });

      return response.data.valid;
    } catch (error) {
      // Token is invalid, clear it
      this.logout();
      return false;
    }
  }

  async logout(): Promise<void> {
    try {
      if (this.token) {
        await axios.post(`${API_BASE_URL}/auth/logout`, {}, {
          headers: {
            Authorization: `Bearer ${this.token}`
          }
        });
      }
    } catch (error) {
      // Ignore logout errors, just clear local data
    } finally {
      // Clear local storage and state
      this.token = null;
      this.user = null;
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
    }
  }

  async getProfile(): Promise<Profile> {
    if (!this.token) throw new Error('Not authenticated');

    const response = await axios.get(`${API_BASE_URL}/profile`, {
      headers: {
        Authorization: `Bearer ${this.token}`
      }
    });

    return response.data;
  }

  async updateProfile(profile: Profile): Promise<void> {
    if (!this.token) throw new Error('Not authenticated');

    await axios.put(`${API_BASE_URL}/profile`, profile, {
      headers: {
        Authorization: `Bearer ${this.token}`
      }
    });
  }

  // Helper method to get auth headers for API calls
  getAuthHeaders() {
    if (!this.token) {
      throw new Error('Not authenticated');
    }
    return {
      Authorization: `Bearer ${this.token}`
    };
  }
}

export const authService = new AuthService();
export default authService;