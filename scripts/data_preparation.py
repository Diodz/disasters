# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 00:07:42 2020

@author: diego
"""
import pandas as pd


def read_and_process_data():
    '''

    Returns
    -------
    None.

    '''
    geomet = pd.read_stata("data/IfoGAME_balanced_panel.dta")
    econ_freedom = read_fraser_institute_data()
    ef_expanded = add_years(econ_freedom)
    ef_expanded = interpolate_fraser_data(ef_expanded)
    merged = geomet.merge(ef_expanded, how='left')
    merged.to_csv('data/econ_freedom_and_geomet.csv', index=False)
    return merged


def read_fraser_institute_data():
    '''

    Returns
    -------
    econ_freedom : TYPE
        DESCRIPTION.

    '''
    econ_freedom = pd.read_excel(
        "data/efw-2019-master-index-data-for-researchers.xlsx",
        sheet_name="EFW Panel Data 2019 Report",
        skiprows=2).drop(columns=['Unnamed: 0'])
    econ_freedom.rename(columns={"ISO_Code": "iso", "Year": "year",
                                 "1  Size of Government": "size_gov",
                                 "2  Legal System & Property Rights":
                                     "prop_rights",
                                 "3  Sound Money": "sound_money",
                                 "4  Freedom to trade internationally":
                                     "freedom_to_trade",
                                 "5  Regulation": "regulation",
                                 "Countries": "country"}, inplace=True)
    return econ_freedom


def interpolate_fraser_data(df):
    '''
    Parameters
    ----------
    df : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    df.sort_values(['iso', 'year'], ascending=[True, True], inplace=True)
    df = df.reset_index().drop(columns=['index'])
    df = df.groupby('iso').apply(lambda group: group.interpolate
                                 (limit_area='inside'))
    return df


def add_years(df):
    '''


    Parameters
    ----------
    df : TYPE
        DESCRIPTION.

    Returns
    -------
    df : TYPE
        DESCRIPTION.

    '''
    dct = {}
    df_aux = df[df['year'] == 1970]
    for row in df_aux.itertuples(index=False):
        dct[row[1]] = row[2]
    for iso in df['iso'].unique():
        df = add_entries_for_country(df, iso, dct[iso])
    return df


def add_entries_for_country(df, iso_code, country_name):
    '''
    Adds years in between.

    Parameters
    ----------
    df : TYPE
        DESCRIPTION.
    iso_code : TYPE
        DESCRIPTION.
    country_name : TYPE
        DESCRIPTION.

    Returns
    -------
    df : TYPE
        DESCRIPTION.

    '''
    for i in range(1971, 2000):
        if i % 5 != 0:
            df = df.append({"year": i, "iso": iso_code, "country": country_name
                            }, ignore_index=True)
    return df
