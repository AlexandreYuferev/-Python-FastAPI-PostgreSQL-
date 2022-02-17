
import os
import json
import uuid
import base64
import uvicorn
import psycopg2
from typing import List
from psycopg2 import Error
from datetime import datetime
from fastapi import (
    FastAPI,
    File,
    UploadFile)
from fastapi.testclient import TestClient

app = FastAPI()

host = '127.0.0.1'
user = 'postgres'
password = 'Q8i@kqUni6@Vlo1w'
db_name = 'database'

workspace = 'C:\\Users\\Yuferev Alexander\\Desktop\\'


@app.put("/frame/{request_code}")
async def upload_files(request_code: str,
                       files: List[UploadFile] = File(...)):
    if len(files) <= 15:
        # Сохранение файлов на диск
        for item in files:
            contents = await item.read()
            file_name = str(uuid.uuid4()) + '.jpg'
            folder = str(datetime.now().date()).replace('-', '')
            path = os.path.join(workspace, 'data\\', folder)
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
            with open(path + '\\' + file_name, 'wb') as file:
                file.write(contents)
            saved_file_name = 'data\\{0}\\{1}'.format(folder, file_name)
            # Регистрация файлов в БД
            global connection
            try:
                connection = psycopg2.connect(
                    host=host,
                    user=user,
                    password=password,
                    database=db_name)
                connection.autocommit = True
                with connection.cursor() as cursor:
                    cursor.execute("""
                            CREATE TABLE IF NOT EXISTS inbox (
                                id serial PRIMARY KEY,
                                request_code VARCHAR,
                                saved_file_name VARCHAR,
                                datetime_of_registration TIMESTAMP
                            )""")
                    cursor.execute("\
                            INSERT INTO inbox (request_code, saved_file_name, datetime_of_registration) \
                            VALUES(%s, %s, CURRENT_TIMESTAMP(0))", (request_code, saved_file_name))
                    connection.commit()
            except (Exception, Error) as error:
                print('[INFO] Error while working PostgreSQL: ', error)
            finally:
                if connection:
                    connection.close()
                    print('[INFO] PostgreSQL connection closed')
        response = {"Uploaded Filenames": [file.filename for file in files]}
    else:
        response = "[ERROR] The number of transferred files is more than 15"
    return response


@app.get("/frame/{request_code}")
def get_files(request_code: str):
    data = {}
    global connection
    try:
        connection = psycopg2.connect(host=host, user=user, password=password, database=db_name)
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM inbox WHERE request_code=%s;", (request_code,))
            records = cursor.fetchall()
            count = 1
            for row in records:
                obj = {}
                with open(workspace + row[2], mode='rb') as binary_file:
                    binary_file_data = binary_file.read()
                    base64_encoded_data = base64.b64encode(binary_file_data)
                    base64_message = base64_encoded_data.decode('utf-8')
                    obj['file'] = base64_message
                    obj['name'] = str(row[2])
                    obj['time'] = str(row[3])
                data['file_{0}'.format(count)] = obj
                count += 1
    except (Exception, Error) as error:
        print('[INFO] Error while working PostgreSQL: ', error)
    finally:
        if connection:
            connection.close()
            print('[INFO] PostgreSQL connection closed')
    print(len(data))
    return {json.dumps(data)}


@app.delete("/frame/{request_code}")
def delete_files(request_code: str):
    file_names = []
    global connection
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name)
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM inbox WHERE request_code=%s;", (request_code,))
            records = cursor.fetchall()
            for row in records:
                file_names.append(str(row[2]))
            cursor.execute("DELETE FROM inbox WHERE request_code=%s;", (request_code,))
            directory_list = set()
            for file_name in file_names:
                path = os.path.join(workspace, file_name)
                os.remove(path)
                directory_list.add(os.path.dirname(path))
            for directory in directory_list:
                os.rmdir(directory)
    except (Exception, Error) as error:
        print('[INFO] Error while working PostgreSQL: ', error)
    finally:
        if connection:
            connection.close()
            print('[INFO] PostgreSQL connection closed')
    return {"Deleted Filenames": file_names[:]}


client = TestClient(app)


def test_1():
    response = client.put("/frame/{request_code}")
    assert response.status_code == 200


def test_2():
    response = client.get("/frame/{request_code}")
    assert response.status_code == 200


def test_3():
    response = client.delete("/frame/{request_code}")
    assert response.status_code == 200


if __name__ == '__main__':

    # uvicorn main:app --reload
    uvicorn.run(
        app,
        host='127.0.0.1',
        port=8000,
        debug=True)

