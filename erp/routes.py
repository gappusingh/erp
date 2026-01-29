from flask import Blueprint, render_template, redirect, url_for, flash, session, request, Response
# Ensure ServiceRecord is imported here
from .models import (db, Product, Customer, Supplier, Invoice, InvoiceItem, Payment, 
                    SupplierPayment, PurchaseOrder, PurchaseOrderItem, Expense, 
                    DeliveryChallan, ChallanItem, PricingTier, Account, JournalEntry, LedgerEntry,
                    ServiceRecord, ServiceCustomer) # <--- Added ServiceCustomer

from .forms import (ProductForm, CustomerForm, SupplierForm, PaymentForm, SupplierPaymentForm,
                   ExpenseForm, PricingTierForm, DateRangeForm, 
                   ServiceRecordForm, SearchForm, ServiceCustomerForm, UnifiedServiceForm) # <--- Added ServiceCustomerForm
from sqlalchemy import func, extract
from datetime import date, datetime, timedelta
from weasyprint import HTML
import io
import base64
from matplotlib.figure import Figure
from .models import ServiceBooking # ... other imports
from .forms import BookingForm

# FIX: Ensure double underscores are used here: __name__
bp = Blueprint('main', __name__)


# ============ DASHBOARD ============
@bp.route('/')
def dashboard():
    """Main dashboard with financial summary and customer cards"""
    today = date.today()
    
    # Financial metrics
    total_collections_today = db.session.query(func.sum(Payment.amount)).filter(
        func.date(Payment.payment_date) == today).scalar() or 0.0
    
    total_credit_today = db.session.query(func.sum(Invoice.total_amount)).filter(
        func.date(Invoice.created_at) == today).scalar() or 0.0
    
    total_market_due = db.session.query(func.sum(Customer.balance)).scalar() or 0.0
    
    total_supplier_due = db.session.query(func.sum(Supplier.balance)).scalar() or 0.0
    
    # Fetch all customers with their data
    customers = Customer.query.order_by(Customer.name).all()
    
    # Calculate monthly order summary for each customer
    for customer in customers:
        orders_by_month = db.session.query(
            func.strftime('%Y-%m', Invoice.created_at).label('month'),
            func.count(Invoice.id).label('count')
        ).filter(Invoice.customer_id == customer.id
        ).group_by('month'
        ).order_by(func.strftime('%Y-%m', Invoice.created_at).desc()
        ).limit(6).all()
        
        customer.orders_summary = orders_by_month
    
    

    return render_template('dashboard.html',
                         collections_today=total_collections_today,
                         credit_today=total_credit_today,
                         market_due=total_market_due,
                         supplier_due=total_supplier_due,
                         customers=customers)

# ============ PRODUCT MANAGEMENT ============
@bp.route('/add/product', methods=['GET', 'POST'])
def add_product():
    """Add new product to inventory"""
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            sku=form.sku.data,
            hsn_code=form.hsn_code.data,
            stock=form.stock.data,
            purchase_price=form.purchase_price.data,
            sale_price=form.sale_price.data
        )
        db.session.add(product)
        db.session.commit()
        flash(f'Product {form.name.data} added successfully!', 'success')
        return redirect(url_for('main.products_list'))
    return render_template('_form_renderer.html', form=form, title="Add New Product")

@bp.route('/products')
def products_list():
    """List all products"""
    products = Product.query.order_by(Product.name).all()
    return render_template('products_list.html', products=products)

