from app.db_service import init_database

if __name__ == '__main__':
    init_database()
    print("Database initialized successfully (admin user verified: admin / admin123).")

