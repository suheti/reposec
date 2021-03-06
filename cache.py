class Cache(object):
    '''
    A cache is a dictionary with set index (int) as key, and a list of
    (tag, state) pairs. The number of pairs in the list is determined by
    associativity.
    cache = dict{ set index : list[(tag, state)] }

    Note that the cache is protocol ignorant (only cache controller's behavior
    is determined by coherence protocl)

    A byte's address can be disected into 3 parts:
    | tag | set index | offset |
    '''
    def __init__(self, cache_size, block_size, assoc, default_state):
        self.cache_size = cache_size # number of bytes
        self.block_size = block_size # number of bytes
        self.assoc = assoc
        self.num_of_sets = cache_size/block_size/assoc
        self.word_size = 4 # number of bytes, fixed
        self.default_state = default_state

        self.cache = {}

    def get_state(self, address):
        '''Get the state of the block containing the requested address

        address: int

        return: state. If not found in cache, return default_state.
        '''
        identifier = address / self.block_size
        index = identifier % self.num_of_sets
        tag = identifier / self.num_of_sets

        current_set = self.cache.get(index)
        if current_set: # if set is not None and is not an empty list
            for pair in current_set:
                if tag == pair[0]:
                    i = current_set.index(pair)
                    if i != (self.assoc-1):
                        current_set.pop(i)
                        current_set.append(pair)
                    return pair[1]

        return self.default_state

    def set_state(self, address, new_state):
        '''Set or update the state of the referenced cache block.

        This method handles LRU logic as well. Each cache set is a python list
        of (tag, state) pairs. The Least Recently Used block has the lowest
        index in list, while the Most Recently Used has the highest index.
        '''
        identifier = address / self.block_size
        index = identifier % self.num_of_sets
        tag = identifier / self.num_of_sets

        current_set = self.cache.get(index)
        if current_set:
            for pair in current_set:
                if pair[0] == tag:
                    if new_state == self.default_state:
                        current_set.remove(pair)
                        return None
                    else:
                        current_set.remove(pair)
                        current_set.append((tag, new_state))
                        return None
            # if runs to here, means tag does not exist in the set
            if len(current_set) < self.assoc:
                current_set.append((tag, new_state))
                return None
            else: # set is already full
                evicted = current_set.pop(0)
                current_set.append((tag, new_state))
                return {'address':
                        evicted[0] * self.num_of_sets * self.block_size
                        + index * self.block_size,
                        'state': evicted[1]}

        else:
            if new_state == self.default_state:
                return None
            else:
                self.cache[index] = []
                self.cache[index].append((tag, new_state))
                return None
