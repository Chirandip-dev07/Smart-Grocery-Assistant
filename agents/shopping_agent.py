import streamlit as st
from typing import List, Dict

class GroceryTools:
    @staticmethod
    def calculate_quantity(item: str, servings: int) -> str:
        quantity_map = {
            "rice": f"{servings * 100}g",
            "tomatoes": f"{servings * 2} pieces",
            "onions": f"{servings} pieces",
            "eggs": f"{servings} pieces",
            
        }
        return quantity_map.get(item.lower(), f"{servings} portions")
    
    @staticmethod
    def categorize_item(item: str) -> str:
        categories = {
            'vegetables': ['tomato', 'onion', 'potato', 'carrot'],
            'spices': ['masala', 'spice', 'turmeric'],
            'dairy': ['milk', 'butter', 'cheese'],
            'grains': ['rice', 'flour', 'bread'],
            'protein': ['chicken', 'fish', 'eggs'],
            'essentials': ['oil', 'salt']
        }
        
        item_lower = item.lower()
        for category, items in categories.items():
            if any(food in item_lower for food in items):
                return category
        return 'other'

class ShoppingListAgent:
    def __init__(self):
        self.tools = GroceryTools()
    
    def generate_list(self, meal_suggestions: List[Dict], servings: int = 2) -> List[Dict]:
        """Generate shopping list from meal suggestions"""
        all_missing = set()
        
        for meal in meal_suggestions:
            for ingredient in meal.get("missing_ingredients", []):
                clean_ingredient = self._clean_ingredient_name(ingredient)
                if clean_ingredient:
                    all_missing.add(clean_ingredient)
        
        shopping_list = []
        for item in all_missing:
            quantity = self.tools.calculate_quantity(item, servings)
            shopping_list.append({
                "item": item.title(),
                "quantity": quantity,
                "category": self.tools.categorize_item(item),
                "estimated_price": None
            })
        
        return shopping_list
    
    def _clean_ingredient_name(self, ingredient: str) -> str:
        """Clean ingredient names"""
        ingredient = ingredient.lower().strip()
        removals = ['fresh ', 'chopped ', 'diced ', 'sliced ']
        for removal in removals:
            ingredient = ingredient.replace(removal, '')
        return ingredient.strip()