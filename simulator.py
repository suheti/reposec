from sys import argv
from cache import Cache
from processor import Processor
import msi
import mesi
import dragon
import time
from time import gmtime, strftime
import logging

_, protocol, input_file, cache, associativity, block= argv
cache_size = int(cache)
assoc = int(associativity)
block_size = int(block)

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)
print 'start time: ' + strftime("%H:%M:%S", gmtime())
start_time = time.time()

"""
dataset = ['blackscholes', 'bodytrack', 'fluidanimate']
cache_size = 1024#[1024,8192,32768]
assoc = 1#[1,2,4]
block_size = 16#[8, 32, 128]
"""
if protocol == 'msi':
    Bus = msi.BusMSI
    CacheController = msi.CacheControllerMSI
    DefaultState = msi.INVALID
elif protocol == 'mesi':
    Bus = mesi.BusMESI
    CacheController = mesi.CacheControllerMESI
    DefaultState = mesi.INVALID
elif protocol == 'dragon':
    Bus = dragon.BusDragon
    CacheController = dragon.CacheControllerDragon
    DefaultState = dragon.INVALID
else:
    exit("Wrong protocol")

# initiate components
list_of_cc = []
bus = Bus(block_size, list_of_cc)

cache_0 = Cache(cache_size, block_size, assoc, DefaultState)
cc_0 = CacheController(bus, cache_0)
pr_0 = Processor(input_file + '_0.data', cc_0)
list_of_cc.append(cc_0)

cache_1 = Cache(cache_size, block_size, assoc, DefaultState)
cc_1 = CacheController(bus, cache_1)
pr_1 = Processor(input_file + '_1.data', cc_1)
list_of_cc.append(cc_1)
#"""
cache_2 = Cache(cache_size, block_size, assoc, DefaultState)
cc_2 = CacheController(bus, cache_2)
pr_2 = Processor(input_file + '_2.data', cc_2)
list_of_cc.append(cc_2)

cache_3 = Cache(cache_size, block_size, assoc, DefaultState)
cc_3 = CacheController(bus, cache_3)
pr_3 = Processor(input_file + '_3.data', cc_3)
list_of_cc.append(cc_3)
#"""
is_running_0 = True
is_running_1 = True
is_running_2 = True
is_running_3 = True
while(True):
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

    bus.tick()

    if not (is_running_0 or is_running_1 or is_running_2 or is_running_3):
        break

    # print pr_0.cycle_count
"""
print 'cache miss count: ' + str(cc_0.miss_count)
print 'private access: ' + str(cc_0.private_data_access_count)
print 'shared access: ' + str(cc_0.shared_data_access_count)
print 'total write latency: ' + str(pr_0.total_write_latency)
print 'total writes: ' + str(pr_0.total_num_writes)
print 'cycle count: ' + str(pr_0.cycle_count)
print '\n'

print 'cache miss count: ' + str(cc_1.miss_count)
print 'private access: ' + str(cc_1.private_data_access_count)
print 'shared access: ' + str(cc_1.shared_data_access_count)
print 'total write latency: ' + str(pr_1.total_write_latency)
print 'total writes: ' + str(pr_1.total_num_writes)
print 'cycle count: ' + str(pr_1.cycle_count)
print '\n'

print 'cache miss count: ' + str(cc_2.miss_count)
print 'private access: ' + str(cc_2.private_data_access_count)
print 'shared access: ' + str(cc_2.shared_data_access_count)
print 'total write latency: ' + str(pr_2.total_write_latency)
print 'total writes: ' + str(pr_2.total_num_writes)
print 'cycle count: ' + str(pr_2.cycle_count)
print '\n'

print 'cache miss count: ' + str(cc_3.miss_count)
print 'private access: ' + str(cc_3.private_data_access_count)
print 'shared access: ' + str(cc_3.shared_data_access_count)
print 'total write latency: ' + str(pr_3.total_write_latency)
print 'total writes: ' + str(pr_3.total_num_writes)
print 'cycle count: ' + str(pr_3.cycle_count)
print '\n'

print 'data traffic on bus: ' + str(bus.total_bytes_passed_on_bus)
print 'num of invalidations on bus: ' + str(bus.total_num_invalidations)

end_time = time.time()
print 'time used in seconds' + str((end_time - start_time))
print 'end time: ' + strftime("%H:%M:%S", gmtime())
"""
output=open(input_file+protocol+'.csv','a')
output.write(' ,miss count,hit count,miss rate, private data access count,shared data access count,'+
             'total write latency,total num writes,average write latency,cycle count,'+
             'total bytes passes on bus,bus invalidation/updates,num evictions\n')
result_0 = ['cache size:'+(str(cache_size)), cc_0.miss_count, cc_0.hit_count, cc_0.miss_count/(cc_0.miss_count+cc_0.hit_count+0.0),
            cc_0.private_data_access_count, cc_0.shared_data_access_count, pr_0.total_write_latency,
            pr_0.total_num_writes, pr_0.total_write_latency/(pr_0.total_num_writes+0.0), pr_0.cycle_count,
            bus.total_bytes_passed_on_bus, bus.total_num_invalidations, bus.total_num_evictions]

result_1 = ['block size:'+(str(block_size)), cc_1.miss_count, cc_1.hit_count, cc_1.miss_count/(cc_1.miss_count+cc_1.hit_count+0.0),
            cc_1.private_data_access_count, cc_1.shared_data_access_count, pr_1.total_write_latency,
            pr_1.total_num_writes, pr_1.total_write_latency/(pr_1.total_num_writes+0.0), pr_1.cycle_count]

result_2 = ['associativity:'+(str(assoc)), cc_2.miss_count, cc_2.hit_count, cc_2.miss_count/(cc_2.miss_count+cc_2.hit_count+0.0),
            cc_2.private_data_access_count, cc_2.shared_data_access_count, pr_2.total_write_latency,
            pr_2.total_num_writes, pr_2.total_write_latency/(pr_2.total_num_writes+0.0), pr_2.cycle_count]

result_3 = ['protocol: '+(str(protocol)), cc_3.miss_count, cc_3.hit_count, cc_3.miss_count/(cc_3.miss_count+cc_3.hit_count+0.0),
            cc_3.private_data_access_count, cc_3.shared_data_access_count, pr_3.total_write_latency,
            pr_3.total_num_writes, pr_3.total_write_latency/(pr_3.total_num_writes+0.0), pr_3.cycle_count]

output.write(','.join(map(str, result_0))+'\n')
output.write(','.join(map(str, result_1))+'\n')
output.write(','.join(map(str, result_2))+'\n')
output.write(','.join(map(str, result_3))+'\n')
output.write('\n')
output.close()