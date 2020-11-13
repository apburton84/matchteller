from poisson_predictor import PoissonPredictor

from helpers import predict_win_lose_draw, start_timer, stop_timer


class PoissonSeasonStrategy(object):
    ''' '''
    def __init__(self, season, training_data, season_data):
        self.season = season
        self.training_data = training_data
        self.season_data = season_data

        self.predictor = PoissonPredictor(self.training_data)

    def predict(self):
        start_time = start_timer()

        self.predictor.calc()
        
        self.season_data = self.season_data.apply(self.predictor.predict, axis=1)
        self.season_data = self.season_data.apply(predict_win_lose_draw, axis=1)

        # TODO: refactor to better location in project
        self.season_data['PC'] = self.season_data.apply(lambda x: 'Y' if x['PFTR'] == x['FTR'] else 'N', axis=1)

        # TODO: refactor to better location in project
        failed = self.season_data[self.season_data['PFTR'] == 'F'].shape[0]
        correct = self.season_data[self.season_data['PFTR'] == self.season_data['FTR']].shape[0]

        elasped_time = stop_timer(start_time)

        return self.season_data, self.predictor, correct, failed, elasped_time


class PoissonMatchStrategy(object):
    ''' '''
    def __init__(self, training_data, match_data):
        self.training_data = training_data
        self.match_data = match_data

        self.predictor = PoissonPredictor(self.training_data)

    def predict(self):
        start_time = start_timer()

        self.predictor.calc()

        self.predictor.predict(self.match_data)

        elasped_time = stop_timer(start_time)

        match = predict_win_lose_draw(self.match_data)
        
        return match, self.predictor, elasped_time
