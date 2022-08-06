#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/8/6 9:25
# @Author  : liyun
# @desc    :
from typing import List
from settings import settings
from ncbi_app.schemas import NumPubOfYear
from functools import partial
import aiometer
import httpx
from loguru import logger

BASE_URL = settings.ncbi_url
API_KEY = settings.ncbi_app_key
TTW = settings.t_waiting
N_DOWNLOADS = settings.download_concurrency


def extract_count(search_res: dict) -> int:
    """
    Extract the number of records from the esearch return of NCBI API
    :param search_res: return of esearch
    :return: number of records
    """
    try:
        res = search_res['esearchresult']
    except KeyError as e:
        logger.error('JSON corrupted. Perhaps you need to reduce the concurrency from settings.')
        raise e
    return int(res.get('count', 0))


async def download_records_by_year(client, disease: str, yr: int) -> dict:
    """
    Return a dictionary that contains all publication IDs within a year
    :param client: the http client
    :param disease: disease of interest
    :param yr: the year of interest
    :return: the publication IDs
    """
    params = {'db': 'pubmed',
              'datetype': 'pdat',
              'retmode': 'json',
              'term': disease,
              'mindate': yr,
              'maxdate': yr,
              'api_key': API_KEY}
    logger.debug(f'downloading year {yr}')
    res = await client.get(f'{BASE_URL}/esearch.fcgi', params=params)
    return res.json()


async def download_trend(disease: str, y0: int, y1: int) -> List[NumPubOfYear]:
    """
    Get the number of publications about the disease of different years
    :param disease: the name of the disease
    :param y0: start of the year range
    :param y1: end of the year range
    :return:
    """
    if y0 > y1:
        raise ValueError(f'The start of year range {y0} cannot be bigger than the end {y1}')
    years = [i for i in range(y0, y1+1)]
    search_term = '+'.join(disease.split())
    async with httpx.AsyncClient() as client:
        data = await aiometer.run_all([partial(download_records_by_year, client, search_term, y) for y in years],
                                      max_at_once=N_DOWNLOADS,
                                      max_per_second=N_DOWNLOADS)
    return [NumPubOfYear.parse_obj({'n_pub': extract_count(d), 'year': y}) for d, y in zip(data, years)]
