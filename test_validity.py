import logging
import time
from time import gmtime, strftime
from cache import Cache
from processor import Processor
import mesi
import msi
import dragon
import msiu

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)
print 'start time: ' + strftime("%H:%M:%S", gmtime())
start_time = time.time()

block_size = 16
cache_size = 1024
assoc = 1

num_of_sets = cache_size/block_size/assoc
def print_cache(cache):
    for index in cache:
        for (tag, state) in cache[index]:
            address = tag * num_of_sets * block_size + index * block_size
            print "%s : %s" % ("{0:#0{1}x}".format(address,8), state)

choice = 'dragon'
filename = 'test_dragon'

if choice == 'msi':
    Bus = msi.BusMSI
    CacheController = msi.CacheControllerMSI
    DefaultState = msi.INVALID
elif choice == 'mesi':
    Bus = mesi.BusMESI
    CacheController = mesi.CacheControllerMESI
    DefaultState = mesi.INVALID
elif choice == 'msiu':
    Bus = msiu.BusMSIu
    CacheController = msiu.CacheControllerMSIu
    DefaultState = msiu.INVALID
else:
    Bus = dragon.BusDragon
    CacheController = dragon.CacheControllerDragon
    DefaultState = dragon.INVALID


# initiate components
list_of_cc = []
bus = Bus(block_size, list_of_cc)

cache_0 = Cache(cache_size, block_size, assoc, DefaultState)
cc_0 = CacheController(bus, cache_0)
pr_0 = Processor(filename + '_0.data', cc_0)
list_of_cc.append(cc_0)

cache_1 = Cache(cache_size, block_size, assoc, DefaultState)
cc_1 = CacheController(bus, cache_1)
pr_1 = Processor(filename + '_1.data', cc_1)
list_of_cc.append(cc_1)

'''
cache_2 = Cache(cache_size, block_size, assoc, DefaultState)
cc_2 = CacheController(bus, cache_2)
pr_2 = Processor('blackscholes_2.data', cc_2)
list_of_cc.append(cc_2)

cache_3 = Cache(cache_size, block_size, assoc, DefaultState)
cc_3 = CacheController(bus, cache_3)
pr_3 = Processor('blackscholes_3.data', cc_3)
list_of_cc.append(cc_3)
'''

is_running_0 = True
is_running_1 = True
# is_running_2 = True
# is_running_3 = True
while(True):
    is_running_0 = pr_0.tick()
    is_running_1 = pr_1.tick()
    '''
    if is_running_0:
        is_running_0 = pr_0.tick()
        if not is_running_0:
            list_of_cc.remove(cc_0)

    if is_running_1:
        is_running_1 = pr_1.tick()
        if not is_running_1:
            list_of_cc.remove(cc_1)
    
    if is_running_2:
        is_running_2 = pr_2.tick()
        if not is_running_2:
            list_of_cc.remove(cc_2)

    if is_running_3:
        is_running_3 = pr_3.tick()
        if not is_running_3:
            list_of_cc.remove(cc_3)
    '''


    bus.tick()

    if not (is_running_0 or is_running_1):# or is_running_2 or is_running_3):
        break

    # print pr_0.cycle_count

print 'core0'
print 'cache miss count: ' + str(cc_0.miss_count)
print 'cache hit count: ' + str(cc_0.hit_count)
print 'private access: ' + str(cc_0.private_data_access_count)
print 'shared access: ' + str(cc_0.shared_data_access_count)
print 'total write latency: ' + str(pr_0.total_write_latency)
print 'total writes: ' + str(pr_0.total_num_writes)
print 'cycle count: ' + str(pr_0.cycle_count)
print

print 'cache0'
print_cache(cache_0.cache)
print

print 'core1'
print 'cache miss count: ' + str(cc_1.miss_count)
print 'cache hit count: ' + str(cc_1.hit_count)
print 'private access: ' + str(cc_1.private_data_access_count)
print 'shared access: ' + str(cc_1.shared_data_access_count)
print 'total write latency: ' + str(pr_1.total_write_latency)
print 'total writes: ' + str(pr_1.total_num_writes)
print 'cycle count: ' + str(pr_1.cycle_count)
print

print 'cache1'
print_cache(cache_1.cache)
print

'''
print 'core2'
print 'cache miss count: ' + str(cc_2.miss_count)
print 'cache hit count: ' + str(cc_2.hit_count)
print 'private access: ' + str(cc_2.private_data_access_count)
print 'shared access: ' + str(cc_2.shared_data_access_count)
print 'total write latency: ' + str(pr_2.total_write_latency)
print 'total writes: ' + str(pr_2.total_num_writes)
print 'cycle count: ' + str(pr_2.cycle_count)
print

print 'core3'
print 'cache miss count: ' + str(cc_3.miss_count)
print 'cache hit count: ' + str(cc_3.hit_count)
print 'private access: ' + str(cc_3.private_data_access_count)
print 'shared access: ' + str(cc_3.shared_data_access_count)
print 'total write latency: ' + str(pr_3.total_write_latency)
print 'total writes: ' + str(pr_3.total_num_writes)
print 'cycle count: ' + str(pr_3.cycle_count)
print
'''

print 'data traffic on bus: ' + str(bus.total_bytes_passed_on_bus)
print 'num of invalidations on bus: ' + str(bus.total_num_invalidations)

end_time = time.time()
print 'time used in seconds: ' + str((end_time - start_time))
print 'end time: ' + strftime("%H:%M:%S", gmtime())
