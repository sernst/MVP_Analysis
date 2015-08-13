# __init__.py
# (C)2015
# Scott Ernst

from __future__ import \
    print_function, absolute_import, \
    unicode_literals, division

import os
import re

import sqlalchemy as sqla
import pandas as pd

from pyaid.file.FileUtils import FileUtils

ROOT_PROJECT_PATH = FileUtils.makeFolderPath(
    FileUtils.getDirectoryOf(__file__), '..', '..')

_data = None

#_______________________________________________________________________________
def getProjectPath(*args, **kwargs):
    """ Creates an absolute path from the relative path arguments within the
        project folder.
    """
    return FileUtils.createPath(ROOT_PROJECT_PATH, *args, **kwargs)

#_______________________________________________________________________________
def getResourcesPath(*args, **kwargs):
    """ Creates an absolute path from the relative path arguments within the
        project folder.
    """
    return FileUtils.createPath(ROOT_PROJECT_PATH, 'resources', *args, **kwargs)

#_______________________________________________________________________________
def getResultsPath(*args, **kwargs):
    """ Creates an absolute path from the relative path arguments within the
        project folder.
    """
    return FileUtils.createPath(ROOT_PROJECT_PATH, 'results', *args, **kwargs)

#_______________________________________________________________________________
def createEngine():
    """ Creates the SqlAlchemy engine to connect to the database and returns
        that engine.
    :return: Engine
    """
    path = getProjectPath('resources', 'lahman2014.sqlite', isFile=True)
    assert os.path.exists(path), \
        'ERROR: Missing Lahman 2014 database file at: %s' % path

    url = 'sqlite:///%s' % path
    return sqla.create_engine(url)

#_______________________________________________________________________________
def readTable(tableName):
    """ Returns a Pandas DataFrame populated with the structure and data of the
        specified table in the database.
    :param tableName: str
    :return: DataFrame
    """
    frame =  pd.read_sql_table(tableName, createEngine())
    columns = list(frame.columns)
    for index in range(len(columns)):
        columns[index] = getSafeColumnName(columns[index])

    frame.columns = columns
    return frame

#_______________________________________________________________________________
def echoDatabaseStructure():
    """ Returns a list of strings for logging or print out, each containing a
        summary of the fields in a table within the database.
    :return: list
    """
    out = ['DATABASE STRUCTURE:']
    with createEngine().connect() as conn:
        inspector = sqla.inspect(conn)

        for table in inspector.get_table_names():
            cols = []
            for column in inspector.get_columns(table):
                cols.append(getSafeColumnName(column['name']))
            out.append('[%s]: %s' % (table, ', '.join(cols)))
    return out

#_______________________________________________________________________________
def getSafeColumnName(name):
    """ Column names must begin with a letter character or underscore. If the
        name in question does not, it gets ab "X" prefixed to the name as is
        the convention in Pandas and other data science toolkits. Valid names
        are returned without editing.
    :param name: str
    :return: str
    """
    if re.compile('^[^a-zA-Z_]+').match(name):
        return 'X%s' % name
    return name
