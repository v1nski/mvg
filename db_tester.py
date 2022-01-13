from datetime import datetime as dt
from math import floor
import sqlite3 as sl

db_name = "tracker.db"


def get_cancelled(con, start=0, end=9999999999):
    cur = con.cursor()
    sql="""
        SELECT cancelled FROM delays WHERE timestamp >= ? AND timestamp < ? AND cancelled > 0
    """
    variables = (start, end)
    cur.execute(sql, variables)
    res = cur.fetchall()
    total_cancelled = 0
    for single in res:
        total_cancelled += single[0]
    return total_cancelled


def get_total_trains(con, start=0, end=9999999999):
    cur = con.cursor()
    sql="""
        SELECT n_trains FROM delays WHERE timestamp >= ? AND timestamp < ?
    """
    variables = (start, end)
    cur.execute(sql, variables)
    res = cur.fetchall()
    total_trains = 0
    for single in res:
        total_trains += single[0]
    return total_trains


def get_total_delay(con, start=0, end=9999999999):
    cur = con.cursor()
    sql="""
        SELECT delay, n_trains FROM delays WHERE timestamp >= ? AND timestamp < ?
    """
    variables = (start, end)
    cur.execute(sql, variables)
    res = cur.fetchall()
    total_delay = 0
    for single in res:
        total_delay += single[0] * single[1]
    return total_delay


def minutes_to_time(minutes):
    days = floor(minutes/(60*24))
    minutes = minutes % (60*24)
    hrs = floor(minutes/60)
    minutes = int(minutes % 60)

    time = ""
    if days>0:
        time += f"{days} days "
    if hrs>0:
        time += f"{hrs}h "
    if minutes>0:
        time += f"{minutes}"
    
    return time



def main():
    con = sl.connect(db_name)
    with con:
        tot_canc = get_cancelled(con)
        tot_delay = get_total_delay(con)
        tot_trains = get_total_trains(con)
    con.close()

    time_string = ""
    if tot_delay > 59:
        time_string = "or " + minutes_to_time(tot_delay)

    if tot_trains > 0:
        print(f"Total departures: {tot_trains}\nTotal delay: {int(tot_delay)} minutes {time_string}\nAverage delay: {round(tot_delay/tot_trains,2)} minutes\nCancelled departures: {tot_canc} or {round(100*tot_canc/tot_trains,2)}%")


main()