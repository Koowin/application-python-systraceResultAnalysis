import sys

class SystraceAnalysis:    
    file = None
    process_name = None

    #생성자
    def __init__(self, file_string, process_name_string):
        try:
            self.file = open(file_string)
        except FileNotFoundError:
            print('파일이 없습니다.')
            exit(0)
        self.process_name = process_name_string

    #프로세스 이름으로 find pid and return
    def find_process_id():
        i = 0
        while True:
            line = self.file.readline()
            if not line:
                return -1
            if line == self.process_name:
                return i
            i = i+1

def main():
    temp_class = SystraceAnalysis(sys.argv[1], sys.argv[2])

    pid = temp_class.find_process_id()

    print(pid + "번째 줄에 있습니다.")

if __name__ == "__main__":
    main()