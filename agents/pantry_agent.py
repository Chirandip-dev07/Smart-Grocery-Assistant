import streamlit as st
import json
from datetime import datetime
from typing import List, Dict

class PantryMemory:
    def __init__(self):
        if 'pantry' not in st.session_state:
            st.session_state.pantry = {}
    
    def add_item(self, item: str, quantity: str = "1", category: str = "general"):
        item_key = item.lower().strip()
        st.session_state.pantry[item_key] = {
            "quantity": quantity,
            "category": category,
            "added_date": datetime.now().isoformat()
        }
    
    def remove_item(self, item: str):
        item_key = item.lower().strip()
        if item_key in st.session_state.pantry:
            del st.session_state.pantry[item_key]
            return True
        return False
    
    def get_all_items(self) -> List[str]:
        return list(st.session_state.pantry.keys())
    
    def get_item_details(self, item: str) -> Dict:
        return st.session_state.pantry.get(item.lower().strip(), {})
    
    def search_by_category(self, category: str) -> List[str]:
        return [item for item, details in st.session_state.pantry.items() 
                if details.get("category", "").lower() == category.lower()]

class PantryAgent:
    def __init__(self):
        self.memory = PantryMemory()
    
    def add_item(self, item: str, quantity: str = "1", category: str = "general"):
        self.memory.add_item(item, quantity, category)
    
    def remove_item(self, item: str):
        return self.memory.remove_item(item)
    
    def get_current_pantry(self) -> List[str]:
        return self.memory.get_all_items()
    
    def get_pantry_data(self) -> Dict:
        return st.session_state.pantry
    
    def display_pantry_stats(self):
        items = self.get_current_pantry()
        categories = {}
        for item, details in st.session_state.pantry.items():
            cat = details.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            "total_items": len(items),
            "categories": categories
        }