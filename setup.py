#!/usr/bin/env python
"""
Setup script to create a test user and sample data for the Diving Administration System
Run this once to initialize the database with a test account
"""

from app import app, db, User, DiveSite
from datetime import datetime

def setup_database():
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database tables created")
        
        # Check if test user already exists
        test_user = User.query.filter_by(username='admin').first()
        if test_user:
            print("⚠ Test user 'admin' already exists")
            return
        
        # Create test user
        user = User(
            username='admin',
            email='admin@diving.local',
            role='admin'
        )
        user.set_password('admin123')
        db.session.add(user)
        
        # Create test user 2
        user2 = User(
            username='diver',
            email='diver@diving.local',
            role='user'
        )
        user2.set_password('diver123')
        db.session.add(user2)
        
        # Add sample dive sites
        sites = [
            DiveSite(
                name='Great Barrier Reef',
                location='Australia',
                depth_min=5,
                depth_max=40,
                description='World\'s largest coral reef system with incredible biodiversity',
                difficulty_level='Intermediate',
                water_temperature=26,
                visibility='20m+'
            ),
            DiveSite(
                name='Blue Hole',
                location='Belize',
                depth_min=20,
                depth_max=125,
                description='Famous underwater sinkhole with dramatic walls and unique formations',
                difficulty_level='Advanced',
                water_temperature=28,
                visibility='15-25m'
            ),
            DiveSite(
                name='Silfra Rift',
                location='Iceland',
                depth_min=2,
                depth_max=65,
                description='Continental rift with crystal clear water and unique geology',
                difficulty_level='Beginner',
                water_temperature=2,
                visibility='100m+'
            ),
            DiveSite(
                name='Palau Peleliu Corner',
                location='Palau',
                depth_min=30,
                depth_max=80,
                description='Drift dive with strong currents and abundant marine life',
                difficulty_level='Advanced',
                water_temperature=29,
                visibility='30m+'
            ),
        ]
        
        for site in sites:
            db.session.add(site)
        
        db.session.commit()
        
        print("\n✅ Database initialized successfully!")
        print("\n📝 Test Accounts Created:")
        print("   Admin Account:")
        print("   - Username: admin")
        print("   - Password: admin123")
        print("\n   Regular Diver Account:")
        print("   - Username: diver")
        print("   - Password: diver123")
        print("\n🌊 Sample dive sites added: Great Barrier Reef, Blue Hole, Silfra Rift, Palau")
        print("\nYou can now login and start using the application!")

if __name__ == '__main__':
    setup_database()
