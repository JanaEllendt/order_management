from datetime import datetime
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_access.models import Base, Product, Customer, Shop, OrderHeader, OrderItem

# Database connection setup (adjust the connection string as necessary)
DATABASE_URL = "sqlite:///orders.db"  # Example using SQLite


# engine = create_engine(DATABASE_URL)
# Base.metadata.create_all(engine)
# Session = sessionmaker(bind=engine)
# session = Session()

# Session State also supports attribute based syntax
if 'database_engine' not in st.session_state:
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    st.session_state.database_engine = engine
else:
    engine = st.session_state.database_engine
    
if 'database_session' not in st.session_state: 
    Session = sessionmaker(bind=engine)
    session = Session()   
    st.session_state.database_session = session
else:
    session = st.session_state.database_session

# Sidebar navigation
st.sidebar.title("Navigation")
pages = st.sidebar.radio("Go to", ["Product Maintenance", "Customer Maintenance", "Shop Maintenance", "Order Creation", "Order Analysis"])

# Product Maintenance Page
def product_maintenance():
    st.title("Product Maintenance")
    
    # Show existing products
    products = session.query(Product).all()
    product_df = pd.DataFrame([(p.articlenumber, p.articlename, p.price, p.currency) for p in products],
                              columns=["Article Number", "Article Name", "Price", "Currency"])
    st.dataframe(product_df)
    
    # Add new product
    with st.form("Add Product"):
        articlenumber = st.text_input("Article Number", value=0)
        articlename = st.text_input("Article Name")
        price = st.number_input("Price", value=0.0, format="%.2f")
        currency = st.text_input("Currency", value="EUR")
        submit = st.form_submit_button("Add Product")
        
        if submit:
            product = Product(articlenumber=articlenumber, articlename=articlename, price=price, currency=currency)
            session.add(product)
            session.commit()
            st.success("Product added successfully!")
            
    
    # Delete product
    st.subheader("Delete Product")
    product_to_delete = st.selectbox("Select Product to Delete", options=[p.articlenumber for p in products])
    if st.button("Delete Product"):
        product = session.query(Product).filter(Product.articlenumber == product_to_delete).first()
        if product:
            session.delete(product)
            session.commit()
            st.success("Product deleted successfully!")

# Customer Maintenance Page
def customer_maintenance():
    st.title("Customer Maintenance")
    
    # Show existing customers
    customers = session.query(Customer).all()
    customer_df = pd.DataFrame([(c.first_name, c.last_name, c.email, c.birthdate) for c in customers],
                               columns=["First Name", "Last Name", "Email", "Birthdate"])
    st.dataframe(customer_df)
    
    # Add new customer
    with st.form("Add Customer"):
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        email = st.text_input("Email")
        birthdate = st.date_input("Birthdate", value=datetime.now().date())
        submit = st.form_submit_button("Add Customer")
        
        if submit:
            customer = Customer(first_name=first_name, last_name=last_name, email=email, birthdate=birthdate)
            session.add(customer)
            session.commit()
            st.success("Customer added successfully!")
            
    
    # Delete customer
    st.subheader("Delete Customer")
    customer_to_delete = st.selectbox("Select Customer to Delete", options=[f"{c.first_name} {c.last_name} ({c.customer_id})" for c in customers])
    if st.button("Delete Customer"):
        customer_id = customer_to_delete.split("(")[-1].strip(")")
        customer = session.query(Customer).filter(Customer.customer_id == customer_id).first()
        if customer:
            session.delete(customer)
            session.commit()
            st.success("Customer deleted successfully!")

# Shop Maintenance Page
def shop_maintenance():
    st.title("Shop Maintenance")
    
    # Show existing shops
    shops = session.query(Shop).all()
    shop_df = pd.DataFrame([(s.shopnumber, s.name, s.location) for s in shops],
                           columns=["Shop Number", "Name", "Location"])
    st.dataframe(shop_df)
    
    # Add new shop
    with st.form("Add Shop"):
        shopnumber = st.number_input("Shop Number", value=0)
        name = st.text_input("Shop Name")
        location = st.text_input("Location")
        submit = st.form_submit_button("Add Shop")
        
        if submit:
            shop = Shop(shopnumber=shopnumber, name=name, location=location)
            session.add(shop)
            session.commit()
            st.success("Shop added successfully!")
            
            
    # Delete shop
    st.subheader("Delete Shop")
    shop_to_delete = st.selectbox("Select Shop to Delete", options=[s.shopnumber for s in shops])
    if st.button("Delete Shop"):
        shop = session.query(Shop).filter(Shop.shopnumber == shop_to_delete).first()
        if shop:
            session.delete(shop)
            session.commit()
            st.success("Shop deleted successfully!")

