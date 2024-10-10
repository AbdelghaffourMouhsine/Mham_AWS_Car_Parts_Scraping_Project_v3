import csv
import threading

class DataWithException:
    def __init__(self, file_path="results/key_words_exceptions", value=None):
        self.file_path = f"{file_path}.csv"
        self.fieldnames = ['key_words']
        self.lock = threading.Lock()
        
        self.file = open(self.file_path, 'a', newline='', encoding='utf-8-sig')
        self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames)
        
        # Check if the file is empty, then write the header
        if self.file.tell() == 0:
            self.writer.writeheader()

        if value:
            if type(value) == list :
                self.insert_exceptions(value)
            else:
                self.insert_exception(value)
            self.close_file()
            
    def insert_exception(self, exception_value):
        data = {
            'key_words' : exception_value
        }
        self.writer.writerow(data)
        
    def insert_exceptions(self, exceptions):
        for exception in exceptions:
            self.insert_exception(exception)
            
    def close_file(self):
        self.file.close()