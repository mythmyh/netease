import sqlite3
conn = sqlite3.connect('url.db')


def insert(values, table='inspect'):
    cursor = conn.cursor()
    sql = "insert into {} (url) values('{}')".format(table, values)
    cursor.execute(sql)
    conn.commit()


def inspect(url, table='inspect'):
    cursor = conn.cursor()
    sql = "select * from {} where url='{}'".format(table, url)
    rs = cursor.execute(sql).fetchone()
    if rs:
        return True
    else:
        return False


d = {'a': 1, 'b': 2, 'c': 3}
t = d.keys()
for x in range(3):
    d['c'] = 4
print(d)
