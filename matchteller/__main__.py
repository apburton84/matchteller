import argparse
from tabulate import tabulate

from poisson_predictor import PoissonPredictor

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Football Match Score Predictor',
        epilog="Author: Anthony Burton <apburton84@googlemail.com>"
    )

    parser.add_argument('--match-data', metavar='path', help='football match data csv')
    parser.add_argument('--home-team', metavar='string', help='the home team')
    parser.add_argument('--away-team', metavar='string', help='the away team')
    parser.add_argument('--output', metavar='type', help='output as table, html, csv, json, xml')

    args = parser.parse_args()

    if args.match_data and args.home_team and args.away_team:
        predictor = PoissonPredictor(args.match_data.split(','))

        predictor.calc()

        predictor.predict(args.home_team, args.away_team)

        if not args.output or args.output.upper() == "TABLE":
            print(tabulate(
                predictor.m_outcome_prob,
                headers='keys',
                tablefmt='simlpe'
            ))

        if args.output.upper() == "CSV":
            print(predictor.m_outcome_prob.to_csv())

        if args.output.upper() == "JSON":
            print(predictor.m_outcome_prob.to_json())

        if args.output.upper() == "XML":
            def row_to_xml(row):
                xml = ['<prediction>']
                for i, col_name in enumerate(row.index):
                    xml.append('  <outcome name="{0}">{1}</outcome>'.format(col_name, row.iloc[i]))
                xml.append('</prediction>')
                return '\n'.join(xml)
            print('\n'.join(predictor.m_outcome_prob.apply(row_to_xml, axis=1)))

        if args.output.upper() == "HTML":
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

        if args.output.upper() == "GRAPH":
            import seaborn as sns

            sns.set()

            heatmap = sns.heatmap(predictor.m_score, annot=True)

            fig = heatmap.get_figure()
            fig.savefig("output.png")

