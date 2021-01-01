from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from paper_trader import crud

router = APIRouter()

@router.get('/search/query')
def search_stocks(q):
    try:
        securities_list = []
        search_results = crud.searches.search(q)
        for tuple in search_results:
            securities_list.append({
                'symbol': tuple[0],
                'company': tuple[1],
                'price': float(tuple[2]),
                'exchange': tuple[3]
            })
        return JSONResponse(content=securities_list)
    except:
        raise HTTPException(404, detail='Search failed')