from datetime import datetime
import sqlite3 as sl

con = sl.connect('tracker.db')

with con:
        sql = """
                CREATE TABLE departures(
                        id INTEGER PRIMARY KEY,
                        station TEXT,
                        label TEXT,
                        destination TEXT,
                        timestamp TIMESTAMP,
                        time DATETIME,
                        delay TINYINT,
                        cancelled BOOL
                )"""
        con.execute(sql)
        sql = """
                CREATE TABLE routes(
                        id INTEGER PRIMARY KEY,
                        station TEXT,
                        destination TEXT,
                        label TEXT
                )"""
        con.execute(sql)
        sql = """
                CREATE TABLE delays(
                        id INTEGER PRIMARY KEY,
                        route_id TINYINT NOT NULL,
                        timestamp TIMESTAMP,
                        time DATETIME,
                        delay SMALLINT,
                        cancelled TINYINT,
                        n_trains SMALLINT,
                        FOREIGN KEY(route_id)
                                REFERENCES routes (id)
                )
        """
        con.execute(sql)