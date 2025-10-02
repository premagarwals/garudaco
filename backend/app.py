from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import random
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
from auth import AuthManager, require_auth
from user_manager import UserDataManager
from engine import (
    get_recommendations, 
    flag_recommendation_set, 
    fetch_all_topics, 
    add_new_topic
)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://localhost'], 
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Initialize managers
auth_manager = AuthManager()
user_data_manager = UserDataManager()

# OpenRouter API Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-api-key-here')
API_MODEL = os.getenv('API_MODEL', 'deepseek/deepseek-chat-v3.1:free')

# OpenRouter API URL (we only support OpenRouter)
OPENAI_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Question types
QUESTION_TYPES = ['mcq', 'code', 'blank']

def call_openai_api(prompt, temperature=0.7):
    """Call OpenRouter API with the given prompt"""
    # Check if API key is available
    if OPENAI_API_KEY == 'your-api-key-here' or not OPENAI_API_KEY:
        # Return mock responses for testing
        return get_mock_response(prompt)
    
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'http://localhost:5000',  # Required by OpenRouter
        'X-Title': 'garudaco Learning Assistant'  # Optional but recommended
    }
    
    data = {
        'model': API_MODEL,
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': temperature,
        'max_tokens': 1000
    }
    
    try:
        response = requests.post(OPENAI_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return f"API Error: {response.status_code} - {response.text}"
    except Exception as e:
        print(f"Error calling API: {str(e)}")
        return f"Error calling API: {str(e)}"

def get_mock_response(prompt):
    """Generate mock responses for testing when API key is not available"""
    if "multiple choice" in prompt.lower() or "mcq" in prompt.lower():
        topic = extract_topic_from_prompt(prompt)
        category = extract_category_from_prompt(prompt)
        return f"""QUESTION: What is the time complexity of {topic} in {category}?
A) O(1)
B) O(log n)
C) O(n)
D) O(n²)
ANSWER: B
EXPLANATION: {topic} typically has O(log n) time complexity due to its divide-and-conquer approach."""
    
    elif "C++ coding" in prompt or "implement" in prompt.lower():
        topic = extract_topic_from_prompt(prompt)
        category = extract_category_from_prompt(prompt)
        return f"""QUESTION: Implement {topic} in C++ for {category}
REQUIREMENTS: Create a function that implements {topic} algorithm
FUNCTION_SIGNATURE: int search(vector<int>& arr, int target)
EXAMPLE_INPUT: [1,2,3,4,5], target = 3
EXAMPLE_OUTPUT: 2"""
    
    elif "fill-in-the-blank" in prompt.lower():
        topic = extract_topic_from_prompt(prompt)
        category = extract_category_from_prompt(prompt)
        return f"""QUESTION: {topic} in {category} has a time complexity of _____ in the average case.
ANSWERS: O(log n)|logarithmic|log n
EXPLANATION: {topic} divides the search space in half with each operation."""
    
    elif "analyze" in prompt.lower() and "code" in prompt.lower():
        return """RESULT: YES
FEEDBACK: The code correctly implements the required algorithm with proper edge case handling.
SUGGESTIONS: Consider adding input validation for robustness."""
    
    return "Mock response generated for testing purposes."

def extract_topic_from_prompt(prompt):
    """Extract topic name from prompt for mock responses"""
    # Simple extraction - look for common patterns
    if "Binary Search" in prompt:
        return "Binary Search"
    elif "DFS" in prompt:
        return "Depth-First Search"
    elif "Union-Find" in prompt:
        return "Union-Find"
    elif "Two Pointers" in prompt:
        return "Two Pointers"
    else:
        # Extract first capitalized word as topic
        words = prompt.split()
        for word in words:
            if word[0].isupper() and len(word) > 3:
                return word
        return "Algorithm"

def extract_category_from_prompt(prompt):
    """Extract category from prompt for mock responses"""
    # Look for category mentions in the prompt
    if "category" in prompt.lower():
        # Try to extract the word after "category"
        words = prompt.split()
        for i, word in enumerate(words):
            if word.lower() == "category" and i + 1 < len(words):
                return words[i + 1].strip(".,")
    
    # Default categories based on common patterns
    if any(term in prompt.lower() for term in ["algorithm", "search", "sort", "tree", "graph"]):
        return "Algorithms"
    elif any(term in prompt.lower() for term in ["data structure", "array", "list", "stack", "queue"]):
        return "Data Structures"
    elif any(term in prompt.lower() for term in ["system", "design", "architecture"]):
        return "System Design"
    else:
        return "Programming"

# ======================== Authentication Endpoints ========================

@app.route('/api/auth/google', methods=['POST'])
def google_auth():
    """Authenticate user with Google OAuth token"""
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({'error': 'Token is required'}), 400
    
    try:
        user_info = auth_manager.verify_google_token(token)
        
        if user_info:
            # Generate JWT token for the user
            jwt_token = auth_manager.generate_token(user_info['sub'])
            
            # Initialize user data if first time
            user_data_manager.ensure_user_directory(user_info['sub'])
            
            return jsonify({
                'token': jwt_token,
                'user': {
                    'id': user_info['sub'],
                    'email': user_info['email'],
                    'name': user_info['name'],
                    'picture': user_info.get('picture', '')
                }
            })
        else:
            return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        print(f"Authentication error: {e}")
        return jsonify({'error': f'Authentication failed: {str(e)}'}), 500

@app.route('/api/auth/verify', methods=['GET'])
@require_auth
def verify_token():
    """Verify if the current token is valid"""
    user_id = request.user_id  # Set by require_auth decorator
    
    # Return user profile if exists
    try:
        profile = user_data_manager.load_user_profile(user_id)
        return jsonify({
            'valid': True,
            'user_id': user_id,
            'profile': profile
        })
    except:
        return jsonify({
            'valid': True,
            'user_id': user_id,
            'profile': None
        })

@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    """Logout user (client should remove token)"""
    return jsonify({'message': 'Logged out successfully'})

# ======================== User Profile Endpoints ========================

@app.route('/api/profile', methods=['GET'])
@require_auth
def get_profile():
    """Get user profile"""
    user_id = request.user_id
    
    try:
        profile = user_data_manager.load_user_profile(user_id)
        return jsonify(profile)
    except:
        # Return default profile if none exists
        return jsonify({
            'preferences': {
                'default_difficulty': 50,
                'preferred_categories': [],
                'question_types': ['mcq', 'code', 'blank']
            },
            'stats': {
                'total_assessments': 0,
                'total_topics': 0,
                'avg_success_rate': 0
            }
        })

@app.route('/api/profile', methods=['PUT'])
@require_auth
def update_profile():
    """Update user profile"""
    user_id = request.user_id
    data = request.get_json()
    
    try:
        user_data_manager.save_user_profile(user_id, data)
        return jsonify({'message': 'Profile updated successfully'})
    except Exception as e:
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500

def generate_mcq_question(topic_name, category, difficulty):
    """Generate MCQ question for a topic"""
    prompt = f"""Generate a multiple choice question about {topic_name} in the {category} category. 
    
Difficulty level: {difficulty:.2f} (0.0 = very easy, 1.0 = very hard)
Since this is an MCQ question, make it HARD regardless of the difficulty level. Focus on advanced concepts, edge cases, or subtle distinctions.

Don't come up with a common or repeated question.

Format your response EXACTLY like this:
QUESTION: [Your question here]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
ANSWER: [A/B/C/D]
EXPLANATION: [Brief explanation]

Make sure the question tests deep understanding of {topic_name} concept in {category}."""
    
    return call_openai_api(prompt)

def generate_code_question(topic_name, category, difficulty):
    """Generate code implementation question for a topic"""
    prompt = f"""Generate a C++ coding question about {topic_name} in the {category} category.
    
Difficulty level: {difficulty:.2f} (0.0 = very easy, 1.0 = very hard)
Since this is a coding question, keep it SIMPLE regardless of the difficulty level. Focus on clear, implementable problems that test understanding without being overly complex.

Don't come up with a common or repeated question. Don't focus on DSA. Make question more focused on implementation.

Format your response EXACTLY like this:
QUESTION: [Your question here - ask to implement a function or algorithm]
REQUIREMENTS: [List specific requirements]
FUNCTION_SIGNATURE: [Provide the exact function signature they should implement]
EXAMPLE_INPUT: [Example input]
EXAMPLE_OUTPUT: [Expected output]

The question should test practical implementation of {topic_name} in {category} using C++."""
    
    return call_openai_api(prompt)

def generate_blank_question(topic_name, category, difficulty):
    """Generate fill-in-the-blank question for a topic"""
    prompt = f"""Generate a fill-in-the-blank question about {topic_name} in the {category} category.
    
Difficulty level: {difficulty:.2f} (0.0 = very easy, 1.0 = very hard)
Since this is a fill-in-the-blank question, make it HARD regardless of the difficulty level. Focus on specific details, precise terminology, or advanced concepts.

Don't come up with a common or repeated question. Try to put only one blank.

Format your response EXACTLY like this:
QUESTION: [Your question with _____ for blanks]
ANSWERS: [answer1|answer2|answer3] (multiple valid answers separated by |, case insensitive)
EXPLANATION: [Brief explanation]

The question should test key concepts of {topic_name} in {category}."""
    
    return call_openai_api(prompt)

def verify_code_solution(question, user_code):
    """Verify if the user's code solution is correct"""
    prompt = f"""Question: {question}

User's C++ Code:
{user_code}

Analyze if this code correctly solves the given problem. Consider:
1. Correctness of algorithm
2. Proper implementation
3. Edge case handling
4. Code structure

Respond EXACTLY in this format:
RESULT: [YES/NO]
FEEDBACK: [Brief explanation of what's correct/incorrect]
SUGGESTIONS: [Specific suggestions for improvement if any]"""
    
    return call_openai_api(prompt, temperature=0.3)

# ======================== Topic Management Endpoints ========================

@app.route('/api/topics', methods=['GET'])
@require_auth
def get_topics():
    """Get all topics for the authenticated user"""
    user_id = request.user_id
    
    try:
        # Parse query parameters
        sort_by = request.args.get('sort_by', 'priority')
        sort_order = request.args.get('sort_order', 'desc')
        category_filter = request.args.get('category')
        
        # Build filters
        filters = {}
        if category_filter:
            filters['categories'] = [category_filter]
        
        # Optional date filters
        if request.args.get('added_in_last_days'):
            try:
                filters['added_in_last_days'] = int(request.args.get('added_in_last_days'))
            except ValueError:
                pass
        
        if request.args.get('not_asked_in_last_days'):
            try:
                filters['not_asked_in_last_days'] = int(request.args.get('not_asked_in_last_days'))
            except ValueError:
                pass
        
        if request.args.get('min_base_score'):
            try:
                filters['min_base_score'] = float(request.args.get('min_base_score'))
            except ValueError:
                pass
        
        # Fetch topics
        topics = fetch_all_topics(user_id)
        
        # Apply filters manually since fetch_all_topics doesn't support them
        if category_filter:
            topics = [t for t in topics if t.get('category', '').lower() == category_filter.lower()]
        
        # Apply sorting
        if sort_by == 'topic_name':
            topics.sort(key=lambda x: x.get('topic_name', ''), reverse=(sort_order == 'desc'))
        elif sort_by == 'date_added':
            topics.sort(key=lambda x: x.get('date_added', datetime.min), reverse=(sort_order == 'desc'))
        elif sort_by == 'success_rate':
            topics.sort(key=lambda x: (x.get('successes', 0) / max(x.get('attempts', 1), 1)), reverse=(sort_order == 'desc'))
        elif sort_by == 'attempts':
            topics.sort(key=lambda x: x.get('attempts', 0), reverse=(sort_order == 'desc'))
        
        # Add computed fields for frontend
        for topic in topics:
            attempts = topic.get('attempts', 0)
            successes = topic.get('successes', 0)
            topic['success_rate'] = round((successes / attempts * 100) if attempts > 0 else 0, 1)
            topic['attempt_count'] = attempts
            
            # Map topic_name to name for frontend compatibility
            if 'topic_name' in topic:
                topic['name'] = topic['topic_name']
            # Map topic_id to id for frontend compatibility  
            if 'topic_id' in topic:
                topic['id'] = topic['topic_id']
            
            # Format dates
            last_seen = topic.get('last_seen')
            if last_seen:
                if isinstance(last_seen, str):
                    try:
                        last_seen_dt = datetime.fromisoformat(last_seen)
                        topic['last_seen_formatted'] = last_seen_dt.strftime('%Y-%m-%d')
                        topic['days_since_last_seen'] = (datetime.now() - last_seen_dt).days
                    except:
                        topic['last_seen_formatted'] = 'Invalid Date'
                        topic['days_since_last_seen'] = 999
                else:
                    topic['last_seen_formatted'] = last_seen.strftime('%Y-%m-%d')
                    topic['days_since_last_seen'] = (datetime.now() - last_seen).days
            else:
                topic['last_seen_formatted'] = 'Never'
                topic['days_since_last_seen'] = 999
            
            date_added = topic.get('date_added')
            if date_added:
                if isinstance(date_added, str):
                    try:
                        date_added_dt = datetime.fromisoformat(date_added)
                        topic['date_added_formatted'] = date_added_dt.strftime('%Y-%m-%d')
                        topic['days_since_added'] = (datetime.now() - date_added_dt).days
                    except:
                        topic['date_added_formatted'] = 'Invalid Date'
                        topic['days_since_added'] = 0
                else:
                    topic['date_added_formatted'] = date_added.strftime('%Y-%m-%d')
                    topic['days_since_added'] = (datetime.now() - date_added).days
            else:
                topic['date_added_formatted'] = ''
                topic['days_since_added'] = 0
        
        return jsonify(topics)
    except Exception as e:
        return jsonify({'error': f'Failed to fetch topics: {str(e)}'}), 500

@app.route('/api/topics', methods=['POST'])
@require_auth
def add_topic():
    """Add a new topic for the authenticated user"""
    user_id = request.user_id
    data = request.get_json()
    
    topic_name = data.get('topic_name')
    category = data.get('category')
    base_score = data.get('base_score', 50)
    
    if not topic_name or not category:
        return jsonify({'error': 'Topic name and category are required'}), 400
    
    try:
        result = add_new_topic(user_id, topic_name, category, base_score)
        return jsonify({'message': 'Topic added successfully', 'topic_id': result})
    except Exception as e:
        return jsonify({'error': f'Failed to add topic: {str(e)}'}), 500

@app.route('/api/categories', methods=['GET'])
@require_auth
def get_categories():
    """Get unique categories for the authenticated user"""
    user_id = request.user_id
    
    try:
        topics = user_data_manager.load_user_topics(user_id)
        categories = list(set(topic.get('category', 'Unknown') for topic in topics))
        return jsonify(sorted(categories))
    except Exception as e:
        return jsonify({'error': f'Failed to fetch categories: {str(e)}'}), 500

# ======================== Assessment Endpoints ========================

@app.route('/api/generate-assessment', methods=['POST'])
@require_auth
def generate_assessment():
    """Generate assessment questions based on filters for the authenticated user"""
    user_id = request.user_id
    data = request.get_json()
    count = data.get('count', 3)
    
    # Extract filters from request
    filters = {}
    
    if 'added_in_last_days' in data and data['added_in_last_days'] is not None:
        try:
            filters['added_in_last_days'] = int(data['added_in_last_days'])
        except (ValueError, TypeError):
            return jsonify({'error': 'added_in_last_days must be a valid number'}), 400
    
    if 'not_asked_in_last_days' in data and data['not_asked_in_last_days'] is not None:
        try:
            filters['not_asked_in_last_days'] = int(data['not_asked_in_last_days'])
        except (ValueError, TypeError):
            return jsonify({'error': 'not_asked_in_last_days must be a valid number'}), 400
    
    if 'min_base_score' in data and data['min_base_score'] is not None:
        try:
            min_score = int(data['min_base_score'])
            if not (1 <= min_score <= 100):
                return jsonify({'error': 'min_base_score must be between 1 and 100'}), 400
            filters['min_base_score'] = min_score
        except (ValueError, TypeError):
            return jsonify({'error': 'min_base_score must be a valid number'}), 400
    
    if 'categories' in data and data['categories']:
        if isinstance(data['categories'], list):
            # Filter out empty strings and None values
            categories = [cat.strip() for cat in data['categories'] if cat and cat.strip()]
            if categories:
                filters['categories'] = categories
        else:
            return jsonify({'error': 'categories must be a list of strings'}), 400
    
    # Get recommendations from engine with filters
    try:
        recommendations = get_recommendations(user_id, count, filters if filters else None)
        if not recommendations:
            if filters:
                return jsonify({'error': 'No topics match the specified filters'}), 400
            else:
                return jsonify({'error': 'No topics available for assessment'}), 400
        
        # Parse recommendations and generate questions
        assessment_questions = []
        
        for rec_json in recommendations:
            rec = json.loads(rec_json)
            topic_name = rec['topic_name']
            category = rec['category']
            base_score = rec.get('base_score', 50)  # Default to 50 if not present
            
            # Calculate difficulty as (100-base_score)/100
            difficulty = (100 - base_score) / 100
            
            # Randomly choose question type
            question_type = random.choice(QUESTION_TYPES)
            
            # Generate question based on type, including difficulty and category
            if question_type == 'mcq':
                question_text = generate_mcq_question(topic_name, category, difficulty)
            elif question_type == 'code':
                question_text = generate_code_question(topic_name, category, difficulty)
            else:  # blank
                question_text = generate_blank_question(topic_name, category, difficulty)
            
            question_data = {
                'rec_id': rec['rec_id'],
                'set_id': rec['set_id'],
                'rec_no': rec['rec_no'],
                'topic_id': rec['topic_id'],
                'topic_name': topic_name,
                'category': rec['category'],
                'question_type': question_type,
                'question_text': question_text,
                'user_answer': None,
                'is_correct': None,
                'difficulty_rating': None
            }
            
            assessment_questions.append(question_data)
        
        return jsonify({
            'set_id': json.loads(recommendations[0])['set_id'],
            'questions': assessment_questions
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate assessment: {str(e)}'}), 500

@app.route('/api/generate-assessment-advanced', methods=['POST'])
def generate_assessment_advanced():
    """Generate assessment questions based on advanced sorting criteria"""
    data = request.get_json()
    count = data.get('count', 3)
    sort_by = data.get('sort_by', 'success_rate')
    sort_order = data.get('sort_order', 'top')
    
    # Validate sort_by parameter
    valid_sort_options = ['success_rate', 'attempt_count', 'base_score', 'last_seen', 'date_added']
    if sort_by not in valid_sort_options:
        return jsonify({'error': f'sort_by must be one of: {", ".join(valid_sort_options)}'}), 400
    
    # Validate sort_order parameter
    if sort_order not in ['top', 'bottom']:
        return jsonify({'error': 'sort_order must be either "top" or "bottom"'}), 400
    
    # Validate count
    try:
        count = int(count)
        if count <= 0:
            return jsonify({'error': 'count must be a positive integer'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'count must be a valid number'}), 400
    
    # Get sorted recommendations from engine
    try:
        from engine import get_sorted_recommendations
        recommendations = get_sorted_recommendations(user_id, count, sort_by, sort_order)
        
        if not recommendations:
            return jsonify({'error': 'No topics available for assessment'}), 400
        
        # Parse recommendations and generate questions
        assessment_questions = []
        
        for rec_json in recommendations:
            rec = json.loads(rec_json)
            topic_name = rec['topic_name']
            category = rec['category']
            base_score = rec.get('base_score', 50)
            
            # Calculate difficulty as (100-base_score)/100
            difficulty = (100 - base_score) / 100
            
            # Randomly choose question type
            question_type = random.choice(QUESTION_TYPES)
            
            # Generate question based on type, including difficulty and category
            if question_type == 'mcq':
                question_text = generate_mcq_question(topic_name, category, difficulty)
            elif question_type == 'code':
                question_text = generate_code_question(topic_name, category, difficulty)
            else:  # blank
                question_text = generate_blank_question(topic_name, category, difficulty)
            
            question_data = {
                'rec_id': rec['rec_id'],
                'set_id': rec['set_id'],
                'rec_no': rec['rec_no'],
                'topic_id': rec['topic_id'],
                'topic_name': topic_name,
                'category': rec['category'],
                'question_type': question_type,
                'question_text': question_text,
                'user_answer': None,
                'is_correct': None,
                'difficulty_rating': None,
                'sort_criteria': rec.get('sort_criteria', ''),
                'sort_value': rec.get('sort_value', 0)
            }
            
            assessment_questions.append(question_data)
        
        return jsonify({
            'set_id': json.loads(recommendations[0])['set_id'],
            'questions': assessment_questions,
            'sort_info': {
                'sort_by': sort_by,
                'sort_order': sort_order,
                'description': f"{'Top' if sort_order == 'top' else 'Bottom'} {count} topics by {sort_by.replace('_', ' ')}"
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate advanced assessment: {str(e)}'}), 500

@app.route('/api/verify-code', methods=['POST'])
@require_auth
def verify_code():
    """Verify user's code solution"""
    user_id = request.user_id
    data = request.get_json()
    question = data.get('question', '')
    user_code = data.get('code', '')
    
    if not question or not user_code:
        return jsonify({'error': 'Question and code are required'}), 400
    
    try:
        verification_result = verify_code_solution(question, user_code)
        return jsonify({'verification': verification_result})
    except Exception as e:
        return jsonify({'error': f'Failed to verify code: {str(e)}'}), 500

@app.route('/api/submit-assessment', methods=['POST'])
@require_auth
def submit_assessment():
    """Submit assessment results and update topic scores for the authenticated user"""
    user_id = request.user_id
    data = request.get_json()
    set_id = data.get('set_id')
    results = data.get('results', [])
    
    if not set_id or not results:
        return jsonify({'error': 'Set ID and results are required'}), 400
    
    # Format feedback for the engine
    feedback = []
    for result in results:
        feedback.append({
            'rec_no': result['rec_no'],
            'difficulty': result['difficulty_rating'],  # easy/medium/hard
            'solved': result['is_correct']
        })
    
    try:
        status = flag_recommendation_set(user_id, set_id, feedback)
        return jsonify({'message': status})
    except Exception as e:
        return jsonify({'error': f'Failed to submit assessment: {str(e)}'}), 500

@app.route('/api/stats', methods=['GET'])
@require_auth
def get_stats():
    """Get comprehensive stats for the authenticated user"""
    user_id = request.user_id
    
    try:
        topics = fetch_all_topics(user_id)
        
        # Add computed stats to topics for the stats page
        for topic in topics:
            attempts = topic.get('attempts', 0)
            successes = topic.get('successes', 0)
            success_rate = (successes / attempts * 100) if attempts > 0 else 0
            topic['success_rate'] = round(success_rate, 1)
            
            # Map topic_name to name for frontend compatibility
            if 'topic_name' in topic:
                topic['name'] = topic['topic_name']
            # Map topic_id to id for frontend compatibility  
            if 'topic_id' in topic:
                topic['id'] = topic['topic_id']
        # Handle last_seen date formatting
        for topic in topics:
            last_seen = topic.get('last_seen')
            if last_seen:
                if isinstance(last_seen, str):
                    try:
                        last_seen_dt = datetime.fromisoformat(last_seen)
                        topic['last_seen_formatted'] = last_seen_dt.strftime('%Y-%m-%d')
                    except:
                        topic['last_seen_formatted'] = 'Invalid Date'
                else:
                    topic['last_seen_formatted'] = last_seen.strftime('%Y-%m-%d')
            else:
                topic['last_seen_formatted'] = 'Never'
        
        # Overall stats
        total_topics = len(topics)
        total_attempts = sum(t.get('attempts', 0) for t in topics)
        total_successes = sum(t.get('successes', 0) for t in topics)
        overall_success_rate = (total_successes / total_attempts * 100) if total_attempts > 0 else 0
        
        # Category stats
        categories = {}
        for topic in topics:
            cat = topic.get('category', 'Unknown')
            if cat not in categories:
                categories[cat] = {
                    'count': 0,
                    'attempts': 0,
                    'successes': 0,
                    'avg_difficulty': 0
                }
            categories[cat]['count'] += 1
            categories[cat]['attempts'] += topic.get('attempts', 0)
            categories[cat]['successes'] += topic.get('successes', 0)
            categories[cat]['avg_difficulty'] += topic.get('base_score', 50)
        
        for cat_data in categories.values():
            if cat_data['count'] > 0:
                cat_data['avg_difficulty'] = round(cat_data['avg_difficulty'] / cat_data['count'], 1)
                cat_data['success_rate'] = round(
                    (cat_data['successes'] / cat_data['attempts'] * 100) if cat_data['attempts'] > 0 else 0, 1
                )
        
        return jsonify({
            'overall': {
                'total_topics': total_topics,
                'total_attempts': total_attempts,
                'total_successes': total_successes,
                'success_rate': round(overall_success_rate, 1),
                'total_sets': 0  # No longer tracking sets
            },
            'categories': categories,
            'topics': topics
        })
    except Exception as e:
        return jsonify({'error': f'Failed to fetch stats: {str(e)}'}), 500

@app.route('/api/assessment-history', methods=['GET'])
@require_auth
def get_assessment_history():
    """Get assessment history for the authenticated user"""
    user_id = request.user_id
    
    try:
        # Get current assessment if exists
        current_assessment = user_data_manager.load_user_current_assessment(user_id)
        
        history = []
        if current_assessment:
            history.append({
                'set_id': current_assessment.get('set_id', 'current'),
                'topic_count': len(current_assessment.get('topics', [])),
                'topics': [t.get('topic_name', 'Unknown') for t in current_assessment.get('topics', [])],
                'date': current_assessment.get('created_at', 'Unknown'),
                'status': 'current'
            })
        
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': f'Failed to fetch assessment history: {str(e)}'}), 500

if __name__ == '__main__':
    # Configuration for Docker deployment
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    app.run(
        host='0.0.0.0',  # Allow external connections (required for Docker)
        port=port,
        debug=debug
    )