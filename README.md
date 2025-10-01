# 🚀 Garudaco - Intelligent Learning Assessment Platform

## Quick Start with Docker

### Prerequisites
- Docker installed on your system
- Docker Compose installed

### One-Command Setup

```bash
# Clone/navigate to the project directory
cd garudaco

# Start everything with one command
docker-compose up --build
```

That's it! The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

### 🔑 OpenRouter API Setup

1. **Get your OpenRouter API key** from https://openrouter.ai/
2. **Edit the `.env` file** in the **root directory** (same level as docker-compose.yml):
   ```bash
   OPENAI_API_KEY=sk-or-v1-your-actual-api-key-here
   ```
3. **Restart the containers**:
   ```bash
   docker-compose down
   docker-compose up
   ```

### 🗄️ Fresh Start

The Docker setup automatically creates fresh, empty data files on first run:
- ✅ **No dummy data** - starts completely clean
- ✅ **Empty topics list** - add your own learning topics
- ✅ **Fresh statistics** - track your real progress from day one

## Features

### 🎯 Intelligent Recommendation Engine
- **Spaced Repetition**: Topics are recommended based on when they were last seen and user performance
- **Difficulty Adjustment**: System adjusts difficulty based on user feedback and success rates
- **Category Diversity**: Ensures variety in topic categories for balanced learning
- **Performance Tracking**: Tracks success rates, attempts, and user-provided difficulty ratings

### 📚 Topic Management
- Add topics you've learned with custom difficulty ratings
- Organize topics by categories (arrays, graphs, DP, etc.)
- Track when topics were added and last assessed

### 🧠 Multi-Type Assessment System
- **Multiple Choice Questions (MCQ)**: Traditional quiz format with explanations
- **Code Implementation**: C++ coding challenges with built-in editor and AI verification
- **Fill-in-the-Blanks**: Test knowledge of key concepts and terminology

### 📊 Comprehensive Statistics
- Overall performance metrics and success rates
- Category-wise breakdown of performance
- Topic-level statistics with sorting and filtering
- Performance insights showing strengths and areas for improvement

### 🎨 Modern UI/UX
- Dark glassy gradient theme
- Responsive design for all devices
- Smooth animations and transitions
- Intuitive card-based assessment interface

## Technology Stack

### Backend
- **Python Flask**: REST API server
- **JSON Storage**: Persistent data storage in JSON files
- **OpenAI API Integration**: AI-powered question generation and code verification
- **CORS Support**: Cross-origin resource sharing for frontend communication

### Frontend
- **React with TypeScript**: Type-safe component development
- **Tailwind CSS**: Utility-first CSS framework
- **Monaco Editor**: VS Code-style code editor for C++ programming
- **React Router**: Client-side routing
- **Axios**: HTTP client for API communication
- **Framer Motion**: Smooth animations (ready for implementation)

## Setup Instructions

### Prerequisites
- Node.js (v14 or higher)
- Python (v3.7 or higher)
- OpenAI API key (for question generation)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd garudaco/backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set your OpenAI API key as an environment variable:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

4. Start the Flask server:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd garudaco/frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the React development server:
```bash
npm start
```

The frontend will run on `http://localhost:3000`

## How It Works

### 1. Learning Flow
1. **Add Topics**: Users add topics they've learned with initial difficulty assessment
2. **Generate Assessment**: System recommends topics based on performance and timing
3. **Take Assessment**: Users answer questions in various formats (MCQ, code, fill-in-blanks)
4. **Rate Difficulty**: After each question, users rate how difficult they found it
5. **Update Statistics**: System updates topic statistics and adjusts future recommendations

### 2. Recommendation Algorithm
The engine uses a sophisticated scoring system that considers:
- **Struggle Index**: How often the user fails questions on this topic
- **Due Factor**: Time since last assessment with spaced repetition
- **Base Difficulty**: User's initial difficulty assessment
- **Novelty Factor**: Boost for recently added topics
- **Category Diversity**: Prevents clustering of similar topics

### 3. Question Generation
- **AI-Powered**: Uses OpenAI's API to generate contextual questions
- **Format-Specific**: Different prompts for MCQ, code, and fill-in-blank questions
- **Verification**: Code solutions are verified by AI for correctness

## API Endpoints

### Topics
- `GET /api/topics` - Get all topics with statistics
- `POST /api/topics` - Add a new topic

### Assessment
- `POST /api/generate-assessment` - Generate assessment questions
- `POST /api/verify-code` - Verify code solution
- `POST /api/submit-assessment` - Submit assessment results

### Statistics
- `GET /api/stats` - Get comprehensive statistics
- `GET /api/assessment-history` - Get assessment history

## Data Storage

The system uses JSON files for data persistence:
- `topics_data.json`: All topic information and statistics
- `recommendation_sets.json`: Generated assessment sets
- `last_set_id.json`: Track the most recent assessment set

## Configuration

### Recommendation Engine Weights
The system uses tuned weights for optimal learning:
- **Struggle Weight (40%)**: Prioritizes topics where user is struggling
- **Due Weight (30%)**: Implements spaced repetition
- **Base Difficulty (15%)**: Considers inherent topic difficulty
- **Novelty (15%)**: Slight boost for newly added topics

### Difficulty Mapping
- Easy: 1-30 (Green)
- Medium: 31-70 (Yellow)
- Hard: 71-100 (Red)

## Future Enhancements

- [ ] Add support for more programming languages
- [ ] Implement streak tracking and gamification
- [ ] Add collaborative features and topic sharing
- [ ] Integration with popular learning platforms
- [ ] Mobile app development
- [ ] Advanced analytics and learning insights
- [ ] Custom assessment scheduling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support or questions, please open an issue in the repository or contact the development team.

---

**Garudaco** - Empowering learners with intelligent assessment and spaced repetition! 🚀