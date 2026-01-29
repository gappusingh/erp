from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db 

# db = SQLAlchemy()

class User(db.Model, UserMixin):
    """User accounts for authentication and RBAC"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='Sales', nullable=False) # Admin, Manager, Sales, Technician, Accountant

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

class PricingTier(db.Model):
    """Different pricing levels for customers (Wholesale, Retail, etc.)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    discount_percentage = db.Column(db.Float, default=0.0)

class Category(db.Model):
    """Product categories (LED, Fans, etc.)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))

    products = db.relationship('Product', backref='category', lazy=True)

class Warehouse(db.Model):
    """Multiple storage locations"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    location = db.Column(db.String(200))

class Product(db.Model):
    """Product catalog with advanced inventory tracking"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    sku = db.Column(db.String(50), nullable=False, unique=True)
    hsn_code = db.Column(db.String(8))
    
    # Pricing & Stock
    purchase_price = db.Column(db.Float, nullable=False)
    sale_price = db.Column(db.Float, nullable=False)
    
    # New Inventory Fields
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    uom_purchase = db.Column(db.String(20), default='Pcs') # e.g., Carton
    uom_sale = db.Column(db.String(20), default='Pcs')     # e.g., Box
    uom_conversion = db.Column(db.Integer, default=1)      # 1 Purchase UoM = X Sale UoM
    reorder_level = db.Column(db.Integer, default=0)       # Low stock threshold
    
    # Deprecated 'stock' column - moving to ProductStock for multi-warehouse
    # Keeping it for backward compatibility or as a 'total' cache
    stock = db.Column(db.Integer, default=0, nullable=False)

    def __repr__(self):
        return f'<Product {self.name}>'

class ProductStock(db.Model):
    """Stock quantity per warehouse"""
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), nullable=False)
    quantity = db.Column(db.Integer, default=0, nullable=False)

    product = db.relationship('Product', backref=db.backref('warehouse_stocks', lazy=True))
    warehouse = db.relationship('Warehouse', backref=db.backref('product_stocks', lazy=True))

class ProductSerialNumber(db.Model):
    """Tracking individual items by serial number/batch"""
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), nullable=True)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(20), default='Available') # Available, Sold, Damaged, Returned
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref=db.backref('serial_numbers', lazy=True))
    warehouse = db.relationship('Warehouse', backref=db.backref('serials', lazy=True))

class Customer(db.Model):
    """Customer/Shop details with credit tracking"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    gstin = db.Column(db.String(15), unique=True)
    state_code = db.Column(db.String(2))
    address = db.Column(db.Text)
    phone = db.Column(db.String(15))
    balance = db.Column(db.Float, default=0.0, nullable=False)
    price_list_id = db.Column(db.Integer, db.ForeignKey('price_list.id'), nullable=True)
    
    price_list = db.relationship('PriceList', backref='customers')
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


   # --- ADD THIS NEW CLASS ---
class ServiceCustomer(db.Model):
    """Separate table strictly for Service/Repair customers"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # unique=True makes the Phone Number the Unique ID
    phone = db.Column(db.String(20), nullable=False, unique=True) 
    address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Link to service records
    services = db.relationship('ServiceRecord', backref='service_customer', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<ServiceCustomer {self.name} - {self.phone}>'

# --- MODIFY THIS EXISTING CLASS ---
class ServiceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # CHANGE: Link to ServiceCustomer instead of Customer
    service_customer_id = db.Column(db.Integer, db.ForeignKey('service_customer.id'), nullable=False)
    
    service_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    serviceman_name = db.Column(db.String(100), nullable=False)
    issue_reported = db.Column(db.Text, nullable=True)
    action_taken = db.Column(db.Text, nullable=True)
    service_charge = db.Column(db.Float, default=0.0)
    parts_cost = db.Column(db.Float, default=0.0)
    total_cost = db.Column(db.Float, default=0.0)
    # next_service_date = db.Column(db.Date, nullable=True)
    due_date_6mo = db.Column(db.Date, nullable=True)  # For 6-month checkup
    due_date_1yr = db.Column(db.Date, nullable=True)  # For 1-year renewal
    # Note: 'service_customer' backref is handled in ServiceCustomer class



class ServiceBooking(db.Model):
    """Temporary table for scheduled/pending jobs"""
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    
    # Booking Details
    scheduled_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    scheduled_time = db.Column(db.String(20), nullable=True) # e.g., "10:00 AM"
    issue_reported = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending') # Pending, Completed, Cancelled
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Booking {self.id} - {self.customer_name}>'

class AuditLog(db.Model):
    """Tracks user actions and system changes"""
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50), nullable=True) # e.g., 'Invoice', 'Product'
    resource_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)

    user = db.relationship('User', backref=db.backref('audit_logs', lazy=True))

    def __repr__(self):
        return f'<AuditLog {self.action} by User {self.user_id}>'

class Lead(db.Model):
    """Potential customers (CRM)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    business_name = db.Column(db.String(100))
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))
    status = db.Column(db.String(20), default='New') # New, Contacted, Interested, Converted, Lost
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    assigned_to = db.relationship('User', backref='leads')

class Quotation(db.Model):
    """Formal price quotes before invoicing"""
    id = db.Column(db.Integer, primary_key=True)
    quote_number = db.Column(db.String(50), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    valid_until = db.Column(db.DateTime)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    lead_id = db.Column(db.Integer, db.ForeignKey('lead.id')) # Can quote leads too
    
    subtotal = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='Draft') # Draft, Sent, Accepted, Invoiced, Expired
    
    customer = db.relationship('Customer', backref='quotations')
    lead = db.relationship('Lead', backref='quotations')
    items = db.relationship('QuotationItem', backref='quotation', cascade="all, delete-orphan")

class QuotationItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quotation_id = db.Column(db.Integer, db.ForeignKey('quotation.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    
    product = db.relationship('Product')

class SalesReturn(db.Model):
    """Customer returns (Credit Notes)"""
    id = db.Column(db.Integer, primary_key=True)
    return_number = db.Column(db.String(50), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id')) # Optional link to orig invoice
    
    total_amount = db.Column(db.Float, default=0.0)
    reason = db.Column(db.String(200))
    status = db.Column(db.String(20), default='Completed')
    
    customer = db.relationship('Customer', backref='returns')
    invoice = db.relationship('Invoice', backref='returns')
    items = db.relationship('SalesReturnItem', backref='sales_return', cascade="all, delete-orphan")

class SalesReturnItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    return_id = db.Column(db.Integer, db.ForeignKey('sales_return.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), nullable=False) # Where items are returned to
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    
    product = db.relationship('Product')
    warehouse = db.relationship('Warehouse')

class PriceList(db.Model):
    """Custom pricing for regions or specific groups"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(200))
    discount_percentage = db.Column(db.Float, default=0.0) # Flat discount for the entire list
    is_active = db.Column(db.Boolean, default=True)
    
    items = db.relationship('PriceListItem', backref='price_list', cascade="all, delete-orphan")

class PriceListItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price_list_id = db.Column(db.Integer, db.ForeignKey('price_list.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    custom_price = db.Column(db.Float, nullable=False)
    
    product = db.relationship('Product')
