from Pipeline import Pipeline
from tasks.HelloTask import HelloTask
from TaskFactory import TaskFactory

factory = TaskFactory(["HelloTask", "RandomTask"])

pipeline = Pipeline()
pipeline.read_nodz("./saves/sample.json")
pipeline.start()
# B = Task("B")
# C = Task("C")
# D = Task("D")
# E = Task("E")
# F = Task("F")

# A.run = increment
# B.run = increment
# C.run = decrement
# D.run = increment
# E.run = decrement
# F.run = increment

# pipeline.add_task(A)
# pipeline.add_task(B)
# pipeline.add_task(C)
# pipeline.add_task(D)
# pipeline.add_task(E)
# pipeline.add_task(F)

# pipeline.connect(A, B)
# pipeline.connect(C, D)
# pipeline.connect(B, C)
# pipeline.connect(C, D)
# pipeline.connect(D, E)
# pipeline.connect(D, F)

