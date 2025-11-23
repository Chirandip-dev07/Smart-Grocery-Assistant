import streamlit as st
from .pantry_agent import PantryAgent
from .meal_agent import MealSuggestionAgent
from .shopping_agent import ShoppingListAgent
from .price_agent import PriceCheckerAgent

class OrchestratorAgent:
    def __init__(self):
        if 'orchestrator' not in st.session_state:
            st.session_state.orchestrator = self._initialize_agents()
        
        self.pantry_agent = st.session_state.orchestrator['pantry_agent']
        self.meal_agent = st.session_state.orchestrator['meal_agent']
        self.shopping_agent = st.session_state.orchestrator['shopping_agent']
        self.price_agent = st.session_state.orchestrator['price_agent']
        self.user_preferences = st.session_state.orchestrator['user_preferences']
    
    def _initialize_agents(self):
        """Initialize all agents and store in session state"""
        return {
            'pantry_agent': PantryAgent(),
            'meal_agent': MealSuggestionAgent(),
            'shopping_agent': ShoppingListAgent(),
            'price_agent': PriceCheckerAgent(),
            'user_preferences': {
                "diet": "vegetarian",
                "spice_level": "medium",
                "allergies": [],
                "cuisine_preference": ["indian", "continental"],
                "budget_per_meal": 200,
                "cooking_skill": "intermediate"
            }
        }
    
    def run_complete_workflow(self, servings=2):
        results = {}
        
        try:
            pantry_items = self.pantry_agent.get_current_pantry()
            if not pantry_items:
                return {"error": "Pantry is empty! Please add some items first."}
            
            meal_suggestions = self.meal_agent.suggest_meals(pantry_items, self.user_preferences)
            if not meal_suggestions:
                return {"error": "No suitable meals found with current pantry items."}
            
            shopping_list = self.shopping_agent.generate_list(meal_suggestions, servings)
            
            if shopping_list:
                price_optimization = self.price_agent.optimize_purchases(shopping_list)
            else:
                price_optimization = {
                    "store_recommendation": "No items needed",
                    "total_cost": 0,
                    "optimized_list": [],
                    "savings": 0
                }
            
            results = {
                "pantry_items": pantry_items,
                "meal_suggestions": meal_suggestions,
                "shopping_list": price_optimization["optimized_list"],
                "store_recommendation": price_optimization["store_recommendation"],
                "total_cost": price_optimization["total_cost"],
                "savings": price_optimization["savings"],
                "servings": servings,
                "success": True
            }
            
        except Exception as e:
            results = {"error": f"Workflow failed: {str(e)}"}
        
        return results
    
    def handle_custom_dish(self, dish_name, servings=2):
        """Handle custom dish workflow"""
        pantry_items = self.pantry_agent.get_current_pantry()
        custom_meal = self.meal_agent.get_custom_dish_ingredients(dish_name, pantry_items, self.user_preferences)
        
        if custom_meal:
            shopping_list = self.shopping_agent.generate_list([custom_meal], servings)
            
            if shopping_list:
                price_optimization = self.price_agent.optimize_purchases(shopping_list)
            else:
                price_optimization = {
                    "store_recommendation": "No items needed",
                    "total_cost": 0,
                    "optimized_list": [],
                    "savings": 0
                }
            
            return {
                "pantry_items": pantry_items,
                "meal_suggestions": [custom_meal],
                "shopping_list": price_optimization["optimized_list"],
                "store_recommendation": price_optimization["store_recommendation"],
                "total_cost": price_optimization["total_cost"],
                "savings": price_optimization["savings"],
                "selected_meal": dish_name,
                "servings": servings,
                "success": True
            }
        return None
    
    def update_preferences(self, preferences):
        """Update user preferences"""
        self.user_preferences.update(preferences)
        st.session_state.orchestrator['user_preferences'] = self.user_preferences