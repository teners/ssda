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
    cursor  = []
    for i in range(shards):
        socket = "/run/mysqld/mysqld" + str(i + 1) + ".sock"
        connect.append(MySQLdb.connect(host="localhost",
                                       user="root",
                                       passwd="",
                                       db="vk",
                                       port=3306 + i + 1,
                                       unix_socket=socket,
                                       charset="utf8"))
        cursor.append(connect[i].cursor())
    return connect, cursor


def kill_me(cursor, connect):
    cursor.close()
    connect.close()


connect, cursor  = get_connections()
redis_connection = redis.StrictRedis(host="localhost",
                                     port=6379)


class Friend:
    def __init__(self, id, name):
        self.id   = id
        self.name = name


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
            return shard[0] - 1

        def get_data(id, shard):
            cursor[shard].execute("select * from users where id=" + str(id))
            data  = cursor[shard].fetchone()
            title = unicodedata.normalize("NFKD", data[1] + data[2])
            data = {"title": title,
                    "age":   data[3],
                    "city":  data[4],
                    "info":  data[5]}
            return data

        def cache_friends(id, shard):
            query = "user:" + id + ":friends"
            cursor[shard].execute("select * from friends where userid=" + id)
            friendlist = {}
            for friend in cursor[shard].fetchall():
                name = get_data(friend[1], get_shard(friend[1]))
                friendlist[friend[1]] = name
            friends_dict = {}
            for id, data in friendlist.items():
                friends_dict[id] = data['title']
            redis_connection.hmset(query, friends_dict)

        start = time.time()
        id    = self.get_argument("id")
        query = "user:" + id
        if not redis_connection.exists(query):
            shard = get_shard(id)
            data  = get_data(id, shard)
            redis_connection.hmset(query, data)
            cache_friends(id, shard)
        friends = []
        for k, v in redis_connection.hgetall(query + ":friends").items():
            friends.append(Friend(k, v))

        self.render("user.html",
                    title=redis_connection.hget(query, "title"),
                    age=redis_connection.hget(query, "age"),
                    city=redis_connection.hget(query, "city"),
                    info=redis_connection.hget(query, "info"),
                    friends=friends,
                    time=round(time.time() - start, 3))

class SearchHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        self.render("search.html")


class ResultHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        def get_results(cursor, table, fn, ln, c, f, t):
            query = "select * from users" + \
                    str(table) + \
                    " where match('" + \
                    fn +\
                    ln +\
                    c + "') "
            if f != "":
                query += " and age >=" + f + " "
            if t != "":
                query += " and age <=" + t + " "
            query += "order by firstname asc;"
            if cursor.execute(query) == 0:
                return []
            result = []
            results = cursor.fetchall()
            for r in results:
                result.append(Friend(r[0], unicodedata.normalize("NFKD", r[1] + r[2])))
            return result

        start = time.time()
        firstname = self.get_argument("firstname")
        lastname  = self.get_argument("lastname")
        city      = self.get_argument("city")
        agefrom   = self.get_argument("agefrom")
        ageto     =  self.get_argument("ageto")
        sphinx_connection = MySQLdb.connect(host="localhost",
                                            port=9306,
                                            db="vk",
                                            unix_socket="/tmp/sphinx.sock")
        sphinx_cursor = sphinx_connection.cursor()
        if firstname != "":
            firstname = "@firstname *" + firstname + "*"
        if lastname != "" :
            lastname = " @lastname " + lastname + "*"
        if city != "":
            city = " @city " + city + "*"
        result = []
        for i in range(1, 6):
            result += get_results(sphinx_cursor, i, firstname, lastname, city, agefrom, ageto)
        results = False
        if len(result) > 0:
            results = True

        self.render("results.html",
                    results=results,
                    result = result,
                    time=round(time.time() - start, 3))


def make_app():
    return tornado.web.Application([(r"/", MainHandler),
                                    (r"/user", UserHandler),
                                    (r"/search", SearchHandler),
                                    (r"/results", ResultHandler)],
                                   static_path=os.path.join(os.path.dirname(__file__), "static"),
                                   template_path=os.path.join(os.path.dirname(__file__), "templates"))


def main():
    app = make_app()
    app.listen(8888)
    tornado.autoreload.start()
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
