# evolution.py
# (C)2015
# Scott Ernst

from __future__ import \
    print_function, absolute_import, \
    unicode_literals, division

import numpy as np
from scipy import stats
import pandas as pd

import plotly.plotly as plotly
from plotly import graph_objs as plotlyGraph
from plotly import tools as plotlyTools

#===============================================================================
#                                                                 P U B L I C

#_______________________________________________________________________________
def generatePercentiles(batting, fields, doPlots =True):
    """ Calculates the percentiles and returns a new batting DataFrame with the
        additional percentile columns listed in the fields. Plotly plots are
        also generated if the doPlots argument is True.
    :param batting: DataFrame
    :param fields: dict
    :param doPlots: bool
    :return: DataFrame
    """
    batting = batting.copy()

    fieldData = []
    for key, title in fields.items():
        percentileColumnName = 'per' + key
        teamPercentileColumnName = 'tper' + key
        batting.loc[:, percentileColumnName] = 0.0
        batting.loc[:, teamPercentileColumnName] = 0.0

        fieldData.append(dict(
            sourceColumnName=key,
            evolution=dict(
                traces=[],
                title='Evolution: Yearly %s' % title,
                filename='MLB/Yearly-%s-evolution' % title.replace(' ', '-') ),
            yearly=dict(
                columnName=percentileColumnName,
                title='Yearly %s' % title,
                filename='MLB/Yearly-%s' % title.replace(' ', '-') ),
            team=dict(
                columnName=teamPercentileColumnName,
                title='Team Yearly %s' % title,
                filename='MLB/Team-Yearly-%s' % title.replace(' ', '-') )))

    #---------------------------------------------------------------------------
    # SLICING
    #   For each year in the data calculate a percentile field for each field
    #   definition. Also calculate for each year the percentile in the within
    #   the player's team.
    for year in batting.yearID.unique():
        yearSlice = batting[batting.yearID == year].copy()

        for entry in fieldData:
            columnName = entry['yearly']['columnName']
            yearSlice = _calculatePercentilesInSlice(
                dataSlice=yearSlice,
                sourceColumnName=entry['sourceColumnName'],
                targetColumnName=columnName)

            if doPlots:
                entry['evolution']['traces'].append(plotlyGraph.Box(
                    y=list(yearSlice[columnName].values),
                    name='%s' % year))

            for teamID in yearSlice.teamID.unique():
                columnName = entry['team']['columnName']
                teamSlice = _calculatePercentilesInSlice(
                    dataSlice=yearSlice[yearSlice.teamID == teamID].copy(),
                    sourceColumnName=entry['sourceColumnName'],
                    targetColumnName=columnName)

                yearSlice = teamSlice.combine_first(yearSlice)

        batting = yearSlice.combine_first(batting)

    if not doPlots:
        return batting

    #---------------------------------------------------------------------------
    # PLOT RESULTS
    #       Merge the percentile data back into the batting table and slice out
    #       the MVP data for plotting
    mvps = batting[batting.MVP]

    for entry in fieldData:
        _plotEvolutionData(entry)
        _plotFieldData(columnData=entry, mvps=mvps)

    return batting

#===============================================================================
#                                                           P R O T E C T E D

#_______________________________________________________________________________
def _calculatePercentilesInSlice(dataSlice, sourceColumnName, targetColumnName):
    """ Calculates the percentiles in the slice and adds those values to the
        slice's target column. """
    values = dataSlice[sourceColumnName].values
    mn = values.mean()
    std = values.std()
    percentiles = []
    for value in values:
        percentiles.append(100.0*stats.norm.cdf((mn - value)/std))

    dataSlice.loc[:, targetColumnName] = pd.Series(
        data=np.array(percentiles),
        index=dataSlice.index)
    return dataSlice

#_______________________________________________________________________________
def _plotEvolutionData(columnData):
    columnSubData = columnData['evolution']

    d = plotlyGraph.Data(columnSubData['traces'])
    l = plotlyGraph.Layout(
        title=columnSubData['title'],
        showlegend=False)

    url = plotly.plot(
        plotlyGraph.Figure(data=plotlyGraph.Data(d), layout=l),
        filename=columnSubData['filename'],
        auto_open=False)

    print('EVOLUTION[%s]: %s' % (columnData['sourceColumnName'], url))

#_______________________________________________________________________________
def _plotFieldData(columnData, mvps):
    srcKey = columnData['sourceColumnName']

    fig = plotlyTools.make_subplots(
        rows=2, cols=3,
        print_grid=False,
        specs=[
            [{}, {}, {}],
            [{'colspan':2}, None, {}]])

    traces = list()

    traces.append(_createHistogram(
        index=1,
        color='blue',
        label='Percentile in Year (%)',
        data=mvps[columnData['yearly']['columnName']]))
    traces.append(_createHistogram(
        index=2,
        color='purple',
        label='Percentile in Team (%)',
        data=mvps[columnData['team']['columnName']] ))
    traces.append(_createHistogram(
        index=3,
        color='red',
        label='Absolute',
        data=mvps[srcKey] ))

    traces.append(_createCumulativeDistributionPlot(
        index=4,
        color='blue',
        label='Percentile CD',
        series=mvps[columnData['yearly']['columnName']]))
    traces.append(_createCumulativeDistributionPlot(
        index=4,
        color='purple',
        label='Team Percentile CD',
        series=mvps[columnData['team']['columnName']]))
    traces.append(_createCumulativeDistributionPlot(
        index=4,
        color='red',
        label='Absolute CD',
        series=mvps[srcKey]))

    fig['data'] += plotlyGraph.Data(traces)
    fig['layout'].update(title=columnData['yearly']['title'])

    url = plotly.plot(
        fig,
        filename=columnData['yearly']['filename'],
        auto_open=False)

    print('STATS[%s]: %s' % (srcKey, url))

#_______________________________________________________________________________
def _createHistogram(index, color, data, label):
    return plotlyGraph.Histogram(
        name=label,
        x=data,
        xaxis='x%s' % int(index),
        yaxis='y%s' % int(index),
        marker=plotlyGraph.Marker(
            color=color,
            line=plotlyGraph.Line(width=0)) )

#_______________________________________________________________________________
def _createCumulativeDistributionPlot(index, series, color, label):
    density = np.histogram(a=series.values, bins=20)
    return plotlyGraph.Scatter(
        name=label,
        x=density[1][:-1],
        xaxis='x%s' % int(index),
        yaxis='y%s' % int(index),
        line=plotlyGraph.Line(color=color),
        y=density[0].cumsum()/density[0].sum())