# ============ CUSTOMER MANAGEMENT ============
@bp.route('/add/customer', methods=['GET', 'POST'])
def add_customer():
    """Add new customer"""
    form = CustomerForm()
    form.pricing_tier.choices = [(0, 'None')] + [(t.id, t.name) for t in PricingTier.query.all()]
    
    if form.validate_on_submit():
        customer = Customer(
            name=form.name.data,
            gstin=form.gstin.data,
            state_code=form.state_code.data,
            address=form.address.data,
            phone=form.phone.data,
            pricing_tier_id=form.pricing_tier.data if form.pricing_tier.data != 0 else None
        )
        db.session.add(customer)
        db.session.commit()
        flash(f'Customer {form.name.data} added successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('_form_renderer.html', form=form, title="Add New Customer")

@bp.route('/customer/<int:customer_id>/statement')
def view_statement(customer_id):
    """View detailed account statement for a customer"""
    customer = Customer.query.get_or_404(customer_id)
    
    # Fetch all transactions
    invoices = Invoice.query.filter_by(customer_id=customer.id).all()
    payments = Payment.query.filter_by(customer_id=customer.id).all()
    
    # Combine into single transaction list
    transactions = []
    for inv in invoices:
        transactions.append({
            'date': inv.created_at,
            'description': f"Invoice #{inv.invoice_number or inv.id}",
            'debit': inv.total_amount,
            'credit': 0,
            'type': 'Invoice',
            'id': inv.id
        })
    
    for pmt in payments:
        transactions.append({
            'date': pmt.payment_date,
            'description': f"Payment - {pmt.payment_mode}",
            'debit': 0,
            'credit': pmt.amount,
            'type': 'Payment',
            'id': pmt.id
        })
    
    # Sort chronologically
    sorted_transactions = sorted(transactions, key=lambda x: x['date'])
    
    return render_template('customer_statement.html',
                         customer=customer,
                         transactions=sorted_transactions)

# ============ INVOICE CREATION ============
@bp.route('/sales/invoice/new', methods=['GET', 'POST'])
def create_invoice():
    """Create new sales invoice with multi-item cart"""
    if request.method == 'POST':
        customer_id = request.form.get('customer')
        cart_items = session.get('cart', [])
        
        if not customer_id or not cart_items:
            flash('Customer and at least one product are required.', 'danger')
            return redirect(url_for('main.create_invoice'))
        
        customer = Customer.query.get(customer_id)
        
        try:
            # Calculate totals
            subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
            
            # GST calculation (simplified - you can enhance this)
            gst_rate = 18  # 18% GST
            cgst = sgst = subtotal * (gst_rate / 2) / 100
            igst = 0
            total = subtotal + cgst + sgst
            
            # Generate invoice number
            last_invoice = Invoice.query.order_by(Invoice.id.desc()).first()
            invoice_number = f"INV-{(last_invoice.id + 1) if last_invoice else 1:05d}"
            
            # Create invoice
            new_invoice = Invoice(
                invoice_number=invoice_number,
                customer_id=customer.id,
                subtotal=subtotal,
                cgst_amount=cgst,
                sgst_amount=sgst,
                igst_amount=igst,
                total_amount=total
            )
            db.session.add(new_invoice)
            db.session.flush()
            
            # Add invoice items and update stock
            for item in cart_items:
                product = Product.query.get(item['product_id'])
                
                if product.stock < item['quantity']:
                    raise ValueError(f"Insufficient stock for {product.name}")
                
                invoice_item = InvoiceItem(
                    invoice_id=new_invoice.id,
                    product_id=product.id,
                    quantity=item['quantity'],
                    unit_price=item['price'],
                    cgst_rate=gst_rate/2,
                    sgst_rate=gst_rate/2,
                    total=item['price'] * item['quantity']
                )
                db.session.add(invoice_item)
                
                # Update stock
                product.stock -= item['quantity']
            
            # Update customer balance
            customer.balance += total
            
            # Create journal entry for double-entry accounting
            create_invoice_journal_entry(new_invoice, subtotal)
            
            db.session.commit()
            session.pop('cart', None)
            
            flash(f'Invoice {invoice_number} created successfully!', 'success')
            return redirect(url_for('main.generate_invoice_pdf', invoice_id=new_invoice.id))
            
        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating invoice: {str(e)}', 'danger')
        
        return redirect(url_for('main.create_invoice'))
    
    # GET request
    customers = Customer.query.order_by('name').all()
    products = Product.query.filter(Product.stock > 0).order_by('name').all()
    cart = session.get('cart', [])
    preselected_customer_id = request.args.get('customer_id', type=int)
    
    return render_template('create_invoice.html',
                         customers=customers,
                         products=products,
                         cart=cart,
                         preselected_customer_id=preselected_customer_id)

@bp.route('/cart/add', methods=['POST'])
def add_to_cart():
    """Add product to invoice cart"""
    cart = session.get('cart', [])
    product_id = int(request.form.get('product_id'))
    quantity = int(request.form.get('quantity'))
    
    product = Product.query.get(product_id)
    
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('main.create_invoice'))
    
    if product.stock < quantity:
        flash(f'Insufficient stock for {product.name}. Available: {product.stock}', 'warning')
        return redirect(url_for('main.create_invoice'))
    
    # Apply pricing tier if applicable
    price = product.sale_price
    
    cart.append({
        'product_id': product_id,
        'name': product.name,
        'sku': product.sku,
        'quantity': quantity,
        'price': price
    })
    
    session['cart'] = cart
    flash(f'Added {product.name} to cart', 'success')
    return redirect(url_for('main.create_invoice'))

@bp.route('/cart/clear')
def clear_cart():
    """Clear invoice cart"""
    session.pop('cart', None)
    return redirect(url_for('main.create_invoice'))

# ============ PAYMENT RECORDING ============
@bp.route('/add/payment', methods=['GET', 'POST'])
def add_payment():
    """Record customer payment"""
    form = PaymentForm()
    form.customer.choices = [(c.id, c.name) for c in Customer.query.order_by('name').all()]
    
    preselected_customer_id = request.args.get('customer_id', type=int)
    if preselected_customer_id and request.method == 'GET':
        form.customer.data = preselected_customer_id
    
    if form.validate_on_submit():
        customer = Customer.query.get(form.customer.data)
        amount = form.amount.data
        
        try:
            # Generate payment number
            last_payment = Payment.query.order_by(Payment.id.desc()).first()
            payment_number = f"PMT-{(last_payment.id + 1) if last_payment else 1:05d}"
            
            # Create payment record
            new_payment = Payment(
                payment_number=payment_number,
                customer_id=customer.id,
                amount=amount,
                payment_mode=form.payment_mode.data,
                notes=form.notes.data
            )
            db.session.add(new_payment)
            
            # Update customer balance
            customer.balance -= amount
            
            # Create journal entry
            create_payment_journal_entry(new_payment)
            
            db.session.commit()
            flash(f'Payment of ₹{amount:.2f} recorded for {customer.name}!', 'success')
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error recording payment: {str(e)}', 'danger')
    
    return render_template('_form_renderer.html', form=form, title="Record Payment")

