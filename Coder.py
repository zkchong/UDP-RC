#
# Filename: Coder.py
# To generate the encoded symbol from a file. And, to reconstruct the original message.
#
# by Chong Zan Kai  zkchong@gmail.com
# Last modify on 21-Jun-2015.
#
# import pickle
from Coding import Coding
import logging
# import random
# import time
from Random_Code import Random_Code, Random_Code_Generator
from Gaussian_Elimination import Gaussian_Elimination
# import threading
# import Hybrid_Packet as HYBRID_PACKET
# import socket




#------------------------------------------------------------------------------
# Data Encoder
#------------------------------------------------------------------------------
class Data_Encoder():

    def __init__(self, file_name, symbol_size):  
        '''
        filename: File name.
        symbol_size: Size of a symbol in bytes.
        '''
        self.__file_name = file_name
        self.__symbol_size = symbol_size

        #
        # Process the file
        #
        file_bitarr = Coding.file_to_bitarray(self.__file_name)
        self.__message_symbol_list = Coding.bit_list_to_symbol_list(file_bitarr, (self.__symbol_size * 8)) 
        self.__total_message_symbol = len(self.__message_symbol_list)
        self.__file_size = int(len(file_bitarr)/8) # one byte = 8 bits.

        self.__code = Random_Code(self.__message_symbol_list)

    def generate_encoded_symbol(self):
        # gen_seed = random.randrange(1, 10**5)
        # g_bitarr = Coding.get_random_bitarr(self.__total_message_symbol, gen_seed)
        # coded_symbol_bitarr = Coding.generate_coded_symbol(g_bitarr, self.__message_symbol_list)
        seed, g_bitarr, encoded_bitarr = self.__code.generate_encoded_symbol()


        return seed, encoded_bitarr

    def get_file_size(self):
        return self.__file_size

    def get_total_message_symbol(self):
        return self.__total_message_symbol

#------------------------------------------------------------------------------
# Data Decoder
#------------------------------------------------------------------------------
class Data_Decoder():
    def __init__(self):
        pass
        # self.__total_message_symbol = total_message_symbol
        # self.__message_size = message_size

        # self.__g_bitarr_list = []
        # self.__encoded_bitarr_list = []
        # self.__reconstructed_message = None

        # self.__code_generator = None
        # # Random_Code_Generator(total_message_symbol)
        # self.__ge = Gaussian_Elimination()


    def reconstruct_message(self, total_message_symbol, message_size, g_seed_list, encoded_symbol_list):
        '''
        Let the caller decide when to attempt reconstructing message.
        Note that the encoded_symbol_list will be disturbed.
        '''
        # Get ready the generator list
        code_generator = Random_Code_Generator(total_message_symbol)
        g_list = [code_generator.get_generator_vector(seed) for seed in g_seed_list]
        
        # Employ Gaussian elimination.
        ge = Gaussian_Elimination()
        ge.form_triangle_matrix (g_list, encoded_symbol_list)
        ge.backward_substitution(g_list, encoded_symbol_list)

        decoded_symbol_list = encoded_symbol_list[:total_message_symbol]
        decoded_message_bitarr = Coding.symbol_list_to_bit_list(decoded_symbol_list, message_size * 8) # Note: (file_size*8) because this function count the string in bits.
        return decoded_message_bitarr.tobytes()

    # def process_encoded_symbol(self, g_seed, encoded_bitarr):
    #     g_bitarr = self.__code_generator.get_generator_vector(g_seed)

    #     self.__g_bitarr_list.append(g_bitarr)
    #     self.__encoded_bitarr_list.append(encoded_bitarr)

    #     # Condition to reconstruct original message
    #     if len(self.__g_bitarr_list) >= (self.__total_message_symbol + 10):
    #         self.__ge.form_triangle_matrix(self.__g_bitarr_list, self.__encoded_bitarr_list)
    #         self.__ge.backward_substitution(self.__g_bitarr_list, self.__encoded_bitarr_list)


    #     # self.__reconstructed_message = self.__encoded_bitarr_list 
    #     decoded_symbol_list = self.__encoded_bitarr_list[:self.__total_message_symbol]
    #     decoded_message_bitarr = Coding.symbol_list_to_bit_list(decoded_symbol_list, self.__message_size * 8) # Note: (file_size*8) because this function count the string in bits.
    #     self.__reconstructed_message = decoded_message_bitarr.tobytes()

    # def get_reconstructed_message(self):
    #     return self.__reconstructed_message



#------------------------------------------------------------------------------
# Test
#------------------------------------------------------------------------------
if __name__ == '__main__':
    filename = 'sample1.txt'
    symbol_size = 2 # byte
    encoder = Data_Encoder(filename, symbol_size)

    g_seed_list = []
    encoded_symbol_list = []

    file_size = encoder.get_file_size()
    total_message_symbol = encoder.get_total_message_symbol()

    print ('file_size = %d bytes.' % file_size)
    print ('get_total_message_symbol = %d symbols.' % total_message_symbol)

    # Put k+10 encoded symbols into list.
    for i in range(total_message_symbol + 10):
        seed, encoded_symbol_bitarr = encoder.generate_encoded_symbol()
        g_seed_list.append(seed)
        encoded_symbol_list.append(encoded_symbol_bitarr)
        print ('%d. seed = %s, encoded_symbol = %s' % (i+1, seed, encoded_symbol_bitarr))


    decoder = Data_Decoder()
    message = decoder.reconstruct_message(total_message_symbol, file_size, g_seed_list, encoded_symbol_list)
    print ('message = %s' % message)
