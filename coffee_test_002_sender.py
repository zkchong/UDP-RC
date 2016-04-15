#
# To send file with erasure code using UDP socket.
# 
# by Chong Zan Kai  zkchong@gmail.com
# Last modify on 11-April-2016.
#
import socket
import argparse
import sys
import pickle
import threading
import time
import random
import logging
import Message as MSG
from Random_Code import Random_Code
# from Coder import Data_Encoder
from Precoder import Precoder_Reader

UDP_BUFFER_SIZE = 4096
SOCKET_TIMEOUT = 5 # Second. If can't establish the connection within SOCKET_TIMEOUT, this script exits with error. 


class Sender():
    def __init__(self, receiver_addr_port, delay_ms, precoded_filename):
        '''
        receiver_addr_port: The receiver's network address and port.
        delay_ms: Delay per udp packet sent. Counted in ms.
        precoded_filename: Name of the precoded file.
        '''
        self.__receiver_addr_port = receiver_addr_port
        self.__delay_ms = delay_ms 
        self.__precoded_filename = precoded_filename
        
        # Exit event. Signal to caller.
        self.__exit_event = threading.Event()

        # Exit if received nothing for $SOCKET_TIMEOUT after the connection has been established.
        self.__exit_timer_event = None

        # To read the precoded file.
        self.__precoder_reader = Precoder_Reader(self.__precoded_filename)

        # To track the last ackn id. 
        # To track whether the connection has been established.
        self.__last_ack_id = None

        # Data id. Used by get_next_id()
        self.__next_data_id = 1

        # Session id. Each session should have its own id. 
        self.__sesssion_id = random.randrange(1000, 2000)

        # UDP socket setting.
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.__sock.settimeout(SOCKET_TIMEOUT)


    def __listener_thread(self):
        '''Listen to the incoming packets. Run this in thread.'''

        while True:
            # data, addr_port = self.__sock.recvfrom(UDP_BUFFER_SIZE) 
            try:
                data, addr_port = self.__sock.recvfrom(UDP_BUFFER_SIZE)
            except socket.timeout:
                logging.warning('Socket timeout.')
                self.exit_with_error(-1)
                return 

            # Unserialization
            request_dict = pickle.loads(data) 

            logging.info('Received %d bytes from %s.' % (len(data), addr_port))
            logging.debug('Content: %s.' % (request_dict))

            self.__process_response(request_dict)


    def __process_response(self, ack_dict):
        '''Process the incoming packets.'''

        assert (ack_dict[MSG.TYPE] == MSG.TYPE_ACK)

        # Record the last response id.
        self.__last_ack_id = ack_dict[MSG.ACK_ID]

        # Reset the exit timer each time receive the response.
        # self.__reset_exit_timer()
        
        # Detected EXIT signal from the receiver's ACK.
        if MSG.EXIT in ack_dict and ack_dict[MSG.EXIT] == True:
            # Inform the receiver that I am exiting too. 
            data_dict = {}
            data_dict[MSG.SESSION_ID] = self.__sesssion_id
            data_dict[MSG.DATA_ID] = self.__get_next_data_id()
            data_dict[MSG.EXIT] = True
            #
            self.__send_data(data_dict)
            self.exit()


    def __send_data(self, data_dict = None, pickle_data_str = None):
        '''Send a data packet to the receiver.'''
        assert ( (bool (data_dict) != bool (pickle_data_str))  )
        
        if not bool(pickle_data_str):
            pickle_data_str = pickle.dumps(data_dict) # serialization.

        if not bool (data_dict):
            data_dict = pickle.loads(pickle_data_str)
        
        self.__sock.sendto(pickle_data_str, self.__receiver_addr_port)

        logging.info('Sending %d bytes.' % ( len(pickle_data_str)) )
        logging.debug('Content: %s' % (data_dict) )


    def __get_data_description(self):
        '''For MSG.DATA_DESCRIPTION field. '''
        return (self.__precoder_reader.get_message_filename(), 
            self.__precoder_reader.get_total_message_symbol(), 
            self.__precoder_reader.get_message_size())


    def __send_data_thread(self):
        '''Send encoded data continuously to the receiver. Call in thread.'''

        total_data_length = 0 # to keep tract of the total message length.

        while True:
            data_dict = {}
            data_dict[MSG.SESSION_ID] = self.__sesssion_id
            data_dict[MSG.TYPE] = MSG.TYPE_DATA
            data_dict[MSG.DATA_ID] = self.__get_next_data_id()
            
            # "self.__last_ack_id == None" implies we have yet to receive any RESPONSE from the receiver.
            # The connection has yet to establish, and hence we need to provide the description about the data. 
            if self.__last_ack_id == None:
                data_dict[MSG.DATA_DESCRIPTION] = self.__get_data_description()

            # Generate encoded symbol
            g_seed, encoded_byte = self.__precoder_reader.get_next_encoded_byte()
            message_dict = (g_seed, encoded_byte) 
            data_dict[MSG.DATA] = message_dict
            
            data_str = pickle.dumps(data_dict) # serialization.
            data_len = len(data_str)

            #
            # The first k + 10 packets are flooded to the OS.
            #
            total_message_symbol = self.__precoder_reader.get_total_message_symbol()
            logging.info('total_message_symbol, data_dict[MSG.DATA_ID] = %d, %d' % (total_message_symbol, data_dict[MSG.DATA_ID]) )
            

            # if data_dict[MSG.DATA_ID] > 0:
            #     # logging.info('Slow transmission.')

            #     #
            #     # Pause for 1 second if over the delay_ms
            #     #
            #     if (total_data_length + data_len) >= self.__delay_ms:
            #         logging.info('Holding data_dict[MSG.DATA_ID=%d] due to over delay_ms.' % (data_dict[MSG.DATA_ID] ))
            #         event = threading.Event()
            #         event.wait(1)
                    
            #         total_data_length = 0

            #     total_data_length += data_len
            
            #
            self.__send_data(pickle_data_str = data_str)

            #
            # Introduce delay
            #
            delay_sec = self.__delay_ms / 1000
            time.sleep(delay_sec)



    def start(self):
        '''Caller will use this to start the main script.'''
        threading.Thread(target = self.__send_data_thread, daemon =  True).start()
        threading.Thread(target = self.__listener_thread, daemon =  True).start()


    def get_exit_event(self):
        '''Caller needs the exit event to know when to quit.'''
        return self.__exit_event


    def __get_next_data_id(self):
        '''Get the next request id.'''
        val = self.__next_data_id 
        self.__next_data_id += 1
        return val


    def exit(self):
        '''Exit normally.'''

        # self.__end_time = time.time()

        # self.__elapsed_time = self.__end_time - self.__start_time
        # logging.info ('transmission time = %f' % self.__elapsed_time)

        self.exit_with_error(0)


    def exit_with_error(self, error_code):
        '''Exit with error.'''
        logging.debug('Exit with error code %s.' % error_code )
        
        # self.__stop_exit_timer()
        self.__exit_event.set()



