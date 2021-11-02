import Drawer
import AwsConnector as aws
import sys

class HtmlReader:

    def __init__(self, option, file_name, process_name):
        self.option = option
        self.file_name = file_name
        self.process_name = process_name
        self.total_time = 0
        self.wrong_option_flag = False
        self.begin_time = 0

        # f2fs_write operation
        if(option == 'w'):
            self.begin_list = list()
            self.write_size = list()
            self.operating_time = 0
            self.sum_of_size = 0
            self.avg_size = 0
        else:
            self.wrong_option_flag = True
            return
    
    def readFile(self):
        if(self.option == 'w'):
            
            try:
                file = open(self.file_name, 'r', encoding='utf-8')
        
                # find PID
                line = None
                while line != '':
                    line = file.readline()
                    if self.process_name in line:
                        break
                pid = line.split()[1]
                
                # fill begin_list and write_size
                # calculate operating_time
                while line != '':
                    line = file.readline()
                    if '#              | |        |      |   ||||       |         |' in line:
                        break
                line = file.readline()
                self.begin_time = int(line[42:56].replace('.', ''))
                
                while line != '  </script>\n':
                    # pid와 같다면
                    if line[24:29] == pid:
                        if 'f2fs_write_begin' in line:
                            len_index = line.rfind('len = ')
                            self.write_size.append(int(line[len_index+6:len_index+10].split()[0].replace(',', '')))
                            new_time = int(line[42:56].replace('.', ''))
                            self.begin_list.append(new_time - self.begin_time)
                        elif 'f2fs_write_end' in line:
                            new_end_time = int(line[42:56].replace('.', ''))
                            self.operating_time += (new_end_time - new_time)
                    line = file.readline()
                
                #find end_time
                
                file.seek(file.tell()-300)
                line = file.readline()
                line = file.readline()
                while line != '  </script>\n':
                    end_time = int(line[42:56].replace('.', ''))
                    line = file.readline()
                self.total_time = end_time - self.begin_time
            except:
                print("파일 읽기 실패")
            return True
        else:
            return False


if __name__=="__main__":
    if len(sys.argv) < 4:
        print("매개변수 개수가 부족합니다.")
    else:
        html_reader = HtmlReader(sys.argv[1], sys.argv[2], sys.argv[3])
        if html_reader.wrong_option_flag:
            print("올바른 옵션이 아닙니다.")
            exit()
        html_reader.readFile()

        operating_ratio = html_reader.operating_time / html_reader.total_time

        aws_connector = aws.AwsConnector(sys.argv[1], sys.argv[3], html_reader.begin_time)
        aws_connector.insert_data(operating_ratio)

        items = aws_connector.get_all_item()
        Drawer.draw_graph(html_reader.begin_list, html_reader.write_size, items, operating_ratio)