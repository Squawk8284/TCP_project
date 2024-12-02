from common import *
from config import *
from synchronise import *


#Total number of slots in a cycle
N = 10 

#State table maintanence
ID = [1,2,3,4]
right = [0,0,0,0]
left = [0,0,0,0]
centre = [0,0,0,0]
right = [0,0,0,0]
queue = [0,0,0,0]
cons_slots = [0,0,0,0]
total_slots = [0,0,0,0]
current_status = ["red","red","red","red"]
prev_slot = [False]
current_cycle = 0
current_slot = 0 #Number of slots completed
min_slot_flag = 0
start_time = None
fail_safe_flag = False
#For the sake of simulating all the RPis their prev_slot status are determined.
prev_slots_total = [prev_slot,False,False,False]
prev_queue_top = -1

def read_queue(id,row,file = FILE_PATH):
    global left, right, centre
    file_name = file
    target_row = row
    queue_sum = 0
    with open(file_name,"r") as file:
        for line_number,line in enumerate(file, start=1):
            if line_number == target_row:
                line = line.strip()
                x,y,z = map(int,line.split())
                queue_sum = x+y+z
                left[id-1] += x
                centre[id-1]+= y
                right[id-1] += z
                #print("The sum of {x},{y},{z} is {queue_sum}\n")
                return queue_sum
        else:
            print(f"Row {target_row} doesnt exist in file {file_name}")
            return queue_sum

def calculate_queue(id,row):
    global queue
    queue[id-1] += read_queue(id,row)

def update(x):
    global min_slot_flag,current_slot,queue,cons_slots,total_slots,prev_slot,prev_slots_total
    global CONTROLLER_ID
    global left, right, centre
    global current_status, N

    min_slot_flag = 0  #Resetting minimum slot criteria flag
    current_slot += 1
    if(current_slot == N+1):
        current_slot = 0
        cons_slots = [0,0,0,0]
        total_slots = [0,0,0,0]
        prev_slot = False
        prev_slots_total = [prev_slot,False,False,False]
    if(x == CONTROLLER_ID-1):
        if(left[x]>10):
            left[x] = left[x]-10
        else:
            left[x] = 0
    
        if(right[x]>10):
            right[x] = right[x]-10
        else:
            right[x] = 0

        if(centre[x]>10):
            centre[x] = centre[x]-10
        else:
            centre[x] = 0
        queue[x] = left[x]+right[x]+centre[x]
        cons_slots[x] += 1
        total_slots[x] += 1
        prev_slots_total[x] = True
        current_status[x] = "green"
        gpio_set("green")
    else:
        current_status[x] = "red"
        gpio_set("red")

def max_queue_resolve(max_list,queue_list):
    global total_slots
    min_time_slots = []
    min_time_slots_indices = []
    print("max_list",max_list)
    min_time_slots = min([total_slots[x] for x in max_list])
    print("min_time_slots",min_time_slots)
    min_time_slots_indices = [value for index,value in enumerate(max_list) if total_slots[value] == min_time_slots]
    print("min_time_slots_indices",min_time_slots_indices)
    if(len(min_time_slots_indices)>1):
        return min_time_slots_indices[0]
    else:
        return min_time_slots_indices[0]

def decision(queue_list = None):
    global min_slot_flag
    global N
    global total_slots, cons_slots, current_slot
    if queue_list is None:
        queue_list = queue
    queue_top = -1
    max_value = max(queue_list)
    zero_indices = [index for index,value in enumerate(total_slots) if value == 0]
    max_indices = [index for index, value in enumerate(queue_list) if value == max_value]
    #print(max_indices)
    if(len(max_indices)>1):
        queue_top = max_queue_resolve(max_indices,queue_list)
        print("queue_top is",queue_top)
    else:
        queue_top = max_indices[0]
    if(min_slot_flag == 0):
        if(N-current_slot>len(zero_indices)):
            if(cons_slots[queue_top] == 3):
                filtered_list = [-1 if value == max_value else value for value in queue_list]
                queue_top = decision(filtered_list)
        else:
            min_slot_flag = 1
            filtered_list = [-1 if value != 0 else value for value in total_slots]
            print(filtered_list)
            queue_top = decision(filtered_list)
    return queue_top


