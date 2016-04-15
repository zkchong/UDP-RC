
TYPE = 100
TYPE_DATA = 200
TYPE_ACK = 300

COUNTER =  500

# TYPE_REQ

# The sender will create a random session id in the first packet.
SESSION_ID = COUNTER; COUNTER += 1 

# ID of the DATA.
DATA_ID = COUNTER; COUNTER += 1

# ID of the ACK. The receiver will use the same DATA_ID that it receives as ACK_ID.
ACK_ID = COUNTER; COUNTER += 1

# To put the encoded symbols and its necessary information.
DATA = COUNTER; COUNTER += 1

# For sender to pass the meta information about the message, i.e. message siza and total message symbol.
DATA_DESCRIPTION = COUNTER; COUNTER += 1

# For the sender and receiver to pass exit signal.
EXIT = COUNTER; COUNTER += 1


# TOTAL_RECV = COUNTER; COUNTER += 1
# MAX_RATE = COUNTER; COUNTER += 1

# REQ_ID = TYPE_REQ + COUNTER; COUNTER+= 1


# # REQ_CODE = TYPE_REQ + COUNTER; COUNTER+= 1
# REQ_DATA = TYPE_REQ + COUNTER; COUNTER+= 1
# REQ_EXIT = TYPE_REQ + COUNTER; COUNTER+= 1
# REQ_MESSAGE_SIZE = TYPE_REQ + COUNTER; COUNTER+= 1
# REQ_TOTAL_MESSAGE_SYMBOL = TYPE_REQ + COUNTER; COUNTER+= 1




# # TYPE_RSP

# RSP_ID = TYPE_RSP + COUNTER; COUNTER+= 1
# # RSP_PE = TYPE_RSP + COUNTER; COUNTER+= 1
# RSP_RECV = TYPE_RSP + COUNTER; COUNTER+= 1
# RSP_EXIT = TYPE_RSP + COUNTER; COUNTER+= 1
# # RSP_MAX_RATE = TYPE_RSP + COUNTER; COUNTER+= 1
