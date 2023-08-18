import xapp_control_ricbypass
import csv
import time
from e2sm_proto import *
from time import sleep

def main():    

    print("Encoding ric monitoring request")
    
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

    # Write header to the CSV file (if needed)
    with open(csv_filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Timestamp', 'Value'])

    try:
        while True:
            r_buf = xapp_control_ricbypass.receive_from_socket()
            ran_ind_resp = RAN_indication_response()
            ran_ind_resp.ParseFromString(r_buf)
            value = ran_ind_resp 
            print(ran_ind_resp)
            sleep(0.5) # Wait for 500 milliseconds
            xapp_control_ricbypass.send_to_socket(buf)
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            data = [timestamp, value]
            append_to_csv(csv_filename, data)

            
    except KeyboardInterrupt:
        print("Data collection stopped.")


def append_to_csv(filename, data):
    with open(filename, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(data)

if __name__ == '__main__':
    main()

