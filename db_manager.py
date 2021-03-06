#fetches data from database, feed_db() is writing to database
import psycopg2
import crawler
import analyzer
import time
import msgpack
import schedule


def connect():
    connection= psycopg2.connect(
        user= 'jojo',
        password= 'postgresql4evver', #mega password
        host= 'localhost',
        port= '5432',
        database= 'technicus'
    )
    return connection


def get_earthquakes(min_mag):
    conn= connect()
    cursor= conn.cursor()
    cursor.execute(f"SELECT longitude, latitude, mag,breakLength, tsunami FROM earthquakes WHERE mag >= {min_mag} AND type='earthquake';")
    data= cursor.fetchall()
    cursor.close()
    conn.close()
    values= []
    for element in data:
        lst_element= list(element)
        lst_element[4]= 0 if lst_element[4] == 'false' else 1
        values.append(lst_element)
    return values


def get_wildfires(min_confidence= 90):
    conn= connect()
    cursor= conn.cursor()
    cursor.execute(f"""SELECT latitude, longitude, confidence FROM wildfires WHERE confidence>{min_confidence}""")
    data= cursor.fetchall()
    cursor.close()
    conn.close()
    values= []
    for element in data:
        values.append(list(element))
    return values


def read_file(name):
    if name == 'eq':
        with open('earthquake_data.msgpack', 'rb') as file:
            data= msgpack.unpackb(file.read())
            return data

    elif name == 'wildfires':
        with open('wildfire_data.msgpack', 'rb') as file:
            data= msgpack.unpackb(file.read())
            return data


def feed_db():
    analyzer.process_earthquakes(read_file('eq'))
    analyzer.process_wildfires(read_file('wildfires'))
    print('done')


if __name__ == '__main__':
    schedule.every(800).seconds.do(feed_db)
    while True:
        schedule.run_pending()
