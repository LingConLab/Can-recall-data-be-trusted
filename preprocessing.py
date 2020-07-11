import json
import numpy as np
import pandas as pd


def add_languages(df):
    """
    Extract languages data from pandas dataframe and return complete dataframe
    with language columns added
    :param df: pandas dataframe
    :return: pandas dataframe
    """

    df = df.reset_index()
    languages = df['languages']
    languages_d = []

    for element in languages:
        json_acceptable_string = element.replace("'", "\"")
        d = json.loads(json_acceptable_string)
        languages_d.append(d)

    element_dict = list(languages_d[1].keys())
    df = df.drop(['languages', 'index', 'Unnamed: 0'], axis=1)
    df = df.join(pd.DataFrame(languages_d))
    df = df.fillna(0)
    df.loc[:, 'русский': 'муиринский диалект даргинского'] = df.loc[:,
                                                             'русский': 'муиринский диалект даргинского'].astype(
        int)

    df = df.replace({2: 1, -1: np.nan, 1: 0, 0: 0})

    return df


def replace_na_and_preprocessing(russian=False, ITM=False, subset=False,
                                 drop_na=True):
    """
    Returns preprocessed dataframe
    :param russian: special procedures for Russian dataframe
    :param ITM: special procedures for ITM dataframe
    :param subset: 1922-1980 subser
    :param drop_na: Remove na from the data
    :return:
    """
    languages_new = pd.read_csv('data/languages_new.csv')
    languages_new = languages_new.fillna(languages_new.mean())
    langs_change = dict(zip(languages_new['Язык'], languages_new['Язык NEW']))
    langs_change['генухский'] = 'гинухский'
    langs_change['кумыкский азербайджанский'] = 'азербайджанский или кумыкский'
    langs_change['литературный даргинский'] = 'акушинский даргинский'
    langs_change['литературный даргинский'] = 'акушинский даргинский'
    langs_change['литературный даргинский акушинский'] = 'акушинский даргинский'
    langs_change['литературный акушинский'] = 'акушинский даргинский'

    data = add_languages(pd.read_csv('parser/informants.csv'))
    data = data[data['type'] != 'неизвестно']
    data.loc[(data['year of death'] < 2000) & (
            data['year of death'] != 0), 'type'] = 'косвенно'
    data = data.drop(data[(data['expedition'] == 'Shangoda, Obokh, Megeb') & (
            data['residence'] == 'Shangoda')].index)
    data['number of na'] = data.isna().sum(axis=1).tolist()
    data['russian na'] = data['русский'].isna()

    if russian:
        data = data.dropna(subset=['русский'])
        data = data.fillna(0)
    if ITM:
        data['русский'] = data['русский'].fillna(0)

    data.loc[data['residence'] == 'Chankurbe', 'акушинский'] = 0
    data.loc[data['residence'] == 'Chabanmakhi', 'акушинский'] = 0
    data.loc[data['residence'] == 'Fiy', 'цахурский'] = 0
    data.loc[data['residence'] == 'Sutbuk', 'урагинский'] = 0
    data.loc[data['residence'] == 'Sutbuk', 'урцакинский'] = 0
    data.loc[data['residence'] == 'Urtsaki', 'сутбукский'] = 0
    data.loc[data['residence'] == 'Urtsaki', 'урагинский'] = 0
    data.loc[data['residence'] == 'Uragi', 'сутбукский'] = 0
    data.loc[data['residence'] == 'Uragi', 'урцакинский'] = 0

    data = data.rename(columns=langs_change)
    data = data.groupby(lambda x: x, axis=1).sum()
    data = data.replace({2: 1})

    langs_dict = dict(zip(languages_new['Village'], languages_new['Язык NEW']))
    data['mother tongue'] = data['residence'].map(langs_dict)

    pop_dict = dict(
        zip(languages_new['Village'], languages_new[' Village population']))
    data['village population'] = data['residence'].map(pop_dict)

    pop_dict = dict(
        zip(languages_new['Village'], languages_new['Language total']))
    data['language population'] = data['residence'].map(pop_dict)

    data['number of lang'] = data.loc[:, 'аварский':'чирагский даргинский'].sum(
        axis=1)
    data = data[data['year of birth'] != 0]

    lang_match = []

    k = 0

    for index, row in data.iterrows():
        if row[row['mother tongue']] == 1:
            k = 1
        else:
            k = 0

        lang_match.append(k)

    data['mother tongue match'] = lang_match
    data['number of lang'] = np.where(data['русский'] == 1,
                                      data['number of lang'] - 1,
                                      data['number of lang'])
    data['number of lang'] = np.where(data['mother tongue match'] == 1,
                                      data['number of lang'] - 1,
                                      data['number of lang'])
    data['number of lang strat'] = 0

    data.loc[data['number of lang'] == 5, 'number of lang strat'] = 4
    data.loc[data['number of lang'] == 4, 'number of lang strat'] = 4
    data.loc[data['number of lang'] == 3, 'number of lang strat'] = 3
    data.loc[data['number of lang'] == 2, 'number of lang strat'] = 2
    data.loc[data['number of lang'] == 1, 'number of lang strat'] = 1
    data.loc[data['number of lang'] == 0, 'number of lang strat'] = 0
    data = data[data['number of lang'] != -1]
    data = data[data['mother tongue match'] != 0]
    data.rename(columns={'year of birth': 'year_of_birth'}, inplace=True)

    data['type'] = data['type'].map({'косвенно': 0, 'лично': 1})
    if drop_na:
        data = data.replace([np.inf, -np.inf], np.nan).dropna()
        data = data.dropna()
    if subset:
        data = data[
            (data['year_of_birth'] >= 1922) & (data['year_of_birth'] <= 1980)]

    elev = pd.read_csv('data/merged_all_census_and_samira.csv')
    elev = elev[['eng_vil_name', 'elevation']].dropna()
    elev2 = pd.DataFrame([['Ersi', 407], ['Gelmets', 1750], ['Hinuq', 1941],
                          ['Mikik', 1640], ['Tad-Magitl', 1457],
                          ['Upper Ubekimakhi', 1246]],
                         columns=['eng_vil_name', 'elevation'])
    elev = elev.append(elev2)
    data = data.set_index('residence').join(
        elev.set_index('eng_vil_name'))
    data = data.reset_index()
    data = data.rename({'index': 'residence'}, axis='columns')
    data = data.dropna()
    return data


# Data without subset
data_plot = replace_na_and_preprocessing()
data_plot.to_csv('data/all.csv')


# ITM preprocessing
data_ITM = replace_na_and_preprocessing(ITM=True, drop_na=True, subset=True)
data_ITM.to_csv('data/ITM.csv')


# Russian preprocessing
data_russian = replace_na_and_preprocessing(russian=True, drop_na=True, subset=True)
data_russian.to_csv('data/russian.csv')
