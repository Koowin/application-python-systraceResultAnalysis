import boto3
from boto3.dynamodb.conditions import Key
import sys

if __name__ == "__main__":
    app_names = list()
    runtime = list()
    try:
        with open("./pattern/"+sys.argv[1], 'r', encoding="utf-8") as file:
            while True:
                line = file.readline()
                if not line:
                    break
                splited_line = line.split()
                app_names.append(splited_line[1])
                runtime.append(int(splited_line[3].replace('ms','')))
                
    except:
        print("Error: File open failed")
    
    dynamodb = boto3.resource('dynamodb')
    
    table = dynamodb.Table("disk")
    response = table.scan()
    result = response["Items"]
    
    result_dict = dict()
    temp_name = 'none'
    temp_sum = 0
    temp_count = 1
    for item in result:
        if temp_name != item['app_name']:
            result_dict[temp_name] = temp_sum / temp_count
            temp_name = item['app_name']
            temp_sum = float(item['value'])
            temp_count = 1
        else:
            temp_sum += float(item['value'])
            temp_count += 1
    
    sum_disk_runtime = 0
    sum_total = 0
    
    for i in range(len(app_names)):
        sum_total += runtime[i]
        try:
            sum_disk_runtime += result_dict[app_names[i]] * runtime[i]
        except:
            continue

    print("\n--Result--")
    print("Total runtime: ", sum_total)
    print("Disk runtime: ", sum_disk_runtime)