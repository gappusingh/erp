from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField, SelectField, TextAreaField, DateField, PasswordField
from wtforms.validators import DataRequired, NumberRange, Optional, Length


class ProductForm(FlaskForm):
    """Form for adding/editing products with advanced inventory fields"""
    name = StringField('Product Name', validators=[DataRequired()])
    sku = StringField('SKU', validators=[DataRequired()])
    hsn_code = StringField('HSN Code', validators=[Optional()])
    category = SelectField('Category', coerce=int, validators=[Optional()])
    
    # Pricing
    purchase_price = FloatField('Purchase Price', validators=[DataRequired(), NumberRange(min=0)])
    sale_price = FloatField('Sale Price', validators=[DataRequired(), NumberRange(min=0)])
    
    # Inventory & UoM
    uom_purchase = StringField('Purchase Unit (e.g. Carton)', default='Pcs', validators=[Optional()])
    uom_sale = StringField('Sales Unit (e.g. Box)', default='Pcs', validators=[Optional()])
    uom_conversion = IntegerField('Units in 1 Purchase Unit', default=1, validators=[Optional(), NumberRange(min=1)])
    reorder_level = IntegerField('Reorder Level (Alert)', default=5, validators=[Optional(), NumberRange(min=0)])
    
    stock = IntegerField('Initial Stock (in Sales Units)', validators=[DataRequired(), NumberRange(min=0)])
    
    submit = SubmitField('Save Product')

class CategoryForm(FlaskForm):
    """Form for adding/editing product categories"""
    name = StringField('Category Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Save Category')

class WarehouseForm(FlaskForm):
    """Form for adding/editing warehouses"""
    name = StringField('Warehouse Name', validators=[DataRequired()])
    location = StringField('Location', validators=[Optional()])
    submit = SubmitField('Save Warehouse')

class CustomerForm(FlaskForm):
    """Form for adding/editing customers"""
    name = StringField('Shop Name', validators=[DataRequired()])
    gstin = StringField('GSTIN', validators=[Optional()])
    state_code = StringField('State Code (e.g., 10 for Bihar)', validators=[Optional()])
    address = TextAreaField('Address', validators=[Optional()])
    phone = StringField('Phone Number', validators=[Optional()])
    price_list = SelectField('Price List', coerce=int, validators=[Optional()])
    submit = SubmitField('Save Customer')

class LeadForm(FlaskForm):
    """Form for tracking potential customers"""
    name = StringField('Contact Name', validators=[DataRequired()])
    business_name = StringField('Business Name (Optional)')
    phone = StringField('Phone Number', validators=[DataRequired()])
    email = StringField('Email', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('New', 'New'),
        ('Contacted', 'Contacted'),
        ('Interested', 'Interested'),
        ('Converted', 'Converted'),
        ('Lost', 'Lost')
    ], default='New')
    notes = TextAreaField('Notes')
    submit = SubmitField('Save Lead')
    
class PriceListForm(FlaskForm):
    """Form for creating new price lists"""
    name = StringField('List Name', validators=[DataRequired()])
    description = StringField('Description')
    discount_percentage = FloatField('Global Discount %', default=0.0, validators=[NumberRange(min=0, max=100)])
    submit = SubmitField('Save Price List')

class SupplierForm(FlaskForm):
    """Form for adding/editing suppliers"""
    name = StringField('Supplier Name', validators=[DataRequired()])
    gstin = StringField('GSTIN', validators=[Optional()])
    address = TextAreaField('Address', validators=[Optional()])
    phone = StringField('Phone Number', validators=[Optional()])
    submit = SubmitField('Save Supplier')

