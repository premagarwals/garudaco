import json
import math
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
from user_manager import user_data_manager

# --------------------------- Configuration (final, tuned weights) ---------------------------
# These weights were chosen to prioritise: (1) struggle (user failing), (2) due/spacing, (3) inherent difficulty,
# (4) novelty for new topics.
W_STRUGGLE = 0.40      # most important: user struggling => repeat sooner
W_DUE = 0.30           # spaced repetition / time-since-last-seen
W_BASE = 0.15          # original difficulty (user-provided initial estimate)
W_NOVELTY = 0.15       # small boost to recently-added topics

# Diversity penalty: when a topic from a category is picked, reduce the priority of other topics in same category
DIVERSITY_PENALTY = 0.70

# New topic window (days) for novelty boost
NEW_TOPIC_WINDOW_DAYS = 14

# Base spacing interval (days)
BASE_INTERVAL_DAYS = 3.0

# Flagging configuration
BASE_SCORE_ADJUSTMENT_RATIO = 0.10 # Max fraction of the difference to adjust base_score
# Map of user feedback ('easy', 'medium', 'hard') to a numeric score (1..100)
# 'easy' (20) means the user found it much easier than average (50), 'hard' (80) much harder.
FLAG_SCORE_MAP = {
    "easy": 20,
    "medium": 50,
    "hard": 80
}
# --------------------------- User-based Data Functions ----------------------------------

def fetch_all_topics(user_id: str) -> List[dict]:
    """Fetch all topics for a specific user"""
    return user_data_manager.load_user_topics(user_id)

def add_new_topic(user_id: str, name: str, category: str, difficulty: int) -> str:
    """Add a new topic for a specific user"""
    topics = user_data_manager.load_user_topics(user_id)
    
    # Check if topic already exists
    for topic in topics:
        if topic['topic_name'].lower() == name.lower():
            return f"Topic '{name}' already exists"
    
    new_topic = {
        'topic_id': str(uuid.uuid4()),
        'topic_name': name,
        'category': category,
        'base_score': difficulty,
        'attempts': 0,
        'successes': 0,
        'date_added': datetime.now(),
        'last_seen': None
    }
    
    topics.append(new_topic)
    user_data_manager.save_user_topics(user_id, topics)
    
    # Update user profile
    profile = user_data_manager.load_user_profile(user_id)
    profile['total_topics_added'] = profile.get('total_topics_added', 0) + 1
    user_data_manager.save_user_profile(user_id, profile)
    
    return f"Topic '{name}' added successfully"

def get_recommendations(user_id: str, count: int, filters: Optional[Dict] = None) -> List[str]:
    """Get topic recommendations for a specific user using the spaced repetition algorithm"""
    topics = user_data_manager.load_user_topics(user_id)
    
    if not topics:
        return []
    
    # Apply filters if provided
    if filters:
        topics = apply_filters(topics, filters)
    
    if len(topics) == 0:
        return []
    
    # Calculate priorities for each topic
    prioritized_topics = []
    for topic in topics:
        priority = calculate_priority(topic, topics)
        prioritized_topics.append((topic, priority))
    
    # Sort by priority (highest first)
    prioritized_topics.sort(key=lambda x: x[1], reverse=True)
    
    # Apply diversity penalty and select topics
    selected_topics = []
    used_categories = set()
    
    for topic, priority in prioritized_topics:
        if len(selected_topics) >= count:
            break
        
        # Apply diversity penalty if category already used
        if topic['category'] in used_categories:
            priority *= DIVERSITY_PENALTY
        
        selected_topics.append(topic)
        used_categories.add(topic['category'])
        
        # If we need more topics and have exhausted unique categories, allow repeats
        if len(selected_topics) < count and len(used_categories) == len(set(t['category'] for t in topics)):
            used_categories.clear()
    
    # Create assessment set and store current assessment
    set_id = f"set_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
    
    # Store current assessment for feedback processing
    assessment_data = {
        'set_id': set_id,
        'topics': selected_topics,
        'timestamp': datetime.now()
    }
    user_data_manager.save_user_current_assessment(user_id, assessment_data)
    
    # Format recommendations as JSON strings (maintaining compatibility)
    recommendations = []
    for i, topic in enumerate(selected_topics):
        rec = {
            'rec_id': f"{set_id}_{i}",
            'set_id': set_id,
            'rec_no': i,
            'topic_id': topic['topic_id'],
            'topic_name': topic['topic_name'],
            'category': topic['category'],
            'base_score': topic['base_score']
        }
        recommendations.append(json.dumps(rec))
    
    return recommendations

