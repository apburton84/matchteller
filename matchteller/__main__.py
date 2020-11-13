import argparse
import os

from data_provider import DataProvider
from dotenv import load_dotenv
from helpers import (accuracy_calc, apply_goal_pooling, get_data_file_paths,
                     matches_from_season, output_as, predict_win_lose_draw,
                     predictor_output_as, start_timer, stop_timer)
from poisson_strategy import PoissonMatchStrategy, PoissonSeasonStrategy

load_dotenv()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Football Match Score Predictor',
        epilog="Author: Anthony Burton <apburton84@googlemail.com>"
    )

    parser.add_argument('--match-data', metavar='path', help='football match data csv')
    parser.add_argument('--all-matches', action='store_true', help='predict all matches in season e.g. 17')
    parser.add_argument('--season', metavar='integer', help='predict all matches in season e.g. 17')
    parser.add_argument('--home-team', metavar='string', help='the home team')
    parser.add_argument('--away-team', metavar='string', help='the away team')
    parser.add_argument('--output', metavar='type', help='output as table, html, csv, json, xml')
    parser.add_argument('--report', action='store_true', help='include output report')
    parser.add_argument('--server', action='store_true', help='start the RESTful API server')

    args = parser.parse_args()

    if args.match_data:
        match_data_file_paths = args.match_data.split(',')
    else:
        match_data_file_paths = get_data_file_paths()

    if args.all_matches and args.season:
        data_provider = DataProvider(match_data_file_paths)
        
        # TODO: At the moment only pre-season data is used as training data.
        #       Ideally, we would use all matches up until the match we wish
        #       to predict.
        training_data = data_provider.matches(before_season=args.season)
        training_data = apply_goal_pooling(training_data, 4)

        season_matches = data_provider.matches(season=args.season)
        season_strategy = PoissonSeasonStrategy(args.season, training_data, season_matches)
        
        season_matches, predictor, correct, failed, elasped_time = season_strategy.predict()

        if (args.report):
            output_as({
               'Datapoints': [predictor.d.shape[0]],
               'Season': [args.season],
               'Matches': [season_matches.shape[0]],
               'Correct': [correct],
               'Failed': [failed],
               'Accuracy': [accuracy_calc(season_matches.shape[0] - failed, correct)],
               'Elasped Time': [elasped_time] 
            }, args.output.upper())
         
        output_as({
            'Date': (season_matches['Date'].dt.strftime('%m/%d/%Y')).tolist(),
            'Home': season_matches['HomeTeam'].tolist(),
            'HAS': season_matches['HAS'].tolist(),
            'HDS': season_matches['HDS'].tolist(),
            'HGE': season_matches['HGE'].tolist(),
            'Away': season_matches['AwayTeam'].tolist(),
            'AAS': season_matches['AAS'].tolist(),
            'ADS': season_matches['ADS'].tolist(),
            'AGE': season_matches['AGE'].tolist(),
            'Result': season_matches['FTR'].tolist(),
            'Predict': season_matches['PFTR'].tolist(),
            'FTHG': season_matches['FTHG'].tolist(), 
            'FTAG': season_matches['FTAG'].tolist(), 
            'PHP': season_matches['PHP'].tolist(),
            'PDP': season_matches['PDP'].tolist(),
            'PAP': season_matches['PAP'].tolist(),
            'Correct': season_matches['PC'].tolist()
        }, args.output.upper())

    if args.match_data and args.home_team and args.away_team:
        data_provider = DataProvider(match_data_file_paths)

        training_data = data_provider.matches()

        home_team = home_team.capitalize()
        away_team = away_team.capitalize()

        match = data_provider.d[
            (data_provider.d['Date'] == match_date) & 
            (data_provider.d['HomeTeam'] == home_team) & 
            (data_provider.d['AwayTeam'] == away_team)
        ]

        predictor = PoissonPredictor(training_data)

        predictor.calc()

        if match.shape[0] > 0:
            match = match.iloc[0]
        else:
            match = pd.Series(
                [request.matchdict['home_team'].capitalize(),
                 request.matchdict['away_team'].capitalize(), 
                 None, None, None],
                index = ['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR'])

        predictor.predict(match)

        if (args.report):
            output_as({
               'Datapoints': [predictor.d.shape[0]],
               'Season': [args.season],
               'Matches': [season_matches.shape[0]],
               'Correct': [correct],
               'Failed': [failed],
               'Accuracy': [accuracy_calc(season_matches.shape[0] - failed, correct)],
               'Elasped Time': [elasped_time] 
            }, args.output.upper())
         
        output_as({
            'Date': (season_matches['Date'].dt.strftime('%m/%d/%Y')).tolist(),
            'Home': season_matches['HomeTeam'].tolist(),
            'HAS': season_matches['HAS'].tolist(),
            'HDS': season_matches['HDS'].tolist(),
            'HGE': season_matches['HGE'].tolist(),
            'Away': season_matches['AwayTeam'].tolist(),
            'AAS': season_matches['AAS'].tolist(),
            'ADS': season_matches['ADS'].tolist(),
            'AGE': season_matches['AGE'].tolist(),
            'Result': season_matches['FTR'].tolist(),
            'Predict': season_matches['PFTR'].tolist(),
            'FTHG': season_matches['FTHG'].tolist(), 
            'FTAG': season_matches['FTAG'].tolist(), 
            'PHP': season_matches['PHP'].tolist(),
            'PDP': season_matches['PDP'].tolist(),
            'PAP': season_matches['PAP'].tolist(),
            'Correct': season_matches['PC'].tolist()
        }, args.output.upper())

    if args.server:
        from wsgiref.simple_server import make_server

        from api import (predict_match_poisson_action,
                         predict_season_poisson_action)
        from pyramid.config import Configurator

        with Configurator() as config:
            config.add_route('match_poisson_predict',
                             '/api/1.0/predict/poisson/{home_team}/{away_team}',
                             request_method='GET')

            config.add_route('match_date_poisson_predict',
                             '/api/1.0/predict/poisson/{home_team}/{away_team}/{date}',
                             request_method='GET')

            config.add_route('match_season_poisson_predict',
                             '/api/1.0/predict/poisson/{season}',
                             request_method='GET')

            config.add_view(predict_match_poisson_action, route_name='match_poisson_predict', renderer='json')
            config.add_view(predict_match_poisson_action, route_name='match_date_poisson_predict', renderer='json')
            config.add_view(predict_season_poisson_action, route_name='match_season_poisson_predict', renderer='json')

            app = config.make_wsgi_app()

        server = make_server(os.getenv('SERVER_IP'), int(os.getenv('SERVER_PORT')), app)

        server.serve_forever()
