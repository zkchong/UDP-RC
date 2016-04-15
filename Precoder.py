#
# Filename: Precoder.py
# To pre-generate the coded symbols for a file.
#
# by Chong Zan Kai  zkchong@gmail.com
# Last modify on 26-Jun-2015.
#
#
import argparse
from Coding import Coding
from Random_Code import Random_Code, Random_Code_Generator
# import time
import pickle

class Precoder_Reader:
    def __init__(self, pickle_filename):
        self.__precode_tuple = pickle.load( open( pickle_filename, "rb" ) )

        self.__get_next_encoded_byte_counter = 0

    def get_message_filename(self):
        return self.__precode_tuple[0]

    def get_symbol_size(self):
        return self.__precode_tuple[1]

    def get_total_message_symbol(self):
        return self.__precode_tuple[2]

    def get_message_size(self):
        return self.__precode_tuple[3]

    def get_g_seed_list(self):
        return self.__precode_tuple[4]

    def get_encoded_byte_list(self):
        return self.__precode_tuple[5]

    def get_next_encoded_byte(self):
        '''Get the next g_seed and encoded byte from the precoded pickle file.'''
        g_seed = self.get_g_seed_list() [self.__get_next_encoded_byte_counter]
        encoded_byte= self.get_encoded_byte_list() [self.__get_next_encoded_byte_counter]

        self.__get_next_encoded_byte_counter += 1
        
        if self.__get_next_encoded_byte_counter >= len(self.get_g_seed_list()):
            self.__get_next_encoded_byte_counter = 0
        
        return (g_seed, encoded_byte)



class Precoder_Generator:
    def __init__(self):
        pass

    def generate(self, target_filename, pickle_filename, symbol_size, total_encoded_symbol):
        file_bitarr = Coding.file_to_bitarray(target_filename)
        message_symbol_list = Coding.bit_list_to_symbol_list(file_bitarr, (symbol_size * 8)) 
        total_message_symbol = len(message_symbol_list)
        file_size = int(len(file_bitarr)/8) # one byte = 8 bits.

        print ('file name = %s' % target_filename)
        print ('symbol size = %d' % symbol_size)
        print ('total message symbol = %d' % total_message_symbol)
        print ('file size = %d' % file_size)

        encoder = Random_Code(message_symbol_list)

        # Generate the encoded symbols now.
        encoded_bitarr_list = []
        g_seed_list = []

        if total_encoded_symbol >0:
            print ('Generate %d encoded symbols to pickle file: %s' % (total_encoded_symbol, pickle_filename))
            #
            for i in range(total_encoded_symbol):
                g_seed, g_bitarr, encoded_bitarr = encoder.generate_encoded_symbol()
                
                g_seed_list.append(g_seed)
                encoded_bitarr_list.append(encoded_bitarr)
            #
            # Put to pickle file
            encoded_tuple = (target_filename, symbol_size, total_message_symbol, file_size, g_seed_list, encoded_bitarr_list)
            pickle.dump( encoded_tuple, open( pickle_filename, "wb" ) )




#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------
if __name__ == '__main__':
        #-------------------------------------------------------------------
    parser = argparse.ArgumentParser(description = 'To pre-generate the encoded symbols for a file.') 
    parser.add_argument('-f', '--filename', required = True, help = 'File name to read/write.') 
    parser.add_argument('-l', '--symbol_size', default=1024, help = 'Symbol size.') 
    # parser.add_argument('-a', '--analysis', action='store_false', help = 'Analyze the file.')
    parser.add_argument('-g', '--total_encoded_symbol', default = 0, help = 'Generate the encoded symbols. ') 
    # parser.add_argument('-r', '--read_file', help = 'Read the detail of a file.') 

    args = parser.parse_args()

    #
    #
    #

    filename = args.filename

    if filename.endswith('.p'):
        reader = Precoder_Reader(filename)

        filename = reader.get_message_filename()
        symbol_size = reader.get_symbol_size()
        total_message_symbol = reader.get_total_message_symbol()
        message_size = reader.get_message_size()
        total_encoded_symbol = len(reader.get_encoded_byte_list())

        print ('Filename = %s' % filename)
        print ('symbol_size = %d' % symbol_size)
        print ('total_message_symbol = %d' % total_message_symbol)
        print ('message_size = %d' % message_size)
        print ('total_encoded_symbol = %d' % total_encoded_symbol)
        

    else:
        symbol_size = int(args.symbol_size)
        total_encoded_symbol = int(args.total_encoded_symbol)

        precoder = Precoder_Generator()
        precoder.generate(filename, '%s.p' % filename, symbol_size, total_encoded_symbol)

    # def precode(self, target_filename, pickle_filename, symbol_size, total_encoded_symbol):

