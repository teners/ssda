import tornado.ioloop
import tornado.autoreload
import tornado.web
import redis
import os
import MySQLdb
import time
import unicodedata


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


def kill_me(cursor, connect):
    cursor.close()
    connect.close()


connect, cursor = get_connections()
r = redis.StrictRedis(host="localhost", port=6379)


class MainHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        self.render("index.html")


class UserHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        def get_shard(id):
            cursor[0].execute("select shard from usershard where user=" + str(id))
            shard = cursor[0].fetchone()
            print(shard, id)
            return shard[0]-1

        def get_data(id, shard):
            cursor[shard].execute("select * from users where id=" + str(id))
            data = cursor[shard].fetchone()
            title = unicodedata.normalize("NFKD", data[1] + data[2])
            data = {"title": title,
                    "age": data[3],
                    "city": data[4],
                    "info": data[5]}
            return data

        id = self.get_argument("id")
        query = "user:" + id
        if not r.exists(query):
            shard = get_shard(id)
            data = get_data(id, shard)
            #print(data)
            r.hmset(query, data)
            cursor[shard].execute("select * from friends where userid=" + id)
            friends = cursor[shard].fetchall()
            # print(friends)
            friendlist = {}
            for friend in friends:
                name = get_data(friend[1], get_shard(friend[1]))
                friendlist[friend[1]] = name
            print(friendlist)

        self.render("user.html",
                    title=r.hget(query, "title"),
                    age=r.hget(query, "age"),
                    city=r.hget(query, "city"),
                    info=r.hget(query, "info"))


def make_app():
    return tornado.web.Application([(r"/", MainHandler),
                                    (r"/user", UserHandler)],
                                   static_path=os.path.join(os.path.dirname(__file__), "static"),
                                   template_path=os.path.join(os.path.dirname(__file__), "templates"))


def main():
    app = make_app()
    app.listen(8888)
    tornado.autoreload.start()
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
