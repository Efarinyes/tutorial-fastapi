from fastapi import FastAPI
from app.core.db import Base, engine
from app.api.v1.posts.router import router as posts_router
from dotenv import load_dotenv

load_dotenv()



def create_app() -> FastAPI:
    app = FastAPI(title='My Mini Blog')
    Base.metadata.create_all(bind=engine) # Només s'usa en desenvolupament. En producció caldrà fer migracions
    app.include_router(posts_router)

    @app.get('/')
    def home():
        return {'message': 'Benvinguts al Mini Blog by Eduard Farinyes'}
    return app

app = create_app()











