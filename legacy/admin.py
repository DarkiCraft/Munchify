import streamlit as st
import pandas as pd
import plotly.express as px

from config import RAW_DATA_DIR


def render_admin_dashboard(service):
    st.header("Admin Dashboard")
    
    stats = service.get_system_stats()
    
    # ROW 1: System Health KPIs
    st.subheader("System Health")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        sparsity = stats.get('sparsity', 0)
        st.metric("Matrix Sparsity", f"{sparsity*100:.2f}%", help="Higher is harder for CF")
        
    with c2:
        coverage = stats.get('catalog_coverage', 0)
        st.metric("Catalog Coverage", f"{coverage*100:.2f}%", help="% of items with at least 1 interaction")
        
    with c3:
        avg_int = stats.get('avg_interactions_per_user', 0)
        st.metric("Avg Actions/User", f"{avg_int:.1f}")
    
    # Organize Admin into Tabs
    tab_eval, tab_sim, tab_data = st.tabs(["Evaluation", "Simulation Sandbox", "Data Inspector"])
    
    with tab_eval:
        st.header("Model Evaluation")
        st.info("Performance on held-out test set (20% split). Metrics calculated @ K=5.")
        
        if st.button("Run Full Evaluation", type="primary"):
            with st.spinner("Calculating metrics logic..."):
                metrics = service.calculate_metrics(k=5)
            
            # Display Metrics in a structured way
            m1, m2, m3 = st.columns(3)
            with m1:
                 st.metric("Precision@5", f"{metrics['precision']:.4f}")
                 st.metric("Recall@5", f"{metrics['recall']:.4f}")
            with m2:
                 st.metric("MAP@5", f"{metrics['map']:.4f}")
                 st.metric("MAR@5", f"{metrics['mar']:.4f}")
            with m3:
                 st.metric("F1-Score", f"{metrics['f1']:.4f}")
                 st.metric("Accuracy (Hit Rate)", f"{metrics['accuracy']:.4f}")
                 
            st.success("Evaluation Complete!")

    with tab_sim:
        st.header("Traffic Simulation")
        st.markdown("""
        Use this sandbox to generate high-quality synthetic data based on latent user preferences.
        1. **Reset**: Clear existing noisy data.
        2. **Simulate**: Generate 'smart' traffic (Users with specific taste profiles).
        3. **Retrain**: Teach the model the new patterns.
        """)
        
        col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
        
        with col_ctrl1:
            st.warning("Destructive Action")
            if st.button("Reset System Data", type="secondary"):
                # if st.checkbox("Confirm Reset?", key="confirm_reset"):
                service.reset_data()
                st.success("System Reset!")
                st.rerun()

        with col_ctrl2:
            st.info("Generate Traffic")
            # User requested 0-99 limit. 
            num_users = st.number_input("Users", 1, 100, 50)
            # Remove max limit for views as requested ("remove the limits on the amount of actions")
            views = st.number_input("Views/User", 1, 10000, 20)
            
            if st.button("Start Simulation", type="primary"):
                from simulation import run_simulation
                with st.spinner(f"Simulating {num_users} users..."):
                    new_interactions = run_simulation(service.items_df, num_users, views)
                    
                    # Append to service
                    # We need to manually append to the CSV and reload? 
                    # Or just use the service's dataframe.
                    # Best is to append to CSV and reload service.

                    # Append to csv
                    # We need to check if file exists to handle header
                    csv_path = RAW_DATA_DIR / "interactions.csv"
                    header = not csv_path.exists()
                    new_interactions.to_csv(csv_path, mode='a', header=header, index=False)
                    
                    st.success(f"Generated {len(new_interactions)} interactions!")
                    # Reload logic needed? User should Retrain.

        with col_ctrl3:
            st.info("Model Training")
            if st.button("Retrain Model", type="primary"):
                 with st.spinner("Retraining NCF & Baselines..."):
                     # Force reload of data first
                     service.__init__() # Re-init reloads data and trains
                     st.success("Model Retrained Successfully!")

    with tab_data:
        # ROW 2: Charts (Enhanced)
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Interaction Mix")
            with st.container(border=True):
                dist = stats.get('interaction_distribution', {})
                if dist:
                    df_dist = pd.DataFrame(list(dist.items()), columns=['Type', 'Count'])
                    # Enhanced Pie Chart
                    fig = px.pie(df_dist, values='Count', names='Type', hole=0.4, 
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
                    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))
                    st.plotly_chart(fig, width="stretch")
                else:
                    st.info("No interactions yet.")
                
        with col2:
            st.subheader("User Deep Dive")
            with st.container(border=True):
                user_id_input = st.number_input("Check User ID", min_value=0, step=1)
                if st.button("Check User Profile"):
                    u_stats = service.get_user_stats(int(user_id_input))
                    if u_stats:
                        st.write(f"**Total Interactions:** {u_stats['total_interactions']}")
                        
                        # Create a mini bar chart for tastes
                        if u_stats['top_cuisines']:
                            st.write("**Top Cuisines:**")
                            c_df = pd.DataFrame(list(u_stats['top_cuisines'].items()), columns=['Cuisine', 'Count'])
                            fig_bar = px.bar(c_df, x='Cuisine', y='Count', color='Count', color_continuous_scale='Bluyl')
                            fig_bar.update_layout(height=200, margin=dict(t=10, b=10, l=10, r=10))
                            st.plotly_chart(fig_bar, width="stretch")
                        else:
                             st.write("No specific cuisine preference yet.")
                    else:
                        st.warning("User not found or no interactions.")
