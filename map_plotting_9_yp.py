import sys
import json
from  pprint import pprint
from time import sleep

import plotly as py
from plotly.graph_objs import *
from googlemaps import Client

from privateKeys import googleMapsKey, mapbox_access_token

#API Keys
GoogleMaps = Client(googleMapsKey)

# Parse the file
def parseSAMIEEE_CSV(filename):
    raw_addresses=[]
    with open(filename) as f:
        header=f.readline()
        indices=[]
        for i,col in enumerate(header.split(',')):
            if 'Primary Address' in col:
                indices.append(i)
            if 'Current Grade Description' in col:
                memberGrade = i
        for line in f:
            raw_data = line.strip().split(',')
            address=''
            for i in indices:
                address += raw_data[i]+' '
            raw_addresses.append(address)
    return raw_addresses

# Pull all of the geocode data
def loadGeocodeData(raw_addresses):
    print('Loading geocode data.',end='')
    step=len(raw_addresses)/100
    results=[]
    status_index=0
    for address in raw_addresses:
        geocode_data = GoogleMaps.geocode(address)
        if geocode_data != []:
            status_index = status_index + 1
            results.append(geocode_data)
        sleep(0.05) # Not to overload API call
        if status_index % step == 0:
            print('.',end='')
    print('Completed.')
    return results
        
def generateLatitudeLongitude(geocodeData):
    print('Processing '+str(len(geocodeData))+' data points...')
    latitude = []
    longitude = []

    for index in range(len(geocodeData)):
        parsed = geocodeData[index][0]
        latitude.append(parsed['geometry']['location']['lat'])
        longitude.append(parsed['geometry']['location']['lng'])
    return (latitude,longitude)

def generateHTML(latitude,longitude,outputFile):
    data = Data([
        Scattermapbox(
            lat=latitude,
            lon=longitude,
            mode='lines+markers',
            marker=Marker(size=9),
        )
    ])
    midLat = (min(latitude)+max(latitude)) / 2
    midLng = (min(longitude)+max(longitude)) / 2
    layout = Layout(
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat = midLat,
                lon = midLng,
            ),
            pitch=0,
            zoom=14
        ),
    )

    fig = dict(data=data, layout=layout)
    py.offline.plot(fig, filename=outputFile, validate=False)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Error: python map_plotting_9_yp.py <input_file>')
        exit()
    raw_addresses = parseSAMIEEE_CSV(sys.argv[1])
    if len(raw_addresses) != 0:
        geocodeData=loadGeocodeData(raw_addresses)
    else:
        print('Error: No data to load, check file.')
        exit()
    latitude,longitude = generateLatitudeLongitude(geocodeData) # returns (latitude[],longitude[])
    generateHTML(latitude,longitude,'Mapbox_IEEE_YP.html')
