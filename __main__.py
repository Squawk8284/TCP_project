from src.common import *
from src.config import *
from src.synchronise import *
from src.data_functions import *
from src.generate_traffic import generate_random_numbers_in_file


def main():
    print("PROGRAM STARTED ........\n")

    gpio_setup()



    # ---------- COMMENT IF NOT MASTER---------------------------
    # sync_req_master_thread = threading.Thread(target=reliable_sync_request_master)
    # sync_ack_master_thread = threading.Thread(target=reliable_sync_ack_master)
    # start_req_master_thread = threading.Thread(target=reliable_start)
    # start_ack_master_thread = threading.Thread(target=reliable_start_ack)
    # sync_req_master_thread.start()
    # sync_ack_master_thread.start()
    # start_req_master_thread.start()
    # start_ack_master_thread.start()
    # ---------------------------------------------------------------------------


    # ----------------- COMMENT IF MASTER ---------------------------
    start_req_handler_thread = threading.Thread(target=start_req_handler)
    start_req_handler_thread.start()

    # ---------------------------------------------------------------


    sync_success_update_thread = threading.Thread(target=sync_success_update)
    handle_sync_requests_thread = threading.Thread(target=handle_sync_requests)
    start_success_update_thread = threading.Thread(target=start_success_update)
    fail_safe_receiver_thread = threading.Thread(target=fail_safe_receiver)
    reliable_data_receiver_thread = threading.Thread(target=reliable_data_receiver)

    base_thread = threading.Thread(target = base_process)
    time_thread = threading.Thread(target = time_update)

    # Start the threads
    sync_success_update_thread.start()
    handle_sync_requests_thread.start()
    start_success_update_thread.start()
    fail_safe_receiver_thread.start()
    reliable_data_receiver_thread.start()
    base_thread.start()
    time_thread.start()


if __name__ == "__main__":
    try:
        generate_random_numbers_in_file(FILE_PATH)
        main()
    
    except Exception as e:
        print("Exception occured:", e)
    
    except KeyboardInterrupt:
        print("Keyboard interrupt")
        pass