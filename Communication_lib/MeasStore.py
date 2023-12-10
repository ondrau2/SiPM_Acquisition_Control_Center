import datetime

##Basic file write functions
class MeasStore:
    def __init__(self, path) -> None:
        self.ct = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.FilePath = path #+ '\\' + str(self.ct) + '.txt'

    #Save data to file
    def SaveBuffer(self, buff, channel):
        with open(self.FilePath + channel,'a', newline='\n') as file:
            file.write('\n'.join(str(i) for i in buff))
            file.write('\n')

    #Change destination file path
    def ChangeTargetAddress(self, newFilePath):
        self.ct = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.FilePath = newFilePath # + '\\' + str(self.ct) + '.txt'

