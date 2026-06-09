from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import (
    napkin_order_route,
    auth_route
)
import logging
import sys
import asyncio
from fastapi.responses import JSONResponse
import json


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)



app = FastAPI(
    title="Rutx AI Services",
    description="A collection of AI services for Rutx",
    version="1.0.0",
)

# CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

routes = [
    napkin_order_route.router,
    auth_route.router

]

# Include all routes
for route in routes:
    app.include_router(route)
