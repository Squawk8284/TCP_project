from config import *
from common import *


# ###############################################
#               MASTER
# ###############################################

# ------------- SYNC ---------------------------------
def reliable_sync_request_master():
    global RETRIES
    global MAX_RETRIES
    global FAILSAFE_EVENT
    global SYNC_SUCCESS
    global SYNC_REQ_MESSAGE
    global RTO
    global DEFAULT_RTO

    RTO = DEFAULT_RTO
    with master_send_lock:
        print("IN SYNC REQ MASTER")
        while(not(FAILSAFE_EVENT) and not(SYNC_SUCCESS)):
            multicast_send(SYNC_REQ_MESSAGE)
            print("Master Sent SYN REQ message")
            time.sleep(RTO)
            print("Waited for RTO")
            if(RETRIES==MAX_RETRIES):
                fail_safe_transmitter()
                RETRIES = 0
                RTO = DEFAULT_RTO
            else:
                RETRIES += 1
                RTO += 2



def reliable_sync_ack_master():
    global FAILSAFE_EVENT
    global SYNC_SUCCESS
    global MASTER_CONTROLLER_ID
    global DEVICES
    global SYNC_ACK_MESSAGE
    
    received_sync_acks = set()

    with master_rec_lock:
        print("IN SYNC ACK MASTER")
        while(not(FAILSAFE_EVENT) and not(SYNC_SUCCESS)):
            received_pkt = next(multicast_recieve())
            if(received_pkt["type"]=="sync_ack" and received_pkt["controller_id"]!=CONTROLLER_ID and (received_pkt["controller_id"] not in received_sync_acks)):
                received_sync_acks.add(received_pkt["controller_id"])
                print("MASTER recieved ack from: ", received_pkt["controller_id"])
                if(len(received_sync_acks)==DEVICES-1):
                    print("MASTER SENT SYN ACK MESSAGE")
                    multicast_send(SYNC_ACK_MESSAGE)

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
    global MAX_RETRIES
    global START_SUCCESS
    global RECIEVED_START_TIME
    global START_REQ_MESSAGE
    global RTO
    global DEFAULT_RTO

    RTO = DEFAULT_RTO

    RETRIES = 0
    while(not(FAILSAFE_EVENT) and not(SYNC_SUCCESS) and not(START_SUCCESS)):
        continue
    with master_send_lock:
        print("IN START REQ MASTER")
        if(CONTROLLER_ID==MASTER_CONTROLLER_ID):
            START_REQ_MESSAGE["timestamp"] = addOffset(time.localtime(),TIME_OFFSET)
            RECIEVED_START_TIME = START_REQ_MESSAGE["timestamp"]

        while(not(FAILSAFE_EVENT) and not(START_SUCCESS)):
            multicast_send(START_REQ_MESSAGE)
            print("MASTER Sent start REQ MESSSAGE")
            time.sleep(RTO)
            if(RETRIES==MAX_RETRIES):
                fail_safe_transmitter()
                RETRIES = 0
                RTO = DEFAULT_RTO
            else:
                RETRIES += 1
                RTO +=2


def reliable_start_ack():
    global FAILSAFE_EVENT
    global SYNC_SUCCESS
    global START_SUCCESS
    global MASTER_CONTROLLER_ID
    global START_ACK_MESSAGE
    
    received_start_acks = set()
    
    while(not(FAILSAFE_EVENT) and not(SYNC_SUCCESS) and not(START_SUCCESS)):
        continue
    with master_rec_lock:
        print("IN MASTER START ACK MASTER")
        while(not(FAILSAFE_EVENT) and SYNC_SUCCESS and not(START_SUCCESS)):
            received_pkt = next(multicast_recieve())
            if(received_pkt["type"]=="start_ack" and received_pkt["controller_id"]!=CONTROLLER_ID and (received_pkt["controller_id"] not in received_start_acks)):
                received_start_acks.add(received_pkt["controller_id"])
                print("Start ACk recieved from: ", received_pkt["controller_id"])
                print(received_pkt["controller_id"])
                if(len(received_start_acks)==DEVICES-1):
                    print("Master Ack Message sent")
                    multicast_send(START_ACK_MESSAGE)

# ###############################################
#               GENERAL
# ###############################################


# ------------- GENERAL SYNC ---------------------------------    

def handle_sync_requests():
    global SYNC_SUCCESS
    global FAILSAFE_EVENT
    global IS_NTP_TIME_SET
    global SYNC_ACK_MESSAGE

    print("IN SLAVE SYNC ACK")
    while (not(FAILSAFE_EVENT)):
        message = next(multicast_recieve())
        if message["type"] == "sync_request" and message["controller_id"]!=CONTROLLER_ID:
            print("Received sync request from controller: ", message["controller_id"])
            if IS_NTP_TIME_SET:
                multicast_send(SYNC_ACK_MESSAGE)
                print("CONTROLLER Sent SYNC ACK")
            else:
                print("NTP TIME NOT SYNCED")
                fail_safe_transmitter()


# ------------------- GENERAL START REQUEST ---------------------------

