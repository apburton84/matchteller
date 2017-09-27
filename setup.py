from io import open

from setuptools import find_packages, setup

with open('matchteller/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip(' \'"')
            break
    else:
        version = '0.0.1'

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()


REQUIRES = [
            'numpy', 'pandas', 'scipy', 'tabulate', 'matplotlib', 'seaborn', 'ipython'
        ]

setup(
    name='matchteller',
    version=version,
    description='',
    long_description=readme,
    author='Anthony Burton',
    author_email='apburton84@googlemail.com',
    maintainer='Anthony Burton',
    maintainer_email='apburton84@googlemail.com',
    url='https://github.com/apburton84/matchteller',
    license='MIT/Apache-2.0',

    keywords=[
        '',
    ],

    classifiers=[
        'Development Status :: 0.1.0 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved ::  BSD-2-Clause',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    install_requires=REQUIRES,
    tests_require=['coverage', 'pytest'],

    packages=find_packages(),
)
