# 
import random
#import bitarray
#from BitVector import BitVector
from bitstring import BitArray
# import serpent
# import base64

#-----------------------------------------------------------------------
#
# This is a common module contains basic methods that help in encoding 
# and decoding.
#
__VERSION__ = '18-Mar-2015'

#-----------------------------------------------------------------------
class Coding:
    
    #
    # To generate the generator row based on $bit_len and $random_seed.
    # bit_len: The length of the generator row.
    # random_seed: Random seed number. 
    #        
    @classmethod
    def get_random_bitarr(self, bit_len, random_seed):
        assert (bit_len >= 1)
        my_random = random.Random()
        my_random.seed (random_seed)
        
        # I need to ensure no generator row of all zeros.
        while True:
            generator_list = [my_random.choice([0,1]) for i in range(bit_len)]
            
            if 1 in generator_list:
                break
            
        #generator_bv = BitVector(bitlist = generator_list)    
        generator_bitarr = BitArray(generator_list)    
            
        return generator_bitarr
    
   
    #
    # A coded symbol is generated by multiplying $generator_row with 
    # $message_symbol_list. 
    # generator_row: generator row.
    # message_symbol_list: message symbol list
    #
    # @classmethod
    # def generate_coded_symbol(self, generator_row, message_symbol_list):
    #     selected_list = [message_symbol_list[i] for i, g in enumerate(generator_row) if g == 1]
        
    #     # create empty symbol
    #     #coded_symbol = bitarray.bitarray('0' * len(message_symbol_list[0]))
    #     #coded_symbol = BitVector(size = len(message_symbol_list[0]))
    #     coded_symbol = BitArray([0] *  len(message_symbol_list[0]))
        
    #     for s in selected_list:
    #         # print ('len(s) = %d' % len(s))
    #         coded_symbol = coded_symbol.__xor__(s)
        
    #     return coded_symbol
    @classmethod
    def generate_coded_symbol(self, generator_row, message_symbol_list):
        coded_symbol = BitArray([0] *  len(message_symbol_list[0]))
        
        for num, val in enumerate(generator_row):
            if val == 1:
                symbol = message_symbol_list[num]
                coded_symbol = coded_symbol.__xor__(symbol)
        
        return coded_symbol

    #-------------------------------------------------------------------
    
    #
    # It chunck a message (bitarray) into symbols of equal size 
    # ($symbol_size). If the last symbol does not have %symbol_size, 
    # it will be filled with zeros. 
    # message: The message in bitarray.
    # symbol_size: The size of the symbol that the message should be 
    #    chunked to.
    #
    @classmethod
    def bit_list_to_symbol_list (self, message, symbol_size):
        def chunk(l, n):
            """ Yield successive n-sized chunks from l.
            """
            #print (l, n)
            for i in range(0, len(l), n):
                yield l[i:i+n]
        
        # Note: converting byte to bit.
        symbol_list = list(chunk (message, symbol_size))
        
        # Need to ensure the last symbol has full length ...
        last_symbol = symbol_list[-1] 
        
        if len(last_symbol) < symbol_size:
            last_symbol += BitArray( [0] * ((symbol_size)- len(last_symbol)) )
            symbol_list[-1] = last_symbol
        
        return symbol_list
    

    #
    # It converts the symbol list back to a line of message (bitarray).
    # symbol_list: The symbol list that we will convert from.
    # msg_size: The length of the symbol list may contain the zero 
    #    padding. We need to specify the actual message length such 
    #    that the zero padding can be removed.
    #
    @classmethod
    def symbol_list_to_bit_list(self, symbol_list, msg_size = -1):
        #msg = bitarray.bitarray()
        #msg_bv = BitVector(size=0)
        message_bitarr = BitArray()
        for s in symbol_list:
            message_bitarr += s
        
        if msg_size == -1:
            #return msg_bv.bv.get_text_from_bitvector().encode()
            # return message_bitarr.tobytes()
            return message_bitarr
        else:
            #return msg_bv.bv.get_text_from_bitvector().encode()[:msg_size]
            # return message_bitarr.tobytes()[:msg_size]
            return message_bitarr[:msg_size]
        
    #
    # # The serpent (something like pickle) will format the binary list to base64.
    # # This function will restore all the base64 formated binary list.
    # #
    # @classmethod
    # def restore_serpent_byte_list(self, symbol_dict, key):
    #     b64_dict_list = symbol_dict[key]
        
    #     data_byte_list = []
        
    #     for b64_dict in b64_dict_list:
    #         assert ('data' in b64_dict)
    #         assert (b64_dict['encoding'] == 'base64')
            
    #         data_byte = serpent.base64.b64decode(b64_dict['data'].encode())
    #         data_byte_list.append(data_byte)
        
    #     symbol_dict[key] = data_byte_list
    
    # #
    # # Encode the whole bitarray list to b64 string list 
    # #
    # @classmethod
    # def b64encode_bitarr_list(self, input_bitarr_list):
    #     b64str_list = []
    #     for bitarr in input_bitarr_list:
    #         b64str = base64.b64encode(bitarr.tobytes())
    #         b64str_list.append(b64str)
    #     return b64str_list
    
    # #
    # # Decode the whole b64 encoded string list to bitarr list
    # #
    # @classmethod
    # def b64decode_to_bitarr_list(self, input_b64str_list):
    #     bitarr_list =[]
    #     for astr in input_b64str_list:
    #         abyte = base64.b64decode(astr)
    #         bitarr = BitArray(bytes= abyte)
    #         bitarr_list.append(bitarr)
    #     return bitarr_list
    

    # #
    # # Encode the whole byte list to b64 string list 
    # #
    # @classmethod
    # def b64encode_byte_list(self, input_byte_list):
    #     b64str_list = []
    #     for abyte in input_byte_list:
    #         b64str = base64.b64encode(abyte)
    #         b64str_list.append(b64str)
    #     return b64str_list
    
    # #
    # # Decode the whole b64 encoded string list to byte list
    # #
    # @classmethod
    # def b64decode_to_byte_list(self, input_b64str_list):
    #     byte_list =[]
    #     for astr in input_b64str_list:
    #         abyte = base64.b64decode(astr)
    #         byte_list.append(abyte)
    #     return byte_list
    
    #
    # Convert the whole bit array list to byte list.
    #
    @classmethod
    def bitarr_list_to_byte_list(self, bitarr_list):
        byte_list = []
        for bitarr in bitarr_list:
            bstr = bitarr.tobytes()
            byte_list.append(bstr)
        return byte_list
    
    
    #
    # Convert the whole byte_list to bit array list
    #
    @classmethod
    def byte_list_to_bitarr_list (self, byte_list):
        bitarr_list = []
        for b in byte_list:
            bitarr = BitArray(b)
            bitarr_list.append(bitarr)
        return bitarr_list
    
    #
    # To read a file content into bit array.
    #
    @classmethod
    def file_to_bitarray(self, input_filename):
        f = open(input_filename, 'rb')
        message_bitarr = BitArray(f)
        f.close()
        return message_bitarr
    
    #
    # Write the bit array to file
    #
    @classmethod
    def bitarray_to_file(self, input_bitarr, target_filename):
        f = open(target_filename, 'wb')
        input_bitarr.tofile(f)
        f.close()