#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------
if __name__ == '__main__':


    #-------------------------------------------------------------------
    # Parser
    #-------------------------------------------------------------------
    parser = argparse.ArgumentParser(description = 'To send file with Random code.') 
    parser.add_argument('-a', '--network_addr', default = '127.0.0.1',  help = 'Responder''s network address. Default value: 127.0.0.1.')
    parser.add_argument('-p', '--network_port', default = 10000, help = 'Responder''s network port. Default value: 10000.')
    parser.add_argument('-t', '--delay_ms', default= 4096 , help = 'Slow transmission in kbps.') 
    parser.add_argument('-f', '--precoded_filename', required = True, help = 'Precoded filename') 
    parser.add_argument ('-d', '--debug', default=1, type=int, help = 'Enable debugging. values:0, 1 and 2.')

    args = parser.parse_args()

    #-------------------------------------------------------------------
    # Setup logging service
    #-------------------------------------------------------------------
    if args.debug == 1:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s,%(module)s,%(levelname)s,%(message)s')
    elif args.debug == 2 :
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s,%(module)s,%(levelname)s,%(message)s')

    #-------------------------------------------------------------------
    # Start
    #-------------------------------------------------------------------

    sender = Sender(
        receiver_addr_port = (args.network_addr, int(args.network_port)), 
        delay_ms= int(args.delay_ms),
        precoded_filename = args.precoded_filename,
    )

    sender.start()
    
    # Exit handler.
    exit_event = sender.get_exit_event()
    exit_event.wait() # Waiting the EXIT signal. 
    sys.exit()