def broadcast(CONTROLLER_ID):
    #Transmit the values to the check it
    #cons_slots[id],total_slots[id],left[0],centre
    # [0],right[0],queue[0],current_status[0]
    global left,centre,right,queue,cons_slots,total_slots,current_status,current_slot
    DATA_MESSAGE = {"type": "data","controller_id": CONTROLLER_ID,"left":left[CONTROLLER_ID-1],"centre":centre[CONTROLLER_ID-1],"right":right[CONTROLLER_ID-1],"Total":queue[CONTROLLER_ID],"Consecutive_Slots":cons_slots[CONTROLLER_ID-1],"Total_Slots":total_slots[CONTROLLER_ID-1],"Slot":current_slot,"LED_state":current_status[CONTROLLER_ID-1]}
    reliable_data_transmit_and_receive_ack(DATA_MESSAGE)

def state_table_update(id):
    global CONTROLLER_DATA
    global ID
    global left,centre,right,queue,cons_slots,total_slots,current_status
    for x in ID:
        if(x != id):
            left[id-1] = CONTROLLER_DATA[id-1]['left']
            centre[id-1] = CONTROLLER_DATA[id-1]['centre']
            right[id-1] = CONTROLLER_DATA[id-1]['right']
            queue[id-1] = CONTROLLER_DATA[id-1]['Total']
            cons_slots[id-1] = CONTROLLER_DATA[id-1]['Consecutive_Slots']
            total_slots[id-1] = CONTROLLER_DATA[id-1]['Total_slots']
            current_status[id-1] = CONTROLLER_DATA[id-1]['Status']
        else:
            continue
    
def base_process():
    global prev_queue_top
    global total_slots
    global RECIEVED_START_TIME
    global CONTROLLER_ID
    global READ_QUEUE_FLAG
    global FAILSAFE_EVENT
    global DATA_SUCCESS
    global queue
    global START_SUCCESS #Check how to use shared flag from failsafe thread
    READ_QUEUE_FLAG = True

    while(not(START_SUCCESS) and (not FAILSAFE_EVENT)):
        continue
    
    print("DATA STARTED")

    row = 0
    #Starting the queue reading, ntp start time is required,
    while(not(FAILSAFE_EVENT) and START_SUCCESS):
        if(time.struct_time(time.localtime())>RECIEVED_START_TIME):
            if(not(FAILSAFE_EVENT)):
                if(READ_QUEUE_FLAG):
                    update(prev_queue_top)
                    row += 1
                    queue[CONTROLLER_ID-1] += read_queue(CONTROLLER_ID,row)
                    if(DATA_SUCCESS):
                        state_table_update(CONTROLLER_ID)
                        DATA_SUCCESS = False
                    if(queue[CONTROLLER_ID-1] > 0):
                        prev_queue_top = decision(queue)
                        broadcast(CONTROLLER_ID)
                        READ_QUEUE_FLAG = False
                    else :
                        continue
                    
                #After Every time slot show the precalculated values.
                green_indices = [index for index,value in enumerate(total_slots) if value == "green"]
                if(len(green_indices)>1):
                    FAILSAFE_EVENT = True
                    fail_safe_transmitter()                    
            else:
                continue
        else:
            continue

def time_update():
    global READ_QUEUE_FLAG
    global START_SUCCESS
    global FAILSAFE_EVENT
    global SLOT_TIME

    while(not(START_SUCCESS) and not(FAILSAFE_EVENT)):
        pass
    while(not(FAILSAFE_EVENT) and START_SUCCESS):
        if(time.localtime()>RECIEVED_START_TIME):
            time.sleep(SLOT_TIME)
            #Measure and track 60 second elapse
            if(not(READ_QUEUE_FLAG)):
                READ_QUEUE_FLAG = not READ_QUEUE_FLAG