
from app import create_app,db
from erp.models import (
    User, Warehouse, Category, Product, ProductStock, Customer, Supplier, 
    Lead, PriceList, Quotation, QuotationItem, Invoice, InvoiceItem, 
    ServiceCustomer, ServiceRecord
)
import random
from datetime import datetime, timedelta

app = create_app()

def seed_users():
    print("Seeding Users...")
    users = [
        ('admin', 'password', 'Admin'),
        ('manager', 'password', 'Manager'),
        ('salesrep', 'password', 'Sales'),
        ('tech1', 'password', 'Technician')
    ]
    for username, ppt, role in users:
        if not User.query.filter_by(username=username).first():
            u = User(username=username, role=role)
            u.set_password(ppt)
            db.session.add(u)
    db.session.commit()

def seed_warehouses():
    print("Seeding Warehouses...")
    warehouses = ['Main Warehouse', 'Showroom Store', 'Service Center']
    for name in warehouses:
        if not Warehouse.query.filter_by(name=name).first():
            db.session.add(Warehouse(name=name, location='New Delhi'))
    db.session.commit()

def seed_categories():
    print("Seeding Categories...")
    categories = ['Electronics', 'Computers', 'Services', 'Accessories', 'Furniture']
    for name in categories:
        if not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))
    db.session.commit()

def seed_products():
    print("Seeding Products...")
    cats = Category.query.all()
    if not cats: return
    
    products = [
        ('Gaming Laptop', 'LAP-001', 50000, 65000, 'Computers'),
        ('Wireless Mouse', 'ACC-001', 500, 999, 'Accessories'),
        ('Office Chair', 'FUR-001', 3000, 5500, 'Furniture'),
        ('LED Monitor 24"', 'MON-001', 8000, 11500, 'Electronics'),
        ('USB-C Cable', 'ACC-002', 100, 399, 'Accessories'),
        ('Installation Service', 'SVC-001', 0, 500, 'Services')
    ]
    
    warehouses = Warehouse.query.all()
    
    for name, sku, p_price, s_price, cat_name in products:
        if not Product.query.filter_by(sku=sku).first():
            cat = Category.query.filter_by(name=cat_name).first()
            p = Product(
                name=name, sku=sku, purchase_price=p_price, sale_price=s_price,
                category_id=cat.id if cat else None,
                stock=50 # Legacy field
            )
            db.session.add(p)
            db.session.flush() # get ID
            
            # Add stock to warehouses
            if cat_name != 'Services':
                for w in warehouses:
                    stock = ProductStock(product_id=p.id, warehouse_id=w.id, quantity=random.randint(5, 50))
                    db.session.add(stock)
    db.session.commit()

def seed_price_lists():
    print("Seeding Price Lists...")
    lists = [
        ('Retail Standard', 0.0),
        ('Wholesale Partner', 15.0),
        ('vip_members', 10.0)
    ]
    for name, disc in lists:
        if not PriceList.query.filter_by(name=name).first():
            db.session.add(PriceList(name=name, discount_percentage=disc))
    db.session.commit()

def seed_customers():
    print("Seeding Customers...")
    pl = PriceList.query.filter_by(name='Wholesale Partner').first()
    
    customers = [
        ('Tech Solutions Ltd', '27ABCDE1234F1Z5', 'Mumbai', '9876543210', pl.id if pl else None),
        ('Rohan Enterprises', None, 'Delhi', '9988776655', None),
        ('Walk-in Client', None, 'Local', '0000000000', None)
    ]
    
    for name, gstin, city, phone, pl_id in customers:
        if not Customer.query.filter_by(name=name).first():
            db.session.add(Customer(
                name=name, gstin=gstin, address=city, phone=phone,
                price_list_id=pl_id, balance=0.0
            ))
    db.session.commit()

def seed_leads():
    print("Seeding Leads...")
    leads = [
        ('Amit Kumar', 'Future Tech', '9123456780', 'amit@example.com'),
        ('Sarah Jones', None, '9876500000', 'sarah@test.com'),
        ('BuildCorp', 'BuildCorp Inc', '8888888888', 'contact@buildcorp.in')
    ]
    for name, business, phone, email in leads:
        if not Lead.query.filter_by(phone=phone).first():
            db.session.add(Lead(name=name, business_name=business, phone=phone, email=email))
    db.session.commit()

def seed_services():
    print("Seeding Service Data...")
    s_cust = ServiceCustomer.query.filter_by(phone='7777777777').first()
    if not s_cust:
        s_cust = ServiceCustomer(name="Rajiv Repair", phone="7777777777", address="Sector 15")
        db.session.add(s_cust)
        db.session.commit()
        
    if not ServiceRecord.query.filter_by(service_customer_id=s_cust.id).first():
        rec = ServiceRecord(
            service_customer_id=s_cust.id,
            serviceman_name="Technician Bob",
            issue_reported="Laptop Overheating",
            action_taken="Cleaned fans, replaced thermal paste",
            total_cost=1200.0,
            service_date=datetime.today() - timedelta(days=5)
        )
        db.session.add(rec)
    db.session.commit()
    
def seed_transactions():
    print("Seeding Invoices & Quotes...")
    cust = Customer.query.first()
    products = Product.query.limit(2).all()
    
    if cust and products:
        # Quote
        if not Quotation.query.first():
            q = Quotation(
                quote_number="QT-SEED-001", 
                customer_id=cust.id, 
                valid_until=datetime.today() + timedelta(days=30),
                subtotal=5000, total_amount=5000
            )
            db.session.add(q)
            db.session.flush()
            db.session.add(QuotationItem(quotation_id=q.id, product_id=products[0].id, quantity=1, unit_price=5000, total=5000))
        
        # Invoice
        if not Invoice.query.first():
            inv = Invoice(
                invoice_number="INV-SEED-001",
                customer_id=cust.id,
                subtotal=1000, total_amount=1180,
                cgst_amount=90, sgst_amount=90
            )
            db.session.add(inv)
            db.session.flush()
            db.session.add(InvoiceItem(
                invoice_id=inv.id, product_id=products[1].id, quantity=2, unit_price=500, total=1000
            ))
            cust.balance += 1180
            
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        seed_users()
        seed_warehouses()
        seed_categories()
        seed_products()
        seed_price_lists()
        seed_customers()
        seed_leads()
        seed_services()
        seed_transactions()
        print("Database seeded successfully!")
