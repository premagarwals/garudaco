#!/usr/bin/env python3
"""Initialize fresh JSON data files for Garudaco"""

import json
import os

def create_fresh_data_files():
    """Create fresh JSON data files with minimal initial data"""
    
    # Create empty topics data
    topics_data = []
    
    # Create empty recommendation sets
    recommendation_sets = {}
    
    # Create initial set ID counter
    last_set_id = {"last_set_id": 0}
    
    # Write files
    with open('topics_data.json', 'w') as f:
        json.dump(topics_data, f, indent=2)
    
    with open('recommendation_sets.json', 'w') as f:
        json.dump(recommendation_sets, f, indent=2)
    
    with open('last_set_id.json', 'w') as f:
        json.dump(last_set_id, f, indent=2)
    
    print("✅ Fresh data files created successfully!")
    print("📁 Created: topics_data.json (empty)")
    print("📁 Created: recommendation_sets.json (empty)")
    print("📁 Created: last_set_id.json (initialized)")

if __name__ == "__main__":
    create_fresh_data_files()