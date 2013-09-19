import requests,time,random,os
##
#Test Options
##
NUM_POINTS = 20
MAX_DRIFT_LONG = 0.01
MAX_DRIFT_LAT = 0.015

START_LONG = 52.484015316712851
START_LAT = -4.060090713045001
WINDOW = 60,200

##
# Test Code
##

now = int(round(time.time()*1000))
random.seed(now)
host = os.getenv('TRAKHOST','15.185.254.46') 

for i in range(0,NUM_POINTS):
    now += random.randint(WINDOW[0],WINDOW[1]) * 1000
    START_LONG += random.uniform(0,MAX_DRIFT_LONG)
    START_LAT -= random.uniform(0,MAX_DRIFT_LAT)
    reqStr = "http://%s/incoming?Body=%i+%.14f%%2C%.14f+90+-1" % (
            host,
            now,
            START_LONG,
            START_LAT
    )

    r = requests.get(reqStr)
    print "%s ::: %s" % (reqStr, r.status_code)