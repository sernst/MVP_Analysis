import plotly.plotly as plotly
from plotly import graph_objs as plotlyGraphs
from plotly import tools as plotlyTools

fig = plotlyTools.make_subplots(
    rows=2, cols=3, specs=[
        [{}, {}, {}],
        [{'colspan':3}, None, None] ])

fig['data'] += plotlyGraphs.Data([
    plotlyGraphs.Histogram(
        name='T1',
        x=[1, 2, 3, 4, 5, 3, 3, 3, 4, 4, 5, 5, 5],
        marker=plotlyGraphs.Marker(
            color='red',
            line=plotlyGraphs.Line(width=0)),
        xaxis='x1', yaxis='y1'),

    plotlyGraphs.Scatter(
        name='T2',
        x=[2, 3, 4, 5, 6],
        y=[1, 2, 3, 4, 5],
        line=plotlyGraphs.Line(color='red'),
        xaxis='x2', yaxis='y2'),

    plotlyGraphs.Scatter(
        name='T3',
        x=[3, 4, 5, 6, 7],
        y=[1, 2, 3, 4, 5],
        xaxis='x3', yaxis='y3'),

    plotlyGraphs.Scatter(
        name='B1',
        x=[1, 2, 3, 4, 5],
        y=[-1, 1, -1, 1, -1],
        xaxis='x4', yaxis='y4'),

    plotlyGraphs.Scatter(
        name='B2',
        x=[1, 2, 3, 4, 5],
        y=[1, -1, 1, -1, 1],
        xaxis='x4', yaxis='y4'),

    plotlyGraphs.Scatter(
        name='B3',
        x=[1, 2, 3, 4, 5],
        y=[2, -2, 2, -2, 2],
        xaxis='x4', yaxis='y4') ])

print(plotly.plot(fig, filename='test-1'))
