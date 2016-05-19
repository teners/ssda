import MySQLdb
import random
import threading
import time


def get_connections(shards=5):
    print("Establishing connection...")
    connect = []
    cursor = []
    try:
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
            print("mysqld{0} connected.".format(i))
    except:
        print("Exception was raised! Shutting down.")
        for c in cursor:
            c.close()
        for c in connect:
            c.close()
        exit()
    print("Connection established.")
    return connect, cursor


def generate_friends():
    # time() returns seconds since January 1, 1970
    # localtime() returns array of human-readable time data like hours, minutes and seconds
    start = time.time()
    start_l = time.localtime()
    print("\"Friends\" generation started at {0}:{1}:{2}".format(start_l[3],
                                                                 start_l[4],
                                                                 start_l[5]))
    friend = {}
    for i in range(0, 500000):
        upper = random.randint(3, 7)
        friend[i] = set([random.randint(0, 499999) for _ in range(upper)])
    # we need a dict where we have keys and values of "friend" dict swapped
    # (values become keys and vice versa
    reverse_friend = {}
    for key, values in friend.items():
        for value in list(values):
            if value not in reverse_friend:
                reverse_friend[value] = set()
            reverse_friend[value].add(key)

    end = time.time()
    end_l = time.localtime()
    print("\"Friends\" generation ended at {0}:{1}:{2} ({3} seconds)".format(end_l[3],
                                                                             end_l[4],
                                                                             end_l[5],
                                                                             int(end - start)))
    # some python magic that merges two dictionaries
    return {**friend, **reverse_friend}


def close_connection(cursor, connect):
    cursor.close()
    connect.close()


def insert(connect, cursor, friends, shard):
    try:
        thread_name = threading.currentThread().getName()
        # time() returns seconds since January 1, 1970
        # localtime() returns array of human-readable time data like hours, minutes and seconds
        start = time.time()
        start_l = time.localtime()
        print("{0} started at {1}:{2}:{3}.".format(thread_name,
                                                   start_l[3],
                                                   start_l[4],
                                                   start_l[5]))
        cursor.execute('begin;')
        for user in range(shard * 100000,
                          shard * 100000 + 100000):
            if user in friends:
                for friend in friends[user]:
                    cursor.execute('insert into friends (userid, friendid) values (%s, %s)', (user, friend))
        cursor.execute('commit;')
        end = time.time()
        end_l = time.localtime()
        print("{0} ended at {1}:{2}:{3} ({4} seconds).".format(thread_name,
                                                               end_l[3],
                                                               end_l[4],
                                                               end_l[5],
                                                               int(end - start)))
    except:
        print("Something went wrong while inserting, you should check databases and try again (maybe?)")
        cursor.execute('rollback;')
        close_connection(cursor, connect)


def main():
    random.seed()
    connect, cursor = get_connections()

    # check if databases are empty with simple SQL query
    cursor[0].execute("select count(userid) from friends;")
    if cursor[0].fetchone()[0] > 0:
        print("Databases aren't empty, execute cleaning procedure.")
        for c in cursor:
            c.execute('begin; delete from friends where userid >= 0; commit;')
        print("Done cleaning.")

    friends = generate_friends()
    threads = []
    for shard in range(5):
        threads.append(threading.Thread(target=insert,
                                        args=(cursor[shard],
                                              friends,
                                              shard),
                                        name="Shard #" + str(shard + 1)))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    for server in range(5):
        close_connection(cursor[server], connect[server])

if __name__ == '__main__':
    main()