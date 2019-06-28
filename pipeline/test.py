from Pipeline import Pipeline
from tasks.HelloTask import HelloTask
from TaskFactory import TaskFactory

factory = TaskFactory(["ReadFileTask", "ConsoleLogTask", "RandomIntTask"])

pipeline = Pipeline()

A = factory.create_task("ReadFileTask", "ReadFileTask")

B = factory.create_task("ConsoleLogTask", "ConsoleLogTask")

C = factory.create_task("RandomIntTask", "RandomIntTask")

pipeline.add_task(A)

pipeline.add_task(B)

pipeline.add_task(C)

pipeline.connect(A, B)
pipeline.connect(C, B)

print(pipeline.tasks)

pipeline.start("./test.txt")