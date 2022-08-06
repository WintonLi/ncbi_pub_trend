#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/8/6 9:23
# @Author  : liyun
# @desc    :
import uvicorn
from fastapi import FastAPI
from typing import List
from ncbi_app.schemas import NumPubOfYear
from ncbi_app.ncbi_api import download_trend
from settings import settings


app = FastAPI(title="NCBI API FastAPI Application",
              description="FastAPI Application that discovers the trend of NCBI publications",
              version="1.0.0", )


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


if __name__ == "__main__":
    uvicorn.run("main:app", port=settings.server_port, reload=True)
