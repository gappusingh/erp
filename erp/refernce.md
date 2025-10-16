# ⚡ Quick Reference Guide

## 📌 Essential Commands

### Setup Commands
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate          # Linux/macOS
venv\Scripts\activate              # Windows

# Install dependencies
pip install -r requirements.txt

# Set Flask app
export FLASK_APP=app.py           # Linux/macOS
set FLASK_APP=app.py              # Windows

# Initialize database
flask db init
flask db migrate -m "message"
flask db upgrade

# Load sample data
flask init-db

# Run application
flask run

# Run on different port
flask run --port 5001

# Run in debug mode
flask run --debug
```

### Database Commands
```bash
# Create new migration
flask db migrate -m "description"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade

# View migration history
flask db history

# Reset database (CAREFUL!)
rm instance/distro.db
flask db upgrade
```

---

## 🔑 Key Features & URLs

### Main Navigation

| Feature | URL | Description |
|---------|-----|-------------|
| Dashboard | `/` | Main dashboard with shop cards |
| Add Product | `/add/product` | Add new product to inventory |
| Products List | `/products` | View all products |
| Add Customer | `/add/customer` | Add new customer/shop |
| Add Supplier | `/add/supplier` | Add new supplier |
| Suppliers List | `/suppliers` | View all suppliers |
| New Invoice | `/sales/invoice/new` | Create multi-item invoice |
| Record Payment | `/add/payment` | Record customer payment |
| New PO | `/purchasing/po/new` | Create purchase order |
| Pay Supplier | `/add/supplier-payment` | Pay supplier |
| Record Expense | `/add/expense` | Record business expense |
| Expenses List | `/expenses` | View all expenses |
| P&L Report | `/reports/profit-and-loss` | Profit & Loss statement |
| Balance Sheet | `/reports/balance-sheet` | Balance Sheet |
| GST Summary | `/reports/gst-summary` | GST filing report |
| Pricing Tiers | `/settings/pricing-tiers` | Manage pricing tiers |

### Dynamic URLs

| Feature | URL Pattern | Example |
|---------|-------------|---------|
| Customer Statement | `/customer/<id>/statement` | `/customer/1/statement` |
| Invoice PDF | `/invoice/<id>/pdf` | `/invoice/123/pdf` |
| Delivery Challan | `/challan/new/<invoice_id>` | `/challan/new/123` |
| Challan PDF | `/challan/<id>/pdf` | `/challan/45/pdf` |

---

## 💼 Business Workflows

### 1. Complete Sales Workflow

```
1. Add Product → Master Data → Add Product
2. Add Customer → Master Data → Add Customer
3. Create Invoice → Transactions → New Invoice
4. Select Products → Add to Cart → Choose Customer → Submit
5. System automatically:
   - Generates invoice number (INV-00001)
   - Reduces stock
   - Adds to customer balance
   - Creates PDF invoice
   - Updates accounting ledger
6. Record Payment → Transactions → Record Payment
7. View Statement → Dashboard → Customer Card → View Statement
```

### 2. Complete Purchase Workflow

```
1. Add Supplier → Master Data → Add Supplier
2. Create PO → Transactions → New Purchase Order
3. Select Supplier → Product → Quantity → Cost → Submit
4. System automatically:
   - Generates PO number (PO-00001)
   - Increases stock
   - Adds to supplier payable
5. Pay Supplier → Transactions → Pay Supplier
```

### 3. Daily Operations Workflow

```
Morning:
1. Check Dashboard → Today's collections, credit given, total due
2. Review customer balances
3. Check low stock items

During Day:
1. Create invoices as orders come
2. Record payments received
3. Generate delivery challans

End of Day:
1. Review daily collection vs credit
2. Check pending payments
3. Plan next day's deliveries
```

---

## 📊 Dashboard Metrics

### Top Metrics (Colored Cards)
- **Green Card**: Total Collection Today (payments received)
- **Yellow Card**: New Credit Given Today (invoices created)
- **Red Card**: Total Market Due (all customer balances)
- **Blue Card**: Supplier Payable (amount owed to suppliers)

### Customer Cards Features
Each customer card shows:
- **Billings Tab**: Last 10 invoices with amounts
- **Payments Tab**: Last 10 payments with modes
- **Stats Tab**: Orders per month for last 6 months
- **Actions**: New Order, Payment, View Statement buttons

---

## 🧮 Invoice & GST Calculation

### GST Calculation (Default: 18%)
```
Subtotal: ₹1000
CGST (9%): ₹90
SGST (9%): ₹90
Total: ₹1180
```

### Invoice Flow
1. Add items to cart → Calculates subtotal
2. Select customer → Applies pricing tier (if any)
3. Calculate GST → CGST + SGST (intrastate) or IGST (interstate)
4. Generate PDF → Professional invoice with terms
5. Update balances → Customer balance increases

### Payment Flow
1. Select customer → Shows current balance
2. Enter amount → Validates amount
3. Record payment → Customer balance decreases
4. Create receipt → Payment history updated

---

## 📈 Financial Reports

### Profit & Loss Statement
```
Income:
  Sales Revenue                 ₹100,000

