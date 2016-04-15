#
# To receive file with Random code in hybrid sockets.
# 
# by Chong Zan Kai  zkchong@gmail.com
# Last modify on 24-June-2015.
#
import socket
import argparse
import pickle
import sys
import time
import threading
import logging
import Message as MSG
from Coder import Data_Decoder
from bitstring import BitArray


UDP_BUFFER_SIZE = 4096
SOCKET_TIMEOUT = 300

class Receiver():
    def __init__(self, listener_addr_port):
        '''
        listener_addr_port: The network address and port of the receiver.
        '''
        # Listening to this network addr and port. 
        self.__listener_addr_port = listener_addr_port
        
        # Sender's network address and port.
        self.__sender_addr_port = None

        # Keep track of last session id
        self.__last_session_id = None

        # For decoder
        self.__filename = None
        self.__total_message_symbol = None
        self.__message_size = None
        self.__g_seed_list = []
        self.__encoded_symbol_list = []
        self.__reconstructed_message = None

        # Exit event -- to signal the caller quit.
        self.__exit_event = threading.Event()
        # self.__exit_timer = None

        # UDP socket setting
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__sock.settimeout(SOCKET_TIMEOUT)
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


    def __listener_thread(self):
        '''Listen to the incoming packets. Call this as a thread.'''
        self.__sock.bind(self.__listener_addr_port)
        logging.info('Listening to %s:%s' % (self.__listener_addr_port))

        while True:
            try:
                data, addr_port = self.__sock.recvfrom(UDP_BUFFER_SIZE)
            except socket.timeout:
                logging.warning('Socket timeout.')
                self.exit_with_error(-1)
                return 
            
            self.__sender_addr_port = addr_port
            
            # Unserialization.
            data_dict = pickle.loads(data) 

            logging.info('Received %d bytes from %s.' % (len(data), addr_port))
            logging.debug('Content: %s' % (data_dict))

            self.__process_data(data_dict)


    def __process_data(self, data_dict):
        '''Process the incoming packets.'''
        
        # Detect new session id
        if self.__last_session_id != data_dict[MSG.SESSION_ID] and MSG.DATA_DESCRIPTION in data_dict:
            # Record the session id
            self.__last_session_id = data_dict[MSG.SESSION_ID]
            # Update the data description
            self.__filename = data_dict[MSG.DATA_DESCRIPTION][0]
            self.__total_message_symbol = data_dict[MSG.DATA_DESCRIPTION][1]
            self.__message_size = data_dict[MSG.DATA_DESCRIPTION][2]
            # Reset            
            self.__g_seed_list = []
            self.__encoded_symbol_list = []
            self.__reconstruct_message = None

        #
        # Generate a ACK packet
        #
        ack_dict = {}
        ack_dict[MSG.TYPE] = MSG.TYPE_ACK
        ack_dict[MSG.SESSION_ID] = data_dict[MSG.SESSION_ID]
        ack_dict[MSG.ACK_ID] = data_dict[MSG.DATA_ID]

        # We may exit when we have k+10 encoded symbols.
        if len(self.__g_seed_list) >= (self.__total_message_symbol + 10 ): 
            ack_dict[MSG.EXIT] = True
        
        self.__send_ack(ack_dict)

        #
        # Process the data packet.
        #
        # if MSG.DATA_DESCRIPTION in data_dict:
        #     self.__message_size = data_dict[MSG.REQ_MESSAGE_SIZE]
        #     logging.info('Received message size = %d' % self.__message_size)

        # if MSG.REQ_TOTAL_MESSAGE_SYMBOL in data_dict:
        #     self.__total_message_symbol = data_dict[MSG.REQ_TOTAL_MESSAGE_SYMBOL]
        #     logging.info('Received total message symbols = %d' % self.__total_message_symbol)

        # The sender shows exit signal. 
        if MSG.EXIT in data_dict:
            logging.info('Received exit = True' )
            pass 
            # self.exit()

        # This request packet consists of data. So, process it. 
        if MSG.DATA in data_dict:
            # logging.info('Received data.')
            #
            g_seed, encoded_symbol_bin = data_dict[MSG.DATA]
            self.__g_seed_list.append(g_seed)
            encoded_symbol_bitarr = BitArray(encoded_symbol_bin)
            self.__encoded_symbol_list.append(encoded_symbol_bitarr)

            logging.info('Received %d/%d encoded symbols.' % (len(self.__encoded_symbol_list), self.__total_message_symbol+10))

            # Received k+10 encoded symbols. Time to decode. 
            if len(self.__g_seed_list) == (self.__total_message_symbol + 10):
                # Non-daemon. The script will stop when this thread stop.
                threading.Thread(target = self.__reconstruct_message_thread, daemon = False).start() 
                
            



    def __reconstruct_message_thread(self):
        # logging.info('Not running Gaussian elimination.')
        logging.info('Running Gaussian elimination in thread.')
        decoder = Data_Decoder()

        start_time = time.time()
        self.__reconstructed_message = decoder.reconstruct_message(
            self.__total_message_symbol, 
            self.__message_size, 
            self.__g_seed_list, 
            self.__encoded_symbol_list)
        end_time = time.time()

        gaussian_elapsed_time = end_time - start_time
        logging.info('decoding time = %f' % gaussian_elapsed_time)

        # logging.info ('__reconstructed_message = %s' % self.__reconstructed_message)
        logging.info('Message reconstructed successfully.')

        # Write to a file.
        f = open('%s.recv' % self.__filename, 'wb')
        f.write(self.__reconstructed_message)
        f.close()

        self.exit()




    def __send_ack(self, ack_dict):
        '''Send ACK to the sender.'''

        ack_str = pickle.dumps(ack_dict) # serialization
        self.__sock.sendto(ack_str, self.__sender_addr_port)

        logging.info('Sending %d bytes to %s.' % (len(ack_str), self.__sender_addr_port))
        logging.debug('Content: %s.' % (ack_dict))


    def start(self):
        '''The caller should call this to start the main script.'''
        threading.Thread(target = self.__listener_thread, daemon = True).start()


    def exit(self):
        '''Normal exit.'''
        self.exit_with_error(0)

    def exit_with_error(self, error_code):
        '''Exit with error.'''
        logging.debug('Exit with error code %s.' % error_code )
        self.__exit_event.set()


    def get_exit_event(self):
        '''Caller needs to have the exit_event to know when to quit the script.'''
        return self.__exit_event




#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------
if __name__ == '__main__':
    

    #-------------------------------------------------------------------
    # Parser
    #-------------------------------------------------------------------
    parser = argparse.ArgumentParser(description = 'To receiver file with Random code.') 
    parser.add_argument ('-a', '--listen_addr', default = '127.0.0.1',  help = 'Listen to network address.Default:127.0.0.1')
    parser.add_argument ('-p', '--listen_port', default = 10000, help = 'Listen to network port. Default: 10000.')
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
    receiver = Receiver(listener_addr_port = (args.listen_addr, int(args.listen_port))) 
    receiver.start()
    exit_event = receiver.get_exit_event()

    # logging.info('Wait exit event')
    exit_event.wait()
    sys.exit()
