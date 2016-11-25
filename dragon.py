'''This module contains Bus class and Cache Controller for MESI protocol

general guideline for cache and bus design:
    Bus and cc when interpreting messages should be state-less. Any state
    information should be explicitly carried in the message.
'''

from collections import deque

# latency in cycles to access main memory
MEM_LATENCY = 100

# possible states
INVALID = 'invalid'
SHARED_CLEAN = 'sharedc'
SHARED_MODIFIED = 'sharedm'
EXCLUSIVE = 'exclusive'
MODIFIED = 'modified'

# message titles
BUSREAD = 'BusRd'
BUSUPD = 'BusUpd'
BUSWB = 'BusWB'
'''message format
a dictionary of values
{title: BUSREAD/BUSUPD/BUSWB,
 sender: the cache controller instance that initiated this message,
 address: the memory address the cache controller wishes to operate on,
 [callback: callback method for bus to inform cache controller that the tass
           is done],
 [share status: True/False, whether the cache block is shared among
        caches, applicable only to BusRead message returned to original sender.
        This attribute is only added by bus, not upon message construction],
 [from prwr: True/False, added by cache controller into BUSREAD messages. This
        is used to determine the action to be taken by the cache controller upon
        receiving back its own BUSREAD.]
}
'''

def construct_message(title, sender, address, callback=None):
    '''helper function to construct a message'''
    return {'title': title, 'sender':sender,
            'address': address, 'callback':callback}

class CacheControllerDragon(object):
    '''Emulate the cache controller for Dragon protocol

    general guideline for sending message to bus:
        If the message is induced by the cache controller's own processor's
        action, i.e. prwr/prrd, it is queued to bus.
        If the message is induced by other controller's action, in
        receve_bus_message(), it is reduced.
    '''
    def __init__(self, bus, cache):
        self.bus = bus
        self.cache = cache

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
            #TODO: share/private data stats for BusRd is done in receive_bus_message
            message = construct_message(BUSREAD, self, address,
                                        pr_callback)
            message['from prwr'] = False
            self.bus.queue_message(message)
            return # method exit point 1
        elif current_state in (SHARED_CLEAN, SHARED_MODIFIED):
            self.shared_data_access_count += 1
        elif current_state in (EXCLUSIVE, MODIFIED):
            self.private_data_access_count += 1

        self.hit_count += 1
        pr_callback()
        return # method exit point 2

    def prwr(self, address, pr_callback):
        '''respond to processor's PrWr call'''
        current_state = self.cache.get_state(address)
        if current_state == INVALID:
            self.miss_count += 1
            #TODO: share/private data stats for BusRd is done in receive_bus_message
            message = construct_message(BUSREAD, self, address,
                                        pr_callback)
            message['from prwr'] = True
            self.bus.queue_message(message)
            return
        elif current_state in (SHARED_CLEAN, SHARED_MODIFIED):
            # depending on the share status, new state will be Sm or M
            self.hit_count += 1
            #TODO: share/private data stats for BusRd is done in receive_bus_message
            message = construct_message(BUSUPD, self, address,
                                        pr_callback)
            message['from prwrmiss'] = False
            self.bus.queue_message(message)
            return
        elif current_state == EXCLUSIVE:
            self.cache.set_state(address, MODIFIED)
        elif current_state == MODIFIED:
            pass

        self.hit_count += 1
        self.private_data_access_count += 1
        pr_callback()
        return

    def receive_bus_message(self, message):
        '''Handles message propagated by bus

        return one of the below:
            None
            {flush: True/False, shared: True/False}
            True/Fals - in response to BusUpd(S?) queries
        '''
        if message['sender'] == self:
            evicted = None
            if message['title'] == BUSREAD: # The referred address is in state INVALID
                if message['from prwr']:
                    if message['share status']: # SHARED_MODIFIED
                        # evicted = self.cache.set_state(message['address'], SHARED_MODIFIED)
                        new_message = construct_message(BUSUPD, self, message['address'], message['callback'])
                        new_message['from prwrmiss'] = True
                        self.bus.queue_message(new_message)
                        return None
                    else: # MODIFIED
                        evicted = self.cache.set_state(message['address'], MODIFIED)
                        self.private_data_access_count += 1
                else:
                    if message['share status']:# SAHRED_CLEAN
                        evicted = self.cache.set_state(message['address'], SHARED_CLEAN)
                        self.shared_data_access_count += 1
                    else: # EXCLUSIVE
                        evicted = self.cache.set_state(message['address'], EXCLUSIVE)
                        self.private_data_access_count += 1

            elif message['title'] == BUSUPD:
                if 'from prwrmiss' in message:
                    evicted = self.cache.set_state(message['address'], SHARED_MODIFIED)
                    self.shared_data_access_count += 1
                elif 'share status' in message:
                    # Sc -> Sm/M, Sm -> Sm/M
                    if message['share status']: # SHARED_MODIFIED
                        self.cache.set_state(message['address'], SHARED_MODIFIED)
                        self.shared_data_access_count += 1
                    else: # MODIFIED
                        self.cache.set_state(message['address'], MODIFIED)
                        self.private_data_access_count += 1

            if (evicted) and (evicted['state'] in (MODIFIED, SHARED_MODIFIED)):
                new_message = construct_message(BUSWB, self, evicted['address'])
                self.bus.queue_message(new_message)

            message['callback']()
            return None # method exit point 1

        # if the message is from other cache controllers
        mystate = self.cache.get_state(message['address'])
        if message['title'] == BUSREAD:
            flush = False
            shared = True
            if mystate == EXCLUSIVE:
                flush = False
                shared = True
                self.cache.set_state(message['address'], SHARED_CLEAN)
            elif mystate == SHARED_CLEAN:
                flush = False
                shared = True
            elif mystate == SHARED_MODIFIED:
                flush = True
                shared = True
            elif mystate == MODIFIED:
                flush = True
                shared = True
                self.cache.set_state(message['address'], SHARED_MODIFIED)
            elif mystate == INVALID:
                flush = False
                shared = False
            return {'flush':flush, 'shared':shared} # method exit point 2

        elif message['title'] == BUSUPD:
            # Note that is is impossible to receive an update from other processor
            # to a block in E/M
            # And Sc receiving a BusUpd has no effect
            shared = True
            if mystate == SHARED_MODIFIED:
                self.cache.set_state(message['address'], SHARED_CLEAN)
                shared = True
            elif mystate == SHARED_CLEAN:
                shared = True
            elif mystate == INVALID:
                shared = False
            return shared

        return None # method exit point 3, default return

