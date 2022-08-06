#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/8/6 9:23
# @Author  : liyun
# @desc    :
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    env: str = Field("develop", env="ENV")
    server_port: int = Field(9000, env='SERVER_PORT')
    ncbi_url: str = Field("https://eutils.ncbi.nlm.nih.gov/entrez/eutils", env="NCBI_URL")
    ncbi_app_key: str = Field("", env="NCBI_APP_KEY")
    t_waiting: int = Field(1, env="T_WAITING")  # time to wait before subsequent request, in seconds

    # How many API calls are made concurrently. Theoretically 10, but 5 seems to be the number that works safely
    download_concurrency: int = Field(5, env="DOWNLOAD_CONCURRENCY")

    class Config:
        env_file = '.env'  # variables in this file have higher priorities


settings = Settings()
if not settings.ncbi_app_key:
    raise ValueError('NCBI app key is missing')
