import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class Dashboard:
    def __init__(self):
        pass
    
    def show_dashboard(self, services_manager, products_manager):
        """Display the main dashboard with summaries and visualizations"""
        st.header("📊 Dashboard")
        
        # Load data
        services = services_manager.load_data()
        products = products_manager.load_data()
        
        # Summary metrics
        self.show_summary_metrics(services, products)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            self.show_services_charts(services)
        
        with col2:
            self.show_products_charts(products)
        
        # Recent alerts and notifications
        self.show_alerts(products)
        
        # Detailed tables
        if st.checkbox("Show detailed data tables"):
            self.show_detailed_tables(services, products)
    
    def show_summary_metrics(self, services, products):
        """Display key metrics in a card layout"""
        st.subheader("Key Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_services = len(services)
            st.metric("Total Services", total_services)
        
        with col2:
            if services:
                avg_service_price = sum(s.get('base_price', 0) for s in services) / len(services)
                st.metric("Avg Service Price", f"${avg_service_price:.2f}")
            else:
                st.metric("Avg Service Price", "$0.00")
        
        with col3:
            total_products = len(products)
            st.metric("Total Products", total_products)
        
        with col4:
            if products:
                total_inventory_value = sum(p.get('quantity', 0) * p.get('cost_price', 0) for p in products)
                st.metric("Inventory Value", f"${total_inventory_value:.2f}")
            else:
                st.metric("Inventory Value", "$0.00")
        
        # Additional metrics row
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            if products:
                low_stock_items = sum(1 for p in products if p.get('quantity', 0) <= p.get('low_stock_threshold', 0))
                st.metric("Low Stock Items", low_stock_items, delta=-low_stock_items if low_stock_items > 0 else None)
            else:
                st.metric("Low Stock Items", "0")
        
        with col6:
            if services:
                service_categories = len(set(s.get('category', '') for s in services))
                st.metric("Service Categories", service_categories)
            else:
                st.metric("Service Categories", "0")
        
        with col7:
            if products:
                product_categories = len(set(p.get('category', '') for p in products))
                st.metric("Product Categories", product_categories)
            else:
                st.metric("Product Categories", "0")
        
        with col8:
            if products:
                total_stock = sum(p.get('quantity', 0) for p in products)
                st.metric("Total Stock Units", total_stock)
            else:
                st.metric("Total Stock Units", "0")
    
    def show_services_charts(self, services):
        """Display charts related to services"""
        st.subheader("Services Analytics")
        
        if not services:
            st.info("No services data available for charts.")
            return
        
        df = pd.DataFrame(services)
        
        # Services by category
        if 'category' in df.columns:
            category_counts = df['category'].value_counts()
            fig_category = px.pie(
                values=category_counts.values, 
                names=category_counts.index,
                title="Services by Category"
            )
            st.plotly_chart(fig_category, use_container_width=True)
        
        # Price distribution
        if 'base_price' in df.columns:
            fig_price = px.histogram(
                df, 
                x='base_price', 
                nbins=20,
                title="Service Price Distribution"
            )
            fig_price.update_layout(xaxis_title="Price ($)", yaxis_title="Number of Services")
            st.plotly_chart(fig_price, use_container_width=True)
        
        # Duration distribution
        if 'duration' in df.columns:
            fig_duration = px.box(
                df, 
                y='duration',
                title="Service Duration Distribution"
            )
            fig_duration.update_layout(yaxis_title="Duration (minutes)")
            st.plotly_chart(fig_duration, use_container_width=True)
    
    def show_products_charts(self, products):
        """Display charts related to products"""
        st.subheader("Products Analytics")
        
        if not products:
            st.info("No products data available for charts.")
            return
        
        df = pd.DataFrame(products)
        
        # Products by category
        if 'category' in df.columns:
            category_counts = df['category'].value_counts()
            fig_category = px.bar(
                x=category_counts.index, 
                y=category_counts.values,
                title="Products by Category"
            )
            fig_category.update_layout(xaxis_title="Category", yaxis_title="Number of Products")
            st.plotly_chart(fig_category, use_container_width=True)
        
        # Stock levels
        if 'quantity' in df.columns and 'name' in df.columns:
            # Show top 10 products by stock
            top_stock = df.nlargest(10, 'quantity')
            fig_stock = px.bar(
                top_stock,
                x='name',
                y='quantity',
                title="Top 10 Products by Stock Level"
            )
            fig_stock.update_layout(xaxis_title="Product", yaxis_title="Stock Quantity", xaxis_tickangle=45)
            st.plotly_chart(fig_stock, use_container_width=True)
        
        # Profit margin analysis
        if all(col in df.columns for col in ['cost_price', 'selling_price', 'name']):
            df_profit = df.copy()
            df_profit['profit_margin'] = ((df_profit['selling_price'] - df_profit['cost_price']) / df_profit['cost_price'] * 100)
            df_profit = df_profit[df_profit['profit_margin'] >= 0]  # Filter out negative margins
            
            if not df_profit.empty:
                top_margin = df_profit.nlargest(10, 'profit_margin')
                fig_margin = px.scatter(
                    top_margin,
                    x='cost_price',
                    y='selling_price',
                    size='profit_margin',
                    hover_name='name',
                    title="Product Profit Margins",
                    labels={
                        'cost_price': 'Cost Price ($)',
                        'selling_price': 'Selling Price ($)'
                    }
                )
                st.plotly_chart(fig_margin, use_container_width=True)
    
    def show_alerts(self, products):
        """Display important alerts and notifications"""
        st.subheader("🚨 Alerts & Notifications")
        
        if not products:
            st.info("No alerts at this time.")
            return
        
        # Low stock alerts
        low_stock_products = [
            p for p in products 
            if p.get('quantity', 0) <= p.get('low_stock_threshold', 0)
        ]
        
        if low_stock_products:
            st.warning(f"⚠️ {len(low_stock_products)} product(s) are running low on stock:")
            
            for product in low_stock_products[:5]:  # Show top 5
                st.write(f"- **{product.get('name', 'Unknown')}** ({product.get('brand', 'Unknown Brand')}): {product.get('quantity', 0)} units remaining (Alert threshold: {product.get('low_stock_threshold', 0)})")
            
            if len(low_stock_products) > 5:
                st.write(f"... and {len(low_stock_products) - 5} more items")
        else:
            st.success("✅ All products are adequately stocked!")
        
        # Out of stock alerts
        out_of_stock = [p for p in products if p.get('quantity', 0) == 0]
        
        if out_of_stock:
            st.error(f"🛑 {len(out_of_stock)} product(s) are out of stock:")
            for product in out_of_stock[:3]:  # Show top 3
                st.write(f"- **{product.get('name', 'Unknown')}** ({product.get('brand', 'Unknown Brand')})")
    
    def show_detailed_tables(self, services, products):
        """Display detailed data tables"""
        st.subheader("📋 Detailed Data Tables")
        
        tab1, tab2 = st.tabs(["Services Details", "Products Details"])
        
        with tab1:
            if services:
                services_df = pd.DataFrame(services)
                
                # Flatten complex columns for display
                display_df = services_df.copy()
                
                # Convert pricing tiers to string
                if 'pricing_tiers' in display_df.columns:
                    display_df['pricing_tiers_summary'] = display_df['pricing_tiers'].apply(
                        lambda x: f"{len(x)} tiers" if x else "No tiers"
                    )
                
                # Convert add-ons to string
                if 'add_ons' in display_df.columns:
                    display_df['add_ons_summary'] = display_df['add_ons'].apply(
                        lambda x: f"{len(x)} add-ons" if x else "No add-ons"
                    )
                
                # Select relevant columns for display
                display_columns = ['name', 'category', 'base_price', 'duration', 'pricing_tiers_summary', 'add_ons_summary']
                available_columns = [col for col in display_columns if col in display_df.columns]
                
                st.dataframe(display_df[available_columns])
            else:
                st.info("No services data available.")
        
        with tab2:
            if products:
                products_df = pd.DataFrame(products)
                
                # Add calculated columns
                if all(col in products_df.columns for col in ['cost_price', 'selling_price']):
                    products_df['profit_margin_%'] = ((products_df['selling_price'] - products_df['cost_price']) / products_df['cost_price'] * 100).round(2)
                
                if all(col in products_df.columns for col in ['quantity', 'cost_price']):
                    products_df['total_value'] = (products_df['quantity'] * products_df['cost_price']).round(2)
                
                if all(col in products_df.columns for col in ['quantity', 'low_stock_threshold']):
                    products_df['stock_status'] = products_df.apply(
                        lambda row: 'Low Stock' if row['quantity'] <= row['low_stock_threshold'] 
                        else 'Out of Stock' if row['quantity'] == 0 
                        else 'In Stock', axis=1
                    )
                
                st.dataframe(products_df)
            else:
                st.info("No products data available.")
