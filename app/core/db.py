
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

# DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///blog.db')
engine_kwargs = {}
if DATABASE_URL.startswith('sqlite'):
    engine_kwargs['connect_args'] = {'check_same_thread': False}
# if not DATABASE_URL:
#     raise RuntimeError("DATABASE_URL No esta definida. Configura PostgreSQL")
engine = create_engine(DATABASE_URL, echo=True, future=True, **engine_kwargs)
print('DATABASE_URL:', DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()