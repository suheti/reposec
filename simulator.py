from sys import argv
from cache import Cache

_, protocol, input_file, cache_size, associativity, block_size = argv
simulator = Cache(cache_size, block_size, associativity)

#print protocol, input_file, cache_size, associativity, block_size
