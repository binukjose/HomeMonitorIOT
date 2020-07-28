#cloud libraris 
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import messaging

def initializeCloudConn(email):
    currentUser = email
    cred = credentials.Certificate("./home-monitor-service.json")
    app = firebase_admin.initialize_app(cred, {
        'databaseURL' : 'https://home-monitor-d6760.firebaseio.com/'
    })

    ref = db.reference('/users')
    #queryResults1 = ref.get()
    #print (queryResults1)
    #exit()


    queryResults = ref.order_by_child('email').equal_to(currentUser).limit_to_first(1).get()
    if(queryResults == None ): 
        print("There is no user with email: ", currentUser)
        cleanExit()
    #print ("len = " , len(queryResults))
    print (queryResults)


    '''
    exit()
    '''
    items = list(queryResults.items())
    userId = items[0][0]
    
    ref = db.reference('/users/' + userId) 
    print ("userid:",userId)
    
    #userId = queryResults[0]
    #print ("user id" , userId)
    #for item in queryResults.values():
    #    print (item)
    #print("alarm state for user", currentUser, " = ", queryResults['alarmState'])
    #return  queryResults[0]['alarmState']
    
    return ref

def getCloudData( ref):
    
    node = ref.get()
    #print ("getCloudData" , node)
    return node['alarmState'],node['enableMotionSensor'],node['enableSoundSensor']
    

def sendTempHumToCloud(node,temp, hum):
    
    if(temp > 0.1) :
        node.update({ 
            'temperature': temp
        })
    if(hum > 0.1) :
            node.update({ 
            'humidity': hum
        })
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
motionCh= 22

#flags
aF = False  #alaram flag 

#GPIO settings
GPIO.setwarnings (False)
GPIO.setmode (GPIO.BCM)
GPIO.setup(soundCh , GPIO.IN)
GPIO.setup(buzzerCh, GPIO.OUT)
GPIO.setup(motionCh , GPIO.IN, GPIO.PUD_DOWN)

def tempHumidity():
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        pass
    else:
        print ("Fault: ") 
        humidity = 0
        temperature = 0 
    #convert to faranheat 
    temperature = (temperature * 9/5) + 32 
    #print ("Temp={0:0.1f}F ".format(temperature))
    #print ("Humidity = {0:0.1f}%".format(humidity))
    return temperature, humidity

def soundDectected(inputchannel):
    #sensor is not working !!!!
    if GPIO.input(soundCh ) :
        print ("soundDectected True")
    else:
        print ("soundDectected False")   


def motionDectected(node):
    if GPIO.input(motionCh) :
        print ("motionDectected True")
        motion = True
    else:
        #print ("motionDectected False")
        motion = False
    
    node.update({ 
    'motionDectected': motion
    }) 
    return motion


def buzzer( aFlg):
    fFlag = not aFlg #true-no buzzer , false=buzzer 
    GPIO.output(buzzerCh, fFlag)


## alert messages to the user app
def sendMotoinAlert():
    pass


def mainLoop(email):

    #add callback events for sound and motion 
    GPIO.add_event_detect(soundCh , GPIO.BOTH, bouncetime=300)
    GPIO.add_event_callback(soundCh , soundDectected)
    # sound sensor not working 

    ref = initializeCloudConn(email)
    while True:
        #print (ref)
        alarmFlag,motionFlag,soundFlag = getCloudData(ref) #get the alarm flag, motionflag, soundFlag as return 
        
        print ("alarmFlag=",alarmFlag," motionFlag=",motionFlag, "soundFlag=",soundFlag )
        buzzer(alarmFlag) #buzzer if needed

        #read humidity and temparature and upload 
        temperature, humidity = tempHumidity()
        sendTempHumToCloud(ref, temperature, humidity)
        
        motion = False
        if(motionFlag) :
            motion = motionDectected(ref)

        if(motion):
            sendMotoinAlert()

        time.sleep(3)    

def cleanExit():
    GPIO.cleanup()
    exit()

#Mian program starts here 
import sys
if( len(sys.argv) != 2):
    print ('Usage:')    
    print ('aze_project.py <user-emailid>')    
    cleanExit
try :
    email = str (sys.argv[1])
    #print(email)
    mainLoop(email)
except KeyboardInterrupt:
    cleanExit()



    