import streamlit as st
import pandas as pd
import plotly.express as px
from agents.orchestrator import OrchestratorAgent

# Page configuration
st.set_page_config(
    page_title="Smart Grocery Assistant",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    .agent-card {
        background-color: #F8F9FA;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2E86AB;
        margin-bottom: 1rem;
    }
    .meal-card {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🛒 Smart Grocery Assistant</h1>', unsafe_allow_html=True)
    st.markdown("### Your AI-Powered Kitchen Companion")
    
    # Initialize orchestrator
    orchestrator = OrchestratorAgent()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # User Preferences
        st.subheader("User Preferences")
        diet = st.selectbox("Diet", ["vegetarian", "non-vegetarian", "vegan"], index=0)
        spice_level = st.select_slider("Spice Level", ["mild", "medium", "hot"], value="medium")
        budget = st.slider("Budget per Meal (₹)", 50, 500, 200)
        
        allergies = st.multiselect(
            "Allergies",
            ["nuts", "dairy", "gluten", "seafood", "eggs"],
            default=[]
        )
        
        # Update preferences
        if st.button("Update Preferences"):
            orchestrator.update_preferences({
                "diet": diet,
                "spice_level": spice_level,
                "allergies": allergies,
                "budget_per_meal": budget
            })
            st.success("Preferences updated!")
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Dashboard", "🫙 Pantry", "🍽️ Meal Planning", "🛒 Shopping"])
    
    with tab1:
        show_dashboard(orchestrator)
    
    with tab2:
        show_pantry_management(orchestrator)
    
    with tab3:
        show_meal_planning(orchestrator)
    
    with tab4:
        show_shopping(orchestrator)

def show_dashboard(orchestrator):
    st.header("📊 Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        stats = orchestrator.pantry_agent.display_pantry_stats()
        st.metric("Total Pantry Items", stats["total_items"])
    
    with col2:
        st.metric("Available Meal Options", "3+")
    
    with col3:
        st.metric("Average Savings", "₹45")
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Quick Meal Check", use_container_width=True):
            st.session_state.current_tab = "Meal Planning"
            st.rerun()
    
    with col2:
        if st.button("📝 Generate Shopping List", use_container_width=True):
            st.session_state.current_tab = "Shopping"
            st.rerun()
    
    with col3:
        if st.button("🫙 Manage Pantry", use_container_width=True):
            st.session_state.current_tab = "Pantry"
            st.rerun()

def show_pantry_management(orchestrator):
    st.header("🫙 Pantry Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Current Pantry")
        pantry_data = orchestrator.pantry_agent.get_pantry_data()
        
        if pantry_data:
            # Convert to DataFrame for better display
            pantry_df = pd.DataFrame([
                {
                    "Item": item.title(),
                    "Quantity": details["quantity"],
                    "Category": details["category"],
                    "Added": details["added_date"][:10]
                }
                for item, details in pantry_data.items()
            ])
            
            st.dataframe(pantry_df, use_container_width=True)
            
            # Statistics
            stats = orchestrator.pantry_agent.display_pantry_stats()
            st.write(f"**Total Items:** {stats['total_items']}")
            for category, count in stats['categories'].items():
                st.write(f"**{category.title()}:** {count}")
        else:
            st.info("Your pantry is empty. Add some items to get started!")
    
    with col2:
        st.subheader("Add New Item")
        
        with st.form("add_item_form"):
            item_name = st.text_input("Item Name")
            quantity = st.text_input("Quantity", value="1")
            category = st.selectbox("Category", 
                ["vegetables", "fruits", "grains", "dairy", "protein", "spices", "essentials", "beverages", "other"])
            
            if st.form_submit_button("Add to Pantry"):
                if item_name:
                    orchestrator.pantry_agent.add_item(item_name, quantity, category)
                    st.success(f"Added {item_name} to pantry!")
                    st.rerun()
                else:
                    st.error("Please enter an item name")
        
        st.subheader("Remove Item")
        if pantry_data:
            item_to_remove = st.selectbox("Select item to remove", list(pantry_data.keys()))
            if st.button("Remove Item"):
                if orchestrator.pantry_agent.remove_item(item_to_remove):
                    st.success(f"Removed {item_to_remove} from pantry!")
                    st.rerun()
                else:
                    st.error("Item not found in pantry")

def show_meal_planning(orchestrator):
    st.header("🍽️ Meal Planning")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Meal Configuration")
        servings = st.slider("Number of Servings", 1, 8, 2)
        
        if st.button("🔄 Generate Meal Suggestions", type="primary"):
            with st.spinner("🤖 Agents are planning your meals..."):
                result = orchestrator.run_complete_workflow(servings)
                st.session_state.meal_result = result
        
        st.subheader("Custom Dish")
        custom_dish = st.text_input("Or enter a custom dish")
        if st.button("Analyze Custom Dish") and custom_dish:
            with st.spinner(f"Analyzing {custom_dish}..."):
                result = orchestrator.handle_custom_dish(custom_dish, servings)
                if result:
                    st.session_state.meal_result = result
                else:
                    st.error("Could not analyze the dish. Please try again.")
    
    with col2:
        if 'meal_result' in st.session_state:
            result = st.session_state.meal_result
            
            if result.get('error'):
                st.error(result['error'])
            elif result.get('success'):
                st.success("🎉 Meal plan generated successfully!")
                
                # Display meal suggestions
                st.subheader("Recommended Meals")
                for i, meal in enumerate(result['meal_suggestions']):
                    with st.expander(f"🍳 {meal['name']} - {meal.get('cooking_time', 'N/A')} - {meal.get('difficulty', 'N/A')}", expanded=i==0):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Ingredients:**")
                            for ingredient in meal.get('ingredients', []):
                                st.write(f"- {ingredient}")
                            
                            if meal.get('missing_ingredients'):
                                st.write("**Missing Ingredients:**")
                                for missing in meal['missing_ingredients']:
                                    st.write(f"❌ {missing}")
                        
                        with col2:
                            st.write("**Instructions:**")
                            for j, step in enumerate(meal.get('instructions', []), 1):
                                st.write(f"{j}. {step}")
                
                # Shopping list preview
                if result.get('shopping_list'):
                    st.subheader("🛒 Required Shopping Items")
                    shopping_df = pd.DataFrame(result['shopping_list'])
                    st.dataframe(shopping_df[['item', 'quantity', 'category']], use_container_width=True)
                    
                    if st.button("View Complete Shopping Plan"):
                        st.session_state.current_tab = "Shopping"
                        st.rerun()

def show_shopping(orchestrator):
    st.header("🛒 Smart Shopping")
    
    if 'meal_result' not in st.session_state:
        st.info("Generate a meal plan first to see your shopping list!")
        return
    
    result = st.session_state.meal_result
    
    if result.get('error'):
        st.error(result['error'])
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Shopping List")
        
        if result.get('shopping_list'):
            # Group by category
            by_category = {}
            for item in result['shopping_list']:
                category = item['category']
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(item)
            
            for category, items in by_category.items():
                st.write(f"**{category.upper()}**")
                for item in items:
                    price_str = f" - ₹{item['estimated_price']}" if item.get('estimated_price') else ""
                    st.write(f"• {item['item']}: {item['quantity']}{price_str}")
                st.write("")
            
            st.metric("Total Estimated Cost", f"₹{result.get('total_cost', 0)}")
        else:
            st.success("🎉 No shopping needed! You have all ingredients.")
    
    with col2:
        st.subheader("Store Optimization")
        
        if result.get('store_recommendation') and result.get('price_comparison'):
            st.success(f"🏆 **Best Store:** {result['store_recommendation']}")
            
            if result.get('savings', 0) > 0:
                st.metric("Total Savings", f"₹{result['savings']}")
            
            # Price comparison chart
            price_data = result['price_comparison']
            stores = list(price_data.keys())
            totals = [price_data[store]['total'] for store in stores]
            
            # Create comparison chart
            comparison_df = pd.DataFrame({
                'Store': stores,
                'Total Cost': totals
            })
            
            fig = px.bar(comparison_df, x='Store', y='Total Cost', 
                        title="Price Comparison Across Stores",
                        color='Total Cost', color_continuous_scale='Viridis')
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()