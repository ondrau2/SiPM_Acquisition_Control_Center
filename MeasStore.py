import datetime

class MeasStore:
    def __init__(self, path) -> None:
        self.ct = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.FilePath = path #+ '\\' + str(self.ct) + '.txt'


    def SaveBuffer(self, buff, channel):
        with open(self.FilePath + channel,'a', newline='\n') as file:
            file.write(','.join(str(i) for i in buff))

    def ChangeTargetAddress(self, newFilePath):
        self.ct = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.FilePath = newFilePath # + '\\' + str(self.ct) + '.txt'

DataSave = MeasStore(r'C:\Users\ondra\Documents\Projekty\INNMEDSCAN\Technical\data')