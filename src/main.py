from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import telegram
from src.configuration.app_lifespan import lifespan


def fastapi_application():

    app = FastAPI(
        title="AI Telegram App",
        lifespan=lifespan
    )

    # Add CORS middleware to allow requests from any origin
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods
        allow_headers=["*"],  # Allow all headers
    )

    app.include_router(telegram.router)

    return app


app = fastapi_application()
