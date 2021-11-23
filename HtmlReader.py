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

        # Find pid with process_name
        for i in range(len(self.lines)):
            if "<!-- BEGIN TRACE -->" in self.lines[i]:
                offset_process_dump = i+4
        for line in self.lines[offset_process_dump:]:
            process_info = line.split()
            try:
                if process_info[8] == self.process_name:
                    # Find pid
                    self.pid = process_info[1]
                    break
            except:
                print("Error: Can't find process name")
                exit()

        # Find trace data line index 
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
            try:
                offset_cpu = line[13:].index('[') + 14
            except:
                continue
            
            offset_time_stamp_end = line[offset_cpu:].index(':') + offset_cpu
            if self.pid == line[offset_cpu-8:offset_cpu-3].replace(' ', ''):
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
        print("Start: Disk I/O operations analyze.")
        cpu_begin = []
        cpu_end = []
        for i in range(0,10):
            cpu_begin.append(list())
            cpu_end.append(list())

        # pid_list = []
        # # Append group pid
        # for i in range(len(self.lines)):
        #     if "USER            PID   TID CMD" in self.lines[i]:
        #         offset_process_list = i+1
        # for i in range(offset_process_list, len(self.lines)):
        #     process_info = self.lines[i].split()
        #     if process_info[1] == self.pid:
        #         offset_process_list = i
        #         break
        # for line in self.lines[offset_process_list:]:
        #     process_info = line.split()
        #     if process_info[1] == self.pid:
        #         pid_list.append(process_info[2])
        #     else:
        #         break
        
        for i in range(self.search_start_line_index, len(self.lines)-7):
            try:
                offset_cpu = self.lines[i][13:].index('[')+14
            except:
                continue
            try:
                cpu_num_i = int(self.lines[i][offset_cpu:offset_cpu+3])
            except:
                offset_cpu = self.lines[i][offset_cpu+1:].index('[') + offset_cpu + 2
                cpu_num_i = int(self.lines[i][offset_cpu:offset_cpu+3])

            if (self.pid in self.lines[i][offset_cpu-8:offset_cpu-3]) and ("sched_switch" in self.lines[i][offset_cpu+24:]):
                offset_time_stamp = self.lines[i][offset_cpu:].index(':') + offset_cpu
                time_stamp = int(self.lines[i][offset_time_stamp-13:offset_time_stamp].replace('.', ''))
                cpu_end[cpu_num_i].append(time_stamp - self.begin_time)
                
                for j in range(i-1, self.search_start_line_index, -1):
                    try:
                        offset_cpu = self.lines[j][13:].index('[')+14
                    except:
                        continue
                    try:
                        cpu_num_j = int(self.lines[j][offset_cpu:offset_cpu+3])
                    except:
                        offset_cpu = self.lines[j][offset_cpu+1:].index('[') + offset_cpu + 2
                        cpu_num_j = int(self.lines[j][offset_cpu:offset_cpu+3])

                    if cpu_num_i == cpu_num_j and "sched_switch" in self.lines[j][offset_cpu+24:]:
                        offset_time_stamp = self.lines[j][offset_cpu:].index(':') + offset_cpu
                        time_stamp = int(self.lines[j][offset_time_stamp-13:offset_time_stamp].replace('.', ''))
                        cpu_begin[cpu_num_j].append(time_stamp - self.begin_time)
                        break
                            

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

    
    def __database_analyze(self):
        print("Start: Database operation analyze.")
        database_begin = []
        self.database_time = 0
        for line in self.lines[self.search_start_line_index:-6]:
            # Find offset
            try:
                offset_cpu = line[13:].index('[') + 14
            except:
                continue
            #print(line[offset_cpu-8:offset_cpu-3])
            if self.pid == line[offset_cpu-8:offset_cpu-3].replace(' ', ''):
                # Check is excute
                if "execute" in line[offset_cpu+49:]:
                    if "S" == line[offset_cpu+45:offset_cpu+46]:
                        offset_time_stamp = line[offset_cpu:].index(':') + offset_cpu
                        time_stamp = int(line[offset_time_stamp-13:offset_time_stamp].replace('.', ''))
                        database_begin.append(time_stamp - self.begin_time)
                    elif "F" == line[offset_cpu+45:offset_cpu+46]:
                        offset_time_stamp = line[offset_cpu:].index(':') + offset_cpu
                        time_stamp = int(line[offset_time_stamp-13:offset_time_stamp].replace('.', ''))
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
            Drawer.cpu_graph(result, html_reader.cpu_time, html_reader.total_time)

        elif html_reader.type == 2:
            # Upload to AWS
            value = html_reader.database_time / html_reader.total_time
            AwsConnector.upload_value(2, sys.argv[1], html_reader.begin_time, value)
            Drawer.database_graph(result)

    # Get average data and show
    else:
        result = AwsConnector.download_all(sys.argv[1])
        Drawer.average_graph(result)