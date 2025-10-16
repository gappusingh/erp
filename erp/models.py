from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property
from . import db 

# db = SQLAlchemy()

class PricingTier(db.Model):
    """Different pricing levels for customers (Wholesale, Retail, etc.)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    discount_percentage = db.Column(db.Float, default=0.0)

class Product(db.Model):
    """Product catalog with inventory tracking"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    sku = db.Column(db.String(50), nullable=False, unique=True)
    hsn_code = db.Column(db.String(8))
    stock = db.Column(db.Integer, default=0, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    sale_price = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<Product {self.name}>'

class Customer(db.Model):
    """Customer/Shop details with credit tracking"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    gstin = db.Column(db.String(15), unique=True)
    state_code = db.Column(db.String(2))
    address = db.Column(db.Text)
    phone = db.Column(db.String(15))
    balance = db.Column(db.Float, default=0.0, nullable=False)
    pricing_tier_id = db.Column(db.Integer, db.ForeignKey('pricing_tier.id'))
    
    pricing_tier = db.relationship('PricingTier')
    invoices = db.relationship('Invoice', backref='customer', lazy=True, cascade="all, delete-orphan")
    payments = db.relationship('Payment', backref='customer', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Customer {self.name}>'

class Supplier(db.Model):
    """Supplier details with payable tracking"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    gstin = db.Column(db.String(15), unique=True)
    address = db.Column(db.Text)
    phone = db.Column(db.String(15))
    balance = db.Column(db.Float, default=0.0, nullable=False)
    
    purchase_orders = db.relationship('PurchaseOrder', backref='supplier', lazy=True)

class Invoice(db.Model):
    """Sales invoice with multi-item support"""
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    subtotal = db.Column(db.Float, default=0.0)
    cgst_amount = db.Column(db.Float, default=0.0)
    sgst_amount = db.Column(db.Float, default=0.0)
    igst_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    notes = db.Column(db.Text)
    
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade="all, delete-orphan")

class InvoiceItem(db.Model):
    """Individual line items in an invoice"""
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    cgst_rate = db.Column(db.Float, default=0.0)
    sgst_rate = db.Column(db.Float, default=0.0)
    igst_rate = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, nullable=False)
    
    product = db.relationship('Product')

class Payment(db.Model):
    """Payment records from customers"""
    id = db.Column(db.Integer, primary_key=True)
    payment_number = db.Column(db.String(50), unique=True)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_mode = db.Column(db.String(50), default='Cash')
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    notes = db.Column(db.Text)

class PurchaseOrder(db.Model):
    """Purchase orders to suppliers"""
    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(50), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(20), default='Pending')
    
    items = db.relationship('PurchaseOrderItem', backref='purchase_order', lazy=True, cascade="all, delete-orphan")

class PurchaseOrderItem(db.Model):
    """Items in a purchase order"""
    id = db.Column(db.Integer, primary_key=True)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    
    product = db.relationship('Product')

class SupplierPayment(db.Model):
    """Payments made to suppliers"""
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_mode = db.Column(db.String(50), default='Cash')
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    notes = db.Column(db.Text)
    
    supplier = db.relationship('Supplier', backref='payments')

class Expense(db.Model):
    """Business expense tracking"""
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    expense_date = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(50))
    payment_mode = db.Column(db.String(50), default='Cash')

class DeliveryChallan(db.Model):
    """Delivery documents for goods dispatch"""
    id = db.Column(db.Integer, primary_key=True)
    challan_number = db.Column(db.String(50), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'))
    vehicle_number = db.Column(db.String(20))
    driver_name = db.Column(db.String(100))
    
    customer = db.relationship('Customer')
    invoice = db.relationship('Invoice')
    items = db.relationship('ChallanItem', backref='challan', lazy=True, cascade="all, delete-orphan")

class ChallanItem(db.Model):
    """Items in delivery challan"""
    id = db.Column(db.Integer, primary_key=True)
    challan_id = db.Column(db.Integer, db.ForeignKey('delivery_challan.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    
    product = db.relationship('Product')

# Double-Entry Accounting System
class Account(db.Model):
    """Chart of accounts for double-entry bookkeeping"""
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), unique=True, nullable=False)
    account_type = db.Column(db.String(50), nullable=False)
    
    @hybrid_property
    def balance(self):
        total_debits = db.session.query(func.sum(LedgerEntry.debit)).filter(
            LedgerEntry.account_id == self.id).scalar() or 0.0
        total_credits = db.session.query(func.sum(LedgerEntry.credit)).filter(
            LedgerEntry.account_id == self.id).scalar() or 0.0
        
        if self.account_type in ['Asset', 'Expense']:
            return total_debits - total_credits
        else:
            return total_credits - total_debits

class JournalEntry(db.Model):
    """Journal entries for accounting transactions"""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(255), nullable=False)
    related_document_id = db.Column(db.Integer)
    document_type = db.Column(db.String(50))
    
    entries = db.relationship('LedgerEntry', backref='journal_entry', cascade="all, delete-orphan")

class LedgerEntry(db.Model):
    """Individual debit/credit entries in journal"""
    id = db.Column(db.Integer, primary_key=True)
    journal_id = db.Column(db.Integer, db.ForeignKey('journal_entry.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    debit = db.Column(db.Float, default=0.0, nullable=False)
    credit = db.Column(db.Float, default=0.0, nullable=False)
    
    account = db.relationship('Account')