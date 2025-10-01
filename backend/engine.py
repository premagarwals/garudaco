import json
import math
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple

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

# --------------------------- JSON Data Storage & Persistence ----------------------------------

# File paths for JSON storage
TOPICS_DATA_FILE = "topics_data.json"
RECOMMENDATION_SETS_FILE = "recommendation_sets.json"
LAST_SET_ID_FILE = "last_set_id.json"

def _load_topics_data() -> List[dict]:
    """Load topics data from JSON file."""
    try:
        with open(TOPICS_DATA_FILE, 'r') as f:
            data = json.load(f)
            # Convert datetime strings back to datetime objects
            for topic in data:
                if topic.get('date_added'):
                    topic['date_added'] = datetime.fromisoformat(topic['date_added'])
                if topic.get('last_seen'):
                    topic['last_seen'] = datetime.fromisoformat(topic['last_seen'])
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        # Return initial data if file doesn't exist or is corrupted
        return _get_initial_topics_data()

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

def fetch_all_topics() -> List[dict]:
    """Load topics from JSON file and return a copy."""
    topics_data = _load_topics_data()
    # Recalculate averages for safety
    for t in topics_data:
        t["rec_score_avg"] = sum(t["rec_scores"]) / len(t["rec_scores"]) if t["rec_scores"] else 50.0
        t["base_score"] = float(t["base_score"]) # Ensure score is float
    return [t.copy() for t in topics_data]

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

# --------------------------- New: Add Topic Function --------------------------------------

def add_new_topic(name: str, category: str, initial_difficulty: int) -> str:
    """Adds a new topic to the JSON storage with user-provided initial difficulty."""
    topics_data = _load_topics_data()
    
    # Simple ID generation
    new_id_num = len(topics_data) + 1
    new_id = f"t{new_id_num}"
    
    # Ensure score is within bounds [1, 100]
    initial_difficulty = max(1, min(100, initial_difficulty))
    
    now = datetime.utcnow()
    new_topic = {
        "id": new_id,
        "name": name,
        "category": category,
        "base_score": float(initial_difficulty), # initial difficulty is the base score
        "date_added": now,
        "last_seen": None,
        "attempts": 0,
        "successes": 0,
        "rec_scores": [],
        "rec_score_avg": 50.0 # Start with neutral average for due calculation
    }
    
    topics_data.append(new_topic)
    _save_topics_data(topics_data)
    return f"Topic '{name}' (ID: {new_id}) added with initial difficulty: {initial_difficulty}/100."

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


# --------------------------- Main API functions --------------------------------------------
def get_recommendations(count: int) -> List[str]:
    """
    Returns a list of JSON strings; each string is a recommendation.
    """
    now = datetime.utcnow()
    topics = fetch_all_topics()

    # compute priorities
    scored = []
    for t in topics:
        priority, breakdown = _compute_priority(t, now)
        scored.append({
            **t,
            "priority": priority,
            "breakdown": breakdown
        })

    # small epsilon to ensure non-zero where everything collapsed
    EPS = 1e-6
    for s in scored:
        if s["priority"] <= 0:
            s["priority"] = EPS

    # weighted sampling without replacement with category diversity handling
    picked = _weighted_sample_without_replacement(scored, count, category_key="category")

    # create set_id and create rec ids
    set_id = uuid.uuid4().hex
    _persist_recommendation_set(set_id, picked) # Persist mapping

    output = []
    for i, p in enumerate(picked, start=1):
        rec_id = f"{set_id}-{i}"
        rec = {
            "rec_id": rec_id,
            "set_id": set_id,
            "rec_no": i,
            "topic_id": p["id"],
            "topic_name": p["name"],
            "category": p.get("category"),
            "priority": round(p["priority"], 6),
            "breakdown": p["breakdown"]
        }
        output.append(json.dumps(rec))
    
    # Save the last set ID to JSON file
    _save_last_set_id(set_id)
    
    return output


