#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/8/6 9:25
# @Author  : liyun
# @desc    :
from typing import List
from settings import settings
from ncbi_app.schemas import NumPubOfYear, PubmedHist
from functools import partial
import aiometer
import httpx
from loguru import logger
import xmltodict
import traceback


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


async def fetch_latest_pubs(disease: str) -> PubmedHist:
    """
    Search for the publication records of the given disease in the last 365 days, and return the search context to
    enable further queries
    :param disease: name of the disease
    :return: the search context (NCBI called it 'history')
    """
    params = {
        'db': 'pubmed',
        'term': '+'.join(disease.split()),
        'reldate': 365,
        'datetype': 'pdat',
        'retmax': 100000,
        'usehistory': 'y',
        'retmode': 'json'
    }
    async with httpx.AsyncClient() as client:
        res = await client.get(f'{BASE_URL}/esearch.fcgi', params=params)
    res_data = res.json()['esearchresult']
    return PubmedHist(**{'web_env': res_data['webenv'], 'query_key': res_data['querykey'], 'count': res_data['count']})


def parse_author(author: dict) -> List[str]:
    """
    Parse author information structure
    :param author: auth infor structure
    :return: list of affiliations of the author
    """
    auth_info = author.get('AffiliationInfo')
    if auth_info is None:
        return []
    affiliations = []
    try:
        if isinstance(auth_info, dict):
            affiliations.append(auth_info['Affiliation'])
        elif isinstance(auth_info, list):
            affiliations.extend([info['Affiliation'] for info in auth_info])
        else:
            logger.warning('Encountered unknown structure')
        return affiliations
    except (KeyError, ValueError, TypeError):
        logger.warning('Unknown auth info format')
        return affiliations


def extract_affi(articles: dict) -> List[str]:
    """
    Extract affiliations of the articles
    :param articles: articles to work on
    :return: list of affiliations
    """
    affiliations = []
    if not len(articles):
        return affiliations
    for article in articles:
        try:
            authors = article['MedlineCitation']['Article']['AuthorList']['Author']
        except (KeyError, ValueError):
            logger.warning('Unknown format')
            continue
        if isinstance(authors, dict):
            affiliations.extend(parse_author(authors))
            continue
        for author in authors:
            affiliations.extend(parse_author(author))

    return list(set(affiliations))


async def get_affiliations(env: str, query_key: int, idx: int, ret_max: int = 1000) -> List[str]:
    """
    Get publications from search history, and retrieve their affiliations
    :param env: NCBI search environment identifier
    :param query_key: query key within the search env
    :param idx: index to start from
    :param ret_max: max number of records to fetch. default 1000
    :return: a list of affiliations
    """
    params = {'db': 'pubmed', 'query_key': query_key, 'WebEnv': env, 'retstart': idx, 'retmax': 1000, 'retmode': 'xml'}
    async with httpx.AsyncClient() as client:
        res = await client.get(f'{BASE_URL}/efetch.fcgi', params=params)
    data = xmltodict.parse(res.content)
    if 'PubmedArticleSet' not in data or 'PubmedArticle' not in data['PubmedArticleSet']:
        return []
    return extract_affi(data['PubmedArticleSet']['PubmedArticle'])
