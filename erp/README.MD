# 🏭 Distribution ERP Management System

A complete, industry-level ERP system for electrical/hardware distribution businesses built with Flask.

## 📋 Table of Contents
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Quick Start Guide](#quick-start-guide)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)

## ✨ Features

### 📊 Sales & Customer Management
- ✅ Multi-item invoice generation with automatic stock deduction
- ✅ Customer credit tracking and balance management
- ✅ Daily collection and credit given tracking
- ✅ Shop-wise dashboard with complete transaction history
- ✅ Customer account statements with running balance
- ✅ Payment recording with multiple payment modes

### 📦 Inventory Management
- ✅ Product catalog with SKU and HSN codes
- ✅ Real-time stock tracking
- ✅ Low stock alerts
- ✅ Stock value calculations
- ✅ Product search and filtering

### 🏢 Supplier & Purchase Management
- ✅ Supplier management
- ✅ Purchase order creation
- ✅ Accounts payable tracking
- ✅ Supplier payment recording

### 💰 Financial Management
- ✅ GST calculation (CGST/SGST/IGST)
- ✅ Expense tracking by category
- ✅ Profit & Loss statements
- ✅ Balance Sheet generation
- ✅ GST summary reports for filing
- ✅ Double-entry accounting foundation

### 📄 Document Generation
- ✅ Professional PDF invoices
- ✅ Delivery challan with vehicle details
- ✅ Print-ready layouts

### 🎯 Advanced Features
- ✅ Pricing tiers (Wholesale, Retail, Distributor)
- ✅ Daily financial dashboard
- ✅ Customer-wise analytics
- ✅ Monthly order tracking
- ✅ Payment reminders (balance tracking)

## 🛠️ Technology Stack

- **Backend**: Flask 3.0 (Python web framework)
- **Database**: SQLAlchemy ORM with SQLite (upgradeable to PostgreSQL)
- **Forms**: Flask-WTF & WTForms
- **PDF Generation**: WeasyPrint
- **Frontend**: Bootstrap 5.3, Bootstrap Icons
- **Database Migrations**: Flask-Migrate

## 📥 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning)

### Step 1: Create Project Directory
```bash
mkdir erp_project
cd erp_project
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### Step 3: Create Project Structure
```bash
# Create directories
mkdir erp
mkdir erp/templates
mkdir erp/templates/pdf
mkdir erp/templates/reports
mkdir instance

# Create __init__.py files
# Windows:
type nul > erp/__init__.py

# macOS/Linux:
touch erp/__init__.py
```

### Step 4: Install Dependencies

Create `requirements.txt`:
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
Flask-WTF==1.2.1
WTForms==3.1.1
python-dotenv==1.0.0
WeasyPrint==60.1
SQLAlchemy==2.0.23
```

Install:
```bash
pip install -r requirements.txt
```

### Step 5: WeasyPrint System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

**macOS:**
```bash
brew install python cairo pango gdk-pixbuf libffi
```

**Windows:**
Download GTK3 runtime from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

### Step 6: Copy All Code Files

Copy the provided code into these files:
```
erp_project/
├── app.py
├── requirements.txt
├── erp/
│   ├── __init__.py
│   ├── models.py
│   ├── forms.py
│   ├── routes.py
│   └── templates/
│       ├── base.html
│       ├── dashboard.html
│       ├── customer_statement.html
│       ├── create_invoice.html
│       ├── _form_renderer.html
│       ├── products_list.html
│       ├── suppliers_list.html
│       ├── expenses_list.html
│       ├── create_po.html
│       ├── create_challan.html
│       ├── pricing_tiers.html
│       ├── pdf/
│       │   ├── invoice_template.html
│       │   └── challan_template.html
│       └── reports/
│           ├── profit_and_loss.html
│           ├── balance_sheet.html
│           └── gst_summary.html
```

### Step 7: Initialize Database
```bash
# Set Flask app
# Windows:
set FLASK_APP=app.py

# macOS/Linux:
export FLASK_APP=app.py

# Initialize migrations
flask db init
flask db migrate -m "Initial database setup"
flask db upgrade

# Load sample data (optional)
flask init-db
```

### Step 8: Run the Application
```bash
flask run
```

Open your browser and navigate to: **http://127.0.0.1:5000**

## 📁 Project Structure

```
/erp_project/
├── app.py                      # Application entry point
├── requirements.txt            # Python dependencies
├── /instance/                  # Database folder (auto-created)
│   └── distro.db              # SQLite database
├── /migrations/               # Database migrations (auto-created)
├── /erp/                      # Main application package
│   ├── __init__.py           # App factory
│   ├── models.py             # Database models
│   ├── forms.py              # WTForms
│   ├── routes.py             # Business logic & routes
│   └── /templates/           # HTML templates
```

## 🚀 Quick Start Guide

### First-Time Setup

1. **Create Pricing Tiers** (Optional)
   - Go to: Settings → Pricing Tiers
   - Add: Retail (0%), Wholesale (10%), Distributor (15%)

2. **Add Products**
   - Go to: Master Data → Add Product
   - Enter: Name, SKU, HSN Code, Stock, Prices

3. **Add Customers**
   - Go to: Master Data → Add Customer
   - Enter: Shop name, GSTIN, Address, Phone

4. **Add Suppliers**
   - Go to: Master Data → Add Supplier
   - Enter: Name, GSTIN, Contact details

### Creating Your First Invoice

1. Click: Transactions → New Invoice
2. Add products to cart from right panel
3. Select customer
4. Click "Create Invoice & Generate PDF"
5. System automatically:
   - Deducts stock
   - Updates customer balance
   - Generates PDF invoice

### Recording a Payment

1. Click: Transactions → Record Payment
2. Select customer
3. Enter amount and payment mode
4. Submit
5. Customer balance automatically updated

### Viewing Reports

- **Daily Dashboard**: Home page shows today's collections, credit given, total due
- **P&L Statement**: Reports → Profit & Loss
- **Balance Sheet**: Reports → Balance Sheet
- **GST Summary**: Reports → GST Summary

## 💡 Usage

### Invoice Features
- Multi-item invoices
- Automatic GST calculation (18% default)
- Real-time stock validation
- Customer balance tracking
- PDF generation with company branding

### Payment Tracking
- Multiple payment modes (Cash, Cheque, Bank Transfer, UPI)
- Automatic balance adjustment
- Payment history per customer
- Daily collection reports

### Customer Statements
- Complete transaction history
- Running balance calculation
- Date-wise sorted
- Print-ready format

### Inventory Management
- Real-time stock levels
- Stock value calculations
- Low stock indicators
- Purchase order integration

### Financial Reports
- **Profit & Loss**: Revenue - COGS - Expenses = Net Profit
- **Balance Sheet**: Assets = Liabilities + Equity
- **GST Summary**: CGST, SGST, IGST calculations

## 🎨 Customization

### Change Company Information

Edit in `erp/routes.py`, function `generate_invoice_pdf`:
```python
company_info = {
    'name': 'Your Company Name',
    'gstin': 'Your GSTIN Number',
    'address': 'Your Complete Address',
    'phone': 'Your Phone Number',
    'email': 'your@email.com'
}
```

### Modify GST Rates

Edit in `erp/routes.py`, function `create_invoice`:
```python
gst_rate = 18  # Change to 5, 12, 18, or 28
```

### Change Database to PostgreSQL

Edit in `erp/__init__.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/database_name'
```

### Customize Invoice Template

Edit `erp/templates/pdf/invoice_template.html` to change:
- Layout and styling
- Company logo (add img tag)
- Terms and conditions
- Additional fields

## 🔧 Troubleshooting

### Database Errors
```bash
# Reset database
flask db downgrade
flask db upgrade

# Or delete database and recreate
rm instance/distro.db
flask db upgrade
flask init-db
```

### Port Already in Use
```bash
flask run --port 5001
```

### WeasyPrint Errors
- Ensure GTK3 runtime is installed (Windows)
- Install system dependencies (Linux/macOS)
- Check Python version compatibility

### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### "No module named erp"
```bash
# Ensure you're in the correct directory
cd erp_project

# Set Flask app
export FLASK_APP=app.py  # or set FLASK_APP=app.py on Windows
```

## 🔐 Security Recommendations

1. **Change SECRET_KEY** in production:
```python
app.config['SECRET_KEY'] = 'your-secure-random-key-here'
```

2. **Use Environment Variables**:
```bash
# Create .env file
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
```

3. **Enable HTTPS** in production

4. **Add User Authentication**:
- Implement Flask-Login
- Add role-based access control
- Secure admin routes

5. **Regular Backups**:
```bash
# Backup database
cp instance/distro.db backup/distro_$(date +%Y%m%d).db
```

## 📈 Future Enhancements

- [ ] User authentication & authorization
- [ ] Multi-warehouse support
- [ ] Barcode scanning
- [ ] SMS/Email notifications
- [ ] Payment gateway integration
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Export to Excel/CSV
- [ ] Automated backup system
- [ ] Multi-currency support

## 📞 Support

For issues or questions:
- Flask Documentation: https://flask.palletsprojects.com/
- SQLAlchemy Documentation: https://www.sqlalchemy.org/
- Bootstrap Documentation: https://getbootstrap.com/

## 📄 License

This project is provided as-is for educational and commercial use.

---

**Built with ❤️ for distribution businesses** 🏭

**Version**: 1.0.0  
**Last Updated**: 2025