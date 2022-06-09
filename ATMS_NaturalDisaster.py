from datetime import datetime
import logging
Sn = 0
logging.basicConfig(filename=datetime.now().strftime('%d_%m_%Y.log'),
                    filemode='a',
                    format='%(asctime)s:%(msecs)d-%(name)s-%(levelname)s-%(message)s',
                    datefmt='%d_%m_%Y_%H:%M:%S',level=logging.DEBUG)

try:
    import requests
    from sinbad import *
    from datetime import datetime
    from math import sin, cos, sqrt, atan2, radians
    from datetime import datetime
    import time 
    import json
    import xml.etree.ElementTree as ET
except Exception as e:
    logging.error(e, exc_info=True)
    
try:
    tree = ET.parse('Earthquake.xml')
    root = tree.getroot()
    config_data = []
    for elem in root:
        for subelem in elem:
            config_data.append(subelem.text)
    configdistance = int(config_data[0])
    SendAPI = config_data[1]
    print(SendAPI)
    lat1 = float(config_data[2])
    long1= float(config_data[3])
except Exception as e:
    logging.error(e, exc_info=True)
    

def checklatlong(lat2,long2):
    R = 6373.0
    global lat1
    global long1
    lat1 = radians(lat1)
    lon1 = radians(long1)
    lat2 = radians(lat2)
    lon2 = radians(long2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    if distance<configdistance:
        return True
    else:
        return False

    
def main():
    global Sn
    ds = Data_Source.connect("http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson")
    ds.set_cache_timeout(180)    # force cache refresh every 3 minutes
    
    ds.load()    
    data = ds.fetch("title", "time", "mag", base_path = "features/properties")
    lst = []
    for d in data:
        Magnitude = d["mag"]
        Description = d["title"]
        Timestamp = d["time"]
        Timestamp = datetime.fromtimestamp(int(Timestamp)/1000).strftime("%Y-%m-%d %H:%M:%S")
        lst.append((Magnitude,Description,Timestamp))
    data = ds.fetch("coordinates", base_path = "features/geometry")
    #for d in data: 
    #print(data)
    del data[3-1::3]
    zipped = [(data[i],data[i+1]) for i in range(0,len(data),2)]
    #print(len(zipped))
    #print(zipped)
    #print("======================")
    earthquake = zip(lst,zipped)
    earthquakelist = list(earthquake)
    
    for item in earthquakelist:
        #print(item)
        #print("--------------------------------------")
        Magnitude = float(item[0][0])
        Descrption = item[0][1]
        Time =  item[0][2]
        lat = float(item[1][1])
        long = float(item[1][0])
        if checklatlong(lat,long)== True:
            print(Magnitude,Descrption,Time,lat,long)
            my_json_string = json.dumps(dict({'EntryId':Sn,'CategoryId':1,'EventType':11, 'EventMessage': Descrption,'EventDateTime':Time,'Latitude':lat,'Longitude':long,'Magnitude':Magnitude}))
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            Sn+=1
            r = requests.post(SendAPI, my_json_string,headers=headers)
            with open('JSON/Earthquake.json', 'w') as json_file:
                json.dump(dict({'EntryId':Sn,'CategoryId':1,'EventType':11, 'EventMessage': Descrption,'EventDateTime':Time,'Latitude':lat,'Longitude':long,'Magnitude':Magnitude}), json_file)
            
        else:
            pass

        
        
while True:
    try:
        main()
        time.sleep(100)
    except Exception as e:
        
        logging.error(e, exc_info=True)
        time.sleep(10)
    