def start_req_handler():
    global FAILSAFE_EVENT
    global SYNC_SUCCESS
    global START_SUCCESS
    global RECIEVED_START_TIME
    global START_ACK_MESSAGE

    print("IN SLAVE START ACK")
    while(not(FAILSAFE_EVENT)):
        received_pkt = next(multicast_recieve())
        if(received_pkt["type"]=="start_request" and received_pkt["controller_id"]!=CONTROLLER_ID):
            if received_pkt["timestamp"] is not None:
                RECIEVED_START_TIME = time.struct_time(received_pkt["timestamp"])
            print("received_start_time",RECIEVED_START_TIME)
            print("Controller start ack message sent")
            multicast_send(START_ACK_MESSAGE)


# ---------- SYNC SUCCESS Variable UPDATE ---------------------

def sync_success_update():
    global SYNC_SUCCESS
    global FAILSAFE_EVENT
    global DEVICES
    
    received_sync_acks = set()
    with general_lock:
        print("IN SYNC UPDATE")
        while(not(SYNC_SUCCESS) and not(FAILSAFE_EVENT)):
            recieved_pkt = next(multicast_recieve())
            if (recieved_pkt["type"]=="sync_ack"):
                received_sync_acks.add(recieved_pkt["controller_id"])
                if( len(received_sync_acks)==DEVICES):
                    print("RECIEVED SYNC ACK FROM CONTROLLER: ", recieved_pkt["controller_id"])
                    SYNC_SUCCESS = True
                    print("SYNC_SUCCESS_UPDATED")


def start_success_update():
    global SYNC_SUCCESS
    global START_SUCCESS
    global FAILSAFE_EVENT
    global DEVICES
    
    received_start_acks = set()
    
    while(not(FAILSAFE_EVENT) and not(SYNC_SUCCESS) and not(START_SUCCESS)):
        continue
    with general_lock:
        print("IN START UPDATE")
        while(not(START_SUCCESS) and SYNC_SUCCESS and not(FAILSAFE_EVENT)):
            recieved_pkt = next(multicast_recieve())
            if (recieved_pkt["type"]=="start_ack"):
                received_start_acks.add(recieved_pkt["controller_id"])
                if(len(received_start_acks)==DEVICES):
                    print("RECIEVED START ACK FROM CONTROLLER: ", recieved_pkt["controller_id"])
                    START_SUCCESS = True
                    print("START_SUCCESS_UPDATED")

# -------------- FAILSAFE ------------------ 

def fail_safe_receiver():
    global FAILSAFE_EVENT
    global FAIL_SAFE_ACK_RECEIVED
    while True:
        message = next(multicast_recieve())
        if message["type"] == "fail_safe":
            print("FAILSAFE TRIGGERED", message["controller_id"])
            FAILSAFE_EVENT = True
            multicast_send(FAILSAFE_ACK_MESSAGE)
            gpio_set("yellow")


# --------------- DATA --------------------

 
 
def reliable_data_receiver():
    global FAILSAFE_EVENT
    global START_SUCCESS
    global CONTROLLER_DATA
    global DATA_SUCCESS

    while(not(FAILSAFE_EVENT)):
        while(None in CONTROLLER_DATA):
            received_pkt = next(multicast_recieve())
            if(received_pkt["type"]=="data"):
                parsed_data = {
                    "left": received_pkt.get("left"),
                    "centre": received_pkt.get("centre"),
                    "right": received_pkt.get("right"),
                    "Total": received_pkt.get("Total"),
                    "Consecutive_Slots": received_pkt.get("Consecutive_Slots"),
                    "Total_Slots": received_pkt.get("Total_Slots"),
                    "Slot": received_pkt.get("Slot"),
                    "Status": received_pkt.get("LED_state"),}
                ID = received_pkt["controller_id"]
                CONTROLLER_DATA[ID-1] = parsed_data
                print(CONTROLLER_DATA[ID-1])
                multicast_send(DATA_ACK_MESSAGE)
                #print("Sent DATA ACK for controller", ID)



def reliable_data_transmit_and_receive_ack(DATA_MESSAGE):
    global FAILSAFE_EVENT
    global RETRIES
    global START_SUCCESS
    global DEVICES
    global DATA_SUCCESS

    RETRIES = 0
    received_acks = set()
    #global sync_success
    while (not(FAILSAFE_EVENT)):
       
        multicast_send(DATA_MESSAGE)
        print("Sent DATA MESSAGE")
           
        while len(received_acks) <= DEVICES:
           
            received_pkt = next(multicast_recieve())
           
            if(received_pkt["type"]=="data_ack" and (received_pkt["controller_id"] not in received_acks)):
                print(received_pkt)
                received_acks.add(received_pkt["controller_id"])
 
                if len(received_acks) == DEVICES:
                    RETRIES = 0
                    DATA_SUCCESS = True
                    break
           
            if (RETRIES > MAX_RETRIES):
                FAILSAFE_EVENT = True
                print("Failsafe Triggered")
                fail_safe_transmitter()
                break
           
            else:
                multicast_send(DATA_MESSAGE)
                RETRIES += 1
 
 