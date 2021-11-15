import sys
import Drawer
import AwsConnector

class HtmlReader:
    #Constructor
    def __init__(self, process_name, file_name):
        try:
            with open("./file/"+file_name, 'r', encoding='utf-8') as file:
                self.lines = file.readlines()
        except:
            print("Error: File open fail.")
        self.process_name = process_name     
        self.file_name = file_name

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

        for i in range(0,3):
            if options[i] in self.lines[-4]:
                string_count = 1
                if options[i] in self.process_name:
                    string_count += self.process_name.count(options[i])
                if options[i] in self.file_name:
                    string_count += self.file_name.count(options[i])
                if string_count > 1:
                    if self.lines[-4].count(options[i]) == string_count:
                        argc += 1
                        self.type = i
                else:
                    argc += 1
                    self.type = i
        if argc != 1:
            self.type = -1

    def start_analyze(self):
        if self.type == -1:
            print("Error: Wrong file. This program can only analyze 'data', 'sched', 'database' types.")
        elif self.type == 0:
            self.__default_setting()
            return self.__disk_analyze()
        elif self.type == 1:
            self.__default_setting()
            return self.__sched_analyze()

        elif self.type == 2:
            self.__default_setting()
            return self.__database_analyze()

    # Find
    #   search start line index
    #   begin time
    #   total systrace running time
    #   process id
    def __default_setting(self):
        self.search_start_line_index = 0

        name_check = False

        for line in self.lines:
            if self.process_name in line:
                self.pid = line[14:19]
                name_check = True
                break
        if not name_check:
            self.type = -1
            print("Error: Your process name not in this file.")
            return

        for line in self.lines:
            if "#              | |        |      |   ||||       |         |" in line:
                self.search_start_line_index += 1
                break
            self.search_start_line_index += 1

        for line in self.lines[self.search_start_line_index:]:
            if (len(line) > 50) and ("trace_event_clock_sync" not in line):
                break
            self.search_start_line_index += 1

        try:
            offset_time_stamp = self.lines[self.search_start_line_index][23:].index(':')
            self.begin_time = int(self.lines[self.search_start_line_index][offset_time_stamp+10:offset_time_stamp+23].replace('.', ''))

            offset_time_stamp = self.lines[-7][23:].index(':')
            end_time = int(self.lines[-7][offset_time_stamp+10:offset_time_stamp+23].replace('.', ''))
            self.total_time = end_time - self.begin_time

        except:
            self.type = -1

    # To do
    def __disk_analyze(self):
        # default_offset_cpu = 32
        # offset_cpu = default_offset_cpu
        # offset_tgid = offset_cpu - 8
        # offset_time_stamp = offset_cpu + 10
        # offset_operation = offset_cpu + 24
        print("Start: Disk I/O operations analyze.")

        disk_begin = []
        disk_file_size = []
        self.disk_time = 0
        
        for line in self.lines[self.search_start_line_index:-6]:
            offset_cpu = line.index('[') + 1
            offset_time_stamp_end = line.index(':')
            if self.pid == line[offset_cpu-8:offset_cpu-3]:
                if "write_begin" in line[offset_time_stamp_end+2:]:
                    time_stamp = int(line[offset_time_stamp_end-13:offset_time_stamp_end].replace('.', ''))
                    disk_begin.append(time_stamp - self.begin_time)

                    file_string = ""
                    offset_size = line.index("len ")
                    
                    if line[offset_size-2] == ',':
                        offset_size += 6
                    else:
                        offset_size += 4

                    for i in line[offset_size:offset_size+4]:
                        if i == ' ' or i == ',':
                            break
                        file_string += i
                    disk_file_size.append(int(file_string))

                elif "write_end" in line[offset_time_stamp_end+2:]:
                    time_stamp = int(line[offset_time_stamp_end-13:offset_time_stamp_end].replace('.', ''))
                    self.disk_time += (time_stamp - disk_begin[-1] - self.begin_time)

        return [disk_begin, disk_file_size]


    def __sched_analyze(self):
        cpu_begin = []
        cpu_end = []
        for i in range(0,10):
            cpu_begin.append(list())
            cpu_end.append(list())
        
        for line in self.lines[self.search_start_line_index:-6]:
            self.pid = self.pid.replace(' ','')
            offset_cpu = line[31:].index('[')+32
            cpu_num = int(line[offset_cpu:offset_cpu+3])
            if "sched_switch" in line[offset_cpu+24:]:
                if "prev_pid="+self.pid in line[offset_cpu+38:]:
                    offset_time_stamp = line[offset_cpu:].index(':') + offset_cpu
                    time_stamp = int(line[offset_time_stamp-13:offset_time_stamp].replace('.', ''))
                    cpu_end[cpu_num].append(time_stamp - self.begin_time)
                elif "next_pid="+self.pid in line[offset_cpu+38:]:
                    offset_time_stamp = line[offset_cpu:].index(':') + offset_cpu
                    time_stamp = int(line[offset_time_stamp-13:offset_time_stamp].replace('.', ''))
                    cpu_begin[cpu_num].append(time_stamp - self.begin_time)

        for i in range(0,10):
            if cpu_begin[-1] == list():
                cpu_begin.pop()
                cpu_end.pop()
            else:
                break
        
        # Calculate cpu using time
        self.cpu_time = 0

        for i in range(0, len(cpu_begin)):
            if len(cpu_begin[i]) < len(cpu_end[i]):
                del cpu_end[i][0]
            elif len(cpu_begin[i]) > len(cpu_end[i]):
                del cpu_begin[i][-1]
            for begin, end in zip(cpu_begin[i], cpu_end[i]):
                self.cpu_time += end - begin
        
        return [cpu_begin, cpu_end]

        
    # To do
    def __database_analyze(self):
        print("Start: Database operation analyze.")
        database_begin = []
        self.database_time = 0
        for line in self.lines[self.search_start_line_index:-6]:
            # Find offset
            offset_cpu = line.index('[')
            if self.pid == line[offset_cpu-7:offset_cpu-2]:
                # Check is excute
                if "execute" in line[offset_cpu+54:offset_cpu+61]:
                    if "S" == line[offset_cpu+46:offset_cpu+47]:
                        time_stamp = int(line[offset_cpu+11:offset_cpu+24].replace('.', '').replace(':', ''))
                        database_begin.append(time_stamp - self.begin_time)
                    elif "F" == line[offset_cpu+46:offset_cpu+47]:
                        time_stamp = int(line[offset_cpu+11:offset_cpu+24].replace('.', '').replace(':', ''))
                        self.database_time += (time_stamp - self.begin_time - database_begin[-1])
        
        return database_begin



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
            # Upload to AWS
            value = html_reader.disk_time / html_reader.total_time
            AwsConnector.upload_value(0, sys.argv[1], html_reader.begin_time, value)
            Drawer.disk_graph(result)
            
        elif html_reader.type == 1:
            # Upload to AWS
            value = html_reader.cpu_time / html_reader.total_time
            AwsConnector.upload_value(1, sys.argv[1], html_reader.begin_time, value)
            Drawer.cpu_graph(result)

        elif html_reader.type == 2:
            # Upload to AWS
            value = html_reader.database_time / html_reader.total_time
            AwsConnector.upload_value(2, sys.argv[1], html_reader.begin_time, value)
            Drawer.database_graph(result)

    # Get average data and show
    else:
        result = AwsConnector.download_all(sys.argv[1])
        Drawer.average_graph(result)