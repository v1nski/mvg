import mvg_api as mvg
import json
import datetime

dep_name = "Dülferstraße"
arr_name = "Garching Forschungszentrum"

id_dep = mvg.get_id_for_station(dep_name)
id_arr = mvg.get_id_for_station(arr_name)

#departures = mvg.get_departures(id_dep)
#lines = mvg.get_lines(id_dep)
route = mvg.get_route(id_dep, id_arr, bus=False, tram=False, sbahn=False)

file = open("out.txt","w")

cntr = 0
for line in route:
    conn = line["connectionPartList"]

    t_start = datetime.datetime.fromtimestamp(line["departure"]/1000)
    t_end = datetime.datetime.fromtimestamp(line["arrival"]/1000)
    t_span = (line["arrival"] - line["departure"])/1000/60
    timespan = "Timespan: " + str(t_start) + " => " + str(t_end) + "   |   " + str(t_span) + " minutes\n"
    
    file.write(timespan)
    file.write(dep_name)

    for s_conn in conn:
        stops = s_conn["stops"]

        for s_stop in stops:
            print(s_stop["location"]["name"])
            t = s_stop["time"]/1000
            t2 = str(datetime.datetime.fromtimestamp(t))

            file.write("  ->  " + s_stop["location"]["name"] + " at " + t2)
            
        file.write("  ->  " + s_conn["to"]["name"] + "\n")

    #file.write(f"  ->  {arr_name}\n\n------------------------\n\n") 



    file.write("\n\n----------------\n\n")
    cntr += 1
    if cntr > 3:
        break
file.close()


#print(f"{dep_name}: {route}")
#print(id_arr)