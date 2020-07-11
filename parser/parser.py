#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Alexey Koshevoy

from requests import get
import pandas as pd
import numpy as np


class Parser:

    def __init__(self):
        self.url = 'https://multidagestan.com/api/respondents/{}'
        self.ids = self.get_codes()

    def request(self):
        page_json = get(self.url.format('')).json()
        return page_json

    def get_codes(self):

        page_json = self.request()

        codes = []

        for element in page_json:
            codes.append(element.get('code'))

        return codes

    def get_dataframe(self):

        df_data = []

        for code in self.ids:

            resp_json = get(self.url.format(code)).json()

            try:
                birth = resp_json.get('birth')
            except:
                birth = np.nan

            try:
                death = resp_json.get('death')
            except:
                death = np.nan

            try:
                residence = resp_json.get('residence').get('en')
            except:
                residence = np.nan

            try:
                name = resp_json.get('name')
            except:
                name = np.nan

            try:
                sex = resp_json.get('sex')
            except:
                sex = np.nan

            try:
                direct = resp_json.get('direct')
            except:
                direct = np.nan

            try:
                languages = resp_json.get('languages')
            except:
                languages = np.nan

            try:
                expedition = resp_json.get('expedition').get('name')
            except:
                expedition = np.nan

            df_data.append([name, birth, death, sex,
                            languages, expedition, residence, direct])

        pd.DataFrame(df_data, columns=['name', 'year of birth', 'year of death',
                                       'sex', 'languages', 'expedition', 'residence',
                                       'type']).to_csv('informants.csv')


if __name__ == '__main__':
    p = Parser()
    p.get_dataframe()
