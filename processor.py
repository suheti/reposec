import logging

class Processor(object):
    '''Emulate a processor core'''

    def __init__(self, filename, cache_controller):
        self.file = open(filename, 'r')
        self.cache_controller = cache_controller

        self.is_stalled = False
        self.count_down_cycle = 0

        self.cycle_count = 0

        self.total_num_writes = 0
        self.total_write_latency = 0
        self.write_start = 0
        self.write_finish = 0

    def tick(self):
        '''
        return: True if the processor should be further ticked;
                False if finished.
        '''

        self.cycle_count += 1

        if self.count_down_cycle > 0:
            self.count_down_cycle -= 1
            return True

        if self.is_stalled:
            return True

        nextline = self.file.readline()
        logging.debug(nextline[0:-1])
        # print nextline
        if nextline == '':
            return False

        instr = [int(x, 16) for x in nextline.split()]
        if instr[0] == 2: # non-mem instructions
            self.count_down_cycle = instr[1] - 1
        elif instr[0] == 0: # load
            self.is_stalled = True
            self.cache_controller.prrd(instr[1], self.resume)

        elif instr[0] == 1: # store
            self.is_stalled = True
            self.cache_controller.prwr(instr[1], self.resume)
            self.write_start = self.cycle_count
            self.total_num_writes += 1

        return True

    def resume(self):
        '''
        alled by the cache_controller to resume processor operation
        '''
        self.is_stalled = False
        if self.write_start > self.write_finish:
            self.write_finish = self.cycle_count
            self.total_write_latency += self.write_finish - self.write_start

