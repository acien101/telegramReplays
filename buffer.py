class Buffer:
    """Simple Buffer for collecting frames"""

    size = 0
    buff = []

    def __init__(self, size):
        self.size = size

    def put(self, data):
        self.buff.append(data)      # Add data
        if len(self.buff) > self.size:
            self.buff.pop(0)     # Pop last element

    def getbuff(self):
        return self.buff
