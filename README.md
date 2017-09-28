# MatchTeller

An associate football match predictor

MatchTeller implements a poisson model from A J Maher's 1982 "Modelling Associate Football Scores" paper.

The original paper can be found [here](http://www.90minut.pl/misc/maher.pdf).

### Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

Clone the repository to your local machine

    git clone http://github.co.uk/apburton84/matchteller

### Dependencies

You will need to install the python dependencies

```
pip install -r requirements.txt
```

A list dependencies can be found in the [requirements.txt](http://github.co.uk/apburton84/matchteller/requirements.txt).

### Historic Data

Historical data can be obtained from [football-data.co.uk](http://football-data.co.uk)

The data used in the following examples of MatchTeller usage can be found at [football-data.co.uk - Premier League 2015-2016](http://www.football-data.co.uk/mmz4281/1516/E0.csv)

### Usage

Output the MatchTeller usage documentation.

```
python matchteller -h
```

```
Usage: matchteller [-h] [--match-data path] [--home-team string]
                   [--away-team string] [--output type]

Poisson Football Match Score Predictor

optional arguments:
  -h, --help          show this help message and exit
  --match-data path   football match data csv
  --home-team string  the home team
  --away-team string  the away team
  --output type       output as table, csv, json, xml

Author: Anthony Burton <apburton84@googlemail.com>
```

You can easily predict the outcome of a particular match, say `Stoke vs Arsenal`, by providing historical match data and an output format:

```
python matchteller --match-data ../2015-2016/E0.csv --home-team Stoke --away-team Arsenal --output table
```

MatchTeller prediction for Stoke vs Arsenal, given the 2015-2016 premier league data as input, is:

```
      AWAY     DRAW     HOME
----  ------  -------  -------
PROB  57.105  18.6692  24.2191
```

### Output Formats

MatchTeller current support the output of the following formats:

* Table
* HTML
* JSON
* XML
* CSV

### Using MatchTeller as a python library

Using MatchTeller in your own applications is easy, simply import matchteller.

```
import matchteller as mt
```

At present MatchTeller had a single predictor, the ``PoissonPredictor``.

```
p = mt.PoissonPredictor('E0.csv')
```

Before we can perform a prediction we must call ``calc()``, which calculates the required team and league statistics.

```
p.calc()
```

To perform a prediction call ``predict()`` and pass in the home and away teams.

```
outcome = p.predict('Stoke', 'Arsenal')
```

The model will return a dataframe containing the predicted outcome.

```
      AWAY       DRAW       HOME
PROB  57.105048  18.669206  24.219059

```

## Built With

MatchTeller was built with the following excellent pieces of software:

* [Numpy](http://www.numpy.org/) Numpy
* [Pandas](https://pandas.pydata.org/) Pandas
* [Scipy](https://www.scipy.org://www.scipy.org/) SciPy

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/apburton84/CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/apburton84/matchteller/tags).

## Authors

* **Anthony Burton** - *Initial work* - [apburton84](https://github.com/apburton84)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Help the python scientific community and [http://numfocus.wpengine.com/community/donate/](donate) to numfocus
