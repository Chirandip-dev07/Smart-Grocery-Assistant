import streamlit as st
from typing import List, Dict

class PriceCheckTool:
    def __init__(self):
        self.store_prices = {
            "JioMart": {
                "tomatoes": 20, "onions": 30, "coriander": 10,
                "masala": 50, "oil": 120, "spices": 40, "eggs": 60,
                "rice": 80, "chicken": 200, "potatoes": 25
            },
            "BigBasket": {
                "tomatoes": 25, "onions": 28, "coriander": 12,
                "masala": 55, "oil": 115, "spices": 45, "eggs": 65,
                "rice": 85, "chicken": 210, "potatoes": 30
            },
            "Local Store": {
                "tomatoes": 18, "onions": 32, "coriander": 8,
                "masala": 48, "oil": 125, "spices": 35, "eggs": 58,
                "rice": 75, "chicken": 190, "potatoes": 20
            }
        }
    
    def get_prices(self, items: List[str]) -> Dict[str, Dict]:
        results = {}
        for store, prices in self.store_prices.items():
            store_total = 0
            store_prices_detail = {}
            for item in items:
                item_key = item.lower()
                price = None
                for price_item, price_value in prices.items():
                    if price_item in item_key or item_key in price_item:
                        price = price_value
                        break
                if price is None:
                    price = 40
                store_prices_detail[item] = price
                store_total += price
            results[store] = {
                "prices": store_prices_detail,
                "total": store_total
            }
        return results

class PriceCheckerAgent:
    def __init__(self):
        self.price_tool = PriceCheckTool()
    
    def optimize_purchases(self, shopping_list: List[Dict]) -> Dict:
        """Find best store for purchases"""
        if not shopping_list:
            return {
                "store_recommendation": "No items needed",
                "total_cost": 0,
                "price_comparison": {},
                "optimized_list": [],
                "savings": 0
            }
        
        items = [item["item"] for item in shopping_list]
        price_data = self.price_tool.get_prices(items)
        
        cheapest_store = min(price_data.keys(), 
                           key=lambda store: price_data[store]["total"])
        
        for item in shopping_list:
            item_name = item["item"].lower()
            item["estimated_price"] = price_data[cheapest_store]["prices"].get(item_name, 0)
        
        prices = [data["total"] for data in price_data.values()]
        max_price = max(prices)
        min_price = min(prices)
        savings = max_price - min_price
        
        return {
            "store_recommendation": cheapest_store,
            "total_cost": price_data[cheapest_store]["total"],
            "price_comparison": price_data,
            "optimized_list": shopping_list,
            "savings": savings,
            "savings_percentage": int((savings / max_price) * 100) if max_price > 0 else 0
        }