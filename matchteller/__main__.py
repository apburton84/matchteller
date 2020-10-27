import argparse

from poisson_predictor import PoissonPredictor
from data_provider import DataProvider

from helpers import output_as
from helpers import predictor_output_as
from helpers import matches_from_season
from helpers import get_data_file_paths
from helpers import accuracy_calc
from helpers import predict_win_lose_draw


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

        predictor = PoissonPredictor(training_data)

        predictor.calc()

        season_matches = data_provider.matches(season=args.season)

        failed_predictions = 0
        correct_predictions = 0
        for index, match in season_matches.iterrows():
            predicted_probs = predictor.predict(match['HomeTeam'],
                                                match['AwayTeam'])

            predicted_probs = predicted_probs.to_dict()
            predicted_result = predict_win_lose_draw(predicted_probs)

            output = {'probability': predicted_probs,
                      'prediction': predicted_result,
                      'result': match['FTR']}

            if predicted_result == match['FTR']:
                correct_predictions = correct_predictions + 1

            if predicted_result == 'F':
                failed_predictions = failed_predictions + 1

            # FIXME: this should be predictor_output_as()
            # predictor_output_as(output, 'TABLE')

        summary = {'datapoints': [predictor.d.shape[0]],
                   'season': [args.season],
                   'matches': [season_matches.shape[0]],
                   'correct': [correct_predictions],
                   'failed': [failed_predictions],
                   'accuracy': [accuracy_calc(season_matches.shape[0] - failed_predictions, correct_predictions)]}

        output_as(summary, 'TABLE')

    if args.match_data and args.home_team and args.away_team:
        data_provider = DataProvider(match_data_file_paths)

        training_data = data_provider.matches()

        predictor = PoissonPredictor(match_data)
        predictor.calc()

        predictor.predict(args.home_team, args.away_team)

        output_as(predictor, args.output.upper())