def get_sorted_recommendations(user_id: str, count: int, sort_by: str, sort_order: str) -> List[str]:
    """Get sorted topic recommendations for a specific user"""
    topics = user_data_manager.load_user_topics(user_id)
    
    if not topics:
        return []
    
    # Add computed fields for sorting
    enriched_topics = []
    for topic in topics:
        attempts = topic.get('attempts', 0)
        successes = topic.get('successes', 0)
        success_rate = (successes / attempts * 100) if attempts > 0 else 0
        
        days_since_last_seen = 999
        if topic.get('last_seen'):
            days_since_last_seen = (datetime.now() - topic['last_seen']).days
        
        days_since_added = (datetime.now() - topic['date_added']).days
        
        enriched_topic = topic.copy()
        enriched_topic.update({
            'success_rate': success_rate,
            'attempt_count': attempts,
            'days_since_last_seen': days_since_last_seen,
            'days_since_added': days_since_added
        })
        enriched_topics.append(enriched_topic)
    
    # Sort based on criteria
    if sort_by == 'success_rate':
        enriched_topics.sort(key=lambda x: x['success_rate'], reverse=(sort_order == 'top'))
    elif sort_by == 'attempt_count':
        enriched_topics.sort(key=lambda x: x['attempt_count'], reverse=(sort_order == 'top'))
    elif sort_by == 'base_score':
        enriched_topics.sort(key=lambda x: x['base_score'], reverse=(sort_order == 'top'))
    elif sort_by == 'last_seen':
        enriched_topics.sort(key=lambda x: x['days_since_last_seen'], reverse=(sort_order == 'bottom'))
    elif sort_by == 'date_added':
        enriched_topics.sort(key=lambda x: x['days_since_added'], reverse=(sort_order == 'bottom'))
    
    # Take the requested count
    selected_topics = enriched_topics[:count]
    
    # Create assessment set and store current assessment
    set_id = f"sorted_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
    
    # Store current assessment for feedback processing
    assessment_data = {
        'set_id': set_id,
        'topics': selected_topics,
        'timestamp': datetime.now(),
        'sort_criteria': {
            'sort_by': sort_by,
            'sort_order': sort_order
        }
    }
    user_data_manager.save_user_current_assessment(user_id, assessment_data)
    
    # Format recommendations as JSON strings
    recommendations = []
    for i, topic in enumerate(selected_topics):
        rec = {
            'rec_id': f"{set_id}_{i}",
            'set_id': set_id,
            'rec_no': i,
            'topic_id': topic['topic_id'],
            'topic_name': topic['topic_name'],
            'category': topic['category'],
            'base_score': topic['base_score'],
            'sort_criteria': f"{sort_by} ({sort_order})",
            'sort_value': get_sort_value(topic, sort_by)
        }
        recommendations.append(json.dumps(rec))
    
    return recommendations

def flag_recommendation_set(user_id: str, set_id: str, feedback: List[Dict]) -> str:
    """Process feedback for the current assessment set"""
    # Get current assessment
    assessment = user_data_manager.load_user_current_assessment(user_id)
    
    if not assessment or assessment['set_id'] != set_id:
        return "No matching assessment found or assessment expired"
    
    # Load current topics
    topics = user_data_manager.load_user_topics(user_id)
    
    # Process feedback for each topic
    for fb in feedback:
        rec_no = fb['rec_no']
        difficulty = fb['difficulty']  # 'easy', 'medium', 'hard'
        solved = fb['solved']  # True/False
        
        if rec_no >= len(assessment['topics']):
            continue
        
        assessment_topic = assessment['topics'][rec_no]
        topic_id = assessment_topic['topic_id']
        
        # Find the topic in the current topics list
        topic_index = None
        for i, topic in enumerate(topics):
            if topic['topic_id'] == topic_id:
                topic_index = i
                break
        
        if topic_index is None:
            continue
        
        # Update topic statistics
        topic = topics[topic_index]
        topic['attempts'] = topic.get('attempts', 0) + 1
        topic['last_seen'] = datetime.now()
        
        if solved:
            topic['successes'] = topic.get('successes', 0) + 1
        
        # Adjust base_score based on difficulty feedback
        if difficulty in FLAG_SCORE_MAP:
            target_score = FLAG_SCORE_MAP[difficulty]
            current_score = topic['base_score']
            score_difference = target_score - current_score
            adjustment = score_difference * BASE_SCORE_ADJUSTMENT_RATIO
            
            # Apply adjustment with bounds
            new_score = current_score + adjustment
            topic['base_score'] = max(1, min(100, new_score))
        
        topics[topic_index] = topic
    
    # Save updated topics
    user_data_manager.save_user_topics(user_id, topics)
    
    # Update user profile
    profile = user_data_manager.load_user_profile(user_id)
    profile['total_assessments'] = profile.get('total_assessments', 0) + 1
    user_data_manager.save_user_profile(user_id, profile)
    
    # Clear current assessment
    user_data_manager.clear_user_current_assessment(user_id)
    
    return "Assessment feedback processed successfully"

