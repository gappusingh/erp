from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField, SelectField, TextAreaField, DateField
from wtforms.validators import DataRequired, NumberRange, Optional

class ProductForm(FlaskForm):
    """Form for adding/editing products"""
    name = StringField('Product Name', validators=[DataRequired()])
    sku = StringField('SKU', validators=[DataRequired()])
    hsn_code = StringField('HSN Code', validators=[Optional()])
    stock = IntegerField('Initial Stock', validators=[DataRequired(), NumberRange(min=0)])
    purchase_price = FloatField('Purchase Price', validators=[DataRequired(), NumberRange(min=0)])
    sale_price = FloatField('Sale Price', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Save Product')

class CustomerForm(FlaskForm):
    """Form for adding/editing customers"""
    name = StringField('Shop Name', validators=[DataRequired()])
    gstin = StringField('GSTIN', validators=[Optional()])
    state_code = StringField('State Code (e.g., 10 for Bihar)', validators=[Optional()])
    address = TextAreaField('Address', validators=[Optional()])
    phone = StringField('Phone Number', validators=[Optional()])
    pricing_tier = SelectField('Pricing Tier', coerce=int, validators=[Optional()])
    submit = SubmitField('Save Customer')

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