# Order Creation Page
def order_creation():
    st.title("Order Creation")
    
    # Customer selection
    customers = session.query(Customer).all()
    customer_options = {f"{c.first_name} {c.last_name} ({c.customer_id})": c.customer_id for c in customers}
    selected_customer = st.selectbox("Select Customer", options=customer_options.keys())
    customer_id = customer_options[selected_customer]
    
    # Shop selection
    shops = session.query(Shop).all()
    shop_options = {s.name: s.shopnumber for s in shops}
    selected_shop = st.selectbox("Select Shop", options=shop_options.keys())
    shopnumber = shop_options[selected_shop]
    
    # Order details
    manufacturer = st.text_input("Manufacturer")
    manufactur_place = st.text_input("Manufacturing Place")
    order_date = st.date_input("Order Date", value=datetime.now().date())
    
    # Add order items
    st.subheader("Order Items")
    items = []
    if 'order_items' not in st.session_state:
        st.session_state['order_items'] = []
    
    with st.form("Add Order Item"):
        articlenumber = st.number_input("Article Number", value=0)
        articlename = st.text_input("Article Name")
        quantity = st.number_input("Quantity", value=1)
        price = st.number_input("Price", value=0.0, format="%.2f")
        currency = st.text_input("Currency", value="USD")
        submit = st.form_submit_button("Add Item")
        
        if submit:
            item = {"articlenumber": articlenumber, "articlename": articlename, "quantity": quantity, "price": price, "currency": currency}
            st.session_state['order_items'].append(item)
            st.success("Item added!")

            
    
    # Display order items
    items_df = pd.DataFrame(st.session_state['order_items'])
    st.dataframe(items_df)
    
    # Submit order
    if st.button("Submit Order"):       
        order = OrderHeader(customer_id=customer_id, manufacturer=manufacturer, manufactur_place=manufactur_place, shopnumber=shopnumber, date=order_date)
        session.add(order)
        session.commit()
        
        for item in st.session_state['order_items']:
            order_item = OrderItem(order_id=order.order_id, articlenumber=item['articlenumber'], articlename=item['articlename'], quantity=item['quantity'], price=item['price'], currency=item['currency'], order_date=order_date)
            session.add(order_item)
        session.commit()
        
        st.success("Order submitted successfully!")
        st.session_state['order_items'] = []

# Order Analysis Page
def order_analysis():
    st.title("Order Analysis")
    
    # Filters
    customers = session.query(Customer).all()
    customer_options = {f"{c.first_name} {c.last_name} ({c.customer_id})": c.customer_id for c in customers}
    selected_customer = st.selectbox("Filter by Customer", options=["All"] + list(customer_options.keys()))
    shops = session.query(Shop).all()
    shop_options = {s.name: s.shopnumber for s in shops}
    selected_shop = st.selectbox("Filter by Shop", options=["All"] + list(shop_options.keys()))
    products = session.query(Product).all()
    product_options = {p.articlename: p.articlenumber for p in products}
    selected_product = st.selectbox("Filter by Product", options=["All"] + list(product_options.keys()))
    start_date = st.date_input("Start Date", value=datetime.now().date())
    end_date = st.date_input("End Date", value=datetime.now().date())
    
    # Query filtered data
    query = session.query(OrderHeader).join(OrderItem).join(Customer).join(Shop).filter(OrderHeader.date.between(start_date, end_date))
    
    if selected_customer != "All":
        query = query.filter(OrderHeader.customer_id == customer_options[selected_customer])
    if selected_shop != "All":
        query = query.filter(OrderHeader.shopnumber == shop_options[selected_shop])
    if selected_product != "All":
        query = query.filter(OrderItem.articlenumber == product_options[selected_product])
    
    orders = query.all()
    
    # Aggregate data
    total_revenue = sum(item.price * item.quantity for order in orders for item in order.items)
    total_items_sold = sum(item.quantity for order in orders for item in order.items)
    st.metric("Total Revenue", f"${total_revenue:,.2f}")
    st.metric("Total Items Sold", total_items_sold)
    
    # Visualization
    if orders:
        # Bar chart
        revenue_per_product = {}
        for order in orders:
            for item in order.items:
                if item.articlename in revenue_per_product:
                    revenue_per_product[item.articlename] += item.price * item.quantity
                else:
                    revenue_per_product[item.articlename] = item.price * item.quantity
        
        st.subheader("Revenue by Product")
        plt.bar(revenue_per_product.keys(), revenue_per_product.values())
        st.pyplot(plt)

        # Pie chart
        st.subheader("Revenue Distribution by Product")
        plt.pie(revenue_per_product.values(), labels=revenue_per_product.keys(), autopct='%1.1f%%')
        st.pyplot(plt)

# Page Routing
if pages == "Product Maintenance":
    product_maintenance()
elif pages == "Customer Maintenance":
    customer_maintenance()
elif pages == "Shop Maintenance":
    shop_maintenance()
elif pages == "Order Creation":
    order_creation()
elif pages == "Order Analysis":
    order_analysis()

