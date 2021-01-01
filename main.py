from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from paper_trader.routers import trades, watchlists, users, searches

app = FastAPI()

app.include_router(users.router)
app.include_router(trades.router)
app.include_router(watchlists.router)
app.include_router(searches.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)