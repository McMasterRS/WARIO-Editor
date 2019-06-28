from Pipeline import Pipeline
from tasks.HelloTask import HelloTask
from TaskFactory import TaskFactory

factory = TaskFactory(["ReadFileTask", "ConsoleLogTask", "RandomIntTask", "TestA", "TestB", "TestC", "TestD", "TestZ"])
pipeline = Pipeline()
A = factory.create_task("TestA", "TestA")
B = factory.create_task("TestB", "TestB")
C = factory.create_task("TestC", "TestC")
D = factory.create_task("TestD", "TestD")
Z = factory.create_task("TestZ", "TestZ")

pipeline.add_task(A)
pipeline.add_task(B)
pipeline.add_task(C)
pipeline.add_task(D)
pipeline.add_task(Z)
pipeline.connect(A, C)
pipeline.connect(A, D)
pipeline.connect(B, C)
pipeline.connect(B, D)
pipeline.connect(B, Z)

pipeline.start()

# pipeline = Pipeline()

# A = factory.create_task("ReadFileTask", "ReadFileTask")

# B = factory.create_task("ConsoleLogTask", "ConsoleLogTask")

# C = factory.create_task("RandomIntTask", "RandomIntTask")

# pipeline.add_task(A)

# pipeline.add_task(B)

# pipeline.add_task(C)

# pipeline.connect(A, B)
# pipeline.connect(C, B)

# print(pipeline.tasks)

# pipeline.start("./test.txt")