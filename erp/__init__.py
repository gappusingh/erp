import os
import click
from flask import Flask
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from sqlalchemy import inspect

# 1. Create extension instances
# These are created outside the factory so they are globally accessible.
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'warning'

def create_app():
    """Application factory pattern"""
    # 2. Create the Flask app instance
    app = Flask(__name__, instance_relative_config=True)
    
    # 3. Configure the app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(app.instance_path, 'distro.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Ensure the instance folder exists for the SQLite database
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # 4. Initialize extensions with the app
    # This connects the db and migrate objects to your specific app instance.
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))
    
    # 5. Register blueprints and import models
    from . import routes
    app.register_blueprint(routes.bp)
    
    # This line is crucial for Flask-Migrate to detect your models.
    from . import models

    # 6. Add custom command-line interface (CLI) commands
    @app.cli.command("seed-db")
    @with_appcontext
    def seed_db_command():
        """Creates the default chart of accounts."""
        if create_default_accounts():
            click.echo("Successfully seeded the database with default accounts.")
    
    # 7. Return the fully configured app
    from datetime import datetime
    @app.context_processor
    def inject_now():
        return dict(now=datetime.now)


    return app

def create_default_accounts():
    """
    Creates default chart of accounts if they don't exist.
    Returns True on success, False on failure.
    """
    # Safety check: Ensure the 'account' table exists before trying to use it.
    inspector = inspect(db.engine)
    if not inspector.has_table("account"):
        click.echo("Error: 'account' table not found. Please run 'flask db upgrade' first.")
        return False

    from .models import Account
    
    default_accounts = [
        {'code': '1000', 'name': 'Cash', 'account_type': 'Asset'},
        {'code': '1100', 'name': 'Accounts Receivable', 'account_type': 'Asset'},
        {'code': '1200', 'name': 'Inventory', 'account_type': 'Asset'},
        {'code': '2000', 'name': 'Accounts Payable', 'account_type': 'Liability'},
        {'code': '3000', 'name': 'Owner Equity', 'account_type': 'Equity'},
        {'code': '4000', 'name': 'Sales Revenue', 'account_type': 'Revenue'},
        {'code': '5000', 'name': 'Cost of Goods Sold', 'account_type': 'Expense'},
        {'code': '6000', 'name': 'Operating Expenses', 'account_type': 'Expense'}
    ]
    
    try:
        for acc_data in default_accounts:
            existing = Account.query.filter_by(code=acc_data['code']).first()
            if not existing:
                account = Account(**acc_data)
                db.session.add(account)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        click.echo(f"An error occurred while seeding accounts: {e}")
        return False
    
    return True