from copy import copy

from gtrackcore_memmap.input.wrappers.GEFilter import GEFilter

class GEMarkRemover(GEFilter):
    def __init__(self, geSource):
        GEFilter.__init__(self, geSource)
    
    def next(self):
        nextEl = copy(self._geIter.next())
        nextEl.val = None
        return nextEl
    
    def getValDataType(self):
        return None