class PaymentForm(FlaskForm):
    """Form for recording customer payments"""
    customer = SelectField('Customer', coerce=int, validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    payment_mode = SelectField('Payment Mode', choices=[
        ('Cash', 'Cash'), 
        ('Cheque', 'Cheque'), 
        ('Bank Transfer', 'Bank Transfer'),
        ('UPI', 'UPI')
    ])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Record Payment')

class SupplierPaymentForm(FlaskForm):
    """Form for recording supplier payments"""
    supplier = SelectField('Supplier', coerce=int, validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    payment_mode = SelectField('Payment Mode', choices=[
        ('Cash', 'Cash'), 
        ('Cheque', 'Cheque'), 
        ('Bank Transfer', 'Bank Transfer'),
        ('UPI', 'UPI')
    ])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Record Payment')

class ExpenseForm(FlaskForm):
    """Form for recording business expenses"""
    description = StringField('Description', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    category = SelectField('Category', choices=[
        ('Transport', 'Transport'), 
        ('Salary', 'Salary'), 
        ('Rent', 'Rent'), 
        ('Utilities', 'Utilities'),
        ('Maintenance', 'Maintenance'),
        ('Other', 'Other')
    ])
    payment_mode = SelectField('Payment Mode', choices=[
        ('Cash', 'Cash'), 
        ('Cheque', 'Cheque'), 
        ('Bank Transfer', 'Bank Transfer')
    ])
    submit = SubmitField('Record Expense')

class PricingTierForm(FlaskForm):
    """Form for creating pricing tiers"""
    name = StringField('Tier Name', validators=[DataRequired()])
    discount_percentage = FloatField('Discount %', validators=[DataRequired(), NumberRange(min=0, max=100)])
    submit = SubmitField('Save Tier')

class DateRangeForm(FlaskForm):
    """Form for date range selection in reports"""
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    submit = SubmitField('Generate Report')


    # Add at the bottom of forms.py

class ServiceCustomerForm(FlaskForm):
    """Quick Add Form for Repair Customers"""
    name = StringField('Customer Name', validators=[DataRequired()])
    phone = StringField('Phone Number (Unique ID)', validators=[DataRequired()])
    address = TextAreaField('Address / Location', validators=[DataRequired()])
    submit = SubmitField('Save & Book')

class ServiceRecordForm(FlaskForm):
    # CHANGE: Logic will be handled in routes, but keep field definition
    customer = SelectField('Customer', coerce=int, validators=[DataRequired()])
    serviceman_name = StringField('Serviceman Name', validators=[DataRequired()])
    issue_reported = TextAreaField('Issue Reported')
    action_taken = TextAreaField('Action Taken / Parts Replaced')
    service_charge = FloatField('Service Charge', default=0.0)
    parts_cost = FloatField('Parts Cost', default=0.0)
    next_service_due = SelectField('Next Service Due', choices=[
        ('3', '3 Months'), 
        ('6', '6 Months'), 
        ('12', '1 Year')
    ], validators=[DataRequired()])
    submit = SubmitField('Save Job Card')




class SearchForm(FlaskForm):
    """Search form for the dashboard"""
    search_query = StringField('Search by Name or Phone', validators=[DataRequired()])
    submit = SubmitField('Search')


class UnifiedServiceForm(FlaskForm):
    """Smart Form: Handles both Customer Creation and Service Booking"""
    
    # --- 1. Customer Details ---
    # The Phone Number is the KEY. The system watches this field.
    customer_phone = StringField('Phone Number (Required)', validators=[DataRequired(), Length(min=10, max=15)])
    customer_name = StringField('Customer Name', validators=[DataRequired()])
    customer_address = TextAreaField('Address', validators=[DataRequired()])
    
    # --- 2. Service Job Details ---
    # New: Date Picker to select today or past dates
    service_date = DateField('Service Date', format='%Y-%m-%d', validators=[DataRequired()])
    
    serviceman_name = StringField('Technician Name', validators=[DataRequired()])
    issue_reported = TextAreaField('Issue Reported', validators=[DataRequired()])
    action_taken = TextAreaField('Action Taken')
    
    # Costs
    service_charge = FloatField('Service Charge', default=0.0)
    parts_cost = FloatField('Parts Cost', default=0.0)
    
    # # Reminder for Next Visit
    # next_service_due = SelectField('Next Service Reminder', choices=[
    #     ('3', '3 Months'), 
    #     ('6', '6 Months'), 
    #     ('12', '1 Year')
    # ], validators=[DataRequired()])
    
    submit = SubmitField('Save Job Card')



class BookingForm(FlaskForm):
    """Form to schedule a NEW job"""
    customer_phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    customer_name = StringField('Customer Name', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[DataRequired()])
    
    scheduled_date = DateField('Scheduled Date', format='%Y-%m-%d', validators=[DataRequired()])
    scheduled_time = StringField('Preferred Time (Optional)')
    issue_reported = TextAreaField('Issue Reported', validators=[DataRequired()])
    
    submit = SubmitField('Book Appointment')


class LoginForm(FlaskForm):
    """Form for user login"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')