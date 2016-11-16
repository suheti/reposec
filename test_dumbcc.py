'''Test processor with a dumb cache_controller
'''
from processor import Processor

class Testcc(object):
    '''eiji'''

    def prwr(self, addr, callback):
        callback()

    def prrd(self, addr, callback):
        callback()


cc = Testcc()
pr = Processor("test_0.data", cc)

while pr.tick():
    pass

print 'finished'
print pr.total_num_writes
