'''
A cache is a dictionary with set index (int) as key, and a list of 
(address, state) pairs. The number of pairs in the list is determined by
associativity.
'''
class Cache:
    def __init__(self, cache_size, block_size, assoc):
        self.cache_size = cache_size # number of bytes
        self.block_size = block_size # number of bytes
        self.assoc = assoc
        self.word_size = 4 # number of bytes, fixed

        self.cache = {}

    '''
    address: int

    return: state. If not found default return INVALID.
    '''
    def getState(self, address):
        return INVALID

    '''
    updateState of cache.
    this function should handle LRU logic as well, using python list 
    built in functions.

    return: None, or the (address, state) replaced. Note that cache is protocol
    ignorant.
    '''
    def setState(self, address, state):
        return None
