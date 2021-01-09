from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from paper_trader.routers import trades, watchlists, users, searches
from paper_trader import crud

app = FastAPI()

app.include_router(users.router)
app.include_router(trades.router)
app.include_router(watchlists.router)
app.include_router(searches.router)

origins = [
    'http://127.0.0.1:8080'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Revoke all tokens on server startup
crud.authentication.revoke_refresh_tokens('%')