from config import *
from common import *

# ------------- SYNC ---------------------------------
def reliable_sync_request_master():
    global RETRIES
    global FAILSAFE_EVENT
    global SYNC_SUCCESS
    global MASTER_SYNC_SUCCESS
    global SEQUENCE_NO
    while(not(FAILSAFE_EVENT) and not(SYNC_SUCCESS) and MASTER_SYNC_SUCCESS):
        multicast_send(SYNC_REQ_MESSAGE)
        print("Sent message")
        time.sleep(RTO)
        print("Waited for RTO")
        if(RETRIES==MAX_RETRIES):
            fail_safe_transmitter()
            RETRIES = 0
        else:
            RETRIES += 1


def reliable_sync_ack_master():
    global FAILSAFE_EVENT
    global SYNC_SUCCESS
    received_acks = set()
    while(not(FAILSAFE_EVENT) and not(SYNC_SUCCESS)):
        received_pkt = next(multicast_recieve())
        if(received_pkt["type"]=="sync_ack"):
            print(received_pkt)
            received_acks.add(received_pkt["controller_id"])
            if(len(received_acks)==DEVICES-1):
                SYNC_SUCCESS = True
                print("sync_success = ",SYNC_SUCCESS)
                received_acks = set()



def is_ntp_time_sync_set():
    #TODO NTP SYNC
    return True
    
def handle_sync_requests():
    global SYNC_SUCCESS
    global FAILSAFE_EVENT
    while (not(SYNC_SUCCESS) and not(FAILSAFE_EVENT)):
        message = next(multicast_recieve())
        if message["type"] == "sync_request":
            print("Received sync request", message["controller_id"])
            if is_ntp_time_sync_set():
                multicast_send(SYNC_ACK_MESSAGE)
                print("Sent SYNC ACK")
            else:
                print("NTP TIME NOT SYNCED")
                fail_safe_transmitter()

# ------------------- START REQUEST ---------------------------
def addOffset(ntp_time,time_offset):
    ntp_timestamp = time.mktime(ntp_time) 
    ntp_time_offset = ntp_timestamp + time_offset
    ntp_time_offset_struct = time.localtime(ntp_time_offset)
    return ntp_time_offset_struct

def reliable_start():
    global FAILSAFE_EVENT
    global SYNC_SUCCESS
    global RETRIES
    global START_SUCCESS
    # global received_start_time
    while(not(FAILSAFE_EVENT) and not(SYNC_SUCCESS) and not(START_SUCCESS)):
        continue
    START_REQ_MESSAGE["timestamp"] = addOffset(time.localtime(),TIME_OFFSET)
    while(not(FAILSAFE_EVENT) and SYNC_SUCCESS and not(START_SUCCESS)):
        # received_start_time = START_REQ_MESSAGE["timestamp"]
        # print("received_start_time",received_start_time)
        print(START_REQ_MESSAGE)
        multicast_send(START_REQ_MESSAGE)
        print("Sent start message")
        time.sleep(RTO)
        print("Waited for RTO in start")
        if(RETRIES==MAX_RETRIES):
            fail_safe_transmitter()
            RETRIES = 0
        else:
            RETRIES += 1


def reliable_start_ack():
    global FAILSAFE_EVENT
    global SYNC_SUCCESS
    global START_SUCCESS
    global RETRIES
    received_acks = set()
    while(not(FAILSAFE_EVENT) and not(SYNC_SUCCESS) and not(START_SUCCESS)):
        continue
    while(not(FAILSAFE_EVENT) and SYNC_SUCCESS and not(START_SUCCESS)):
        received_pkt = next(multicast_recieve())
        if(received_pkt["type"]=="start_ack"):
            print(received_pkt)
            received_acks.add(received_pkt["controller_id"])
            if(len(received_acks)==DEVICES):
                START_SUCCESS = True
                multicast_send(START_ACK_MESSAGE)
                print("start_success = ",START_SUCCESS)
                received_acks = set()


def start_req_handler():
    global FAILSAFE_EVENT
    global SYNC_SUCCESS
    global RETRIES
    global START_SUCCESS
    global RECIEVED_START_TIME
    while(not(FAILSAFE_EVENT) and not(SYNC_SUCCESS)):
        continue
    while(not(FAILSAFE_EVENT) and SYNC_SUCCESS and not(START_SUCCESS)):
        received_pkt = next(multicast_recieve())
        if(received_pkt["type"]=="start_request"):
            RECIEVED_START_TIME = time.struct_time(received_pkt["timestamp"])
            #print(RECIEVED_START_TIME==time.localtime())
            print("received_start_time",RECIEVED_START_TIME)
            multicast_send(START_ACK_MESSAGE)


# ---------- SYNC SUCCESS Variable UPDATE ---------------------

def sync_success_update():
    global SYNC_SUCCESS
    global FAILSAFE_EVENT

    while(not(SYNC_SUCCESS) and not(FAILSAFE_EVENT)):
        recieved_pkt = next(multicast_recieve())
        if (recieved_pkt["type"]=="sync_ack" and recieved_pkt["controller_id"]==MASTER_CONTROLLER_ID):
            SYNC_SUCCESS = True
            print("SYNC_SUCCESS_UPDATED")


def start_success_update():
    global START_SUCCESS
    global FAILSAFE_EVENT

    while(not(START_SUCCESS) and not(FAILSAFE_EVENT)):
        recieved_pkt = next(multicast_recieve())
        if (recieved_pkt["type"]=="start_ack" and recieved_pkt["controller_id"]==MASTER_CONTROLLER_ID):
            START_SUCCESS = True
            print("START_SUCCESS_UPDATED")

# -------------- FAILSAFE ------------------

def fail_safe_transmitter():
    global FAILSAFE_EVENT
    
    multicast_send(FAILSAFE_MESSAGE)
    FAILSAFE_EVENT = True
    print("Failsafe Triggered")
 

def fail_safe_receiver():
    global FAILSAFE_EVENT
    global FAIL_SAFE_ACK_RECEIVED
    while True:
        message = next(multicast_recieve())
        if message["type"] == "fail_safe":
            print("FAILSAFE TRIGGERED", message["controller_id"])
            FAILSAFE_EVENT = True
            multicast_send(FAILSAFE_ACK_MESSAGE)
            # TODO SET THE GPIO PINS