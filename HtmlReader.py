import sys
import os

class HtmlReader:
    #Constructor
    def __init__(self, process_name, file_name):
        try:
            with open("./file/"+file_name, 'r', encoding='utf-8') as file:
                self.lines = file.readlines()
        except:
            print("Error: File open fail.")
        self.process_name = process_name     
        self.begin_time = 0
        self.total_time = 0

    # Type check
    # Type value - description table
    # | value | description |
    # ----------------------|
    # |   -1  | error type  |
    # |   0   | disk        |
    # |   1   | sched       |
    # |   2   | database    |
    def type_checker(self):
        argc = 0
        options = ("disk", "sched", "database")

        # To do: if optionsp[n] in __proceess_name
        for i in range(0,3):
            if options[i] in self.lines[-4]:
                argc += 1
                self.type = i
        if argc != 1:
            self.type = -1

    def start_analyze(self):
        if self.type == -1:
            print("Error: Wrong file. This program can only analyze 'data', 'sched', 'database' types.")
        elif self.type == 0:
            self.__disk_analyze()
        elif self.type == 1:
            self.__sched_analyze()
        elif self.type == 2:
            self.__database_analyze()

    # To do
    def __disk_analyze(self):
        print("disk")
    
    # To do
    def __sched_analyze(self):
        print("sched")
    
    # To do
    def __database_analyze(self):
        print("database")
    



if __name__=="__main__":
    if len(sys.argv) > 3:
        print("Error: Too many arguments.")
        exit()
    
    # HTML read
    if len(sys.argv) == 3:
        html_reader = HtmlReader(sys.argv[1], sys.argv[2])
        html_reader.type_checker()
        html_reader.start_analyze()

    # Get average data and show