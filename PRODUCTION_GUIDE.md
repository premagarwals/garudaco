# 🚀 Garudaco - Complete Setup Guide

## Quick Start

1. **Clone and Setup**:
   ```bash
   git clone <your-repo>
   cd garudaco
   ```

2. **Configure Google OAuth** (Required):
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a project or select existing one
   - Enable Google Sign-In API
   - Create OAuth 2.0 credentials
   - Add authorized origins: `http://localhost:3000`
   - Add redirect URIs: `http://localhost:3000`, `http://localhost:3000/login`

3. **Update Environment Variables**:
   
   **Root `.env` file**:
   ```bash
   OPENAI_API_KEY=your-openrouter-api-key
   API_MODEL=deepseek/deepseek-chat-v3.1:free
   GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   JWT_SECRET=your-super-secret-jwt-key
   ```

   **Frontend `.env` file** (`frontend/.env`):
   ```bash
   REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
   REACT_APP_API_URL=http://localhost:5000/api
   ```

4. **Start Application**:
   ```bash
   docker-compose up --build
   ```

5. **Access Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

## Features ✨

### 🔐 **Authentication**
- **Mandatory Google OAuth Login**: All users must authenticate to access the application
- **JWT Token Security**: Secure session management with 7-day token expiration
- **Per-User Data Isolation**: Each user has completely separate data storage

### 📚 **Learning Management**
- **Topic Tracking**: Add topics you've learned with difficulty ratings
- **Intelligent Recommendations**: AI-powered topic selection based on:
  - Your struggle patterns (failure rate)
  - Spaced repetition intervals
  - Topic difficulty levels
  - Recency of practice

### 📝 **Assessment System**
- **Multiple Question Types**:
  - Multiple Choice Questions (MCQ)
  - Code Implementation Challenges
  - Fill-in-the-blank Questions
- **AI-Generated Content**: Powered by OpenRouter API with customizable models
- **Difficulty Feedback**: Rate questions as Easy/Medium/Hard to improve recommendations

### 📊 **Progress Analytics**
- **Personal Statistics**: Track your learning progress over time
- **Category Analysis**: See performance breakdown by topic categories
- **Success Rate Tracking**: Monitor improvement in different areas
- **Learning History**: View your assessment history and patterns

### 🎯 **Smart Algorithms**
- **Spaced Repetition**: Topics resurface based on your mastery level
- **Struggle Detection**: More practice for topics you find challenging
- **Adaptive Scheduling**: Longer intervals for mastered topics
- **Priority Scoring**: Intelligent topic selection for optimal learning

## Architecture 🏗️

### Frontend (React + TypeScript)
- **Modern React 19**: Latest React features with TypeScript
- **Protected Routes**: Authentication-gated navigation
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Dynamic UI updates based on user actions

### Backend (Flask + Python)
- **RESTful API**: Clean API design with proper HTTP methods
- **JWT Authentication**: Stateless authentication with secure tokens
- **User Data Isolation**: Separate data storage per user
- **Error Handling**: Comprehensive error responses and logging

### Database Design
```
user_data/
├── user_123/
│   ├── topics_data.json     # User's topics and progress
│   ├── profile.json         # User preferences and stats
│   └── current_assessment.json  # Active assessment state
└── user_456/
    ├── topics_data.json
    ├── profile.json
    └── current_assessment.json
```

## API Endpoints 🔌

### Authentication
- `POST /api/auth/google` - Google OAuth login
- `GET /api/auth/verify` - Verify JWT token
- `POST /api/auth/logout` - User logout

### Topics Management
- `GET /api/topics` - Get user's topics (with filtering/sorting)
- `POST /api/topics` - Add new topic
- `GET /api/categories` - Get user's categories

### Assessment System
- `POST /api/generate-assessment` - Generate questions with filters
- `POST /api/generate-assessment-advanced` - Generate with sorting criteria
- `POST /api/verify-code` - Verify code solutions
- `POST /api/submit-assessment` - Submit assessment results

### Analytics
- `GET /api/stats` - Get comprehensive user statistics
- `GET /api/assessment-history` - Get assessment history

### User Profile
- `GET /api/profile` - Get user profile and preferences
- `PUT /api/profile` - Update user profile

## Security Features 🔒

- **OAuth 2.0**: Industry-standard Google authentication
- **JWT Tokens**: Secure, stateless authentication
- **CORS Protection**: Properly configured cross-origin requests
- **Input Validation**: Server-side validation for all inputs
- **Error Sanitization**: No sensitive data exposed in error messages
- **User Isolation**: Complete data separation between users

## Deployment Options 🚀

### Development (Current Setup)
```bash
docker-compose up --build
```

### Production Deployment
1. **Update OAuth Settings**: Add production domain to Google Console
2. **Environment Variables**: Update all placeholder values
3. **HTTPS Setup**: Configure SSL certificates
4. **Database**: Consider moving to persistent database
5. **Monitoring**: Add logging and monitoring solutions

## Troubleshooting 🔧

### Common Issues

1. **Google Sign-In Not Working**:
   - Verify Google Client ID in both `.env` files
   - Check authorized origins in Google Console
   - Ensure domains match exactly (no trailing slashes)

2. **Backend Connection Issues**:
   - Check if containers are running: `docker ps`
   - View backend logs: `docker logs garudaco-backend`
   - Verify CORS settings in app.py

3. **Authentication Errors**:
   - Check JWT secret is set in `.env`
   - Verify Google OAuth configuration
   - Clear browser cache and localStorage

4. **API Key Issues**:
   - Verify OpenRouter API key is valid
   - Check API model availability
   - Monitor API usage and limits

### Health Checks
```bash
# Check container status
docker ps

# Check backend health
curl http://localhost:5000/api/auth/verify

# Check frontend build
docker logs garudaco-frontend
```

## Performance Optimization 🚄

- **Efficient Algorithms**: O(n log n) sorting for large topic sets
- **Lazy Loading**: Components load on demand
- **Caching**: Browser caching for static assets
- **Compressed Builds**: Optimized production bundles
- **Database Indexing**: Efficient data retrieval patterns

## Contributing 🤝

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Ready to enhance your learning journey?** 🎓

Start by setting up your Google OAuth credentials and launch the application!