# --------------------------- Helper Functions ----------------------------------

def apply_filters(topics: List[dict], filters: Dict) -> List[dict]:
    """Apply filters to topics list"""
    filtered_topics = []
    now = datetime.now()
    
    for topic in topics:
        # Filter by added_in_last_days
        if 'added_in_last_days' in filters and filters['added_in_last_days'] is not None:
            days_since_added = (now - topic['date_added']).days
            if days_since_added > filters['added_in_last_days']:
                continue
        
        # Filter by not_asked_in_last_days
        if 'not_asked_in_last_days' in filters and filters['not_asked_in_last_days'] is not None:
            if topic.get('last_seen'):
                days_since_last_seen = (now - topic['last_seen']).days
                if days_since_last_seen < filters['not_asked_in_last_days']:
                    continue
        
        # Filter by min_base_score
        if 'min_base_score' in filters and filters['min_base_score'] is not None:
            if topic['base_score'] < filters['min_base_score']:
                continue
        
        # Filter by categories
        if 'categories' in filters and filters['categories']:
            if topic['category'] not in filters['categories']:
                continue
        
        filtered_topics.append(topic)
    
    return filtered_topics

def calculate_priority(topic: Dict, all_topics: List[Dict]) -> float:
    """Calculate priority score for a topic"""
    struggle_score = calculate_struggle_score(topic)
    due_score = calculate_due_score(topic)
    base_score = calculate_base_score(topic)
    novelty_score = calculate_novelty_score(topic)
    
    priority = (
        W_STRUGGLE * struggle_score +
        W_DUE * due_score +
        W_BASE * base_score +
        W_NOVELTY * novelty_score
    )
    
    return priority

def calculate_struggle_score(topic: Dict) -> float:
    """Calculate struggle score based on failure rate"""
    attempts = topic.get('attempts', 0)
    successes = topic.get('successes', 0)
    
    if attempts == 0:
        return 0.5  # Neutral score for untested topics
    
    failure_rate = 1 - (successes / attempts)
    # Higher failure rate = higher struggle score = higher priority
    return min(failure_rate * 2, 1.0)

def calculate_due_score(topic: Dict) -> float:
    """Calculate due score based on spaced repetition"""
    last_seen = topic.get('last_seen')
    
    if not last_seen:
        return 1.0  # High priority for never-seen topics
    
    days_since_last_seen = (datetime.now() - last_seen).days
    
    # Calculate target interval based on success rate
    attempts = topic.get('attempts', 0)
    successes = topic.get('successes', 0)
    success_rate = successes / attempts if attempts > 0 else 0
    
    # More successful topics can wait longer
    interval_multiplier = max(1, success_rate * 3)
    target_interval = BASE_INTERVAL_DAYS * interval_multiplier
    
    if days_since_last_seen >= target_interval:
        # Topic is due or overdue
        return min(days_since_last_seen / target_interval, 1.0)
    else:
        # Topic is not yet due
        return (days_since_last_seen / target_interval) * 0.3

def calculate_base_score(topic: Dict) -> float:
    """Calculate priority based on base difficulty"""
    # Higher difficulty = higher priority (more practice needed)
    return topic['base_score'] / 100.0

