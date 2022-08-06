#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/8/6 9:25
# @Author  : liyun
# @desc    :
from typing import List
from pydantic import BaseModel
from humps import camelize


def to_camel(string):
    return camelize(string)


class CamelModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class NumPubOfYear(CamelModel):
    n_pub: int
    year: int

