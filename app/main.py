from fastapi import FastAPI, Depends
from app.dependencies import verify_api_key
from app.parser.router import router as parse_router

app = FastAPI(title="Parser")

app.include_router(parse_router, dependencies=[Depends(verify_api_key)])
