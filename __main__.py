from src.common import *
from src.config import *
from src.synchronise import *


def main():

    # ---------- ENSURE TO COMMENT BELOW IF NOT MASTER---------------------------
    # sync_req_master_thread = threading.Thread(target=reliable_sync_request_master)
    # sync_ack_master_thread = threading.Thread(target=reliable_sync_ack_master)
    # start_req_master_thread = threading.Thread(target=reliable_start)
    # start_ack_master_thread = threading.Thread(target=reliable_start_ack)
    # sync_req_master_thread.start()
    # sync_ack_master_thread.start()
    # start_req_master_thread.start()
    # start_ack_master_thread.start()
    # ---------------------------------------------------------------------------

    sync_success_update_thread = threading.Thread(target=sync_success_update)
    handle_sync_requests_thread = threading.Thread(target=handle_sync_requests)
    start_req_handler_thread = threading.Thread(target=start_req_handler)
    start_success_update_thread = threading.Thread(target=start_success_update)
    fail_safe_receiver_thread = threading.Thread(target=fail_safe_receiver)


    # Start the threads
    sync_success_update_thread.start()
    handle_sync_requests_thread.start()
    start_req_handler_thread.start()
    start_success_update_thread.start()
    fail_safe_receiver_thread.start()

if __name__ == "__main__":
    try:
        main()
    
    except Exception as e:
        print("Exception occured:", e)
    
    except KeyboardInterrupt:
        pass