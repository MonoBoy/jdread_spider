import logging

class Logger:
    def __init__(self, name, filename):
        self.log = logging.getLogger(name)
        self.log.setLevel(logging.INFO)

        fmt = '%(asctime)s %(thread)d|%(threadName)s %(filename)s:%(lineno)s %(levelname)s %(name)s :%(message)s'
        formatter = logging.Formatter(fmt)

        # memory
        streamHandle = logging.StreamHandler()
        streamHandle.setFormatter(formatter)
        streamHandle.setLevel(logging.INFO)
        # file
        fileHandle = logging.FileHandler(filename)
        fileHandle.setFormatter(formatter)
        fileHandle.setLevel(logging.INFO)

        # add handle of memory and file
        self.log.addHandler(fileHandle)
        self.log.addHandler(streamHandle)

    def get_logger(self):
        return self.log