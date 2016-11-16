from cache import Cache

mycache = Cache(1024, 16, 1, 'invalid')

print 'get 1024' + str(mycache.get_state(1024))

print 'get 2970:' + str(mycache.get_state(2970))

return1024 = mycache.set_state(1025, 'modified')

print 'return1024:' + str(return1024)

return0 = mycache.set_state(0, 'shared')

print 'return0:' + str(return0)

print 'get 2970:' + str(mycache.get_state(2970))
