# Brief: Implement a class for the automatic focusing and astigmatism correction algorithm.
#
# Author: Liuchuyao Xu, 2020

class SemCorrector:
    def __init__(self, sem):
        self.sem = sem
        try:
            version = self.sem.getState("SV_VERSION")
        except:
            raise TypeError("SemCorrector was not initialised with an SEM_API instance.")

    def start(self):
        self.semMagnification = self.sem.getValue("")
        self.semWorkingDistance = self.sem.getValue("")
        self.semFocus = self.sem.getValue("")
        self.semStigmaX = self.sem.getValue("")
        self.semStigmaY = self.sem.getValue("")

    def adjustFocus(self):
        pass
    
    def adjustStigmaX(self):
        pass

    def adjustStigmasY(self):
        pass

if __name__ == "__main__":
    pass
