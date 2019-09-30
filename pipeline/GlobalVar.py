import sys

class GlobalVar():
    def __init__(self, type, val, cons):
        self.__type = type
        self.__val = val
        self.__cons = cons
        
    def getVal():
        return self.__val
        
    def setVal(newVal):
        if not self.__cons:
            self.__val = newVal
        else:
            print("ERROR: ATTEMPTED TO MODIFY VALUE OF CONSTANT GLOBAL VARIABLE")
            sys.exit()
