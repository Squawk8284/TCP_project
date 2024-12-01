import threading

MASTER_CONTROLLER_ID = 1
CONTROLLER_ID = 2
DEVICES = 3

MULTICAST_GROUP = "224.0.0.1"
PORT = 5007

FAILSAFE_EVENT = False
FAIL_SAFE_ACK_RECEIVED = False

SYNC_SUCCESS = False
START_SUCCESS = False

MASTER_SYNC_SUCCESS = True
RECIEVED_START_TIME = None
RETRIES = 0
SEQUENCE_NO = 0
lock = threading.Lock()

TIME_OFFSET = 60
RTO = 10
MAX_RETRIES = 20

RECIEVED_CONTROLLER_ID = None

SYNC_REQ_MESSAGE = {"type": "sync_request", "controller_id": MASTER_CONTROLLER_ID}
SYNC_ACK_MESSAGE = {"type": "sync_ack", "controller_id": CONTROLLER_ID}
START_REQ_MESSAGE = {"type": "start_request", "controller_id": MASTER_CONTROLLER_ID,"timestamp":None}
START_ACK_MESSAGE = {"type": "start_ack", "controller_id": CONTROLLER_ID}
DATA_MESSAGE = {"type": "data","controller_id": CONTROLLER_ID,"left":None,"centre":None,"right":None,"Total":None,"Consecutive_Slots":None,"Total_Slots":None,"Slot":None,"LED_state":None}
DATA_ACK_MESSAGE = {"type":"data_ack","controller_id": CONTROLLER_ID}
FAILSAFE_MESSAGE = {"type": "fail_safe","controller_id": CONTROLLER_ID}
FAILSAFE_ACK_MESSAGE = {"type":"fail_safe_ack","controller_id":CONTROLLER_ID}
