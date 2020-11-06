from tabulate import tabulate

import pandas as pd
import numpy as np
import json
import os
import time

def start_timer():
    return time.time()

def stop_timer(start):
    end = time.time()
    return end- start

def predict_win_lose_draw(prediction):
    prediction['PFTR'] = 'F'
    if prediction['PHP'] > prediction['PAP']:
        prediction['PFTR'] = 'H'

    if prediction['PAP'] > prediction['PHP']:
        prediction['PFTR'] = 'A'

    if ((prediction['PDP'] > prediction['PHP']) and
        (prediction['PDP'] > prediction['PAP'])):
        prediction['PFTR'] = 'D'

    return prediction


def get_data_file_paths():
    match_data = []
    for root, dirs, files in os.walk('./data/'):
        for f in files:
            match_data.append(os.path.join(root, f))
    return match_data


def accuracy_calc(total, correct):
    return ((100 / total) * correct)


def matches_from_season(season, dataframe):
    df = pd.DataFrame(np.random.random((dataframe.shape[0], 3)))
    df['Date'] = pd.to_datetime(dataframe['Date'])

    return dataframe.loc[(df['Date'] > '2016-01-01') &
                         (df['Date'] < '2017-12-31')]


def output_as(data, format_as):
    if format_as == "TABLE":
        print(tabulate(
            data,
            headers='keys',
            tablefmt='simlpe'
        ), '\n')


def predictor_output_as(predictor, format_as):
    if format_as == "TABLE":
        print(tabulate(
            predictor.m_outcome_prob,
            headers='keys',
            tablefmt='simlpe'
        ))

    if format_as == "CSV":
        print(predictor.m_outcome_prob.to_csv())

    if format_as == "JSON":
        try:
            print(predictor.to_json())
        except:
            print(json.dumps(predictor))

    if format_as == "XML":
        def row_to_xml(row):
            xml = ['<prediction>']
            for i, col_name in enumerate(row.index):
                xml.append('  <outcome name="{0}">{1}</outcome>'.format(col_name, row.iloc[i]))
            xml.append('</prediction>')
            return '\n'.join(xml)
        print('\n'.join(predictor.m_outcome_prob.apply(row_to_xml, axis=1)))

    if format_as == "HTML":
        def row_to_xml(row):
            html = ['<table>\n<thead>']
            for i, col_name in enumerate(row.index):
                html.append('  <th>{0}</th>'.format(col_name))
            html.append('</thead>\n<tbody>')
            for i, col_name in enumerate(row.index):
                html.append('  <td>{0}</td>'.format(row.iloc[i]))
            html.append('</tbody>\n</table>')
            return '\n'.join(html)
        print('\n'.join(predictor.m_outcome_prob.apply(row_to_xml, axis=1)))

    if format_as == "GRAPH":
        import seaborn as sns

        sns.set()

        heatmap = sns.heatmap(predictor.m_score, annot=True)

        fig = heatmap.get_figure()
        fig.savefig("output.png")
