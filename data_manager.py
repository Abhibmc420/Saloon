import json
import os
import pandas as pd
from typing import List, Dict, Any

class DataManager:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.ensure_data_directory()
        self.ensure_file_exists()
    
    def ensure_data_directory(self):
        """Ensure the data directory exists"""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
    
    def ensure_file_exists(self):
        """Ensure the JSON file exists with empty array if not present"""
        if not os.path.exists(self.file_path):
            self.save_data([])
    
    def load_data(self) -> List[Dict[str, Any]]:
        """Load data from JSON file"""
        try:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_data(self, data: List[Dict[str, Any]]):
        """Save data to JSON file"""
        with open(self.file_path, 'w') as file:
            json.dump(data, file, indent=2)
    
    def add_item(self, item: Dict[str, Any]) -> bool:
        """Add a new item to the data"""
        data = self.load_data()
        # Generate ID if not provided
        if 'id' not in item:
            max_id = max([d.get('id', 0) for d in data], default=0)
            item['id'] = max_id + 1
        data.append(item)
        self.save_data(data)
        return True
    
    def update_item(self, item_id: int, updated_item: Dict[str, Any]) -> bool:
        """Update an existing item"""
        data = self.load_data()
        for i, item in enumerate(data):
            if item.get('id') == item_id:
                updated_item['id'] = item_id
                data[i] = updated_item
                self.save_data(data)
                return True
        return False
    
    def delete_item(self, item_id: int) -> bool:
        """Delete an item by ID"""
        data = self.load_data()
        original_length = len(data)
        data = [item for item in data if item.get('id') != item_id]
        if len(data) < original_length:
            self.save_data(data)
            return True
        return False
    
    def get_item_by_id(self, item_id: int) -> Dict[str, Any]:
        """Get a specific item by ID"""
        data = self.load_data()
        for item in data:
            if item.get('id') == item_id:
                return item
        return {}
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert data to pandas DataFrame"""
        data = self.load_data()
        if not data:
            return pd.DataFrame()
        return pd.DataFrame(data)
