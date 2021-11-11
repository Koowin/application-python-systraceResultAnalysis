import sys
import os
import Drawer

class HtmlReader:
    #Constructor
    def __init__(self, process_name, file_name):
        try:
            with open("./file/"+file_name, 'r', encoding='utf-8') as file:
                self.lines = file.readlines()
        except:
            print("Error: File open fail.")
        self.process_name = process_name     

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
            self.__default_setting()
            self.__disk_analyze()
        elif self.type == 1:
            self.__default_setting()
            return self.__sched_analyze()
        elif self.type == 2:
            self.__default_setting()
            self.__database_analyze()

    # Find
    #   search start line index
    #   begin time
    #   total systrace running time
    #   process id
    def __default_setting(self):
        offset_time_stamp = 42
        self.search_start_line_index = 0
        
        for line in self.lines:
            if self.process_name in line:
                self.pid = line[14:19]
                break
        for line in self.lines:
            if "#              | |        |      |   ||||       |         |" in line:
                self.search_start_line_index += 3
                break
            self.search_start_line_index += 1
        
        self.begin_time = int(self.lines[self.search_start_line_index][offset_time_stamp:offset_time_stamp+12].replace('.', ''))
        end_time = int(self.lines[-7][offset_time_stamp:offset_time_stamp+12].replace('.', ''))
        self.total_time = end_time - self.begin_time
        # print(self.pid)
        # print(self.begin_time)
        # print(self.total_time)


    # To do
    def __disk_analyze(self):
        print("disk")
    
    # To do
    def __sched_analyze(self):
        default_offset_cpu = 32
        offset_cpu = default_offset_cpu
        offset_time_stamp = offset_cpu + 10
        offset_operation = offset_cpu + 24
        offset_arg = offset_cpu + 38
        # print("sched")
        # print(self.lines[self.search_start_line_index+2][offset_cpu:offset_cpu+3])
        # print(self.lines[self.search_start_line_index+2][offset_time_stamp:offset_time_stamp+12])
        # print(self.lines[self.search_start_line_index+2][offset_operation:offset_operation+12])
        # print(self.lines[self.search_start_line_index+2][offset_arg:])

        cpu_begin = []
        cpu_end = []
        for i in range(0,10):
            cpu_begin.append(list())
            cpu_end.append(list())
        

        for line in self.lines[self.search_start_line_index:-6]:
            try:
                cpu_num = int(line[offset_cpu:offset_cpu+3])
                if "sched_switch" in line[offset_operation:offset_operation+12]:
                    if "prev_pid="+self.pid in line[offset_arg:]:
                        time_stamp = int(line[offset_time_stamp:offset_time_stamp+12].replace('.', ''))
                        cpu_end[cpu_num].append(time_stamp - self.begin_time)
                    elif "next_pid="+self.pid in line[offset_arg:]:
                        time_stamp = int(line[offset_time_stamp:offset_time_stamp+12].replace('.', ''))
                        cpu_begin[cpu_num].append(time_stamp - self.begin_time)
                
            except:
                # No default string location.
                offset_cpu = line.index('[') + 1
                offset_time_stamp = offset_cpu + 10
                offset_operation = offset_cpu + 24
                offset_arg = offset_cpu + 38

                # Do job
                cpu_num = int(line[offset_cpu:offset_cpu+3])
                if "sched_switch" in line[offset_operation:offset_operation+12]:
                    if "prev_pid="+self.pid in line[offset_arg:]:
                        time_stamp = int(line[offset_time_stamp:offset_time_stamp+12].replace('.', ''))
                        cpu_end[cpu_num].append(time_stamp - self.begin_time)
                    elif "next_pid="+self.pid in line[offset_arg:]:
                        time_stamp = int(line[offset_time_stamp:offset_time_stamp+12].replace('.', ''))
                        cpu_begin[cpu_num].append(time_stamp - self.begin_time)

                # Re arange offset
                offset_cpu = default_offset_cpu
                offset_time_stamp = offset_cpu + 10
                offset_operation = offset_cpu + 24
                offset_arg = offset_cpu + 38
        
        for i in range(0,10):
            if cpu_begin[-1] == list():
                cpu_begin.pop()
                cpu_end.pop()
            else:
                break

        return [cpu_begin, cpu_end]

        
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
        result = html_reader.start_analyze()

        if html_reader.type == 0:
            print()
            # To do : Draw Graph
            # To do : Upload to AWS
        elif html_reader.type == 1:
            Drawer.cpu_graph(result)
            # To do : Upload to AWS
        elif html_reader.type == 2:
            print()
            # To do : Draw Graph
            # To do : Upload to AWS

    # Get average data and show
    else:
        print()