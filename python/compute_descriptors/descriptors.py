'''
Documentation, License etc.

@package compute_descriptors
'''

class Descriptor:
    def __init__(self, mse, frequencyError):
        self.mse = mse
        self.frequencyError = frequencyError

def comp_partial_descriptor(meanImage, filePath):
    pass