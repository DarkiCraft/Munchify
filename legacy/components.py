import streamlit as st

def render_item_card(item, on_click_callback=None, on_rate_callback=None, key_suffix=""):
    """Renders a single food item card."""
    with st.container(border=True):
        st.markdown(f"### {item['item_name']}") 
        st.caption(f"by {item['restaurant_name']}")
        st.write(f"**Cuisine:** {item['cuisine_type']}")
        
        # Price display
        price_sign = "$" * int(item['price_range'])
        st.write(f"**Price:** {price_sign}")
        
        # Rating display
        st.write(f"**Rating:** {'⭐' * int(round(item['avg_rating']))} ({item['avg_rating']})")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Order Now", key=f"order_{item['item_id']}_{key_suffix}"):
                if on_click_callback:
                    on_click_callback(item['item_id'], 'order')
                    st.success("Ordered!")
        
        with col2:
             # Just a view details button for 'click' simulation
            if st.button("View Details", key=f"view_{item['item_id']}_{key_suffix}"):
                 if on_click_callback:
                    on_click_callback(item['item_id'], 'click')
                    st.info("Viewed details")

        # Rating input (simple)
        st.write("---")
        with st.expander("Rate this item"):
            rating = st.slider("Your Rating", 1, 5, 5, key=f"rate_{item['item_id']}_{key_suffix}")
            if st.button("Submit Rating", key=f"sub_rate_{item['item_id']}_{key_suffix}"):
                if on_rate_callback:
                    on_rate_callback(item['item_id'], rating)
                    st.success("Rating submitted!")

def render_login_sidebar():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username", "user_1")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        # Simple Logic: Parse user_id from username (user_X)
        try:
            if username == "admin":
                 st.session_state['user_id'] = "admin"
                 st.session_state['logged_in'] = True
                 st.sidebar.success("Logged in as Admin")
            elif username.startswith("user_"):
                uid = int(username.split("_")[1])
                st.session_state['user_id'] = uid
                st.session_state['logged_in'] = True
                st.sidebar.success(f"Logged in as User {uid}")
            else:
                 st.sidebar.error("Username format: user_ID (e.g. user_1) or admin")
        except:
             st.sidebar.error("Invalid username format")
