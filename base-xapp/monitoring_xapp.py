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

    with open('data.csv', 'a') as file:
        file_write = csv.writer(file)
        file_write.writerow(['Timestamp', 'RSRP', 'BER_UP', 'BER_DOWN', 'MCS_UP', 'MCS_DOWN', 'CELL_LOAD'])
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
                        prbs = ue_list.allocated_prbs
                        rsrp_avg = 0
                        ber_up_avg = 0
                        ber_down_avg = 0
                        mcs_up_avg = 0
                        mcs_down_avg = 0

                        for ue_info in ue_list.ue_info:
                            rsrp_avg += ue_info.ue_rsrp
                            ber_up_avg += ue_info.ue_ber_up
                            ber_down_avg += ue_info.ue_ber_down
                            mcs_up_avg += ue_info.ue_mcs_up
                            mcs_down_avg += ue_info.ue_mcs_down
                            cell_load_avg += ue_info.cell_load

                        rsrp_avg /= prbs
                        ber_up_avg /= prbs
                        ber_down_avg /= prbs
                        mcs_up_avg /= prbs
                        mcs_down_avg /= prbs
                        cell_load_avg /= prbs

                        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                        data = [timestamp, rsrp_avg, ber_up_avg, ber_down_avg, mcs_up_avg, mcs_down_avg, cell_load_avg]
                        file_write.writerow(data)
                
                print(ran_ind_resp)
                sleep(0.5) # Wait for 500 milliseconds
                xapp_control_ricbypass.send_to_socket(buf)
                
        except KeyboardInterrupt:
            print("Data collection stopped.")

if __name__ == '__main__':
    main()