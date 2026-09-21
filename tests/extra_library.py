"""A test-only stand-in for an installed third-party library."""
class Widget:
    def __init__(self):
        self.value = 'hello'
    def read(self):
        return self.value
    def write(self, value):
        self.value = value
        return value

def make():
    return Widget()