Cost of Goods Sold:
  Cost of Products Sold         ₹60,000
                                --------
Gross Profit                    ₹40,000

Operating Expenses:
  Business Expenses             ₹15,000
                                --------
Net Profit                      ₹25,000
```

### Balance Sheet
```
ASSETS                          LIABILITIES & EQUITY
Cash & Bank         ₹10,000     Accounts Payable    ₹30,000
Accounts Receivable ₹80,000     Owner's Equity      ₹130,000
Inventory           ₹70,000     
                    -------                         -------
Total Assets        ₹160,000    Total L+E           ₹160,000
```

---

## 🎨 Customization Points

### Company Information
**File**: `erp/routes.py`  
**Function**: `generate_invoice_pdf`, `generate_challan_pdf`
```python
company_info = {
    'name': 'Your Company Name',
    'gstin': 'Your GSTIN',
    'address': 'Your Address',
    'phone': 'Your Phone',
    'email': 'your@email.com'
}
```

### GST Rate
**File**: `erp/routes.py`  
**Function**: `create_invoice`
```python
gst_rate = 18  # Change to 5, 12, 18, or 28
```

### Currency Symbol
**Files**: All HTML templates
```html
<!-- Change ₹ to $ or other currency -->
₹{{ "%.2f"|format(amount) }}
```

### Invoice Numbering
**File**: `erp/routes.py`
```python
invoice_number = f"INV-{(last_invoice.id + 1):05d}"
# Change INV to your prefix, :05d to desired padding
```

---

## 🔐 Security Checklist

### Before Production

```python
# 1. Change SECRET_KEY in erp/__init__.py
app.config['SECRET_KEY'] = 'generate-secure-random-key-here'

# 2. Use environment variables
import os
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# 3. Switch to PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

# 4. Disable debug mode
app.config['DEBUG'] = False

# 5. Add user authentication
# Install Flask-Login and implement login system
```

---

## 🐛 Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "No module named 'erp'" | Wrong directory | `cd erp_project` |
| "Unable to locate configuration file" | Flask app not set | `export FLASK_APP=app.py` |
| "Table doesn't exist" | Database not initialized | `flask db upgrade` |
| "Port 5000 in use" | Port occupied | `flask run --port 5001` |
| WeasyPrint error | Missing dependencies | Install GTK3/Cairo |
| "CSRF token missing" | Form security issue | Check SECRET_KEY is set |
| "Insufficient stock" | Stock validation | Check product.stock >= quantity |
| Import errors | Dependencies not installed | `pip install -r requirements.txt` |

---

## 📝 Sample Data Included

When you run `flask init-db`, these are created:

### Pricing Tiers
- Retail (0% discount)
- Wholesale (10% discount)
- Distributor (15% discount)

### Sample Products
- LED Bulb 9W (SKU: LED-9W, Stock: 100)
- LED Bulb 12W (SKU: LED-12W, Stock: 80)
- Fan Regulator (SKU: FAN-REG, Stock: 50)
- Switch 1-Way (SKU: SW-1W, Stock: 200)

### Chart of Accounts
- Cash (Asset)
- Accounts Receivable (Asset)
- Inventory (Asset)
- Accounts Payable (Liability)
- Owner Equity (Equity)
- Sales Revenue (Revenue)
- Cost of Goods Sold (Expense)
- Operating Expenses (Expense)

---

## 📞 Support Resources

### Official Documentation
- Flask: https://flask.palletsprojects.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- WTForms: https://wtforms.readthedocs.io/
- WeasyPrint: https://doc.courtbouillon.org/weasyprint/
- Bootstrap: https://getbootstrap.com/

### Useful Flask Extensions
- Flask-Login: User authentication
- Flask-Mail: Email notifications
- Flask-Caching: Performance optimization
- Flask-Admin: Auto-generated admin panel

---

## 🚀 Performance Tips

1. **Use PostgreSQL in production** (faster than SQLite)
2. **Enable query caching** for reports
3. **Optimize images** in PDFs (if using logos)
4. **Add database indexes** on frequently queried fields
5. **Use pagination** for large data lists
6. **Enable GZIP compression** in production
7. **Use CDN** for Bootstrap/CSS files

---

## 📦 Backup Strategy

### Daily Backup
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
cp instance/distro.db backups/distro_$DATE.db
# Keep only last 30 days
find backups/ -name "distro_*.db" -mtime +30 -delete
```

### Restore Backup
```bash
cp backups/distro_YYYYMMDD_HHMMSS.db instance/distro.db
flask run
```

---

**Quick Reference Complete!** 🎉

Print this guide for daily reference while using the ERP system.