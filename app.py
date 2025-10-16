from erp import create_app, db
from erp.models import (Customer, Product, Supplier, Invoice, Payment, 
                        Expense, PricingTier, Account)

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
        'Account': Account
    }

@app.cli.command()
def init_db():
    """Initialize the database with sample data"""
    db.create_all()
    
    # Create default pricing tiers
    if not PricingTier.query.first():
        tiers = [
            PricingTier(name='Retail', discount_percentage=0),
            PricingTier(name='Wholesale', discount_percentage=10),
            PricingTier(name='Distributor', discount_percentage=15)
        ]
        for tier in tiers:
            db.session.add(tier)
    
    # Create sample products
    if not Product.query.first():
        products = [
            Product(name='LED Bulb 9W', sku='LED-9W', hsn_code='85395000', 
                   stock=100, purchase_price=50, sale_price=75),
            Product(name='LED Bulb 12W', sku='LED-12W', hsn_code='85395000',
                   stock=80, purchase_price=70, sale_price=100),
            Product(name='Fan Regulator', sku='FAN-REG', hsn_code='85381010',
                   stock=50, purchase_price=120, sale_price=180),
            Product(name='Switch 1-Way', sku='SW-1W', hsn_code='85381010',
                   stock=200, purchase_price=15, sale_price=25)
        ]
        for product in products:
            db.session.add(product)
    
    try:
        db.session.commit()
        print('Database initialized successfully!')
    except Exception as e:
        db.session.rollback()
        print(f'Error initializing database: {e}')

from erp import create_app

if __name__ == '__main__':
    app.run(debug=True)