#
# Filename: Random_code.py
#
# The generator vector and coded vector of Random Code. 
# Note that we will use BitArray for all the symbols/vectors.
#
# By Chong Zan Kai zkchong@gmail.com
# Last modified on 21-June-2015.
#

import random
from bitstring import BitArray

#
# Given a message of k vectors, Random code will generate a coded 
# vector that is random combination of the k vectors.
#
class Random_Code():
    def __init__(self, uncoded_vector_list):
        self.__uncoded_vector_list = uncoded_vector_list
        
        self.__vector_size = len (uncoded_vector_list[0])
        self.__total_vector = len (uncoded_vector_list)
        
        self.__random_code_generator = Random_Code_Generator(self.__total_vector)
        
    #
    # Generate next coded vector
    #
    def generate_encoded_symbol(self):
        seed = random.randint(0, 2**16-1)
        
        g_vec = self.__random_code_generator.get_generator_vector(seed)
        
        #coded_vector = bitarray('0' *  self.__vector_size)
        coded_vector = BitArray([0]  *  self.__vector_size)
        
        for i in range(self.__total_vector):
            if g_vec[i] == 1:
                coded_vector = coded_vector.__xor__(self.__uncoded_vector_list[i])
                # coded_vector = [ x ^ y for x, y in zip(coded_vector, vec)]
        
        return seed, g_vec, coded_vector 

#-----------------------------------------------------------------------
    
class Random_Code_Generator():
    def __init__(self, total_input_vector):
        self.__total_input_vector = total_input_vector
        # print ('total_input_vector = %d' % total_input_vector)
        assert (total_input_vector >= 1)
    
    def get_generator_vector(self, rand_seed= None):
        # Generate seed for user if not specify.
        if rand_seed == None:
            rand_seed = random.randrange(10**10)
            
        r = random.Random()
        r.seed(rand_seed)
        
        repeat = True
        while repeat:
            value_list = [r.choice([0, 1]) for i in range(self.__total_input_vector)]
            if value_list.count(1) is not 0: # avoid the random list of all zeros.
                repeat = False
            
        return BitArray(value_list)



#-----------------------------------------------------------------------



#-----------------------------------------------------------------------
# Testing
#-----------------------------------------------------------------------
if __name__ == '__main__':
   
    #-------------------------------------------------------------------
    # 
    #-------------------------------------------------------------------
    print ('#')
    print ('# Test on Random Code Generator')
    print ('#')
    
    random_code_gen = Random_Code_Generator(6)
    
    for seed in range(100, 106):
        result = random_code_gen.get_generator_vector(seed)
        print ('seed=%d, result=%s' % (seed, result))
    print ('')
    
    print ('# Repeat. I should get the same result.')
    for seed in range(100, 106):
        result = random_code_gen.get_generator_vector(seed)
        print ('seed=%d, result=%s' % (seed, result))
    print ('')
    
    #-------------------------------------------------------------------
    # 
    #-------------------------------------------------------------------

    print ('#')
    print ('# Test on Random Code')
    print ('#')
    
    uncoded_vector_list = [
        BitArray([1,1,0,0]),
        BitArray([1,1,0,1]), 
        BitArray([0,1,0,1]), 
        BitArray([0,1,1,1]),
        BitArray([1,1,1,1]), 
        BitArray([1,0,1,1]), 
    ]

    print ('uncoded_vector_list:')
    for i, vector in enumerate(uncoded_vector_list):
        print ('%d. %s' % (i, vector.bin))
    print 

    random_code = Random_Code(uncoded_vector_list) 

    for i in range (len (uncoded_vector_list)):
        seed, generator_vector, coded_vector = random_code.generate_encoded_symbol()
        print ('%02d. seed=%s, generator_vector=%s, code_vector=%s' % (i, seed, generator_vector.bin, coded_vector.bin))
    print ('')

    #-------------------------------------------------------------------


