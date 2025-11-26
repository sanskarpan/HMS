"""
Database initialization script for the Hospital Management System.

This script:
1. Creates all database tables
2. Creates the admin user (programmatically as required)
3. Seeds default departments

Usage:
    python backend/init_db.py
    python backend/init_db.py --reset  # Reset database (development only)
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.app.models import db, User, Department
from backend.app.models.department import DEFAULT_DEPARTMENTS
from backend.config import Config


def init_database(reset=False):
    """
    Initialize the database with tables, admin user, and default data.

    Args:
        reset: If True, drop all tables before creating (development only)
    """
    app = create_app()

    with app.app_context():
        if reset:
            print("Dropping all tables...")
            db.drop_all()

        print("Creating database tables...")
        db.create_all()

        # Create admin user if not exists
        create_admin_user()

        # Seed default departments
        seed_departments()

        print("\nDatabase initialization complete!")
        print_summary()


def create_admin_user():
    """Create the admin user if it doesn't exist."""
    admin = User.find_by_username(Config.ADMIN_USERNAME)

    if admin:
        print(f"Admin user '{Config.ADMIN_USERNAME}' already exists.")
        return admin

    print("Creating admin user...")
    admin = User(
        username=Config.ADMIN_USERNAME,
        email=Config.ADMIN_EMAIL,
        password=Config.ADMIN_PASSWORD,
        role='admin'
    )
    admin.is_active = True

    db.session.add(admin)
    db.session.commit()

    print(f"Admin user created:")
    print(f"  Username: {Config.ADMIN_USERNAME}")
    print(f"  Email: {Config.ADMIN_EMAIL}")
    print(f"  Password: {Config.ADMIN_PASSWORD}")

    return admin


def seed_departments():
    """Seed default departments if they don't exist."""
    print("Seeding departments...")

    created_count = 0
    for dept_data in DEFAULT_DEPARTMENTS:
        existing = Department.find_by_name(dept_data['name'])
        if not existing:
            dept = Department(
                name=dept_data['name'],
                description=dept_data['description']
            )
            db.session.add(dept)
            created_count += 1

    db.session.commit()

    if created_count > 0:
        print(f"Created {created_count} new departments.")
    else:
        print("All departments already exist.")


def print_summary():
    """Print summary of database contents."""
    user_count = User.query.count()
    dept_count = Department.query.count()

    print("\n--- Database Summary ---")
    print(f"Users: {user_count}")
    print(f"Departments: {dept_count}")

    # List departments
    print("\nDepartments:")
    for dept in Department.query.order_by(Department.name).all():
        print(f"  - {dept.name}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Initialize the Hospital Management System database')
    parser.add_argument('--reset', action='store_true',
                        help='Reset database (drops all tables - development only)')

    args = parser.parse_args()

    if args.reset:
        confirm = input("WARNING: This will delete all data. Type 'yes' to confirm: ")
        if confirm.lower() != 'yes':
            print("Aborted.")
            sys.exit(0)

    init_database(reset=args.reset)
