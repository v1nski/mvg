from datetime import datetime
import sqlite3 as sl

con = sl.connect('tracker.db')

with con:
    sql = """
            SELECT timestamp FROM abfahrten
    """
    cur = con.cursor()
    cur.execute(sql)
    time = cur.fetchall()

    for t in time:
        t2 = t[0] - 60*70
        sql = """
                UPDATE abfahrten SET timestamp = ?, time = ? WHERE timestamp = ?
        """
        variables = (t2, datetime.fromtimestamp(t[0]),t[0])
        cur.execute(sql, variables)