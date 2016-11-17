'''This module contains Bus class and Cache Controller for MSI protocol
'''
from collections import deque

# latency in cycles to access main memory
MEM_LATENCY = 100

# possible states
INVALID = 'invalid'
SHARED = 'shared'
MODIFIED = 'modified'

# message titles
BUSREAD = 'BusRd'
BUSREADX = 'BusRdX'
BUSWB = 'BusWB'
'''message format
a dictionary of values
{title: BUSREAD/BUSREADX/BUSWB,
 sender: the cache controller instance,
 address: the memory address the cache controller wishes to operate on,
 new state: the target state the memory block
 [callback: callback method for bus to inform cache controller that the tass
           is done]}
'''

def construct_message(title, sender, address, new_state=None, callback=None):
    '''helper function to construct a message'''
    return {'title': title, 'sender':sender,
            'address': address, 'new state': new_state,
            'callback':callback}

class CacheControllerMSI(object):
    '''Emulate the cache controller for MSI protocol

    general guideline for sending message to bus:
        If the message is induced by a processor action, i.e. prwr/prrd, it is
        queued to bus.
        If the message is induced by a bus action, i.e. receve_bus_message, it
        is reduced.
    '''
    def __init__(self, bus, cache):
        self.bus = bus
        self.cache = cache

        self.is_waiting = False
        self.addr_wating_for = -1
        self.processor_callback = None

        self.hit_count = 0
        self.miss_count = 0
        self.private_data_access_count = 0
        self.shared_data_access_count = 0

    def prrd(self, address, pr_callback):
        '''respond to processor's PrRd call

        pr_callback: processor's callback function
        '''
        current_state = self.cache.get_state(address)
        if current_state == INVALID:
            self.miss_count += 1
            self.shared_data_access_count += 1
            message = construct_message(BUSREAD, self, address, SHARED,
                                        pr_callback)
            self.bus.queue_message(message)
            return # method exit point 1
        elif current_state == SHARED:
            self.hit_count += 1
            self.shared_data_access_count += 1
        elif current_state == MODIFIED:
            self.hit_count += 1
            self.private_data_access_count += 1

        pr_callback() # call back processor
        return # method exit point 2

    def prwr(self, address, pr_callback):
        '''respond to processor's PrWr call'''
        current_state = self.cache.get_state(address)
        if (current_state == INVALID) or (current_state == SHARED):
            self.miss_count += 1
            self.private_data_access_count += 1
            message = construct_message(BUSREADX, self, address, MODIFIED,
                                        pr_callback)
            self.bus.queue_message(message)
            return # method exit point 1
        elif current_state == MODIFIED:
            self.hit_count += 1
            self.private_data_access_count += 1

        pr_callback() # call back processor
        return # method exit point 2

    def receive_bus_message(self, message):
        '''Handles message propagated by bus

        By contract:
        Three types of message can appear on the bus and propagate to cache
        controllers: BusRd, BusRdX, BusWB.
        The bus sends back BusRd/BusRdX messages to the original sender to
        indicate successful data transfer. The cache controller does not need to
        know the source of this data.

        The bus does not propagate BusWB to cache controllers. Instead, when the
        flushed write back data needs to be sent back to a controller, the bus
        sends back the BusRd or BusRdX message to signal the cache controller
        that the data is ready.

        BusWB incurred due to the cache controller's own message (i.e. evistion)
        is enqueued to bus. In contrast, BusWB incurred due to other cache
        controllers' message is returned by the function. This is in accordance
        with the "general guideline for sending message to bus" in the class
        docstring.

        Upon receiving the message, the cache controller needs to do some or all
        of the following where applicable:
        - update cache line state
        - callback processor
        - flush line, if there is evicted line and it is in M state

        return:
            None. Or flushed line.
        '''
        if message['sender'] == self:
            evicted = self.cache.set_state(message['address'],
                                           message['new state'])
            if (evicted) and (evicted['state'] == MODIFIED):
                new_message = construct_message(BUSWB, self, evicted['address'])
                self.bus.queue_message(new_message)
            message['callback']() # processor callback
            return None # method exit point 1

        # if the message is from other cache controllers
        mystate = self.cache.get_state(message['address'])
        if message['title'] == BUSREAD:
            if mystate == MODIFIED:
                self.cache.set_state(message['address'], SHARED)
                new_message = construct_message(BUSWB, self, message['address'])
                return new_message # method exit point 2
        elif message['title'] == BUSREADX:
            if mystate == SHARED:
                self.cache.set_state(message['address'], INVALID)
                return None # method exit point 3
            elif mystate == MODIFIED:
                self.cache.set_state(message['address'], INVALID)
                new_message = construct_message(BUSWB, self, message['address'])
                return new_message # method exit point 4

        return None # method exit point 5, default return None

