import streamlit as st
import google.generativeai as genai
import json
import os
from typing import List, Dict

class MealSuggestionAgent:
    def __init__(self):
        self.model = None
        self.model_name = None
        self.setup_gemini()
    
    def setup_gemini(self):
        """Setup Gemini API with model detection"""
        try:
            api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                
                # Try to get available models and select the best one
                self.model_name = self.select_available_model()
                
                if self.model_name:
                    self.model = genai.GenerativeModel(self.model_name)
                    st.success(f"✅ Gemini AI connected with model: {self.model_name}")
                else:
                    st.warning("⚠️ No compatible Gemini model found. Using fallback mode.")
            else:
                st.warning("⚠️ Gemini API key not found. Using fallback mode.")
        except Exception as e:
            st.error(f"❌ Failed to setup Gemini: {e}")
    
    def select_available_model(self):
        """Select the best available model from the API"""
        try:
            # List of models to try in priority order
            preferred_models = [
                "gemini-2.5-flash-lite",  # Primary choice
                "gemini-1.5-flash",       # Fallback 1
                "gemini-1.5-pro",         # Fallback 2
                "gemini-1.0-pro",         # Fallback 3
            ]
            
            # Get available models
            available_models = list(genai.list_models())
            available_model_names = [model.name for model in available_models]
            
            st.write(f"🔍 Available models: {[name.split('/')[-1] for name in available_model_names]}")
            
            # Find the first preferred model that's available
            for model in preferred_models:
                full_model_name = f"models/{model}"
                if full_model_name in available_model_names:
                    st.write(f"✅ Selected model: {model}")
                    return model
            
            # If no preferred model found, use first available model that supports generation
            for model in available_models:
                if 'generateContent' in model.supported_generation_methods:
                    selected = model.name.split('/')[-1]
                    st.write(f"⚠️ Using available model: {selected}")
                    return selected
            
            return None
            
        except Exception as e:
            st.error(f"❌ Error detecting models: {e}")
            # Fallback to the specific model we know should work
            return "gemini-2.5-flash-lite"
    
    def suggest_meals(self, pantry_items: List[str], preferences: Dict) -> List[Dict]:
        """Generate meal suggestions"""
        if self.model:
            try:
                return self._get_gemini_suggestions(pantry_items, preferences)
            except Exception as e:
                st.error(f"⚠️ Gemini API failed: {e}")
                st.info("🔄 Using fallback meal suggestions...")
        
        return self._get_fallback_suggestions(pantry_items, preferences)
    
    def _get_gemini_suggestions(self, pantry_items: List[str], preferences: Dict) -> List[Dict]:
        """Get suggestions from Gemini"""
        prompt = self._build_meal_prompt(pantry_items, preferences)
        
        try:
            # Configure generation for better results
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
            
            response = self.model.generate_content(prompt, generation_config=generation_config)
            return self._parse_response(response.text, pantry_items)
        except Exception as e:
            raise Exception(f"Gemini API error: {e}")
    
    def _build_meal_prompt(self, pantry_items: List[str], preferences: Dict) -> str:
        return f"""
        You are a helpful cooking assistant. Suggest 3 simple meals based on available ingredients.
        
        AVAILABLE INGREDIENTS: {', '.join(pantry_items)}
        
        USER PREFERENCES:
        - Diet: {preferences.get('diet', 'no restrictions')}
        - Allergies: {', '.join(preferences.get('allergies', ['none']))}
        - Spice Level: {preferences.get('spice_level', 'medium')}
        - Cuisine Preference: {', '.join(preferences.get('cuisine_preference', ['any']))}
        
        IMPORTANT: Return ONLY valid JSON format. No additional text.
        
        Return a JSON array with exactly 3 meal objects. Each meal should have:
        - "name": meal name (string)
        - "ingredients": array of ingredient strings
        - "instructions": array of cooking step strings (2-3 steps)
        - "cooking_time": string like "20 minutes"
        - "difficulty": "Easy", "Medium", or "Hard"
        
        Be practical and use mostly available ingredients. Mark missing ingredients appropriately.
        """
    
    def _parse_response(self, response_text: str, pantry_items: List[str]) -> List[Dict]:
        """Parse Gemini response with robust error handling"""
        try:
            # Clean response text
            cleaned_text = response_text.strip()
            
            # Remove markdown code blocks
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()
            
            # Try to extract JSON if not directly parseable
            start_idx = cleaned_text.find('[')
            end_idx = cleaned_text.rfind(']') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = cleaned_text[start_idx:end_idx]
                suggestions = json.loads(json_str)
            else:
                # If no array found, try to find any JSON structure
                start_idx = cleaned_text.find('{')
                end_idx = cleaned_text.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = cleaned_text[start_idx:end_idx]
                    single_meal = json.loads(json_str)
                    suggestions = [single_meal]
                else:
                    raise ValueError("No valid JSON found in response")
            
            # Ensure we have a list
            if not isinstance(suggestions, list):
                suggestions = [suggestions]
            
            # Add missing ingredients analysis
            pantry_lower = [item.lower() for item in pantry_items]
            for meal in suggestions:
                missing = []
                for ingredient in meal.get('ingredients', []):
                    if isinstance(ingredient, str):
                        ing_lower = ingredient.lower()
                        found = False
                        for pantry_item in pantry_lower:
                            if pantry_item in ing_lower or ing_lower in pantry_item:
                                found = True
                                break
                        if not found:
                            missing.append(ingredient)
                meal['missing_ingredients'] = missing
            
            return suggestions[:3]  # Return max 3 meals
            
        except Exception as e:
            st.error(f"⚠️ Failed to parse Gemini response: {e}")
            st.write("📄 Response was:", response_text[:500] + "..." if len(response_text) > 500 else response_text)
            return self._get_fallback_suggestions(pantry_items, {})
    
    def _get_fallback_suggestions(self, pantry_items: List[str], preferences: Dict) -> List[Dict]:
        """Enhanced fallback meal suggestions"""
        pantry_str = " ".join(pantry_items).lower()
        diet = preferences.get('diet', 'vegetarian')
        
        # Enhanced fallback meals with better matching
        all_meals = [
            {
                "name": "Tomato Rice",
                "ingredients": ["rice", "tomatoes", "onions", "oil", "salt", "spices"],
                "instructions": ["Cook rice separately", "Sauté tomatoes and onions in oil", "Mix with rice and spices", "Cook for 5 more minutes"],
                "cooking_time": "20 minutes",
                "difficulty": "Easy"
            },
            {
                "name": "Egg Curry", 
                "ingredients": ["eggs", "tomatoes", "onions", "coriander", "masala", "oil", "spices"],
                "instructions": ["Boil and peel eggs", "Sauté onions and tomatoes", "Add masala and spices", "Add eggs and simmer", "Garnish with coriander"],
                "cooking_time": "25 minutes", 
                "difficulty": "Medium"
            },
            {
                "name": "Vegetable Fried Rice",
                "ingredients": ["rice", "onions", "carrots", "oil", "soy sauce", "vegetables"],
                "instructions": ["Cook rice and cool", "Stir-fry vegetables", "Add rice and soy sauce", "Mix well and serve"],
                "cooking_time": "30 minutes",
                "difficulty": "Easy"
            },
            {
                "name": "Potato Curry",
                "ingredients": ["potatoes", "onions", "tomatoes", "spices", "oil", "coriander"],
                "instructions": ["Boil and chop potatoes", "Make onion-tomato gravy", "Add potatoes and spices", "Simmer for 10 minutes"],
                "cooking_time": "35 minutes",
                "difficulty": "Easy"
            }
        ]
        
        # Filter meals based on available ingredients and diet
        suitable_meals = []
        for meal in all_meals:
            if diet != "vegetarian" and "chicken" in meal['name'].lower():
                continue
                
            # Count available ingredients
            available_count = 0
            missing_ingredients = []
            
            for ingredient in meal['ingredients']:
                found = False
                for pantry_item in pantry_items:
                    if pantry_item.lower() in ingredient.lower() or ingredient.lower() in pantry_item.lower():
                        found = True
                        break
                if found:
                    available_count += 1
                else:
                    missing_ingredients.append(ingredient)
            
            # Include meal if at least 50% ingredients are available
            if available_count >= len(meal['ingredients']) * 0.5:
                meal['missing_ingredients'] = missing_ingredients
                suitable_meals.append(meal)
        
        return suitable_meals[:3]  # Return max 3 meals
    
    def get_custom_dish_ingredients(self, dish_name: str, pantry_items: List[str], preferences: Dict) -> Dict:
        """Analyze custom dish"""
        if self.model:
            try:
                prompt = f"""
                Analyze the dish "{dish_name}" and provide ingredients and instructions.
                
                Available pantry: {', '.join(pantry_items)}
                Preferences: {json.dumps(preferences)}
                
                Return ONLY valid JSON with these exact keys:
                - "name": dish name
                - "ingredients": array of strings
                - "instructions": array of strings (2-3 steps)
                - "cooking_time": string
                - "difficulty": "Easy", "Medium", or "Hard"
                
                No additional text.
                """
                
                generation_config = {
                    "temperature": 0.3,  # Lower temperature for more consistent output
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 1024,
                }
                
                response = self.model.generate_content(prompt, generation_config=generation_config)
                return self._parse_custom_response(response.text, dish_name, pantry_items)
            except Exception as e:
                st.error(f"Custom dish analysis failed: {e}")
        
        return self._get_fallback_custom_dish(dish_name, pantry_items, preferences)
    
    def _parse_custom_response(self, response_text: str, dish_name: str, pantry_items: List[str]) -> Dict:
        """Parse custom dish response"""
        try:
            # Clean response
            cleaned_text = response_text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()
            
            # Extract JSON
            start_idx = cleaned_text.find('{')
            end_idx = cleaned_text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = cleaned_text[start_idx:end_idx]
                meal_data = json.loads(json_str)
            else:
                meal_data = json.loads(cleaned_text)
            
            # Add missing ingredients analysis
            pantry_lower = [item.lower() for item in pantry_items]
            missing_ingredients = []
            for ingredient in meal_data.get('ingredients', []):
                if isinstance(ingredient, str):
                    ing_lower = ingredient.lower()
                    found = False
                    for pantry_item in pantry_lower:
                        if pantry_item in ing_lower or ing_lower in pantry_item:
                            found = True
                            break
                    if not found:
                        missing_ingredients.append(ingredient)
            
            meal_data['missing_ingredients'] = missing_ingredients
            
            # Ensure all required fields
            meal_data.setdefault('name', dish_name)
            meal_data.setdefault('cooking_time', '30 minutes')
            meal_data.setdefault('difficulty', 'Medium')
            meal_data.setdefault('instructions', ['Prepare ingredients', 'Cook according to recipe', 'Serve hot'])
            
            return meal_data
            
        except Exception as e:
            st.error(f"Failed to parse custom dish response: {e}")
            return self._get_fallback_custom_dish(dish_name, pantry_items, {})
    
    def _get_fallback_custom_dish(self, dish_name: str, pantry_items: List[str], preferences: Dict) -> Dict:
        """Enhanced fallback for custom dishes"""
        dish_lower = dish_name.lower()
        
        # Enhanced common ingredient patterns
        common_ingredients = {
            "biriyani": ["basmati rice", "chicken", "onions", "tomatoes", "yogurt", "ginger", "garlic", "biriyani masala", "mint", "coriander", "oil", "spices"],
            "biryani": ["basmati rice", "chicken", "onions", "tomatoes", "yogurt", "ginger", "garlic", "biryani masala", "mint", "coriander", "oil", "spices"],
            "pasta": ["pasta", "tomatoes", "onions", "garlic", "oil", "herbs", "cheese"],
            "curry": ["onions", "tomatoes", "spices", "oil", "main protein/vegetable", "ginger", "garlic"],
            "fried rice": ["rice", "vegetables", "oil", "soy sauce", "eggs", "spring onions"],
            "soup": ["vegetables", "broth", "herbs", "spices", "main ingredient"],
            "salad": ["lettuce", "vegetables", "dressing", "herbs", "protein"]
        }
        
        # Find matching dish type
        ingredients = []
        for dish_type, common_ingreds in common_ingredients.items():
            if dish_type in dish_lower:
                ingredients = common_ingreds
        
        # If no match, use generic ingredients
        if not ingredients:
            ingredients = ["main ingredient", "vegetables", "spices", "oil", "herbs", "seasoning"]
        
        # Analyze missing ingredients
        pantry_lower = [item.lower() for item in pantry_items]
        missing_ingredients = []
        for ingredient in ingredients:
            found = False
            for pantry_item in pantry_lower:
                if pantry_item in ingredient or ingredient in pantry_item:
                    found = True
                    break
            if not found:
                missing_ingredients.append(ingredient)
        
        # Special instructions for common dishes
        if 'biriyani' in dish_lower or 'biryani' in dish_lower:
            instructions = [
                "Marinate chicken with yogurt and spices for 30 minutes",
                "Fry onions until golden brown and cook rice separately",
                "Layer rice and chicken mixture in a pot and cook on low heat",
                "Let it rest for 15 minutes before serving with raita"
            ]
            cooking_time = "60 minutes"
            difficulty = "Medium"
        else:
            instructions = [
                f"Prepare ingredients for {dish_name}",
                "Cook according to your preferred recipe",
                "Serve hot and enjoy"
            ]
            cooking_time = "30 minutes"
            difficulty = "Medium"
        
        return {
            "name": dish_name,
            "ingredients": ingredients,
            "instructions": instructions,
            "cooking_time": cooking_time,
            "difficulty": difficulty,
            "missing_ingredients": missing_ingredients
        }