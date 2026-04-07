import streamlit as st

from recommender import RecommendationService
from components import render_item_card, render_login_sidebar
from admin import render_admin_dashboard

st.set_page_config(page_title="Personalized Food", layout="wide")

# Initialize Service
@st.cache_resource
def get_service():
    return RecommendationService()

service = get_service()

# Session State
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Callbacks
def on_click(item_id, interaction_type):
    if st.session_state['logged_in']:
        service.log_interaction(st.session_state['user_id'], item_id, interaction_type)
    else:
        st.warning("Please login to track history")

def on_rate(item_id, rating):
     if st.session_state['logged_in']:
        service.log_interaction(st.session_state['user_id'], item_id, 'rating', rating)
     else:
        st.warning("Please login to rate")

# Layout
st.title("🍽️ Personalized Food Recommendations")

render_login_sidebar()

if st.session_state['logged_in']:
    if st.session_state['user_id'] == "admin":
        render_admin_dashboard(service)
    else:
        st.write(f"Welcome back, User {st.session_state['user_id']}!")
        
        tab1, tab2, tab3 = st.tabs(["For You", "Trending", "Cuisine Match"])
    
        with tab1:
            st.header("Recommended For You")
            recs = service.get_recommendations(st.session_state['user_id'], strategy='personalized')
            if not recs.empty:
                cols = st.columns(len(recs))
                for i, row in enumerate(recs.iterrows()):
                    item = row[1]
                    with cols[i % len(cols)]:
                        render_item_card(item, on_click, on_rate, key_suffix="personalized")
            else:
                st.info("No recommendations yet. Start ordering!")
                
        with tab2:
            st.header("Trending Now")
            recs = service.get_recommendations(st.session_state['user_id'], strategy='popularity')
            if not recs.empty:
                cols = st.columns(len(recs))
                for i, row in enumerate(recs.iterrows()):
                    item = row[1]
                    with cols[i % len(cols)]:
                        render_item_card(item, on_click, on_rate, key_suffix="trending")
            else:
                st.info("Nothing trending right now.")

        with tab3:
            st.header("Based on your Taste")
            recs = service.get_recommendations(st.session_state['user_id'], strategy='content')
            if not recs.empty:
                cols = st.columns(len(recs))
                for i, row in enumerate(recs.iterrows()):
                    item = row[1]
                    with cols[i % len(cols)]:
                        render_item_card(item, on_click, on_rate, key_suffix="content")
            else:
                st.info("explore more to get cuisine matches!")

else:
    st.info("Please login to see your personalized recommendations.")
    st.header("Popular Items")
    recs = service.get_recommendations(None, strategy='popularity')
    if not recs.empty:
        cols = st.columns(len(recs))
        for i, row in enumerate(recs.iterrows()):
            item = row[1]
            with cols[i % len(cols)]:
                render_item_card(item, key_suffix="guest")
