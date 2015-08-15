# run.py
# (C)2015
# Scott Ernst

from __future__ import \
    print_function, absolute_import, \
    unicode_literals, division

import pandas as pd

from pyaid.file.FileUtils import FileUtils

FileUtils.addToSysPath(
    FileUtils.makePathFromFile(__file__, 'src', 'mlb'))

import mlb
from mlb.analysis import evolution

#-------------------------------------------------------------------------------
# INITIALIZATION

START_YEAR = 1963
MINIMUM_AT_BATS = 25

# Database Structure
print('\n'.join(mlb.echoDatabaseStructure()))

batting = mlb.readTable('Batting')
awards = mlb.readTable('AwardsPlayers')
pitching = mlb.readTable('Pitching')

#-------------------------------------------------------------------------------
# TRANSFORM BATTING DATA

awards['MVP'] = (awards.awardID == 'Most Valuable Player')
batting = pd.merge(
    left=batting,
    right=awards[['playerID', 'yearID', 'MVP']],
    how='left',
    on=['playerID', 'yearID'])
batting.MVP.fillna(False, inplace=True)

batting = batting[
    (batting.yearID > START_YEAR) &
    (batting.AB >= MINIMUM_AT_BATS)]

# Pitchers handled separately
batting = batting[~batting.playerID.isin(pitching.playerID)]

b = batting
b['BA'] = b.H/b.AB
b['X1B'] = b.H - b.X2B - b.X3B - b.HR
b['OBP'] = (b.H + b.BB + b.HBP)/(b.AB + b.BB + b.HBP + b.SF)
b['TB'] = b.X1B + 2*b.X2B + 3*b.X3B + 4*b.HR
b['SLUG'] = (b.X1B + 2*b.X2B + 3*b.X3B + 4*b.HR)/b.AB
b['OPS'] = b.OBP + b.SLUG
b['SLUGMAX'] = (b.X1B + 2*b.X2B + 4*b.HR)/b.AB

batting = evolution.generatePercentiles(
    batting=batting,
    fields=dict(
        BA='Batting Averages',
        HR='Home Runs',
        OBP='OBP',
        X1B='1st Bases',
        X2B='2nd Bases',
        X3B='3rd Bases',
        SLUG='Slugging',
        SLUGMAX='Slugging (Adjusted)'))

#-------------------------------------------------------------------------------
# EXPLORE MVP

mvps = batting[batting.MVP]
print('Minimum at bats: %s' % mvps.AB.values.argmin())
print('MVP Count: %s' % int(batting.MVP.sum()))
