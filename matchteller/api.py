from datetime import date
from os import listdir
from os.path import isfile, join

import pandas as pd
from data_provider import DataProvider
from helpers import (accuracy_calc, apply_goal_pooling, get_data_file_paths,
                     predict_win_lose_draw, start_timer, stop_timer)
from poisson_strategy import PoissonMatchStrategy, PoissonSeasonStrategy


def api_response(outcome, data, msg=None):
    code = None
    return {
        'response': {
            'code': code, 'outcome': outcome, 'msg': msg
        },
        'data': data
    }


def predict_match_poisson_action(request):
    ''' API Endpoint to Predict Match 

    '''
    match_data_file_paths = get_data_file_paths()

    data_provider = DataProvider(match_data_file_paths)

    match_date = date.today().strftime("%d-%m-%Y") 
    if 'date' in request.matchdict:
        match_date = request.matchdict['date']
    
    training_data = data_provider.matches(date=match_date)

    training_data = apply_goal_pooling(training_data, 4)
    
    home_team = request.matchdict['home_team'].capitalize()
    away_team = request.matchdict['away_team'].capitalize()

    # TODO: Here we are searching for an known football match, if
    match = data_provider.d[
        (data_provider.d['Date'] == match_date) & 
        (data_provider.d['HomeTeam'] == home_team) & 
        (data_provider.d['AwayTeam'] == away_team)
    ]

    if match.shape[0] > 0:
        match = match.iloc[0]
    else:
        match = pd.Series(
            [request.matchdict['home_team'].capitalize(),
             request.matchdict['away_team'].capitalize(), 
             None, None, None],
            index = ['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR'])

    match_strategy = PoissonMatchStrategy(training_data, match)

    match, predictor, elasped_time = match_strategy.predict()

    # TODO: refactor to better location in project
    # match['PC'] = match.apply(lambda x: 'Y' if x['PFTR'] == x['FTR'] else 'N')

    return api_response('success', {
        'Date': match_date,
        'Home': match['HomeTeam'],
        'HAS': match['HAS'],
        'HDS': match['HDS'],
        'HGE': match['HGE'],
        'FTHG': match['FTHG'],
        'Away': match['AwayTeam'],
        'AAS': match['AAS'],
        'ADS': match['ADS'],
        'AGE': match['AGE'],
        'FTAG': match['FTAG'],
        'Result': match['FTR'],
        'Predict': match['PFTR'],
        # 'Correct': match['PC'],
        'PHP': match['PHP'],
        'PDP': match['PDP'],
        'PAP': match['PAP'],
        'Elasped_Time': elasped_time,
    })

def predict_season_poisson_action(request):
    ''' API Endpoint to Predict Season 

    '''
    match_data_file_paths = get_data_file_paths()

    data_provider = DataProvider(match_data_file_paths)

    season = date.today().strftime("%Y") 
    if 'season' in request.matchdict:
        season = request.matchdict['season']

    # TODO: At the moment only pre-season data is used as training data.
    #       Ideally, we would use all matches up until the match we wish
    #       to predict.
    training_data = data_provider.matches(before_season=season)
    training_data = apply_goal_pooling(training_data, 4)

    season_matches = data_provider.matches(season=season)
    season_strategy = PoissonSeasonStrategy(season, training_data, season_matches)
    
    season_matches, predictor, correct, failed, elasped_time = season_strategy.predict()

    season_matches = season_matches[[
        # 'Date',
        'HomeTeam', 'HAS', 'HDS', 'HGE', 'FTHG', 
        'AwayTeam', 'AAS', 'ADS', 'AGE', 'FTAG', 
        'FTR', 'PFTR', 'PC', 'PHP', 'PDP', 'PAP'
    ]]

    resp_data = {
        'summary': {
           'Datapoints': predictor.d.shape[0],
           'Season': season,
           'Matches': season_matches.shape[0],
           'Correct': correct,
           'Failed': failed,
           'Accuracy': accuracy_calc(season_matches.shape[0] - failed, correct),
           'Elasped Time': elasped_time 
        },
        'matches': season_matches.to_dict('r')
    } 

    return api_response('success', resp_data)