class BusDragon(object):
    '''Emulate the bus line for Dragon protocol

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
        self.total_num_evictions = 0

    def tick(self):
        '''Emulates a clock tick'''
        if self.countdown_memory >= 0:
            if self.countdown_cache >= 0:
                # if cache-cache transfer is done
                if self.countdown_cache == 0:
                    '''only when active_message is BusRd/BusUpd, the
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
                if ((self.active_message) and
                        (self.active_message['title'] != BUSWB)):
                    self.active_message['sender'].receive_bus_message(
                        self.active_message)
                self.active_message = None # this statement is actually not necessary?

                '''when block_size > mem_latency,cache countdown should be reset
                here to avoid bleeding into next active_message's countdown!
                '''
                self.countdown_cache = -1
            self.countdown_memory -= 1
            return # method exit point 2

        if self.msg_q:
            self.active_message = self.msg_q.popleft()

            # increment analysis stats
            if self.active_message['title'] == BUSUPD:
                self.total_num_invalidations += 1

            if self.active_message['title'] == BUSREAD:
                self.total_bytes_passed_on_bus += self.block_size

                sender = self.active_message['sender']
                other_cc = {c for c in self.list_of_cc if c not in [sender]}
                is_shared = False
                '''A cache with the requested address in Modified state would
                flush the block. The returned messag will contain [share status]'''
                for cache_controller in other_cc:
                    returned = cache_controller.receive_bus_message(self.active_message)
                    if returned['flush']:
                        self.countdown_cache = self.CACHE_COUNTDOWN
                        is_shared = True
                        break
                    is_shared = is_shared or returned['shared']
                self.active_message['share status'] = is_shared

                self.countdown_memory = self.MEM_COUNTDOWN
            elif self.active_message['title'] == BUSUPD:
                self.total_bytes_passed_on_bus += 4 # TODO:word size, hard coded

                sender = self.active_message['sender']
                other_cc = {c for c in self.list_of_cc if c not in [sender]}
                is_shared = False
                '''A cache with the requested address in Modified state would
                flush the block. Otherwise flush is None'''
                for cache_controller in other_cc:
                    is_shared = (is_shared or
                                 cache_controller.receive_bus_message(self.active_message))
                self.active_message['share status'] = is_shared
                sender.receive_bus_message(self.active_message)

            elif self.active_message['title'] == BUSWB:
                self.total_bytes_passed_on_bus += self.block_size
                self.countdown_memory = self.MEM_COUNTDOWN
                self.total_num_evictions += 1

        return # method exit point 4, default exit point

    def queue_message(self, message):
        '''enqueue a message'''
        self.msg_q.append(message)
