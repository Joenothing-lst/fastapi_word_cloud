from fastapi import FastAPI
from app.middleware import middleware_init

# from app.core import auth
from app.routes import word_cloud

app = FastAPI()

# Set all CORS enabled origins
middleware_init(app)

app.include_router(word_cloud.router)


@app.get("/")
def home():
    return "Hello, World!"