def calculate_novelty_score(topic: Dict) -> float:
    """Calculate novelty score for recently added topics"""
    days_since_added = (datetime.now() - topic['date_added']).days
    
    if days_since_added <= NEW_TOPIC_WINDOW_DAYS:
        # Linear decay from 1.0 to 0.0 over the novelty window
        return 1.0 - (days_since_added / NEW_TOPIC_WINDOW_DAYS)
    
    return 0.0

def get_sort_value(topic: Dict, sort_by: str) -> float:
    """Get the sort value for a topic based on sort criteria"""
    if sort_by == 'success_rate':
        return topic.get('success_rate', 0)
    elif sort_by == 'attempt_count':
        return topic.get('attempt_count', 0)
    elif sort_by == 'base_score':
        return topic['base_score']
    elif sort_by == 'last_seen':
        return topic.get('days_since_last_seen', 999)
    elif sort_by == 'date_added':
        return topic.get('days_since_added', 0)
    return 0

def _save_topics_data(topics_data: List[dict]):
    """Save topics data to JSON file."""
    # Convert datetime objects to strings for JSON serialization
    serializable_data = []
    for topic in topics_data:
        topic_copy = topic.copy()
        if topic_copy.get('date_added'):
            topic_copy['date_added'] = topic_copy['date_added'].isoformat()
        if topic_copy.get('last_seen'):
            topic_copy['last_seen'] = topic_copy['last_seen'].isoformat()
        serializable_data.append(topic_copy)
    
    with open(TOPICS_DATA_FILE, 'w') as f:
        json.dump(serializable_data, f, indent=2)

