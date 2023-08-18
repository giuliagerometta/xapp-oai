import xapp_control_ricbypass
import csv
import time
from e2sm_proto import *
from time import sleep
import os

def main():    

    print("Encoding ric monitoring request")
    print("Current working directory:", os.getcwd())
    
    # external message
    master_mess = RAN_message()
    master_mess.msg_type = RAN_message_type.INDICATION_REQUEST

    # internal message
    inner_mess = RAN_indication_request()
    inner_mess.target_params.extend([RAN_parameter.GNB_ID, RAN_parameter.UE_LIST])

    # assign and serialize
    master_mess.ran_indication_request.CopyFrom(inner_mess)
    buf = master_mess.SerializeToString()
    xapp_control_ricbypass.send_to_socket(buf)
    

    csv_filename = 'data.csv'
    try:
        with open(csv_filename, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['Timestamp', 'Value'])
    except Exception as e:
        print("Error creating CSV file:", e)

    try:
        while True:
            r_buf = xapp_control_ricbypass.receive_from_socket()
            ran_ind_resp = RAN_indication_response()
            ran_ind_resp.ParseFromString(r_buf)

            ue_list = None  

            for i in ran_ind_resp.param_map:
                if i.HasField('ue_list'):
                    ue_list = i.ue_list

                if ue_list is not None:
                    for ue_info in ue_list.ue_info:
                        ue_rsrp = ue_info.ue_rsrp
                        
                        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                        data = [timestamp, ue_rsrp]
                        append_to_csv(csv_filename, data)
            
            print(ran_ind_resp)
            sleep(0.5) # Wait for 500 milliseconds
            xapp_control_ricbypass.send_to_socket(buf)
            
    except KeyboardInterrupt:
        print("Data collection stopped.")


def append_to_csv(filename, data):
    with open(filename, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(data)

if __name__ == '__main__':
    main()

