from config import *
from time import ctime
import time
import ntplib
import json
import socket
import threading
from threading import Event
import RPi.GPIO as GPIO
 
#GPIO Pin Definitions
RED_LED = int(17)
GREEN_LED = int(27)
YELLOW_LED = int(22)
 
LED_pin_dict = {"red":RED_LED,"yellow":YELLOW_LED,"green":GREEN_LED}


# -------------------------- Variables ----------------

CONTROLLER_DATA = [None, None, None, None]

FAILSAFE_EVENT = False
FAIL_SAFE_ACK_RECEIVED = False

SYNC_SUCCESS = Event()
START_SUCCESS = Event()
DATA_SUCCESS = Event()

MASTER_SYNC_SUCCESS = True
RECIEVED_START_TIME = time.localtime()
IS_NTP_TIME_SET = True
READ_QUEUE_FLAG = Event()

master_send_lock = threading.Lock()
master_rec_lock = threading.Lock()
slave_lock = threading.Lock()
general_lock = threading.Lock()


# ---------------------------- FUNCTIONS -------------------

def ntp_time_sync_master():
    global MASTER_SYNC_SUCCESS
    global IS_NTP_TIME_SET
    try:
        client = ntplib.NTPClient()
        # response = client.request("pool.ntp.org", version=3)
        response = client.request("ntp.nic.in")
        if response:
            IS_NTP_TIME_SET = True
        return ctime(response.tx_time)
    
    except Exception as e:
        print(f"Failed to synchronise time: {e}")
        fail_safe_transmitter()
        return time.time()

def gpio_setup():
    # GPIO Setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RED_LED, GPIO.OUT)
    GPIO.setup(GREEN_LED, GPIO.OUT)
    GPIO.setup(YELLOW_LED, GPIO.OUT)
    # for pin in LED_pin_dict.values():
    #     GPIO.output(pin, GPIO.LOW)
    # pass
def gpio_set(LED_state):
    # Turn on the selected LED
    GPIO.output(LED_pin_dict[LED_state], GPIO.HIGH)
    print("GPIO SET TO ", LED_state)

# -------------------- MULTICAST FUNCTIONS -------------------

def multicast_send(message):
    message = json.dumps(message)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sock.sendto(message.encode(), (MULTICAST_GROUP, PORT))


def multicast_recieve():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        sock.bind(('', PORT))
        # mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
        group = socket.inet_aton(MULTICAST_GROUP)
        mreq = group + socket.inet_aton('0.0.0.0')
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        while True:
            data, _ = sock.recvfrom(1024)
            yield json.loads(data.decode())



# ----------------- FAILSAFE TRANSMIT --------------
def fail_safe_transmitter():
    global FAILSAFE_EVENT
    
    multicast_send(FAILSAFE_MESSAGE)
    FAILSAFE_EVENT = True
    print("Failsafe Triggered")