#
# Filename: Gaussian_Elimination.py
# 
# To invert a matrix to identity matrix.
#
# By Chong Zan Kai zkchong@gmail.com
# Last modified on 21-Jun-2015.
#

from bitstring import BitArray

#-----------------------------------------------------------------------
#
#-----------------------------------------------------------------------
class Gaussian_Elimination:
    
    

    #
    # To form a triangular matrix.
    #
    def form_triangle_matrix(self, input_list, aux_list = None):
        dim_col = len(input_list[0]) 
        dim_row = len(input_list)

        for col_num in range(dim_col):
            # print ('col_num = %d' % col_num)
            # Search pivoting row.
            pivoting_row_num= -1
            for row_num in range(col_num, dim_row):
                if input_list[row_num][col_num] == 1:
                    pivoting_row_num = row_num
                    break

            # Throw error if cannot find.
            assert (pivoting_row_num >= 0)

            # print ('pivoting_row_num = %s' % pivoting_row_num)

            # Move the pivoting row to the correct position
            input_list.insert(col_num, input_list.pop(pivoting_row_num))
            if aux_list:
                aux_list.insert(col_num, aux_list.pop(pivoting_row_num))

            # the current pivoting row is at location
            # pivoting_row = input_list[col_num]
            # print ('pivoting_row = %s' % pivoting_row.bin)

            # Clean all the rows below, in which their $col_num is nonzero.
            for row_num in range(col_num + 1, dim_row):
                if input_list[row_num][col_num] == 1:
                    input_list[row_num] = input_list[row_num].__xor__(input_list[col_num])
                    if aux_list:
                        aux_list[row_num] = aux_list[row_num].__xor__(aux_list[col_num])

        return

    # 
    # Backward substitution. 
    #
    def backward_substitution(self, input_list, aux_list = None):
        dim_col = len(input_list[0])

        # Starting from the rightmost column.
        for col_num in reversed(range(1, dim_col)):
            
            # pivoting_row = input_list[col_num]

            # The row numbers should start from (col_num-1) to 0.
            for row_num in reversed(range(col_num)):
                # Clean all the rows above, in which thir $col_num is nonzero.
                if input_list[row_num][col_num] == 1:
                    input_list[row_num] = input_list[row_num].__xor__(input_list[col_num])
                    if aux_list:
                        aux_list[row_num] = aux_list[row_num].__xor__(aux_list[col_num])

#-----------------------------------------------------------------------
# For testing.
#-----------------------------------------------------------------------
if __name__ == '__main__':
    import sys
    import random
    #-------------------------------------------------------------------
    # Necessary function
    #-------------------------------------------------------------------
    #
    # To generate Random code's coded symbols. 
    #
    def generate_coded_symbol(generator_row, message_symbol_list):
        selected_list = [message_symbol_list[i] for i, g in enumerate(generator_row) if g == 1]
        coded_symbol = BitArray( [0] * len(message_symbol_list[0]) )
        for s in selected_list:
            coded_symbol = coded_symbol.__xor__(s)
        
        return coded_symbol
    
    #
    # To print the list in a nice format
    # 
    def print_list(input_list):
        for i, g in enumerate(input_list):
            print ('[%02d]: %s' % (i, g.bin) )  
    
    #-------------------------------------------------------------------
    

    
    randnum = random.randint(0,100000)
    random.seed(randnum)
    print ('randnum = %d' % randnum)
    
    # Data
    total_message_symbol = 10 # This message has $total_message_symbol symbols.
    message_symbol_size = 10  # The message symbol has $message_symbol_size bits.
    
    # Total generator row to generate.
    total_generator_row = total_message_symbol + 10 # I will generate k+10 rows.
    
    generator_list = []
    data_list = []
    coded_symbol_list = []
    
    #
    # Generate message symbols.
    #
    for i in range(total_message_symbol):
        data_bitarr = BitArray([random.choice([0, 1]) for i in range(message_symbol_size)])
        data_list.append(data_bitarr)
    
    #
    # Generate generator_list and coded_symbol_bv_list.
    #
    for i in range(total_generator_row):
        generator_bitarr = BitArray([random.choice([0, 1]) for i in range(total_message_symbol) ])
        generator_list.append( generator_bitarr )
        
        coded_symbol_list.append( generate_coded_symbol(generator_bitarr, data_list) )
    
    #
    # Report
    #

    ge = Gaussian_Elimination()

    print ('#------------------------------------------------------------')
    print ('Sage 0: Original data')
    print ('#------------------------------------------------------------')
    
    print ('data_list :')
    print_list (data_list)
    print 
    
    print ('generator_list :')
    print_list (generator_list)
    print 
    
    print ('coded_symbol_list :')
    print_list (coded_symbol_list)
    print 

    
    print ('#------------------------------------------------------------')
    print ('Step 1: form_triangle_matrix')
    print ('#------------------------------------------------------------')
    
    ge.form_triangle_matrix(generator_list, coded_symbol_list)
    print ('generator_list :')
    print_list (generator_list)
    print
    
    print ('coded_symbol_list :')
    print_list (coded_symbol_list)
    print

    print ('#------------------------------------------------------------')
    print ('Step 2: backward_substitution')
    print ('#------------------------------------------------------------')

    ge.backward_substitution(generator_list, coded_symbol_list)
    print ('generator_list :')
    print_list (generator_list)
    print
    
    print ('coded_symbol_list :')
    print_list (coded_symbol_list)
    print

    print ('#------------------------------------------------------------')
    print ('Step 3: Verification')
    print ('#------------------------------------------------------------')
    # print ('The first %d rows of coded_symbol_list')
    print ('coded_symbol_list[0:total_message_symbol]:')
    print_list (coded_symbol_list[0:total_message_symbol])
    print

    print ('data_list:')
    print_list (data_list)
    print


    if coded_symbol_list[0:total_message_symbol] == data_list:
        print ('Decoding correctly')
    else:
        print ('Decoding wrongly')
