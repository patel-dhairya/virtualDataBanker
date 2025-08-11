"""
This file contains utility functions used throughout the projoect.
Author: Dhairya
"""
import pandas as pd


def pretty_panda() -> None:
    """
    Prettyfy the pandas output
    :return: None
    """
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', None)
    pd.options.display.float_format = '{:,.2f}'.format
