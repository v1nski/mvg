import mvg_api as mvg
import sqlite3 as sl
import datetime
import json


def update(station, station_id):
    departures = mvg.get_departures(station_id)

    result = 0
    con = sl.connect('tracker.db')
    with con:
        sql = """
            SELECT MAX(timestamp) FROM departures WHERE station = ?
        """
        cur = con.cursor()
        entry = (station,)
        cur.execute(sql, entry)
        x = cur.fetchone()
        for z in x:
            if z != None:
                result += z

    for departure in departures:
        if departure["product"]=="UBAHN" and not int(departure["departureTime"]/1000) <= result:
            destination = departure["destination"]
            timestamp = departure["departureTime"]/1000
            time = datetime.datetime.fromtimestamp(timestamp)
            label = departure["label"]
            delay = departure["delay"]
            cancelled = departure["cancelled"]

            with con:
                sql = """
                    INSERT INTO departures (station, label, destination, timestamp, time, delay, cancelled)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                cur = con.cursor()
                entry = (station, label, destination, timestamp, time, delay, cancelled)
                cur.execute(sql, entry)
                con.commit()
        else:
            timestamp = departure["departureTime"]/1000
            try:
                delay = departure["delay"]
            except KeyError:
                delay = 0

            cancelled = departure["cancelled"]
            with con:
                sql = """
                    UPDATE departures
                    SET delay = ?, cancelled = ?
                    WHERE timestamp = ? AND station = ?
                """
                cur = con.cursor()
                entry = (delay, cancelled, timestamp, station)
                cur.execute(sql, entry)
                con.commit()


def find_new_routes():
    routes = []
    con = sl.connect('tracker.db')
    with con:
        sql = """
            SELECT station, destination, label FROM routes
        """
        cur = con.cursor()
        cur.execute(sql)
        old_routes = cur.fetchall()

        sql = """
            SELECT station, destination, label FROM departures ORDER BY id DESC LIMIT 200
        """
        cur.execute(sql)
        results = cur.fetchall()

        for new_route in results:
            known = False
            for known_route in routes:
                if new_route == known_route:
                    known = True
                    break
            for known_route in old_routes:
                if new_route == known_route:
                    known = True
                    break
            if not known:
                routes.append(new_route)

        return routes


def update_routes():
    new_routes = find_new_routes()
    con = sl.connect('tracker.db')
    with con:
        sql = """
            INSERT INTO routes (station, destination, label) VALUES (?, ?, ?)
        """
        cur = con.cursor()

        for route in new_routes:
            cur.execute(sql, route)


def get_average_delay(dep, dest, start_time, dt):
    min_tm = start_time
    max_tm = start_time + dt # T -1hr

    con = sl.connect('tracker.db')
    with con:
        sql = """
            SELECT delay, cancelled FROM departures WHERE station = ? AND destination = ? AND timestamp < ? AND timestamp > ?
        """
        variables = (dep, dest, max_tm, min_tm)
        cur = con.cursor()
        cur.execute(sql, variables)
        results = cur.fetchall()
        n_res = 0
        av_delay = 0
        n_canc = 0
        for res in results:
            n_res += 1
            av_delay += res[0] # get total delay
            n_canc += res[1]
        if n_res > 0:
            av_delay /= n_res
        return (av_delay, n_canc, n_res)


def process_delays():   
    # I:    get first timestamp
    # II:   check for overlap
    # III:  get all routes
    # IV:   calculate average delays
    # V:    input to delay-table
    # VI:   delete rows from departure-table

    dt = 60*60

    con = sl.connect('tracker.db')
    with con:
        # I:    get first timestamp
        sql = """
            SELECT MIN(timestamp) FROM departures LIMIT 1
        """
        cur = con.cursor()
        cur.execute(sql)
        (timestamp,) = cur.fetchone()
        if timestamp == None:
            print("ERROR: There are no departures to be processed")
            return False

        # II:    check overlap
        sql = """
            SELECT MAX(timestamp) FROM delays LIMIT 1
        """
        cur.execute(sql)
        (last_tm,) = cur.fetchone()
        if not last_tm == None and timestamp < last_tm:
                print("ERROR: There already exist later delays")
                return False
        elif timestamp + dt> datetime.datetime.timestamp(datetime.datetime.now()):
            print(timestamp)
            print(datetime.datetime.timestamp(datetime.datetime.now()) - 60*60)
            print("ERROR: Cannot set future departures")
            return False

        # II:   get all routes
        sql = """
            SELECT id, station, destination FROM routes
        """
        cur.execute(sql)
        routes = cur.fetchall()

        for (route_id, dep, dest) in routes:
            # III:  calculate average delays
            (delay, canc, n_trains) = get_average_delay(dep, dest, timestamp, dt)

            # IV:   input to delay-table
            print(n_trains)
            if n_trains > 0:
                sql = """
                    INSERT INTO delays (route_id, timestamp, time, delay, cancelled, n_trains) VALUES (?, ?, ?, ?, ?, ?)
                """
                variables = (route_id, timestamp, datetime.datetime.fromtimestamp(timestamp), delay, canc, n_trains)
                cur.execute(sql, variables)

        # V:    delete rows from departure-table
        sql = """
            DELETE FROM departure WHERE timestamp >= ? AND timestamp <= ?
        """
        variables = (timestamp, timestamp + dt)
        cur.execute(sql, variables)

    return True


dep_names = [['Scheidplatz', 'de:09162:400'], ['Muenchner Freiheit', 'de:09162:500'], ['Sendlinger Tor', 'de:09162:50'], ['Hauptbahnhof', 'de:09162:6'], ['Marienplatz', 'de:09162:2']]

#for station in dep_names:
#    station.append(mvg.get_id_for_station(station[0]))

for station in dep_names:
    print(station[0])
    update(station[0], station[1])

update_routes()

res = True
while res:
    res = process_delays()