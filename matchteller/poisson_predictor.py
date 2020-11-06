import pandas as pd
import numpy as np
import scipy.stats as st


class PoissonPredictor(object):
    """ Poisson Model to Predict the out of Associate Football Matches"""

    def __init__(self, d):
        """ Initialise the Predictor"""
        self.d = d
        self.t = d.groupby('AwayTeam').groups.keys()

    def calc(self):
        """ Calculate a set of base score for each team"""
        self.t_scores = pd.DataFrame({
                # Total Goals
                'TG': pd.Series(
                    self.d.groupby('HomeTeam')['FTHG'].sum().values +
                    self.d.groupby('AwayTeam')['FTAG'].sum().values,
                    index=self.t
                ),
                # Total Home Goals
                'THG': pd.Series(
                    self.d.groupby('HomeTeam')['FTHG'].sum().values,
                    index=self.t
                ),
                # Average Home Goals
                'AHG': pd.Series(
                    self.d.groupby('HomeTeam')['FTHG'].mean().values,
                    index=self.t
                ),
                # Total Home Goals Conceded
                'THGC': pd.Series(
                    self.d.groupby('HomeTeam')['FTAG'].sum().values,
                    index=self.t
                ),
                # Average Home Goal Conceded
                'AHGC': pd.Series(
                    self.d.groupby('HomeTeam')['FTAG'].mean().values,
                    index=self.t
                ),
                # Total Away Goals
                'TAG': pd.Series(
                    self.d.groupby('AwayTeam')['FTAG'].sum().values,
                    index=self.t
                ),
                # Average Away Goals
                'AAG': pd.Series(
                    self.d.groupby('AwayTeam')['FTAG'].mean().values,
                    index=self.t
                ),
                # Total Away Goals Conceded
                'TAGC': pd.Series(
                    self.d.groupby('AwayTeam')['FTHG'].sum().values,
                    index=self.t
                ),
                # Average Away Goals Conceded
                'AAGC': pd.Series(
                    self.d.groupby('AwayTeam')['FTHG'].mean().values,
                    index=self.t
                ),
            }
        )

        self.t_scores_ttl = self.t_scores[['TG', 'THG', 'THGC', 'TAG', 'TAGC']].sum()
        self.t_scores_avg = self.t_scores[['AHG', 'AHGC', 'AAG', 'AAGC']].apply(axis=0, func=st.hmean)

        self.t_strengths = pd.DataFrame({
            'HAS': self.t_scores['AHG'] / self.t_scores_avg['AHG'],
            'HDS': self.t_scores['AHGC'] / self.t_scores_avg['AHGC'],
            'AAS': self.t_scores['AAG'] / self.t_scores_avg['AAG'],
            'ADS': self.t_scores['AAGC'] / self.t_scores_avg['AAGC']
        })

        self.t_goals_exp = pd.DataFrame({
            'HGE': self.t_scores['AHG'] * self.t_strengths['HAS'] * self.t_strengths['ADS'],
            'AGE': self.t_scores['AAG'] * self.t_strengths['HDS'] * self.t_strengths['AAS']
        })

        self.home_team_advant = self.d.groupby('FTR')['FTR'].count()['H'] / ((self.d.groupby('FTR')['FTR'].count()['H'] + self.d.groupby('FTR')['FTR'].count()['A']) / 2)


    def predict(self, data):
        """ Predict probability of the matches final outcome"""
        home_team = data['HomeTeam']
        away_team = data['AwayTeam']
        
        # TODO: Handle the scenario where we do not have training data for a team
        if home_team not in self.t or away_team not in self.t:
            data['Home_P'], data['Draw_P'], data['Away_P'] = [0,0,0]
            data['PHP'], data['PDP'], data['PAP'] = [0,0,0]
            data['HGE'], data['AGE'], data['HAS'], data['AAS'] = [0,0,0,0]
            data['HDS'], data['ADS'] = [0,0]

            return data

        self.m_score_pre = pd.DataFrame(
            np.zeros((11, 11), dtype=int),
            index=np.arange(11)
        )

        # TODO: Add ability to remove home team advantage from calculation
        self.m_score = self.m_score_pre.apply(
            lambda x: x + (
                #  (st.poisson.pmf(x.index + 1, self.home_team_advant * self.t_goals_exp.loc[home_team]['HGE'], 1)) *
                (st.poisson.pmf(x.index + 1, self.t_goals_exp.loc[home_team]['HGE'], 1)) *

                #  (st.poisson.pmf(x.name + 1, self.t_goals_exp.loc[away_team]['AGE'] / self.home_team_advant, 1)) *
                (st.poisson.pmf(x.name + 1, self.t_goals_exp.loc[away_team]['AGE'], 1)) *
                100
            )
        )

        self.m_outcome_prob = pd.DataFrame({
            'HOME': self.m_score[self.m_score.apply(lambda x: x.name < x.index)].sum(axis=0).sum(),
            'DRAW': self.m_score[self.m_score.apply(lambda x: x.name == x.index)].sum().sum(),
            'AWAY': self.m_score[self.m_score.apply(lambda x: x.name > x.index)].sum().sum()
        }, index=['PROB'])

        self.m_outcome_odds = pd.DataFrame({
            'HOME': (1/self.m_outcome_prob['HOME']) * 100,
            'DRAW': (1/self.m_outcome_prob['DRAW']) * 100,
            'AWAY': (1/self.m_outcome_prob['AWAY']) * 100
        }, index=['ODDS'])
      
        # TODO: Is there a better way to augment the match data with the following ?
        data['HAS'] = self.t_strengths.loc[home_team]['HAS']
        data['AAS'] = self.t_strengths.loc[away_team]['AAS']
 
        data['HDS'] = self.t_strengths.loc[home_team]['HDS']
        data['ADS'] = self.t_strengths.loc[away_team]['ADS']

        data['HGE'] = self.t_goals_exp.loc[home_team]['HGE']
        data['AGE'] = self.t_goals_exp.loc[away_team]['AGE']
        
        data['PHP'] = self.m_outcome_prob['HOME']['PROB']
        data['PDP'] = self.m_outcome_prob['DRAW']['PROB']
        data['PAP'] = self.m_outcome_prob['AWAY']['PROB']

        return data
