import argparse

from data_provider import DataProvider
from helpers import (accuracy_calc, get_data_file_paths, matches_from_season,
                     output_as, predict_win_lose_draw, predictor_output_as,
                     start_timer, stop_timer)
from poisson_predictor import PoissonPredictor

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

        # TODO: Primative goal pooling
        training_data['FTHG'] = training_data.apply(lambda x: x['FTHG'] if x['FTHG'] <= 4 else 4, axis=1)
        training_data['FTAG'] = training_data.apply(lambda x: x['FTAG'] if x['FTAG'] <= 4 else 4, axis=1)

        predictor = PoissonPredictor(training_data)

        predictor.calc()

        season_matches = data_provider.matches(season=args.season)

        start_time = start_timer()

        season_matches = season_matches.apply(predictor.predict, axis=1)
        season_matches = season_matches.apply(predict_win_lose_draw, axis=1)
        
        # TODO: refactor to better location in project
        season_matches['PC'] = season_matches.apply(lambda x: 'Y' if x['PFTR'] == x['FTR'] else 'N', axis=1)

        # TODO: refactor to better location in project
        failed_predictions = season_matches[season_matches['PFTR'] == 'F'].shape[0]
        correct_predictions = season_matches[season_matches['PFTR'] == season_matches['FTR']].shape[0]

        elasped_time = stop_timer(start_time)

        if (args.report):
            output_as({
               'Datapoints': [predictor.d.shape[0]],
               'Season': [args.season],
               'Matches': [season_matches.shape[0]],
               'Correct': [correct_predictions],
               'Failed': [failed_predictions],
               'Accuracy': [accuracy_calc(season_matches.shape[0] - failed_predictions, correct_predictions)],
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
            'Correct': season_matches['PC'].tolist()
        }, args.output.upper())


    if args.match_data and args.home_team and args.away_team:
        data_provider = DataProvider(match_data_file_paths)

        training_data = data_provider.matches()

        predictor = PoissonPredictor(match_data)
        predictor.calc()

        predictor.predict(args.home_team, args.away_team)

        output_as(predictor, args.output.upper())