# ============ SUPPLIER & PURCHASE ORDERS ============
@bp.route('/add/supplier', methods=['GET', 'POST'])
def add_supplier():
    """Add new supplier"""
    form = SupplierForm()
    if form.validate_on_submit():
        supplier = Supplier(
            name=form.name.data,
            gstin=form.gstin.data,
            address=form.address.data,
            phone=form.phone.data
        )
        db.session.add(supplier)
        db.session.commit()
        flash(f'Supplier {form.name.data} added successfully!', 'success')
        return redirect(url_for('main.suppliers_list'))
    return render_template('_form_renderer.html', form=form, title="Add New Supplier")

@bp.route('/suppliers')
def suppliers_list():
    """List all suppliers"""
    suppliers = Supplier.query.order_by(Supplier.name).all()
    return render_template('suppliers_list.html', suppliers=suppliers)

@bp.route('/purchasing/po/new', methods=['GET', 'POST'])
def create_purchase_order():
    """Create purchase order (simplified single-item version)"""
    if request.method == 'POST':
        supplier_id = request.form.get('supplier')
        product_id = request.form.get('product')
        quantity = int(request.form.get('quantity'))
        unit_cost = float(request.form.get('unit_cost'))
        
        supplier = Supplier.query.get(supplier_id)
        product = Product.query.get(product_id)
        total = quantity * unit_cost
        
        try:
            # Generate PO number
            last_po = PurchaseOrder.query.order_by(PurchaseOrder.id.desc()).first()
            po_number = f"PO-{(last_po.id + 1) if last_po else 1:05d}"
            
            # Create PO
            new_po = PurchaseOrder(
                po_number=po_number,
                supplier_id=supplier.id,
                total_amount=total,
                status='Completed'
            )
            db.session.add(new_po)
            db.session.flush()
            
            # Add PO item
            po_item = PurchaseOrderItem(
                po_id=new_po.id,
                product_id=product.id,
                quantity=quantity,
                unit_cost=unit_cost,
                total=total
            )
            db.session.add(po_item)
            
            # Update stock and supplier balance
            product.stock += quantity
            supplier.balance += total
            
            db.session.commit()
            flash(f'Purchase Order {po_number} created successfully!', 'success')
            return redirect(url_for('main.suppliers_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating PO: {str(e)}', 'danger')
        
        return redirect(url_for('main.create_purchase_order'))
    
    # GET request
    suppliers = Supplier.query.order_by('name').all()
    products = Product.query.order_by('name').all()
    return render_template('create_po.html', suppliers=suppliers, products=products)


# In erp/routes.py

@bp.route('/purchases')
def purchase_orders_list():
    """List all purchase orders"""
    # Query the database for all purchase orders, showing the newest first
    purchase_orders = PurchaseOrder.query.order_by(PurchaseOrder.created_at.desc()).all()
    return render_template('purchase_orders_list.html', purchase_orders=purchase_orders)

# In erp/routes.py

@bp.route('/customer/<int:customer_id>/challans')
def customer_challans_list(customer_id):
    """List all delivery challans for a specific customer"""
    customer = Customer.query.get_or_404(customer_id)
    challans = DeliveryChallan.query.filter_by(customer_id=customer_id).order_by(DeliveryChallan.created_at.desc()).all()
    return render_template('customer_challans.html', challans=challans, customer=customer)

@bp.route('/add/supplier-payment', methods=['GET', 'POST'])
def add_supplier_payment():
    """Record payment to supplier"""
    form = SupplierPaymentForm()
    form.supplier.choices = [(s.id, s.name) for s in Supplier.query.order_by('name').all()]
    
    if form.validate_on_submit():
        supplier = Supplier.query.get(form.supplier.data)
        amount = form.amount.data
        
        try:
            payment = SupplierPayment(
                supplier_id=supplier.id,
                amount=amount,
                payment_mode=form.payment_mode.data,
                notes=form.notes.data
            )
            db.session.add(payment)
            
            # Update supplier balance
            supplier.balance -= amount
            
            db.session.commit()
            flash(f'Payment of ₹{amount:.2f} made to {supplier.name}!', 'success')
            return redirect(url_for('main.suppliers_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error recording payment: {str(e)}', 'danger')
    
    return render_template('_form_renderer.html', form=form, title="Pay Supplier")

# ============ EXPENSE TRACKING ============
@bp.route('/add/expense', methods=['GET', 'POST'])
def add_expense():
    """Record business expense"""
    form = ExpenseForm()
    if form.validate_on_submit():
        expense = Expense(
            description=form.description.data,
            amount=form.amount.data,
            category=form.category.data,
            payment_mode=form.payment_mode.data
        )
        db.session.add(expense)
        db.session.commit()
        flash(f'Expense of ₹{form.amount.data:.2f} recorded!', 'success')
        return redirect(url_for('main.expenses_list'))
    return render_template('_form_renderer.html', form=form, title="Record Expense")

@bp.route('/expenses')
def expenses_list():
    """List all expenses"""
    expenses = Expense.query.order_by(Expense.expense_date.desc()).all()
    
    # Calculate category totals
    category_totals = db.session.query(
        Expense.category,
        func.sum(Expense.amount).label('total')
    ).group_by(Expense.category).all()
    
    return render_template('expenses_list.html', 
                         expenses=expenses, 
                         category_totals=category_totals)

# ============ REPORTS ============
@bp.route('/reports/profit-and-loss', methods=['GET', 'POST'])
def profit_and_loss():
    """Generate Profit & Loss statement"""
    form = DateRangeForm()
    
    if form.validate_on_submit():
        start_date = datetime.combine(form.start_date.data, datetime.min.time())
        end_date = datetime.combine(form.end_date.data, datetime.max.time())
    else:
        # Default to current month
        today = datetime.today()
        start_date = today.replace(day=1, hour=0, minute=0, second=0)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        form.start_date.data = start_date.date()
        form.end_date.data = end_date.date()
    
    # Calculate Revenue
    revenue_items = db.session.query(InvoiceItem).join(Invoice).filter(
        Invoice.created_at.between(start_date, end_date)).all()
    total_revenue = sum(item.unit_price * item.quantity for item in revenue_items)
    
    # Calculate COGS
    total_cogs = sum(item.product.purchase_price * item.quantity for item in revenue_items)
    gross_profit = total_revenue - total_cogs
    
    # Calculate Expenses
    total_expenses = db.session.query(func.sum(Expense.amount)).filter(
        Expense.expense_date.between(start_date, end_date)).scalar() or 0.0
    
    # Net Profit
    net_profit = gross_profit - total_expenses
    
    expenses_query = db.session.query(
        Expense.category,
        func.sum(Expense.amount).label('total_amount')
    ).filter(
        Expense.expense_date.between(start_date, end_date)
    ).group_by(Expense.category).all()

    # Convert the query result into the list of dictionaries the chart needs
    expenses_by_category = [
        {'category': item.category, 'amount': float(item.total_amount)}
        for item in expenses_query
    ]
    
    return render_template('reports/profit_and_loss.html',
                         form=form,
                         start_date=start_date.date(),
                         end_date=end_date.date(),
                         total_revenue=total_revenue,
                         total_cogs=total_cogs,
                         gross_profit=gross_profit,
                         total_expenses=total_expenses,
                         net_profit=net_profit,
                         expenses_by_category=expenses_by_category)



# Add these imports to the top of routes.py
import io
import base64
from matplotlib.figure import Figure

# ... your other routes ...

# HELPER FUNCTION to generate chart images (place this before the route)
def generate_chart_image(labels, data, chart_title, chart_type='pie'):
    """Generates a chart image and returns it as a base64 string."""
    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)
    
    if chart_type == 'pie':
        ax.pie(data, labels=labels, autopct='%1.1f%%', startangle=90)
    elif chart_type == 'bar':
        ax.bar(labels, data)

    ax.set_title(chart_title)
    
    # Save it to a temporary buffer.
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return data

# NEW ROUTE for downloading the report
@bp.route('/reports/download-summary-pdf')
def download_summary_report():
    """Gathers all data for a date range and generates a comprehensive PDF report."""
    # 1. Get dates from URL parameters
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        end_date = end_date.replace(hour=23, minute=59, second=59) # include whole day
    except (ValueError, TypeError):
        flash('Invalid date format provided.', 'danger')
        return redirect(url_for('main.profit_and_loss'))

    # 2. GATHER ALL DATA
    # P&L Data
    revenue_items = db.session.query(InvoiceItem).join(Invoice).filter(Invoice.created_at.between(start_date, end_date)).all()
    total_revenue = sum(item.total for item in revenue_items)
    total_cogs = sum(item.product.purchase_price * item.quantity for item in revenue_items)
    gross_profit = total_revenue - total_cogs
    total_expenses = db.session.query(func.sum(Expense.amount)).filter(Expense.expense_date.between(start_date, end_date)).scalar() or 0.0
    net_profit = gross_profit - total_expenses
    
    expenses_by_category_query = db.session.query(Expense.category, func.sum(Expense.amount).label('total')).filter(Expense.expense_date.between(start_date, end_date)).group_by(Expense.category).all()
    expenses_by_category = [{'category': r.category, 'amount': r.total} for r in expenses_by_category_query]

    # Detailed Lists
    all_sales = Invoice.query.filter(Invoice.created_at.between(start_date, end_date)).order_by(Invoice.created_at.desc()).all()
    all_purchases = PurchaseOrder.query.filter(PurchaseOrder.created_at.between(start_date, end_date)).order_by(PurchaseOrder.created_at.desc()).all()
    all_expenses_list = Expense.query.filter(Expense.expense_date.between(start_date, end_date)).order_by(Expense.expense_date.desc()).all()
    all_customer_payments = Payment.query.filter(Payment.payment_date.between(start_date, end_date)).order_by(Payment.payment_date.desc()).all()

    # 3. GENERATE CHART IMAGES
    # Profit Breakdown Chart
    profit_labels = ['COGS', 'Expenses', 'Net Profit']
    profit_data = [total_cogs, total_expenses, net_profit if net_profit > 0 else 0]
    profit_chart_image = generate_chart_image(profit_labels, profit_data, 'Revenue Breakdown', 'pie')
     

    total_purchases_amount = sum(p.total_amount for p in all_purchases)
    total_payments_received = sum(p.amount for p in all_customer_payments)

    # Expense Breakdown Chart
    expense_labels = [e['category'] for e in expenses_by_category]
    expense_data = [e['amount'] for e in expenses_by_category]
    expense_chart_image = generate_chart_image(expense_labels, expense_data, 'Expense Categories', 'pie')
    
    # 4. RENDER HTML TEMPLATE FOR PDF
    rendered_html = render_template('pdf/comprehensive_report.html',
                                  start_date=start_date,
                                  end_date=end_date,
                                  total_revenue=total_revenue,
                                  total_cogs=total_cogs,
                                  gross_profit=gross_profit,
                                  total_expenses=total_expenses,
                                  net_profit=net_profit,
                                  all_sales=all_sales,
                                  all_purchases=all_purchases,
                                  all_expenses_list=all_expenses_list,
                                  all_customer_payments=all_customer_payments,
                                  profit_chart_image=profit_chart_image,
                                  expense_chart_image=expense_chart_image,
                                  total_purchases_amount=total_purchases_amount,
                                  total_payments_received=total_payments_received)
    
    # 5. CONVERT TO PDF
    pdf = HTML(string=rendered_html).write_pdf()
    
    return Response(pdf,
                  mimetype='application/pdf',
                  headers={'Content-Disposition': f'inline; filename=Business_Report_{start_date.date()}to{end_date.date()}.pdf'})

@bp.route('/reports/balance-sheet')
def balance_sheet():
    """Generate Balance Sheet"""
    # Assets
    total_cash = 0  # Would come from cash account in full accounting system
    accounts_receivable = db.session.query(func.sum(Customer.balance)).scalar() or 0.0
    inventory_value = db.session.query(
        func.sum(Product.stock * Product.purchase_price)).scalar() or 0.0
    total_assets = total_cash + accounts_receivable + inventory_value
    
    # Liabilities
    accounts_payable = db.session.query(func.sum(Supplier.balance)).scalar() or 0.0
    total_liabilities = accounts_payable
    
    # Equity
    total_equity = total_assets - total_liabilities
    
    return render_template('reports/balance_sheet.html',
                         total_cash=total_cash,
                         accounts_receivable=accounts_receivable,
                         inventory_value=inventory_value,
                         total_assets=total_assets,
                         accounts_payable=accounts_payable,
                         total_liabilities=total_liabilities,
                         total_equity=total_equity)

@bp.route('/reports/gst-summary', methods=['GET', 'POST'])
def gst_summary():
    """GST filing summary report"""
    form = DateRangeForm()
    
    if form.validate_on_submit():
        start_date = datetime.combine(form.start_date.data, datetime.min.time())
        end_date = datetime.combine(form.end_date.data, datetime.max.time())
    else:
        # Default to current month
        today = datetime.today()
        start_date = today.replace(day=1, hour=0, minute=0, second=0)
        end_date = today
        form.start_date.data = start_date.date()
        form.end_date.data = end_date.date()
    
    # Get all invoices in period
    invoices = Invoice.query.filter(
        Invoice.created_at.between(start_date, end_date)).all()
    
    total_sales = sum(inv.subtotal for inv in invoices)
    total_cgst = sum(inv.cgst_amount for inv in invoices)
    total_sgst = sum(inv.sgst_amount for inv in invoices)
    total_igst = sum(inv.igst_amount for inv in invoices)
    total_gst = total_cgst + total_sgst + total_igst
    
    return render_template('reports/gst_summary.html',
                         form=form,
                         start_date=start_date.date(),
                         end_date=end_date.date(),
                         invoices=invoices,
                         total_sales=total_sales,
                         total_cgst=total_cgst,
                         total_sgst=total_sgst,
                         total_igst=total_igst,
                         total_gst=total_gst)

# ============ INVOICE PDF GENERATION ============
@bp.route('/invoice/<int:invoice_id>/pdf')
def generate_invoice_pdf(invoice_id):
    """Generate PDF invoice"""
    invoice = Invoice.query.get_or_404(invoice_id)
    customer = invoice.customer
    
    # Calculate payment summary
    invoice_total = invoice.total_amount
    new_balance_due = customer.balance
    previous_balance = new_balance_due - invoice_total
    
    # Get company details (would come from settings in full system)
    company_info = {
        'name': 'Your Company Name',
        'gstin': 'Your GSTIN',
        'address': 'Your Complete Address',
        'phone': 'Your Phone Number',
        'email': 'your@email.com'
    }
    
    rendered_html = render_template('pdf/invoice_template.html',
                                  invoice=invoice,
                                  customer=customer,
                                  company_info=company_info,
                                  previous_balance=previous_balance,
                                  new_balance_due=new_balance_due)
    
    pdf = HTML(string=rendered_html).write_pdf()
    
    return Response(pdf,
                   mimetype='application/pdf',
                   headers={'Content-Disposition': f'inline; filename=invoice_{invoice.invoice_number}.pdf'})

# ============ DELIVERY CHALLAN ============
@bp.route('/challan/new/<int:invoice_id>', methods=['GET', 'POST'])
def create_challan(invoice_id):
    """Create delivery challan for invoice"""
    invoice = Invoice.query.get_or_404(invoice_id)
    
    if request.method == 'POST':
        vehicle_number = request.form.get('vehicle_number')
        driver_name = request.form.get('driver_name')
        
        try:
            # Generate challan number
            last_challan = DeliveryChallan.query.order_by(DeliveryChallan.id.desc()).first()
            challan_number = f"DC-{(last_challan.id + 1) if last_challan else 1:05d}"
            
            challan = DeliveryChallan(
                challan_number=challan_number,
                customer_id=invoice.customer_id,
                invoice_id=invoice.id,
                vehicle_number=vehicle_number,
                driver_name=driver_name
            )
            db.session.add(challan)
            db.session.flush()
            
            # Copy invoice items to challan
            for item in invoice.items:
                challan_item = ChallanItem(
                    challan_id=challan.id,
                    product_id=item.product_id,
                    quantity=item.quantity
                )
                db.session.add(challan_item)
            
            db.session.commit()
            flash(f'Delivery Challan {challan_number} created!', 'success')
            return redirect(url_for('main.generate_challan_pdf', challan_id=challan.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating challan: {str(e)}', 'danger')
    
    return render_template('create_challan.html', invoice=invoice)

@bp.route('/challan/<int:challan_id>/pdf')
def generate_challan_pdf(challan_id):
    """Generate PDF delivery challan"""
    challan = DeliveryChallan.query.get_or_404(challan_id)
    
    company_info = {
        'name': 'Your Company Name',
        'address': 'Your Complete Address',
        'phone': 'Your Phone Number'
    }
    
    rendered_html = render_template('pdf/challan_template.html',
                                  challan=challan,
                                  company_info=company_info)
    
    pdf = HTML(string=rendered_html).write_pdf()
    
    return Response(pdf,
                   mimetype='application/pdf',
                   headers={'Content-Disposition': f'inline; filename=challan_{challan.challan_number}.pdf'})

# ============ PRICING TIERS ============
@bp.route('/settings/pricing-tiers', methods=['GET', 'POST'])
def pricing_tiers():
    """Manage pricing tiers"""
    form = PricingTierForm()
    
    if form.validate_on_submit():
        tier = PricingTier(
            name=form.name.data,
            discount_percentage=form.discount_percentage.data
        )
        db.session.add(tier)
        db.session.commit()
        flash(f'Pricing tier {form.name.data} created!', 'success')
        return redirect(url_for('main.pricing_tiers'))
    
    tiers = PricingTier.query.all()
    return render_template('pricing_tiers.html', form=form, tiers=tiers)

# ============ HELPER FUNCTIONS FOR ACCOUNTING ============
def create_invoice_journal_entry(invoice, subtotal):
    """Create double-entry journal for invoice"""
    try:
        ar_account = Account.query.filter_by(name='Accounts Receivable').first()
        sales_account = Account.query.filter_by(name='Sales Revenue').first()
        
        if ar_account and sales_account:
            journal = JournalEntry(
                description=f"Sale - Invoice {invoice.invoice_number}",
                related_document_id=invoice.id,
                document_type='Invoice'
            )
            db.session.add(journal)
            db.session.flush()
            
            # Debit AR, Credit Sales
            db.session.add(LedgerEntry(
                journal_id=journal.id,
                account_id=ar_account.id,
                debit=invoice.total_amount,
                credit=0
            ))
            db.session.add(LedgerEntry(
                journal_id=journal.id,
                account_id=sales_account.id,
                debit=0,
                credit=invoice.total_amount
            ))
    except Exception as e:
        print(f"Journal entry creation failed: {e}")

def create_payment_journal_entry(payment):
    """Create double-entry journal for payment"""
    try:
        cash_account = Account.query.filter_by(name='Cash').first()
        ar_account = Account.query.filter_by(name='Accounts Receivable').first()
        
        if cash_account and ar_account:
            journal = JournalEntry(
                description=f"Payment - {payment.payment_number}",
                related_document_id=payment.id,
                document_type='Payment'
            )
            db.session.add(journal)
            db.session.flush()
            
            # Debit Cash, Credit AR
            db.session.add(LedgerEntry(
                journal_id=journal.id,
                account_id=cash_account.id,
                debit=payment.amount,
                credit=0
            ))
            db.session.add(LedgerEntry(
                journal_id=journal.id,
                account_id=ar_account.id,
                debit=0,
                credit=payment.amount
            ))
    except Exception as e:
        print(f"Journal entry creation failed: {e}")

# ==========================================
#      NEW SERVICE & REPAIR SECTION (SMART ID)
# ==========================================

@bp.route('/service-dashboard', methods=['GET', 'POST'])
def service_dashboard():
    """The Separate 'Room' for Repair & Service Management"""
    today = date.today()
    search_form = SearchForm()
    
    # 1. Handle Search
    if search_form.validate_on_submit():
        query = search_form.search_query.data.strip()
        found_customers = ServiceCustomer.query.filter(
            (ServiceCustomer.phone.ilike(f'%{query}%')) | 
            (ServiceCustomer.name.ilike(f'%{query}%'))
        ).all()
        return render_template('service_search_results.html', customers=found_customers, query=query)
    
    # === LOGIC FIX: Get only the LATEST record for each customer ===
    
    # A. Subquery to find the latest job ID for each customer
    latest_jobs_subquery = db.session.query(
        func.max(ServiceRecord.id).label('max_id')
    ).group_by(ServiceRecord.service_customer_id).subquery()

    # B. Filter: Show if 6mo date OR 1yr date is within next 30 days
    alert_limit = today + timedelta(days=30)
    
    # UPDATED QUERY: We now look at due_date_6mo OR due_date_1yr
    upcoming_services = ServiceRecord.query.join(
        latest_jobs_subquery,
        ServiceRecord.id == latest_jobs_subquery.c.max_id
    ).filter(
        (ServiceRecord.due_date_6mo <= alert_limit) | 
        (ServiceRecord.due_date_1yr <= alert_limit)
    ).all()
    
    # 3. Recent Repairs List
    recent_repairs = ServiceRecord.query.order_by(ServiceRecord.service_date.desc()).limit(10).all()
    
    return render_template('dashboard_service.html',
                           search_form=search_form,
                           upcoming_services=upcoming_services,
                           recent_repairs=recent_repairs,
                           today=today,              # <--- ADD THIS
                           alert_limit=alert_limit)

# @bp.route('/service/add-customer', methods=['GET', 'POST'])
# def add_service_customer():
#     """Smart Add: Detects existing phone numbers to prevent duplicates"""
#     form = ServiceCustomerForm()
    
#     if form.validate_on_submit():
#         phone_number = form.phone.data.strip()
        
#         # === SMART LOGIC: Check uniqueness ===
#         existing_customer = ServiceCustomer.query.filter_by(phone=phone_number).first()
        
#         if existing_customer:
#             # If found, DO NOT create new. Redirect to existing profile.
#             flash(f'Found existing customer: {existing_customer.name}. Opening their file.', 'info')
#             return redirect(url_for('main.add_service_record', customer_id=existing_customer.id))
            
#         # If not found, Create New
#         new_customer = ServiceCustomer(
#             name=form.name.data,
#             phone=phone_number,
#             address=form.address.data
#         )
#         db.session.add(new_customer)
#         db.session.commit()
#         flash(f'New Service Customer {new_customer.name} added!', 'success')
#         return redirect(url_for('main.add_service_record', customer_id=new_customer.id))
        
#     return render_template('add_service_customer.html', form=form)

# In erp/routes.py

@bp.route('/service/new', methods=['GET', 'POST'])
def add_service_record():
    form = UnifiedServiceForm()
    
    # Pre-fill Date with Today (so the user doesn't have to pick if it's today)
    if request.method == 'GET':
        form.service_date.data = date.today()
        
        # If we clicked "Call" or "Book" on a specific customer, pre-fill their info
        if request.args.get('customer_id'):
            existing = ServiceCustomer.query.get(int(request.args.get('customer_id')))
            if existing:
                form.customer_phone.data = existing.phone
                form.customer_name.data = existing.name
                form.customer_address.data = existing.address

    if form.validate_on_submit():
        # 1. Get the Phone Number (The Unique Key)
        phone_input = form.customer_phone.data.strip()
        
        # 2. DATABASE CHECK: Does this person exist?
        customer = ServiceCustomer.query.filter_by(phone=phone_input).first()
        
        if customer:
            # === PATH A: EXISTING CUSTOMER ===
            # The phone number matches an existing ID.
            # We LINK this new job to that EXISTING ID.
            flash(f'Welcome back! Adding service to existing history for {customer.name}.', 'info')
            
            # Optional: Update address if they moved
            customer.address = form.customer_address.data
            db.session.commit()
            
        else:
            # === PATH B: NEW CUSTOMER ===
            # Phone number is new. Create a BRAND NEW Profile ID.
            customer = ServiceCustomer(
                name=form.customer_name.data,
                phone=phone_input,
                address=form.customer_address.data
            )
            db.session.add(customer)
            db.session.commit() # Commit now to generate the new ID
            flash(f'New Customer Profile created for {customer.name}!', 'success')

        # 3. CREATE SERVICE RECORD
        # Now we have a 'customer.id' (either old or new). We attach the job to it.
        
        # Calculate Next Due Date based on the SELECTED Service Date
        job_date = form.service_date.data
        # months = int(form.next_service_due.data)
        # next_due = job_date + timedelta(days=months*30)

        # === NEW LOGIC: Auto-calculate 6 months and 1 year ===
        date_6mo = job_date + timedelta(days=180)           # <--- NEW
        date_1yr = job_date + timedelta(days=365)           # <--- NEW
        
        total = form.service_charge.data + form.parts_cost.data
        
        service = ServiceRecord(
            service_customer_id=customer.id, # <--- The Magic Link
            service_date=job_date,
            serviceman_name=form.serviceman_name.data,
            issue_reported=form.issue_reported.data,
            action_taken=form.action_taken.data,
            service_charge=form.service_charge.data,
            parts_cost=form.parts_cost.data,
            total_cost=total,
            # next_service_date=next_due
            due_date_6mo=date_6mo,                          # <--- NEW
            due_date_1yr=date_1yr                           # <--- NEW
        )
        
        db.session.add(service)
        db.session.commit()
        
        return redirect(url_for('main.service_dashboard'))
        
    return render_template('add_service_unified.html', form=form)

@bp.route('/service/history/<int:customer_id>')
def customer_service_history(customer_id):
    """View complete repair history for a specific ServiceCustomer"""
    customer = ServiceCustomer.query.get_or_404(customer_id)
    # Fetch all records for this unique phone number ID
    services = ServiceRecord.query.filter_by(service_customer_id=customer_id).order_by(ServiceRecord.service_date.desc()).all()
    return render_template('service_history.html', customer=customer, services=services)



@bp.route('/service/book-appointment', methods=['GET', 'POST'])
def book_appointment():
    form = BookingForm()
    
    # === NEW: Pre-fill logic starts here ===
    if request.method == 'GET':
        form.scheduled_date.data = date.today()
        
        # Check if we clicked "Book Now" from the dashboard
        customer_id = request.args.get('customer_id')
        if customer_id:
            customer = ServiceCustomer.query.get(customer_id)
            if customer:
                # Fill the form with their data automatically
                form.customer_name.data = customer.name
                form.customer_phone.data = customer.phone
                form.address.data = customer.address
    # =======================================

    if form.validate_on_submit():
        booking = ServiceBooking(
            customer_name=form.customer_name.data,
            customer_phone=form.customer_phone.data,
            address=form.address.data,
            scheduled_date=form.scheduled_date.data,
            scheduled_time=form.scheduled_time.data,
            issue_reported=form.issue_reported.data,
            status='Pending'
        )
        db.session.add(booking)
        db.session.commit()
        flash('Appointment Booked Successfully!', 'success')
        return redirect(url_for('main.list_bookings'))
        
    return render_template('book_appointment.html', form=form)

# 2. LIST ALL PENDING BOOKINGS
@bp.route('/service/bookings')
def list_bookings():
    # Show Pending jobs first, ordered by date
    bookings = ServiceBooking.query.filter_by(status='Pending').order_by(ServiceBooking.scheduled_date.asc()).all()
    return render_template('bookings_list.html', bookings=bookings)

# 3. COMPLETE A JOB (The "Magic" Step)
@bp.route('/service/complete-booking/<int:booking_id>', methods=['GET', 'POST'])
def complete_booking(booking_id):
    booking = ServiceBooking.query.get_or_404(booking_id)
    form = UnifiedServiceForm()

    # PRE-FILL Form with Booking Data
    if request.method == 'GET':
        form.customer_phone.data = booking.customer_phone
        form.customer_name.data = booking.customer_name
        form.customer_address.data = booking.address
        form.issue_reported.data = booking.issue_reported
        form.service_date.data = date.today()

    if form.validate_on_submit():
        # A. Handle Customer (Find or Create)
        phone_input = form.customer_phone.data.strip()
        customer = ServiceCustomer.query.filter_by(phone=phone_input).first()
        
        if not customer:
            customer = ServiceCustomer(
                name=form.customer_name.data,
                phone=phone_input,
                address=form.customer_address.data
            )
            db.session.add(customer)
            db.session.commit()

        # B. Create the Permanent Service Record
        # months = int(form.next_service_due.data)
        # next_due = form.service_date.data + timedelta(days=months*30)
        job_date = form.service_date.data
        date_6mo = job_date + timedelta(days=180)           # <--- NEW
        date_1yr = job_date + timedelta(days=365)           # <--- NEW
        total = form.service_charge.data + form.parts_cost.data
        
        service = ServiceRecord(
            service_customer_id=customer.id,
            service_date=form.service_date.data,
            serviceman_name=form.serviceman_name.data,
            issue_reported=form.issue_reported.data,
            action_taken=form.action_taken.data,
            service_charge=form.service_charge.data,
            parts_cost=form.parts_cost.data,
            total_cost=total,
            # next_service_date=next_due

            due_date_6mo=date_6mo,                          # <--- NEW
            due_date_1yr=date_1yr                           # <--- NEW
        )
        db.session.add(service)
        
        # C. Mark Booking as Completed
        booking.status = 'Completed'
        
        db.session.commit()
        flash('Job Completed and History Updated!', 'success')
        return redirect(url_for('main.service_dashboard'))

    return render_template('add_service_unified.html', form=form, title="Complete Job")

@bp.route('/service/reminders')
def service_reminders():
    """Show separate lists for 6-month and 1-year dues"""
    today = date.today()
    alert_window = today + timedelta(days=30) # Show anyone due in next 30 days
    
    # 1. Fetch 6-Month Dues (Due soon OR Overdue)
    # We check if due_date_6mo is BEFORE the alert window AND not too old (optional)
    list_6mo = ServiceRecord.query.filter(
        ServiceRecord.due_date_6mo <= alert_window,
        ServiceRecord.due_date_6mo >= (today - timedelta(days=60)) # Don't show extremely old ones
    ).order_by(ServiceRecord.due_date_6mo.asc()).all()
    
    # 2. Fetch 1-Year Dues
    list_1yr = ServiceRecord.query.filter(
        ServiceRecord.due_date_1yr <= alert_window,
        ServiceRecord.due_date_1yr >= (today - timedelta(days=60))
    ).order_by(ServiceRecord.due_date_1yr.asc()).all()

    return render_template('service_reminders.html', list_6mo=list_6mo, list_1yr=list_1yr)