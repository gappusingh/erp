from erp import create_app, db
from erp.models import (Customer, Product, Supplier, Invoice, Payment, 
                        Expense, Account, User, AuditLog,
                        Category, Warehouse, ProductStock, ProductSerialNumber, PriceList, Quotation, Lead, SalesReturn)

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Make models available in flask shell"""
    return {
        'db': db,
        'Customer': Customer,
        'Product': Product,
        'Supplier': Supplier,
        'Invoice': Invoice,
        'Payment': Payment,
        'Expense': Expense,
        'PricingTier': PricingTier,
        'Account': Account,
        'User': User,
        'AuditLog': AuditLog,
        'Category': Category,
        'Warehouse': Warehouse,
        'ProductStock': ProductStock,
        'ProductSerialNumber': ProductSerialNumber
    }

@app.cli.command()
def init_db():
    """Initialize the database with sample data"""
    db.create_all()
    
    # Create default Price Lists
    if not PriceList.query.first():
        lists = [
            PriceList(name='Retail', description='Standard retail pricing'),
            PriceList(name='Wholesale', description='Bulk buyer pricing'),
            PriceList(name='Distributor', description='Authorized distributor pricing')
        ]
        for pl in lists:
            db.session.add(pl)
        print('Default price lists created.')

    # Create default Categories
    if not Category.query.first():
        categories = [
            Category(name='LED Lighting', description='All LED Bulbs and Tubes'),
            Category(name='Fans', description='Ceiling and Wall Fans'),
            Category(name='Switches', description='Modular and Semi-Modular Switches'),
            Category(name='Wires', description='House Wiring and Cables')
        ]
        for cat in categories:
            db.session.add(cat)
        print('Default categories created.')

    # Create default Warehouse
    if not Warehouse.query.first():
        main_wh = Warehouse(name='Main Warehouse', location='Patna Head Office')
        db.session.add(main_wh)
        print('Main warehouse created.')
    
    # Create default users for testing RBAC
    users_data = [
        ('admin', 'admin123', 'Admin'),
        ('sales', 'sales123', 'Sales'),
        ('tech', 'tech123', 'Technician'),
        ('accountant', 'acc123', 'Accountant'),
        ('manager', 'mgr123', 'Manager')
    ]
    
    for username, password, role in users_data:
        if not User.query.filter_by(username=username).first():
            user = User(username=username, role=role)
            user.set_password(password)
            db.session.add(user)
            print(f'Created {role} user: {username}/{password}')
    
    # Create sample products
    if not Product.query.first():
        products = [
            Product(name='LED Bulb 9W', sku='LED-9W', hsn_code='85395000', 
                   purchase_price=50, sale_price=75),
            Product(name='LED Bulb 12W', sku='LED-12W', hsn_code='85395000',
                   purchase_price=70, sale_price=100),
            Product(name='Fan Regulator', sku='FAN-REG', hsn_code='85381010',
                   purchase_price=120, sale_price=180),
            Product(name='Switch 1-Way', sku='SW-1W', hsn_code='85381010',
                   purchase_price=15, sale_price=25)
        ]
        for product in products:
            db.session.add(product)
            
    # Create sample customers
    if not Customer.query.first():
        retail_pl = PriceList.query.filter_by(name='Retail').first()
        wholesale_pl = PriceList.query.filter_by(name='Wholesale').first()
        
        customers = [
            Customer(name='Aman Electronics', phone='9876543210', address='Main Market, Patna', price_list_id=retail_pl.id),
            Customer(name='Rahul Light House', phone='8765432109', address='Bakarganj, Patna', price_list_id=wholesale_pl.id),
            Customer(name='Deepak General Store', phone='7654321098', address='Kankarbagh, Patna', price_list_id=retail_pl.id)
        ]
        for customer in customers:
            db.session.add(customer)
        print('Sample customers added.')
    
    try:
        db.session.commit()
        print('Database initialized successfully!')
    except Exception as e:
        db.session.rollback()
        print(f'Error initializing database: {e}')

from erp import create_app


if __name__ == '__main__':
    app.run(debug=True)
else:
    # Auto-initialize database on first run (for Coolify/production)
    import random
    with app.app_context():
        from sqlalchemy import inspect as sa_inspect
        inspector = sa_inspect(db.engine)
        if not inspector.has_table('user'):
            print("🔧 First run detected — creating database tables...")
            db.create_all()
            print("✅ Tables created!")

            # === SEED ALL SAMPLE DATA ===
            print("📦 Seeding sample data...")

            # 1. Users
            users_data = [
                ('admin', 'password', 'Admin'),
                ('manager', 'password', 'Manager'),
                ('salesrep', 'password', 'Sales'),
                ('tech1', 'password', 'Technician'),
                ('accountant', 'password', 'Accountant'),
            ]
            for username, pwd, role in users_data:
                u = User(username=username, role=role)
                u.set_password(pwd)
                db.session.add(u)
            db.session.flush()
            print("  ✅ Users created")

            # 2. Warehouses
            from erp.models import Warehouse, Category, ProductStock, PriceList
            for wh_name, loc in [('Main Warehouse', 'Head Office'), ('Showroom Store', 'Market'), ('Service Center', 'Workshop')]:
                db.session.add(Warehouse(name=wh_name, location=loc))
            db.session.flush()
            print("  ✅ Warehouses created")

            # 3. Categories
            for cat_name in ['Electronics', 'Computers', 'Services', 'Accessories', 'Furniture', 'LED Lighting', 'Fans', 'Switches', 'Wires']:
                db.session.add(Category(name=cat_name))
            db.session.flush()
            print("  ✅ Categories created")

            # 4. Products
            from erp.models import Product
            products_data = [
                ('Gaming Laptop', 'LAP-001', 50000, 65000),
                ('Wireless Mouse', 'ACC-001', 500, 999),
                ('Office Chair', 'FUR-001', 3000, 5500),
                ('LED Monitor 24"', 'MON-001', 8000, 11500),
                ('USB-C Cable', 'ACC-002', 100, 399),
                ('LED Bulb 9W', 'LED-9W', 50, 75),
                ('LED Bulb 12W', 'LED-12W', 70, 100),
                ('Fan Regulator', 'FAN-REG', 120, 180),
                ('Switch 1-Way', 'SW-1W', 15, 25),
                ('Installation Service', 'SVC-001', 0, 500),
            ]
            warehouses = Warehouse.query.all()
            for name, sku, pp, sp in products_data:
                p = Product(name=name, sku=sku, purchase_price=pp, sale_price=sp, stock=50)
                db.session.add(p)
                db.session.flush()
                for wh in warehouses:
                    db.session.add(ProductStock(product_id=p.id, warehouse_id=wh.id, quantity=random.randint(5, 50)))
            print("  ✅ Products created with warehouse stock")

            # 5. Price Lists
            for pl_name, disc in [('Retail Standard', 0.0), ('Wholesale Partner', 15.0), ('VIP Members', 10.0), ('Distributor', 20.0)]:
                db.session.add(PriceList(name=pl_name, discount_percentage=disc))
            db.session.flush()
            print("  ✅ Price Lists created")

            # 6. Customers
            from erp.models import Customer
            pl = PriceList.query.first()
            for c_name, gstin, addr, phone in [
                ('Tech Solutions Ltd', '27ABCDE1234F1Z5', 'Mumbai', '9876543210'),
                ('Rohan Enterprises', None, 'Delhi', '9988776655'),
                ('Walk-in Client', None, 'Local', '0000000000'),
                ('Sharma Electronics', None, 'Patna', '9876543001'),
                ('Gupta Light House', '27GHIJK5678L1Z5', 'Patna', '9876543002'),
                ('Singh Trading Co.', None, 'Danapur', '9876543003'),
            ]:
                db.session.add(Customer(name=c_name, gstin=gstin, address=addr, phone=phone, price_list_id=pl.id if pl else None, balance=0.0))
            db.session.flush()
            print("  ✅ Customers created")

            # 7. Suppliers
            from erp.models import Supplier
            for s_name, addr, phone in [
                ('National Electronics Pvt Ltd', 'Noida', '9111222333'),
                ('Star Components', 'Shenzhen Import', '9444555666'),
            ]:
                db.session.add(Supplier(name=s_name, address=addr, phone=phone, balance=0.0))
            db.session.flush()
            print("  ✅ Suppliers created")

            # 8. Leads
            from erp.models import Lead
            admin_user = User.query.filter_by(username='admin').first()
            for l_name, biz, phone, email in [
                ('Amit Kumar', 'Future Tech', '9123456780', 'amit@example.com'),
                ('Sarah Jones', None, '9876500000', 'sarah@test.com'),
                ('BuildCorp', 'BuildCorp Inc', '8888888888', 'contact@buildcorp.in'),
            ]:
                db.session.add(Lead(name=l_name, business_name=biz, phone=phone, email=email, assigned_to_id=admin_user.id if admin_user else None))
            print("  ✅ Leads created")

            # 9. Expenses
            from erp.models import Expense
            from datetime import datetime, timedelta
            for desc, amt, cat in [
                ('Electricity Bill', 4500, 'Utilities'),
                ('Godown Rent', 12000, 'Rent'),
                ('Delivery Van Fuel', 2200, 'Transport'),
                ('Staff Salary', 15000, 'Salary'),
                ('AC Repair', 3500, 'Maintenance'),
            ]:
                db.session.add(Expense(description=desc, amount=amt, category=cat,
                    expense_date=datetime.now() - timedelta(days=random.randint(1, 30))))
            print("  ✅ Expenses created")

            # 10. Invoices
            from erp.models import Invoice, InvoiceItem
            customers = Customer.query.all()
            products = Product.query.all()
            for i in range(3):
                cust = customers[i % len(customers)]
                prod = products[i % len(products)]
                qty = random.randint(1, 5)
                subtotal = prod.sale_price * qty
                cgst = round(subtotal * 0.09, 2)
                sgst = round(subtotal * 0.09, 2)
                total = subtotal + cgst + sgst
                inv = Invoice(
                    invoice_number=f'INV-{i+1:05d}', customer_id=cust.id,
                    subtotal=subtotal, total_amount=total, cgst_amount=cgst, sgst_amount=sgst,
                    created_at=datetime.now() - timedelta(days=random.randint(1, 60))
                )
                db.session.add(inv)
                db.session.flush()
                db.session.add(InvoiceItem(invoice_id=inv.id, product_id=prod.id, quantity=qty, unit_price=prod.sale_price, total=subtotal))
                cust.balance += total
            print("  ✅ Invoices created")

            # 11. Quotations
            from erp.models import Quotation, QuotationItem
            for i in range(2):
                cust = customers[i % len(customers)]
                prod = products[(i+2) % len(products)]
                q = Quotation(
                    quote_number=f'QT-{i+1:05d}', customer_id=cust.id,
                    valid_until=datetime.now() + timedelta(days=30),
                    subtotal=prod.sale_price * 3, total_amount=prod.sale_price * 3, status='Draft'
                )
                db.session.add(q)
                db.session.flush()
                db.session.add(QuotationItem(quotation_id=q.id, product_id=prod.id, quantity=3, unit_price=prod.sale_price, total=prod.sale_price*3))
            print("  ✅ Quotations created")

            # 12. Service Data
            from erp.models import ServiceCustomer, ServiceRecord
            sc = ServiceCustomer(name='Rajiv Repair', phone='7777777777', address='Sector 15')
            db.session.add(sc)
            db.session.flush()
            db.session.add(ServiceRecord(
                service_customer_id=sc.id, serviceman_name='Technician Bob',
                issue_reported='Laptop Overheating', action_taken='Cleaned fans, replaced thermal paste',
                total_cost=1200.0, service_date=datetime.now() - timedelta(days=5)
            ))
            print("  ✅ Service records created")

            # 13. Audit Logs
            if admin_user:
                for action, rtype, details in [
                    ('User Login', 'User', 'admin logged in'),
                    ('Created Invoice', 'Invoice', 'INV-00001 created'),
                    ('Added Product', 'Product', 'Gaming Laptop added'),
                    ('Updated Customer', 'Customer', 'Balance adjusted'),
                    ('Created Quotation', 'Quotation', 'QT-00001 sent to client'),
                ]:
                    db.session.add(AuditLog(action=action, resource_type=rtype, details=details,
                        user_id=admin_user.id, timestamp=datetime.now() - timedelta(hours=random.randint(1, 72))))
                print("  ✅ Audit logs created")

            db.session.commit()
            print("🎉 Database fully initialized with sample data!")
