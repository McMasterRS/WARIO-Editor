from Task import Task

class TestC(Task):

    def run(self, A, C):
        print("A C :", A, C)
        return {}


# class TestC(Task):

#     def __init__(self, A, B):
#         self.A = A
#         self.B = B

#     def run(self):
#         print("A C :", self.A, self.C)
#         return {}


# class TestC(Task):
 
#     def __init__(self):
#     # def __init__(self, config):
#     # def __init__(self, param1, param2):
#     # def __init__(self, param1=None, param2=None):
#         self.A = A
#         self.B = B

#     def run(self):
#     # def run(self, item):
#     # def run(self, A, B, C):
#         print("A C :", self.A, self.C)
#         return {}
