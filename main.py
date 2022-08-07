#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/8/6 9:23
# @Author  : liyun
# @desc    :
import uvicorn
from fastapi import FastAPI, status
from typing import List
from ncbi_app.schemas import NumPubOfYear, PubmedHist
from ncbi_app.ncbi_api import download_trend, fetch_latest_pubs, get_affiliations
from settings import settings
from starlette.requests import Request
from fastapi.responses import JSONResponse
from starlette.middleware.errors import ServerErrorMiddleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp


app = FastAPI(title="NCBI API FastAPI Application",
              description="FastAPI Application that discovers the trend of NCBI publications",
              version="1.0.0", )


# TODO: remove the following usage when the CROS bug is fixed
async def global_execution_handler(request: Request, exc: Exception) -> ASGIApp:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content="Unknown Error",
    )
app.add_middleware(
    ServerErrorMiddleware,
    handler=global_execution_handler,
)


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/trend', response_model=List[NumPubOfYear])
async def get_trend(disease: str, min_yr: int, max_yr: int):
    """
    Return the number of publications mentioning the given disease over time
    :param disease: the name of the disease
    :param min_yr: start of the year span
    :param max_yr: end of the year span
    :return:
    """
    return await download_trend(disease, min_yr, max_yr)


@app.get('/latest_pubs', response_model=PubmedHist)
async def get_latest_pubs(disease: str):
    """
    Search for the publication records of the given disease in the last 365 days, and return the search context
    :param disease: name of the disease
    :return: Search context (history)
    """
    return await fetch_latest_pubs(disease)


@app.get('/institutions', response_model=List[str])
async def get_institutions(env: str, qid: int, idx: int, retmax: int = 1000):
    """
    Find out the institutions that have published the articles of interest, making use of the NCBI History Server
    :param env: NCBI historical environment
    :param qid: NCBI query id
    :param idx: starting index of the articles
    :param retmax: maximum article to search
    :return: a list of institution names
    """
    return await get_affiliations(env, qid, idx, retmax)


if __name__ == "__main__":
    uvicorn.run("main:app", port=settings.server_port, reload=True)
