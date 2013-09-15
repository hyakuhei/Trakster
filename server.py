from googlemaps import GoogleMaps
from flask import Flask, request, redirect, Response
import twilio.twiml
import random
app = Flask(__name__)

kmlHeader = """<?xml version="1.0" encoding="utf-8"?>
<kml xmlns="http://earth.google.com/kml/2.2">
<Document>
"""

kmlPlacemark = """
<Placemark>
    <name>%s</name>
      <ExtendedData>
        <Data name="Latitude">
          <value>
            %s
          </value>
        </Data>
        <Data name="Longitude">
          <value>
            %s
          </value>
        </Data>
        <Data name="Update">
          <value>
            %s
          </value>
        </Data>
        <Data name="Battery Level">
          <value>
            %s
          </value>
        </Data>
        <Data name="GSM Signal">
          <value>
            %s
          </value>
        </Data>
      </ExtendedData>
      <Point>
        <coordinates>
          %s,%s
        </coordinates>
   </Point>
</Placemark>
"""

kmlFooter = """
</Document>
</kml>
"""

kmlMeat = []
entries = []

def printRequest(req):
	print req
	print req.url
#	for key in req.__dict__.keys():
#		print "%s : %s" % (key, req.__dict__[key])

@app.route("/")
@app.route("/index")
def index():
	random.seed()
	printRequest(request)
	resp = """<html>
			<head>GSM Tracker</head>
			<body>
				<h2>View Track</h2>
				<ul>
					<li><a href='https://maps.google.co.uk/maps?q=http://15.185.254.46/kml/%i'>View track in Google Maps</a><Note, if the output needs refreshing, add an integer to the web address that appears in the search bar of google maps</li>
					<li><a href='http://15.185.254.46/kml'>Download KML to view in Google Earth</a></li>
				</ul>""" % random.randint(0,65535)

	resp += "<h3>Tracker Entries</h3>"
	resp+="<table><tr><td>Time</td><td>latitude</td><td>longitude</td><td>battery</td><td>signal</td></tr>"
	for entry in entries:
		resp+="<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (entry['time'],entry['latitude'],entry['longitude'],entry['battery'],entry['signal'])
		
	resp += "</table>"
	resp += "</body></html>"	
	return resp, 200

def addMeat(body):
	x = body.split()
	if len(x) != 4:
		return
	entry = {}
	entry['time'] = x[0]
	entry['coord'] = x[1]
	entry['latitude'] = entry['coord'].split(',')[0]
	entry['longitude'] = entry['coord'].split(',')[1]
	entry['battery'] = x[2]
	entry['signal'] = x[3]

	entries.append(entry)

	kmlMeat.append(kmlPlacemark % ((len(kmlMeat) +1),entry['latitude'],entry['longitude'],entry['time'],	entry['battery'],entry['signal'],entry['longitude'],entry['latitude']))

def kmlFile():
	kml = kmlHeader
	for k in kmlMeat:
		kml += k
	kml += kmlFooter
	return kml
	
def haversine(pos1, pos2):
    lat1 = float(pos1['lat'])
    long1 = float(pos1['long'])
    lat2 = float(pos2['lat'])
    long2 = float(pos2['long'])

    degree_to_rad = float(pi / 180.0)

    d_lat = (lat2 - lat1) * degree_to_rad
    d_long = (long2 - long1) * degree_to_rad

    a = pow(sin(d_lat / 2), 2) + cos(lat1 * degree_to_rad) * cos(lat2 * degree_to_rad) * pow(sin(d_long / 2), 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    km = 6367 * c
    mi = 3956 * c

    return {"km":km, "miles":mi}



@app.route("/incoming", methods=['GET'])
def incoming():
#	printRequest(request)
	if request.args.has_key('Body'):
		print request.args['Body']
		addMeat(request.args['Body'])	
		resp = twilio.twiml.Response()
		return str(resp), 200
	
	return 'Nope\n',404

@app.route("/kml",methods=['GET'])
def getkml():
	filestr = kmlFile()
	return Response(filestr,mimetype="application/vnd.google-earth.kml+xml",headers={'Content-Disposition':"attachment;filename=gpstrack.kml"})
#	return kmlFile(), 200

#Stupid hack, basically should get around the google caching of our pages
@app.route("/kml/<rand>",methods=['GET'])
def getkmlrand(rand):
	return getkml()

@app.route("/clean",methods=['GET'])
def clean():
	kmlMeat = []
	return 'Cleaned\n',200

if __name__ == '__main__':
	app.run(debug = True, host='0.0.0.0', port=80)
