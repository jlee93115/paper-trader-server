import requests
import json
import re

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from paper_trader.routers import securities, watchlist, user

app = FastAPI()

app.include_router(user.router)
app.include_router(securities.router)
app.include_router(watchlist.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)