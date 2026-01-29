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