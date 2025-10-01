from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import random
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
from engine import (
    get_recommendations, 
    flag_recommendation_set, 
    fetch_all_topics, 
    add_new_topic,
    _load_recommendation_sets,
    _load_last_set_id
)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

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

@app.route('/api/topics', methods=['GET'])
def get_topics():
    """Get all topics with stats"""
    topics = fetch_all_topics()
    
    # Add computed stats
    for topic in topics:
        attempts = topic.get('attempts', 0)
        successes = topic.get('successes', 0)
        success_rate = (successes / attempts * 100) if attempts > 0 else 0
        
        topic['success_rate'] = round(success_rate, 1)
        
        # Handle last_seen date formatting
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
            
        # Handle date_added formatting
        date_added = topic.get('date_added')
        if date_added:
            if isinstance(date_added, str):
                try:
                    date_added_dt = datetime.fromisoformat(date_added)
                    topic['date_added_formatted'] = date_added_dt.strftime('%Y-%m-%d')
                except:
                    topic['date_added_formatted'] = 'Invalid Date'
            else:
                topic['date_added_formatted'] = date_added.strftime('%Y-%m-%d')
        else:
            topic['date_added_formatted'] = ''
    
    return jsonify(topics)

@app.route('/api/topics', methods=['POST'])
def add_topic():
    """Add a new topic"""
    data = request.get_json()
    name = data.get('name', '').strip()
    category = data.get('category', '').strip()
    difficulty = data.get('difficulty', 50)
    
    if not name or not category:
        return jsonify({'error': 'Name and category are required'}), 400
    
    try:
        difficulty = int(difficulty)
        if not (1 <= difficulty <= 100):
            return jsonify({'error': 'Difficulty must be between 1 and 100'}), 400
    except ValueError:
        return jsonify({'error': 'Difficulty must be a number'}), 400
    
    result = add_new_topic(name, category, difficulty)
    return jsonify({'message': result})

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all unique categories from topics"""
    topics = fetch_all_topics()
    categories = list(set(topic.get('category', '').strip() for topic in topics if topic.get('category', '').strip()))
    categories.sort()  # Sort alphabetically
    return jsonify(categories)

@app.route('/api/generate-assessment', methods=['POST'])
def generate_assessment():
    """Generate assessment questions based on filters"""
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
        recommendations = get_recommendations(count, filters if filters else None)
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
        recommendations = get_sorted_recommendations(count, sort_by, sort_order)
        
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
def verify_code():
    """Verify user's code solution"""
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
def submit_assessment():
    """Submit assessment results and update topic scores"""
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
        status = flag_recommendation_set(set_id, feedback)
        return jsonify({'message': status})
    except Exception as e:
        return jsonify({'error': f'Failed to submit assessment: {str(e)}'}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get comprehensive stats"""
    topics = fetch_all_topics()
    recommendation_sets = _load_recommendation_sets()
    
    # Add computed stats to topics for the stats page
    for topic in topics:
        attempts = topic.get('attempts', 0)
        successes = topic.get('successes', 0)
        success_rate = (successes / attempts * 100) if attempts > 0 else 0
        topic['success_rate'] = round(success_rate, 1)
        
        # Handle last_seen date formatting
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
            'total_sets': len(recommendation_sets)
        },
        'categories': categories,
        'topics': topics
    })

@app.route('/api/assessment-history', methods=['GET'])
def get_assessment_history():
    """Get assessment history"""
    recommendation_sets = _load_recommendation_sets()
    
    # For now, return basic set information
    # In a full implementation, you'd store more detailed assessment results
    history = []
    for set_id, topics in recommendation_sets.items():
        history.append({
            'set_id': set_id,
            'topic_count': len(topics),
            'topics': [t['topic_id'] for t in topics],
            'date': 'Unknown'  # You'd store this when creating sets
        })
    
    return jsonify(history)

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