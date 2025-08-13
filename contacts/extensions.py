import os
from abc import ABC, abstractmethod
import pandas as pd
class FileFormat(ABC):
    def __init__(self):

        self.upload_dir = 'files'
    def upload(self,file):
        file_path = os.path.join(self.upload_dir, file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return file_path
    @abstractmethod
    def read(self,file):
        pass
    @abstractmethod
    def write(self,data):
        pass
class FileCSV(FileFormat):
    def read(self,file):
        reader = pd.read_csv(self.upload(file),encoding='windows-1251',sep=';')

        return reader

    def write(self,data):
        df = pd.DataFrame(data)
        df.to_csv(f'{self.upload_dir}/export.csv',index=False,sep=';',encoding='windows-1251')

class FileXLSX(FileFormat):
    def read(self,file):
        reader = pd.read_excel(self.upload(file)).to_dict()
        return reader
    def write(self,data):
        df = pd.DataFrame(data)
        df.to_excel('export.xlsx',sheet_name='Contacts',index=False)

file_handler_dict = {
    'xlsx':FileXLSX,
    'csv':FileCSV
}

def get_file_handler(file):
    extension = file.name.split('.')[-1]
    handler_class = file_handler_dict.get(extension)
    return handler_class()
