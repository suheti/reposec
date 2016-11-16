
# states
EXCLUSIVE= 'Exclusive'
MODIFIED = 'Modified'
SC = 'SharedClean'
SM = 'SharedModified'

# operations
VALID = 'valid'
INVALID = 'invalid'
PRRD = 'PrRd'
PRWR = 'PrWr'
PRRDMISS = 'PrRdMiss'
PRWRMISS = 'PrWrMiss'
BUSRD = 'BusRd'
BUSUPD = 'BusUpd'
BUSRDS = 'BusRdS'
BUSRDNS = 'BusRdNotS'
BUSUPDS = 'BusUpdS'
BUSUPDNS = 'BusUpdNotS'
UPDATE = 'Update'
FLUSH = 'flush'

# state machine
# New state, bus transaction, time tick
# A bad state machine implmentation
"""
State_Machine = {
    EXCLUSIVE: {
        PRRD: (EXCLUSIVE, None, 1),
        PRWR: (MODIFIED, None, 1),
        BUSRD: (SC, None, 100),
    },
    MODIFIED: {
        PRRD: (MODIFIED, None, 1),
        PRWR: (MODIFIED, None, 1),
        BUSRD: (SM, FLUSH, 100),
    },
    SC: {
        PRRD: (SC, None, 1),
        PRWR: (SM, BUSUPDS, 100),
        BUSUPD: (SC, UPDATE, 100),
        
    }
}"""
