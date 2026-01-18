import streamlit as st
import pandas as pd
from models import DatabaseManager
from db_manager import DatabaseProductManager
from typing import Dict


class DbProductsManager:
    def __init__(self):
        """Initialize database-backed products manager (no JSON dependency)."""
        try:
            self.db_manager = DatabaseManager()
            self.db_manager.create_tables()
            self.product_manager = DatabaseProductManager(self.db_manager)
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            raise

    def load_data(self):
        """Load products data from the database."""
        return self.product_manager.get_all_products()
    
    def show_products_interface(self):
        """Display the products management interface"""
        st.header("📦 Products Management")
        
        # Show database status
        st.success("✅ Connected to PostgreSQL database")
        
        # Tabs for different operations
        tab1, tab2, tab3, tab4 = st.tabs(["View Products", "Add Product", "Edit Product", "Export Data"])
        
        with tab1:
            self.show_products_list()
        
        with tab2:
            self.add_product_form()
        
        with tab3:
            self.edit_product_form()
        
        with tab4:
            self.export_products_data()
    
    def show_products_list(self):
        """Display list of products with search and filter functionality"""
        st.subheader("Products Inventory")
        
        products = self.load_data()
        
        if not products:
            st.info("No products found. Add your first product using the 'Add Product' tab.")
            return
        
        df = pd.DataFrame(products)
        
        # Search functionality
        search_term = st.text_input("🔍 Search products by name, brand, or category:")
        if search_term:
            mask = (
                df['name'].str.contains(search_term, case=False, na=False) |
                df['brand'].str.contains(search_term, case=False, na=False) |
                df['category'].str.contains(search_term, case=False, na=False)
            )
            df = df[mask]
        
        # Category filter
        categories = ['All'] + sorted(df['category'].unique().tolist())
        selected_category = st.selectbox("Filter by category:", categories)
        
        if selected_category != 'All':
            df = df[df['category'] == selected_category]
        
        # Low stock filter
        show_low_stock = st.checkbox("Show only low stock items")
        if show_low_stock:
            df = df[df['quantity'] <= df['low_stock_threshold']]
        
        # Display products
        if df.empty:
            st.warning("No products match your search criteria.")
        else:
            for _, product in df.iterrows():
                # Color code based on stock level
                stock_color = "🔴" if product['quantity'] <= product['low_stock_threshold'] else "🟢"
                
                with st.expander(f"{stock_color} {product['name']} - {product['brand']} (Stock: {product['quantity']})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Category:** {product['category']}")
                        st.write(f"**Brand:** {product['brand']}")
                        st.write(f"**Cost Price:** ${product['cost_price']:.2f}")
                        st.write(f"**Selling Price:** ${product['selling_price']:.2f}")
                    
                    with col2:
                        st.write(f"**Current Stock:** {product['quantity']}")
                        st.write(f"**Low Stock Alert:** {product['low_stock_threshold']}")
                        st.write(f"**SKU:** {product.get('sku', 'N/A')}")
                        
                        # Calculate profit margin
                        if product['cost_price'] > 0:
                            margin = ((product['selling_price'] - product['cost_price']) / product['cost_price']) * 100
                            st.write(f"**Profit Margin:** {margin:.1f}%")
                    
                    with col3:
                        st.write(f"**Description:** {product.get('description', 'No description provided')}")
                        
                        # Stock level warning
                        if product['quantity'] <= product['low_stock_threshold']:
                            st.warning("⚠️ Low stock alert!")
                    
                    # Update stock buttons
                    stock_col1, stock_col2, stock_col3 = st.columns(3)
                    
                    with stock_col1:
                        if st.button(f"➖ Remove 1", key=f"remove_stock_{product['id']}"):
                            if product['quantity'] > 0:
                                updated_product = dict(product)
                                updated_product['quantity'] -= 1
                                if self._update_product(int(product['id']), updated_product):
                                    st.success("Stock updated!")
                                    st.rerun()
                    
                    with stock_col2:
                        if st.button(f"➕ Add 1", key=f"add_stock_{product['id']}"):
                            updated_product = dict(product)
                            updated_product['quantity'] += 1
                            if self._update_product(int(product['id']), updated_product):
                                st.success("Stock updated!")
                                st.rerun()
                    
                    with stock_col3:
                        # Delete button
                        if st.button(f"🗑️ Delete", key=f"delete_product_{product['id']}"):
                            if self._delete_product(int(product['id'])):
                                st.success(f"Product '{product['name']}' deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to delete product.")
    
    def add_product_form(self):
        """Form to add a new product"""
        st.subheader("Add New Product")
        
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Product Name *", placeholder="e.g., Shampoo")
                brand = st.text_input("Brand *", placeholder="e.g., L'Oreal")
                category = st.text_input("Category *", placeholder="e.g., Hair Care")
                sku = st.text_input("SKU", placeholder="Product code")
                
            with col2:
                cost_price = st.number_input("Cost Price ($) *", min_value=0.0, step=0.01)
                selling_price = st.number_input("Selling Price ($) *", min_value=0.0, step=0.01)
                quantity = st.number_input("Initial Quantity *", min_value=0, step=1, value=0)
                low_stock_threshold = st.number_input("Low Stock Alert Threshold *", min_value=0, step=1, value=5)
            
            description = st.text_area("Description", placeholder="Product description...")
            
            submitted = st.form_submit_button("Add Product")
            
            if submitted:
                if name and brand and category and cost_price >= 0 and selling_price >= 0:
                    product_data = {
                        "name": name,
                        "brand": brand,
                        "category": category,
                        "sku": sku,
                        "cost_price": cost_price,
                        "selling_price": selling_price,
                        "quantity": quantity,
                        "low_stock_threshold": low_stock_threshold,
                        "description": description,
                    }

                    if self._add_product(product_data):
                        st.success(f"Product '{name}' added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add product.")
                else:
                    st.error("Please fill in all required fields (marked with *).")
    
    def edit_product_form(self):
        """Form to edit an existing product"""
        st.subheader("Edit Product")
        
        products = self.load_data()
        
        if not products:
            st.info("No products available to edit.")
            return
        
        product_options = {f"{p['name']} - {p['brand']}": p['id'] for p in products}
        selected_product_key = st.selectbox("Select product to edit:", list(product_options.keys()))
        
        if selected_product_key:
            product_id = product_options[selected_product_key]
            product = self._get_product_by_id(product_id)
            
            if product:
                with st.form("edit_product_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        name = st.text_input("Product Name *", value=product.get('name', ''))
                        brand = st.text_input("Brand *", value=product.get('brand', ''))
                        category = st.text_input("Category *", value=product.get('category', ''))
                        sku = st.text_input("SKU", value=product.get('sku', ''))
                    
                    with col2:
                        cost_price = st.number_input("Cost Price ($) *", min_value=0.0, step=0.01, value=product.get('cost_price', 0.0))
                        selling_price = st.number_input("Selling Price ($) *", min_value=0.0, step=0.01, value=product.get('selling_price', 0.0))
                        quantity = st.number_input("Current Quantity *", min_value=0, step=1, value=product.get('quantity', 0))
                        low_stock_threshold = st.number_input("Low Stock Alert Threshold *", min_value=0, step=1, value=product.get('low_stock_threshold', 5))
                    
                    description = st.text_area("Description", value=product.get('description', ''))
                    
                    submitted = st.form_submit_button("Update Product")
                    
                    if submitted:
                        if name and brand and category and cost_price >= 0 and selling_price >= 0:
                            updated_product = {
                                "name": name,
                                "brand": brand,
                                "category": category,
                                "sku": sku,
                                "cost_price": cost_price,
                                "selling_price": selling_price,
                                "quantity": quantity,
                                "low_stock_threshold": low_stock_threshold,
                                "description": description
                            }
                            
                            if self._update_product(product_id, updated_product):
                                st.success(f"Product '{name}' updated successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to update product.")
                        else:
                            st.error("Please fill in all required fields (marked with *).")
    
    def export_products_data(self):
        """Export products data"""
        st.subheader("Export Products Data")
        
        products = self.load_data()
        
        if not products:
            st.info("No products data to export.")
            return
        
        df = pd.DataFrame(products)
        
        # Add calculated fields
        if not df.empty:
            df['total_value'] = df['quantity'] * df['cost_price']
            df['profit_margin_percent'] = ((df['selling_price'] - df['cost_price']) / df['cost_price'] * 100).round(2)
            df['low_stock_alert'] = df['quantity'] <= df['low_stock_threshold']
        
        st.write("Preview of export data:")
        st.dataframe(df)
        
        # Download button
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Products CSV",
            data=csv_data,
            file_name="salon_products.csv",
            mime="text/csv"
        )
    
    def _add_product(self, product_data: Dict) -> bool:
        """Add product using the database manager."""
        return self.product_manager.add_product(product_data)

    def _update_product(self, product_id: int, product_data: Dict) -> bool:
        """Update product using the database manager."""
        return self.product_manager.update_product(product_id, product_data)

    def _delete_product(self, product_id: int) -> bool:
        """Delete product using the database manager."""
        return self.product_manager.delete_product(product_id)

    def _get_product_by_id(self, product_id: int) -> Dict:
        """Get product by ID using the database manager."""
        return self.product_manager.get_product_by_id(product_id) or {}