def flag_recommendation_set(
    set_id: str,
    feedback: List[Dict[str, str or bool or int]]
) -> str:
    """
    Processes user feedback (easy/medium/hard and solved/unsolved) for a recommendation set.
    """
    recommendation_sets = _load_recommendation_sets()
    if set_id not in recommendation_sets:
        return f"Error: Recommendation set ID '{set_id}' not found."

    set_mapping = recommendation_sets[set_id]
    
    # 1. Map rec_no to topic_id
    rec_to_topic = {int(m["rec_id"].split('-')[-1]): m["topic_id"] for m in set_mapping}

    topics_data = _load_topics_data()
    
    for item in feedback:
        rec_no = item.get('rec_no')
        difficulty = item.get('difficulty', '').lower()
        solved = item.get('solved', False)

        if rec_no not in rec_to_topic or difficulty not in FLAG_SCORE_MAP:
            continue

        topic_id = rec_to_topic[rec_no]
        flag_score = FLAG_SCORE_MAP[difficulty]
        
        # Get current topic data to apply changes
        current_topic = next((t for t in topics_data if t["id"] == topic_id), None)
        if not current_topic:
            continue

        updates = {}

        # --- A. Update Attempts/Successes and last_seen ---
        updates["attempts"] = current_topic.get("attempts", 0) + 1
        if solved:
            updates["successes"] = current_topic.get("successes", 0) + 1
        updates["last_seen"] = datetime.utcnow()

        # --- B. Update Base Score (Slight Adjustment) and Rec Score Avg ---
        
        # 1. Adjust base_score
        current_base_score = current_topic.get("base_score", 50.0)
        # Move base score slightly towards the flagged difficulty score
        diff = flag_score - current_base_score
        base_score_adjustment = diff * BASE_SCORE_ADJUSTMENT_RATIO
        updates["base_score"] = round(max(1.0, min(100.0, current_base_score + base_score_adjustment)), 2)

        # 2. Update rec_scores list and average
        current_rec_scores = current_topic.get("rec_scores", [])
        current_rec_scores.append(float(flag_score))
        updates["rec_scores"] = current_rec_scores
        updates["rec_score_avg"] = round(sum(current_rec_scores) / len(current_rec_scores), 2)
        
        # --- C. Persist Updates ---
        _persist_topic_update(topic_id, updates)

    return f"Successfully processed feedback for {len(feedback)} recommendations in set '{set_id}'. Topic data updated."


# --------------------------- Interactive CLI (Demo) ------------------------------------------

def print_topic_summary(topics: List[dict]):
    """Prints a formatted table of core topic data."""
    print("\n" + "="*95)
    print(f"{'ID':<4} | {'Name':<25} | {'Cat':<10} | {'Base Score':<10} | {'Attempts/Suc.':<13} | {'Avg. Rec Score':<14}")
    print("-" * 95)
    for t in topics:
        attempts = t.get("attempts", 0)
        successes = t.get("successes", 0)
        rec_score_avg = t.get("rec_score_avg", 50.0)
        print(
            f"{t['id']:<4} | {t['name']:<25} | {t['category']:<10} | {t['base_score']:<10.2f} | "
            f"{attempts:>5}/{successes:<5} | {rec_score_avg:<14.2f}"
        )
    print("="*95 + "\n")

def print_recommendation_details(recs_json: List[str]):
    """Prints a formatted table of recommendation data."""
    print("\n" + "="*120)
    print("Recommendation Set Details:")
    recs = [json.loads(r) for r in recs_json]
    if not recs:
        print("No recommendations generated.")
        return
    
    print(f"Set ID: {recs[0]['set_id']}")
    
    print(f"{'Rec No':<6} | {'Topic ID':<8} | {'Topic Name':<20} | {'Category':<10} | {'Priority':<10} | {'Struggle':<10} | {'Due':<10} | {'Desired Int.':<12}")
    print("-" * 120)
    for r in recs:
        breakdown = r['breakdown']
        print(
            f"{r['rec_no']:<6} | {r['topic_id']:<8} | {r['topic_name']:<20} | {r['category']:<10} | {r['priority']:<10.4f} | "
            f"{breakdown['struggle_index']:<10.4f} | {breakdown['due_norm']:<10.4f} | {breakdown['desired_interval']:<12.2f}"
        )
    print("="*120 + "\n")


