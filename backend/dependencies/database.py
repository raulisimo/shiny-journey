# Dependency for database session
def get_db():
    from config.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
