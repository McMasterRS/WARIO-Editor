# Custom Signals

WARIO uses the blinker class for message passing. This class allows for the creation of signals with custom labels, each label acting as the signal's instance name. The signals are created as singletons, meaning that if you create signal objects with identical labels in two seperate files, they will both reference the same signal instance during runtime. This allows for the 