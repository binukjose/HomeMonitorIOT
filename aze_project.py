#cloud libraris 
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

def initializeCloudConn():
    currentUser = "a@b.com"
    cred = credentials.Certificate("./home-monitor-service.json")
    app = firebase_admin.initialize_app(cred, {
        'databaseURL' : 'https://home-monitor-d6760.firebaseio.com/'
    })

    ref = db.reference('/')
    print(ref.get())
    ref = db.reference('/users')
    return ref

def getCloudData( ref):
    currentUser = "a@b.com"

    #queryResults = ref.order_by_key().end_at("l\.com").get()
    queryResults = ref.order_by_child('email').equal_to(currentUser).limit_to_first(1).get()

    #print (queryResults)

    #for item in queryResults.values():
    #    print (item)

    print("alarm state for user", currentUser, " = ", queryResults[0]['alarmState'])
    return  queryResults[0]['alarmState']



#Iot libraries 
import Adafruit_DHT
import RPi.GPIO as GPIO 
import time

#initilaze 
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

#channels 
soundCh = 17
buzzerCh = 27 

#flags
aF = False  #alaram flag 

#GPIO settings
GPIO.setwarnings (False)
GPIO.setmode (GPIO.BCM)
GPIO.setup(soundCh , GPIO.IN)
GPIO.setup(buzzerCh, GPIO.OUT)

def tempHumidity():
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        print ("Temp={0:0.1f}C ".format(temperature))
        print ("Humidity = {0:0.1f}%".format(humidity))
    else:
        print ("Fault: ") 

def soundDectected(inputchannel):
    #sensor is not working !!!!
    if GPIO.input(soundCh ) :
        print ("soundDectected True")
    else:
        print ("soundDectected False")   


GPIO.add_event_detect(soundCh , GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(soundCh , soundDectected)


def buzzer( aFlg):
    fFlag = not aFlg #true-no buzzer , false=buzzer 
    GPIO.output(buzzerCh, fFlag)
    print ("aFlg={0}", aFlg)   

def mainLoop():
    ref = initializeCloudConn()
    while True:
        aF = getCloudData(ref) #get the alarm flag as return 
        buzzer(aF) #buzzer if needed

        #read humidity and temparature and upload 
        tempHumidity()
        
        time.sleep(3)    

try :
    mainLoop()
except KeyboardInterrupt:
    
    GPIO.cleanup()
    exit



    