def _load_recommendation_sets() -> Dict[str, List[dict]]:
    """Load recommendation sets from JSON file."""
    try:
        with open(RECOMMENDATION_SETS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def _save_recommendation_sets(recommendation_sets: Dict[str, List[dict]]):
    """Save recommendation sets to JSON file."""
    with open(RECOMMENDATION_SETS_FILE, 'w') as f:
        json.dump(recommendation_sets, f, indent=2)

def _load_last_set_id() -> Optional[str]:
    """Load last set ID from JSON file."""
    try:
        with open(LAST_SET_ID_FILE, 'r') as f:
            data = json.load(f)
            return data.get('last_set_id')
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def _save_last_set_id(set_id: Optional[str]):
    """Save last set ID to JSON file."""
    with open(LAST_SET_ID_FILE, 'w') as f:
        json.dump({'last_set_id': set_id}, f, indent=2)

def _get_initial_topics_data() -> List[dict]:
    """Returns the initial topics data."""
    now = datetime.utcnow()
    # Note: Using float for scores to allow for fractional updates
    return [
        {
            "id": "t1", "name": "Binary Search", "category": "arrays",
            "base_score": 30.0, "date_added": now - timedelta(days=120),
            "last_seen": now - timedelta(days=10), "attempts": 10, "successes": 9,
            "rec_scores": [30.0, 40.0], "rec_score_avg": 35.0
        },
        {
            "id": "t2", "name": "DFS (recursive)", "category": "graphs",
            "base_score": 70.0, "date_added": now - timedelta(days=200),
            "last_seen": now - timedelta(days=20), "attempts": 20, "successes": 8,
            "rec_scores": [70.0, 80.0], "rec_score_avg": 75.0
        },
        {
            "id": "t3", "name": "Union-Find", "category": "graphs",
            "base_score": 90.0, "date_added": now - timedelta(days=7),  # newly added
            "last_seen": None, "attempts": 2, "successes": 0,
            "rec_scores": [], "rec_score_avg": 50.0
        },
        {
            "id": "t4", "name": "Two Pointers", "category": "arrays",
            "base_score": 40.0, "date_added": now - timedelta(days=3),  # very recent
            "last_seen": None, "attempts": 0, "successes": 0,
            "rec_scores": [], "rec_score_avg": 50.0
        },
        {
            "id": "t5", "name": "Bitmask DP", "category": "dp",
            "base_score": 95.0, "date_added": now - timedelta(days=400),
            "last_seen": now - timedelta(days=50), "attempts": 5, "successes": 1,
            "rec_scores": [90.0], "rec_score_avg": 90.0
        },
        {
            "id": "t6", "name": "Sliding Window", "category": "arrays",
            "base_score": 45.0, "date_added": now - timedelta(days=60),
            "last_seen": now - timedelta(days=2), "attempts": 8, "successes": 6,
            "rec_scores": [40.0, 50.0], "rec_score_avg": 45.0
        },
        {
            "id": "t7", "name": "Topological Sort", "category": "graphs",
            "base_score": 80.0, "date_added": now - timedelta(days=30),
            "last_seen": now - timedelta(days=15), "attempts": 4, "successes": 1,
            "rec_scores": [70.0], "rec_score_avg": 70.0
        },
    ]

def _persist_topic_update(topic_id: str, updates: dict):
    """Update a single topic and save to JSON file."""
    topics_data = _load_topics_data()
    for t in topics_data:
        if t["id"] == topic_id:
            t.update(updates)
            _save_topics_data(topics_data)
            return
    print(f"ERROR: Topic ID {topic_id} not found for persistence.")

def _persist_recommendation_set(set_id: str, picked: List[dict]):
    """Store the generated set-to-topic mapping in JSON file."""
    recommendation_sets = _load_recommendation_sets()
    recommendation_sets[set_id] = [
        {"rec_id": f"{set_id}-{i}", "topic_id": p["id"], "category": p["category"]}
        for i, p in enumerate(picked, start=1)
    ]
    _save_recommendation_sets(recommendation_sets)

# --------------------------- Utility functions --------------------------------------------
def days_since(dt: Optional[datetime], now: datetime) -> Optional[float]:
    if dt is None:
        return None
    return max(0.0, (now - dt).total_seconds() / 86400.0)


def laplace_success_rate(successes: int, attempts: int, alpha: float = 1.0, beta: float = 1.0) -> float:
    """Return smoothed success rate using Laplace smoothing to handle zero attempts."""
    return (successes + alpha) / (attempts + alpha + beta)


# --------------------------- Core priority function --------------------------------------
def _compute_priority(topic: dict, now: datetime) -> Tuple[float, dict]:
    """
    Returns (priority_score, breakdown) for a topic.
    Includes Anki-like adjustment to desired interval based on rec_score_avg.
    """
    attempts = int(topic.get("attempts", 0))
    successes = int(topic.get("successes", 0))
    success_rate = laplace_success_rate(successes, attempts)  # 0..1, smoothed
    struggle_index = 1.0 - success_rate

    # Base difficulty normalization (1..100 -> 0..1)
    base_score = float(topic.get("base_score", 50))
    base_norm = max(0.0, min(1.0, (base_score - 1.0) / 99.0))

    # Novelty: linear decay over NEW_TOPIC_WINDOW_DAYS
    date_added = topic.get("date_added", now)
    days_added = days_since(date_added, now)
    if days_added is None:
        days_added = 9999.0
    novelty = 0.0
    if days_added <= NEW_TOPIC_WINDOW_DAYS:
        novelty = max(0.0, (NEW_TOPIC_WINDOW_DAYS - days_added) / float(NEW_TOPIC_WINDOW_DAYS))

    # Due factor (spaced repetition)
    last_seen = topic.get("last_seen")
    # if never seen, treat as "very due" but respect date_added
    if last_seen is None:
        days_since_seen = min(days_added + 30.0, 365.0)
    else:
        days_since_seen = days_since(last_seen, now)

    # Anki-like Spacing Adjustment: harder topics (higher rec_score_avg) should be spaced less
    rec_score_avg = topic.get("rec_score_avg", 50.0)
    # Scale from 0 to 1, where 0=easiest (1), 1=hardest (100). Default (50) is 0.5.
    rec_difficulty_norm = max(0.0, min(1.0, (rec_score_avg - 1.0) / 99.0))
    
    # Due multiplier: Easier topics (low rec_difficulty_norm) get a larger multiplier (more spacing).
    # Range: Hardest (1.0) => 1.0, Easiest (0.0) => 4.0. Default (0.5) => 2.5.
    due_multiplier = 1.0 + (1.0 - rec_difficulty_norm) * 3.0 # Range 1.0 to 4.0

    # desired_interval grows with success_rate AND due_multiplier (from rec_score_avg)
    desired_interval = BASE_INTERVAL_DAYS * (1.0 + success_rate * 7.0) * due_multiplier # range ~3 .. 96 days
    
    due_raw = days_since_seen / max(1.0, desired_interval)
    due_norm = min(2.0, due_raw) / 2.0  # clamp and normalize into 0..1

    # final weighted priority
    priority = (
        W_STRUGGLE * struggle_index +
        W_DUE * due_norm +
        W_BASE * base_norm +
        W_NOVELTY * novelty
    )

    breakdown = {
        "success_rate": round(success_rate, 4),
        "struggle_index": round(struggle_index, 4),
        "base_norm": round(base_norm, 4),
        "novelty": round(novelty, 4),
        "days_since_seen": round(days_since_seen, 2),
        "rec_score_avg": round(rec_score_avg, 2),
        "due_multiplier": round(due_multiplier, 2),
        "desired_interval": round(desired_interval, 2),
        "due_norm": round(due_norm, 4),
        "priority_raw": round(priority, 6)
    }

    return max(0.0, priority), breakdown


# --------------------------- Weighted sampling without replacement ------------------------
def _weighted_sample_without_replacement(items: List[dict], k: int, category_key: str = "category") -> List[dict]:
    """
    items: list of dicts, each dict must have 'priority' key (>=0) and optionally 'category' key.
    k: number to sample
    Returns chosen list (in chosen order).
    Applies a diversity penalty to topics sharing category with an already-picked item.
    """
    remaining = [dict(item) for item in items]  # shallow copy
    chosen = []

    if k <= 0:
        return chosen

    k = min(k, len(remaining))
    for pick_index in range(k):
        total_weight = sum(t["priority"] for t in remaining)
        if total_weight <= 0.0:
            # fallback: pick uniformly at random from remaining
            if not remaining:
                break
            pick = random.choice(remaining)
            remaining.remove(pick)
            chosen.append(pick)
        else:
            r = random.random() * total_weight
            acc = 0.0
            pick = None
            pick_idx = -1
            for idx, t in enumerate(remaining):
                acc += t["priority"]
                if acc >= r:
                    pick = remaining.pop(idx)
                    pick_idx = idx
                    break
            if pick is None:
                # floating-point safety
                pick = remaining.pop(-1)

            chosen.append(pick)

        # diversity penalty: reduce priorities in same category
        chosen_category = pick.get(category_key, None)
        if chosen_category is not None:
            for r in remaining:
                if r.get(category_key, None) == chosen_category:
                    r["priority"] *= DIVERSITY_PENALTY

    return chosen


# --------------------------- Filtering functions -------------------------------------------
def filter_topics(topics: List[dict], filters: Dict = None) -> List[dict]:
    """
    Filter topics based on provided criteria.
    
    filters dict can contain:
    - added_in_last_days: int - only topics added in last X days
    - not_asked_in_last_days: int - only topics not asked in last X days  
    - min_base_score: int - only topics with base_score >= X
    - categories: List[str] - only topics from specified categories
    """
    if not filters:
        return topics
    
    now = datetime.utcnow()
    filtered = topics.copy()
    
    # Filter by topics added in last X days
    if 'added_in_last_days' in filters:
        days_limit = filters['added_in_last_days']
        filtered = [
            t for t in filtered 
            if t.get('date_added') and 
            days_since(t['date_added'], now) is not None and 
            days_since(t['date_added'], now) <= days_limit
        ]
    
    # Filter by topics not asked in last X days
    if 'not_asked_in_last_days' in filters:
        days_limit = filters['not_asked_in_last_days']
        filtered = [
            t for t in filtered 
            if not t.get('last_seen') or 
            days_since(t['last_seen'], now) is None or 
            days_since(t['last_seen'], now) >= days_limit
        ]
    
    # Filter by minimum base score
    if 'min_base_score' in filters:
        min_score = filters['min_base_score']
        filtered = [
            t for t in filtered 
            if t.get('base_score', 50) >= min_score
        ]
    
    # Filter by categories
    if 'categories' in filters and filters['categories']:
        categories = [cat.lower() for cat in filters['categories']]
        filtered = [
            t for t in filtered 
            if t.get('category', '').lower() in categories
        ]
    
    return filtered


if __name__ == "__main__":
    random.seed(42)  # for deterministic demo run
    print("Engine module loaded successfully")
