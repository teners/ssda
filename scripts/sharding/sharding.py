import MySQLdb
import time
import random
from multiprocessing import Process, current_process


# connect to databases and get their cursors
def get_connections(shards=5):
    connect = []
    cursor = []
    for i in range(shards):
        socket = '/run/mysqld/mysqld' + str(i + 1) + '.sock'
        connect.append(MySQLdb.connect(host='localhost',
                                       user='root',
                                       passwd='',
                                       db='vk',
                                       port=3306 + i + 1,
                                       unix_socket=socket,
                                       charset='utf8'))
        cursor.append(connect[i].cursor())
    return connect, cursor


# get 100k values from db connected with cursor
def get_values(cursor):
    for i in range(4):
        # rows boundaries
        low = str(100000 * (i + 1))
        high = str(int(low) + 100000)

        # sql select routine
        cursor.execute("select * from users where id >= %s and id < %s", (low, high,))
        values = []
        value = cursor.fetchall()
        values.append(list(value))
    return values


def kill_me(cursor, connect):
    cursor.close()
    connect.close()


# insert tuple of values in db connected with cursor
def insert(cursorid, values, connectid):
    # get unique id and current time
    id = current_process().name
    start = time.time()
    startl = time.localtime()
    print("{0} started at {1}:{2}:{3}".format(id, startl[3], startl[4], startl[5]))

    # insert routine
    cursorid.execute("BEGIN;")
    for value in values:
        cursorid.execute("INSERT INTO users (id, firstname, lastname, age, city, info) VALUES (%s, %s, %s, %s, %s, %s)",
                         value)
    cursorid.execute("commit;")

    # get current time
    end = time.time()
    endl = time.localtime()
    print("{0} ended at {1}:{2}:{3} ({4} seconds)".format(id, endl[3], endl[4], endl[5], end - start))

    # close connections
    kill_me(cursorid, connectid)


# delete last 400k entries in first db
def delete_first(cursor):
    cursor[0].execute("BEGIN;")
    cursor[0].execute("DELETE FROM users WHERE id > %s", (100000,))
    cursor[0].execute("commit;")


connect, cursor = get_connections()
values = get_values(cursor[0])

for i in range(1, 5):
    Process(target=insert, args=(cursor[i], values[i - 1], connect[i]), name="shard" + str(i)).start()

delete_first(cursor[0])
kill_me(cursor[0], connect[0])
