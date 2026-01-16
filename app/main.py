from fastapi import FastAPI
from app.core.db import Base, engine
from dotenv import load_dotenv
from app.api.v1.posts.router import router as posts_router
from app.api.v1.auth.router import router as auth_router


load_dotenv()

def create_app() -> FastAPI:
    app = FastAPI(title='My Mini Blog')
    Base.metadata.create_all(bind=engine) # Només s'usa en desenvolupament. En producció caldrà fer migracions
    app.include_router(auth_router, prefix='/api/v1')
    app.include_router(posts_router)

    @app.get('/')
    def home():
        return {'message': 'Benvinguts al Mini Blog by Eduard Farinyes'}
    return app

app = create_app()











