import markovify
import random
import multiprocessing

first_names = [line.rstrip('\n') for line in open('first')]
last_names = [line.rstrip('\n') for line in open('last')]
cities = [line.rstrip('\n') for line in open('city')]
with open('startrek') as f:
    text = f.read()
text_model = markovify.Text(text)

class Generate(multiprocessing.Process):
    def __init__(self, num):
        multiprocessing.Process.__init__(self)
        self.num = num
    def run(self):
        f = open('users'+str(self.num), 'w')
        fn = len(first_names) - 1
        ln = len(last_names) - 1
        cl = len(cities) - 1
        for id in range(125000 * self.num + 1, 125000 * (self.num + 1)):
            line = 'insert into users (id,firstname,lastname,age,city,info) values (' + \
                   str(id) + ',\"' + \
                   first_names[random.randint(0, fn)] + '\",\"' + \
                   last_names[random.randint(0, ln)] + '\",' + \
                   str(random.randint(15, 45)) + ',\"' + cities[random.randint(0, cl)] + '\",\"' + text_model.make_short_sentence(50) + '\");\n'
            f.write(line)
        f.close()
        return

if __name__ == '__main__':
    p0 = Generate(0)
    p0.start()

    p1 = Generate(1)
    p1.start()

    p2 = Generate(2)
    p2.start()

    p3 = Generate(3)
    p3.start()