def cli_generate_recs():
    """CLI to generate and display recommendations."""
    while True:
        try:
            count = int(input("Enter number of recommendations to generate (e.g., 4): "))
            if count > 0:
                break
            print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    recs = get_recommendations(count)
    if not recs:
        print("Could not generate any recommendations.")
        return
        
    print_recommendation_details(recs)
    last_set_id = _load_last_set_id()
    print(f"Set ID '{last_set_id}' generated and stored for flagging.")


def cli_flag_recs():
    """CLI to simulate user flagging of the last generated set."""
    last_set_id = _load_last_set_id()
    if not last_set_id:
        print("Please generate a recommendation set first.")
        return

    set_id = last_set_id
    recommendation_sets = _load_recommendation_sets()
    set_mapping = recommendation_sets.get(set_id)
    if not set_mapping:
        print(f"Error: No mapping found for set ID '{set_id}'.")
        return

    feedback_list = []
    print(f"\nFlagging recommendations for Set ID: {last_set_id}")
    
    # Map rec_no to topic_name for display
    rec_info = {
        int(m["rec_id"].split('-')[-1]): m["topic_id"] for m in set_mapping
    }
    topic_map = {t["id"]: t["name"] for t in fetch_all_topics()}

    for rec_no in sorted(rec_info.keys()):
        topic_id = rec_info[rec_no]
        topic_name = topic_map.get(topic_id, "Unknown Topic")
        
        while True:
            difficulty_raw = input(f"Rec {rec_no} ({topic_name}) - Difficulty (E/M/H): ").lower()
            if difficulty_raw.startswith('e'):
                difficulty = 'easy'
                break
            elif difficulty_raw.startswith('m'):
                difficulty = 'medium'
                break
            elif difficulty_raw.startswith('h'):
                difficulty = 'hard'
                break
            else:
                print("Invalid difficulty. Please enter E (Easy), M (Medium), or H (Hard).")

        while True:
            solved_raw = input(f"Rec {rec_no} ({topic_name}) - Solved (Y/N): ").lower()
            if solved_raw.startswith('y'):
                solved = True
                break
            elif solved_raw.startswith('n'):
                solved = False
                break
            else:
                print("Invalid input. Please enter Y (Yes) or N (No).")
        
        feedback_list.append({
            'rec_no': rec_no,
            'difficulty': difficulty,
            'solved': solved
        })
        print("-" * 40)

    if feedback_list:
        status = flag_recommendation_set(set_id, feedback_list)
        print(f"\nFlagging Status: {status}")
        print("\nTOPIC DATA AFTER FLAGGING:")
        print_topic_summary(fetch_all_topics())
        
        # Invalidate last set ID to prevent re-flagging
        _save_last_set_id(None)
        
def cli_add_topic():
    """CLI to add a new topic."""
    name = input("Enter Topic Name: ")
    category = input("Enter Topic Category (e.g., arrays, graphs): ")
    
    while True:
        try:
            difficulty = int(input("Enter Initial Difficulty (1-100, 100=Hardest): "))
            if 1 <= difficulty <= 100:
                break
            print("Difficulty must be between 1 and 100.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            
    status = add_new_topic(name, category, difficulty)
    print(f"\n{status}")
    print_topic_summary(fetch_all_topics())


def cli_main():
    """Main function for the interactive CLI."""
    print("Welcome to the Recommendation Engine CLI.")
    
    while True:
        print("\n--- Main Menu ---")
        print("1. View Current Topic Data")
        print("2. Generate Recommendations")
        print("3. Add New Topic")
        last_set_id = _load_last_set_id()
        if last_set_id:
            print(f"4. Flag Last Set ({last_set_id})")
        else:
            print("4. (Generate recommendations first to enable flagging)")
        print("5. Exit")
        
        choice = input("Enter your choice (1-5): ")
        
        if choice == '1':
            print_topic_summary(fetch_all_topics())
        elif choice == '2':
            cli_generate_recs()
        elif choice == '3':
            cli_add_topic()
        elif choice == '4' and last_set_id:
            cli_flag_recs()
        elif choice == '5':
            print("Exiting. Goodbye! 👋")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    random.seed(42)  # for deterministic demo run
    cli_main()