#-----------------------------------------------------------------------
if __name__ == '__main__':
    from Coding import Coding
    
    #
    # Test on file_to_bitarray()
    # 
    sample_filename = 'sample4.txt'
    message_bitarr = Coding.file_to_bitarray(sample_filename)
    
    f = open(sample_filename, 'rb')
    sample_text = f.read()
    
    #print ('message_bitarr.bytes', message_bitarr.bytes)
    #print ()
    #print ('sample_text', sample_text)
    print ('Test on file_to_bitarray()')
    assert( sample_text == message_bitarr.bytes)
    print ('file_to_bitarray() works correctly.')
    print ()
    
    
    #
    # Test on bitvector_to_file
    #
    input_bitarr = message_bitarr
    target_filename = '%s.tmp' % sample_filename
    Coding.bitarray_to_file(input_bitarr, target_filename)
    print ('Test on bitarray_to_file()')
    print ('Please run: diff %s %s' % (sample_filename, target_filename))
    print ('to ensure both of the files are the same.')
    print ()
    
    #-------------------------------------------------------------------
    #
    # Test on b64encode_bitarr_list and b64decode_to_bitarr_list
    #
    symbol_size = 8
    total_symbol = 4
    input_list = [BitArray(random.choice([0,1]) for i in range(symbol_size)) for i in range (total_symbol)]
    b64_encoded_list = Coding.b64encode_bitarr_list(input_list)
    b64_decoded_list = Coding.b64decode_to_bitarr_list(b64_encoded_list)
    print ('Test on b64encode_bitarr_list and b64decode_to_bitarr_list')
    assert (input_list == b64_decoded_list)
    print ('b64encode_bitarr_list and b64decode_to_bitarr_list runs correctly.')
    print()
    
    #-------------------------------------------------------------------
    #
    # Test on b64encode_bitarr_list and b64decode_to_bitarr_list
    #
    symbol_size = 8
    total_symbol = 4
    input_list = [BitArray(random.choice([0,1]) for i in range(symbol_size)).tobytes()  for i in range (total_symbol)]

    b64_encoded_list = Coding.b64encode_byte_list(input_list)
    b64_decoded_list = Coding.b64decode_to_byte_list(b64_encoded_list)
    print ('Test on b64encode_byte_list and b64decode_to_byte_list')
    assert (input_list == b64_decoded_list)
    print ('b64encode_byte_list and b64decode_to_byte_list runs correctly.')
    print()