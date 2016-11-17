import logging
import time
from time import gmtime, strftime
from cache import Cache
from processor import Processor
import msi

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)
print 'start time: ' + strftime("%H:%M:%S", gmtime())
start_time = time.time()

block_size = 16
cache_size = 1024
assoc = 1

Bus = msi.BusMSI
CacheController = msi.CacheControllerMSI 

# initiate components
list_of_cc = []
bus = Bus(block_size, list_of_cc)

cache_0 = Cache(cache_size, block_size, assoc, msi.INVALID)
cc_0 = CacheController(bus, cache_0)
pr_0 = Processor('blackscholes_0.data', cc_0)
list_of_cc.append(cc_0)

cache_1 = Cache(cache_size, block_size, assoc, msi.INVALID)
cc_1 = CacheController(bus, cache_1)
pr_1 = Processor('blackscholes_1.data', cc_1)
list_of_cc.append(cc_1)

cache_2 = Cache(cache_size, block_size, assoc, msi.INVALID)
cc_2 = CacheController(bus, cache_2)
pr_2 = Processor('blackscholes_2.data', cc_2)
list_of_cc.append(cc_2)

cache_3 = Cache(cache_size, block_size, assoc, msi.INVALID)
cc_3 = CacheController(bus, cache_3)
pr_3 = Processor('blackscholes_3.data', cc_3)
list_of_cc.append(cc_3)

while(True):
    is_running_0 = pr_0.tick()
    is_running_1 = pr_1.tick()
    is_running_2 = pr_2.tick()
    is_running_3 = pr_3.tick()

    bus.tick()

    if not (is_running_0 or is_running_1 or is_running_2 or is_running_3):
        break

    # print pr_0.cycle_count

print 'the end'
print 'cache miss count: ' + str(cc_0.miss_count)
print 'data traffic on bus: ' + str(bus.total_bytes_passed_on_bus)
print 'num of invalidations on bus: ' + str(bus.total_num_invalidations)
print 'private access: ' + str(cc_0.private_data_access_count)
print 'shared access: ' + str(cc_0.shared_data_access_count)
print 'total write latency: ' + str(pr_0.total_write_latency)
print 'total writes: ' + str(pr_0.total_num_writes) 
print 'cycle count: ' + str(pr_0.cycle_count)

end_time = time.time()
print 'time used in seconds' + str((end_time - start_time))
print 'end time: ' + strftime("%H:%M:%S", gmtime())
