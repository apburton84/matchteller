import pandas as pd
import numpy as np
from datetime import datetime


class DataProvider(object):
    """ Data Provider to handle the football data"""

    def __init__(self, data_paths=[]):
        """ Initialise the DataProvider"""
        def date_parser(x):
            # Check for nan
            if x != x:
                return np.nan
            try:
                return datetime.strptime(x, "%d/%m/%y")
            except Exception as e:
                return datetime.strptime(x, "%d/%m/%Y")

        list_ = []
        for path in data_paths:
            df = pd.read_csv(path,
                             parse_dates=['Date'],
                             date_parser=date_parser)

            list_.append(df)

        # Create a single dataset of all CSV files
        self.d = pd.concat(list_, ignore_index=True)

        # self.d['Date'] = pd.to_datetime(self.d['Date'])
        # self.d['Date'] = self.d['Date'].dt.strftime('%d/%m/%Y')

        # Remove any row containing all nan
        self.d = self.d.dropna(how='all')

        # Sort by match date
        self.d = self.d.sort_values(by="Date")

    def matches(self, date=False, season=False, before_season=False):
        """ Get Matches from dataset, all or by season """
        if date:
            # TODO: consider better start date for this scenario
            return self.filter_by_date('1970-01-01', date)
        elif season:
            start_date, end_date = self.season_to_date_range(season)
            return self.filter_by_date(start_date, end_date)
        elif before_season:
            start_date, end_date = self.season_to_date_range(before_season)
            # TODO: consider better start date for this scenario
            return self.filter_by_date('1970-01-01', start_date)
        else:
            return self.d

    def teams(self, season=False, keys=False):
        """ Get Teams from dataset, all or by season """
        if season:
            match_data = self.matches(season)
        else:
            match_data = self.d

        teams = match_data.groupby('HomeTeam').groups.keys()

        if keys:
            return teams
        else:
            return list(teams)

    def filter_by_date(self, start_date, end_date):
        """ Date range based filtering of the dataset """
        date_range = pd.date_range(start=start_date, end=end_date)
        mask = self.d['Date'].map(lambda row: str(row) in date_range)

        return pd.DataFrame(self.d.loc[mask])

    def season_to_date_range(self, season):
        return str(season) + '-08-01', str(int(season) + 1) + '-05-31'