class BusMSI(object):
    '''Emulate the bus line for MSI protocol

    The bus uses a deque as its message queue:
        enqueue is msg_q.append()
        dequeue is msg_q.popleft()
    '''
    def __init__(self, block_size, list_of_cc):
        '''list_of_cc: the list of cache controllers(cc)'''
        self.CACHE_COUNTDOWN = block_size-1 # cache-cache data transfer countdown
        self.MEM_COUNTDOWN = MEM_LATENCY-1
        self.block_size = block_size
        self.msg_q = deque()
        self.list_of_cc = list_of_cc

        '''default value of countdown timers is -1, indicating the bus is not
        stalled.
        '''
        self.countdown_memory = -1
        self.countdown_cache = -1
        self.active_message = None

        self.total_bytes_passed_on_bus = 0
        # count the number of BusRdX appeared on bus
        self.total_num_invalidations = 0

    def tick(self):
        '''Emulates a clock tick'''
        if self.countdown_memory >= 0:
            if self.countdown_cache >= 0:
                # if cache-cache transfer is done
                if self.countdown_cache == 0:
                    '''only when active_message is BusRd/BusRdX, the
                    countdown_cache timer can be set. So it is guranteed that
                    BusWB won't be sent back to cache controllers.
                    '''
                    self.active_message['sender'].receive_bus_message(
                        self.active_message)
                    # clear variable once the message is sent back
                    self.active_message = None
                    # decrement the countdown timers before return
                    self.countdown_cache -= 1
                    self.countdown_memory -= 1
                    return # method exit point 1
                self.countdown_cache -= 1

            # if memory transfer is done
            if self.countdown_memory == 0:
                # if active_message is not None and not BusWB
                if (self.active_message and
                        self.active_message['title'] != BUSWB):
                    self.active_message['sender'].receive_bus_message(
                        self.active_message)
                self.active_message = None # this statement is actually not necessary?
            self.countdown_memory -= 1
            return # method exit point 2

        if self.msg_q:
            self.active_message = self.msg_q.popleft()

            # increment analysis stats
            self.total_bytes_passed_on_bus += self.block_size
            if self.active_message['title'] == BUSREADX:
                self.total_num_invalidations += 1

            if (self.active_message['title'] == BUSREAD or
                    self.active_message['title'] == BUSREADX):
                sender = self.active_message['sender']
                other_cc = {c for c in self.list_of_cc if c not in [sender]}
                flush = None
                '''A cache with the requested address in Modified state would
                flush the block. Otherwise flush is None'''
                for cache_controller in other_cc:
                    flush = cache_controller.receive_bus_message(self.active_message)
                    if flush:
                        break
                if flush:
                    self.countdown_cache = self.CACHE_COUNTDOWN
                self.countdown_memory = self.MEM_COUNTDOWN
            elif self.active_message['title'] == BUSWB:
                self.countdown_memory = self.MEM_COUNTDOWN

        return # method exit point 4, default exit point

    def queue_message(self, message):
        '''enqueue a message'''
        self.msg_q.append(message)
