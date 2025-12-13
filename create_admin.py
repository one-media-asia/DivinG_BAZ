from app import app, db, User

with app.app_context():
    # Check if admin already exists
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print("Admin user already exists")
    else:
        # Create admin user
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created: username='admin', password='admin'")
