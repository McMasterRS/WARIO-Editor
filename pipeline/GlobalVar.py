import sys

class GlobalVar():
    def __init__(self, type, val, cons):
        self.__type = type
        self.__val = val
        self.__cons = cons
        
    def getVal(self):
        return self.__val
        
    def setVal(self, newVal):
        assert(not self.__cons), "ERROR: ATTEMPTED TO MODIFY VALUE OF CONSTANT GLOBAL VARIABLE"
        self.__val = newVal

