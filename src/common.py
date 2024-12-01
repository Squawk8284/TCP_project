from config import MULTICAST_GROUP, PORT, MASTER_SYNC_SUCCESS
from time import ctime
import time
import ntplib
import json
import socket



def ntp_time_sync():
    global MASTER_SYNC_SUCCESS
    try:
        client = ntplib.NTPClient()
        # response = client.request("pool.ntp.org", version=3)
        response = client.request("ntp.nic.in")
        return ctime(response.tx_time)
    
    except Exception as e:
        print(f"Failed to synchronise time: {e}")
        #TODO ADD send multicast failsafe message
        return time.time()
    

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