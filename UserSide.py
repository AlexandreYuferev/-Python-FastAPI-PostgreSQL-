
import json
import base64
import requests
from typing import List

url = 'http://127.0.0.1:8000/frame/'
path = 'C:\\Users\\Yuferev Alexander\\Desktop\\'


def put_request(request_code):
    files = [
        ('files', open(path + 'New folder (3)\\' + '01.jpg', 'rb')),
        ('files', open(path + 'New folder (3)\\' + '02.jpg', 'rb')),
        ('files', open(path + 'New folder (3)\\' + '03.jpg', 'rb')),
        ('files', open(path + 'New folder (3)\\' + '04.jpg', 'rb')),
        ('files', open(path + 'New folder (3)\\' + '05.jpg', 'rb')),
        ('files', open(path + 'New folder (3)\\' + '06.jpg', 'rb')),
        ('files', open(path + 'New folder (3)\\' + '07.jpg', 'rb')),
        ('files', open(path + 'New folder (3)\\' + '08.jpg', 'rb')),
        ('files', open(path + 'New folder (3)\\' + '09.jpg', 'rb')),
        ('files', open(path + 'New folder (3)\\' + '10.jpg', 'rb'))
    ]
    response = requests.put(url="{0}{1}".format(url, request_code), files=files)
    print(response.json())


def get_request(request_code):
    response = requests.get(url="{0}{1}".format(url, request_code))
    list: List = response.json()
    obj = json.loads(list[0])
    for index in range(1, len(obj) + 1):
        print('\n')
        print(obj['file_{0}'.format(index)]['name'])
        print(obj['file_{0}'.format(index)]['time'])
        file_name = obj['file_{0}'.format(index)]['name']
        datetime_of_registration = obj['file_{0}'.format(index)]['time']
        base64_img_bytes = obj['file_{0}'.format(index)]['file'].encode('utf-8')
        with open(path + 'New folder (7)\\' + file_name[file_name.rfind('\\'):], 'wb') as file_to_save:
            decoded_image_data = base64.decodebytes(base64_img_bytes)
            file_to_save.write(decoded_image_data)


def del_request(request_code):
    response = requests.delete(url="{0}{1}".format(url, request_code))
    print(response.json())


if __name__ == '__main__':
    #put_request('request_code')
    #get_request('request_code')
    #del_request('request_code')
    pass
