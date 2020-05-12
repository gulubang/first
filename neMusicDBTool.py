import sqlite3

conn=sqlite3.connect('neMusic.db')
cur=conn.cursor()

def createTable():
    try:
        cur.execute(('''CREATE TABLE IF NOT EXISTS nemusic
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userid VARCHAR(10) NOT NULL,
            nickname VARCHAR(30) NOT NULL,
            viptype TINYINT NOT NULL,
            likedcount VARCHAR(17) NOT NULL,
            content VARCHAR(280) NOT NULL
        );
        '''))
    except:
        print('表出问题了')
        raise SystemExit

    try:
        cur.execute('''
            DELETE FROM nemusic;
        ''')
        cur.execute('''
            DELETE FROM sqlite_sequence;
        ''')
    except:
        print('表或自增列未清空，但仍在运行')
    conn.commit()
    print('删除',conn.total_changes,'条')
    return conn.total_changes

def insertTable(comment,counter):
    for i in comment:
        try:
            cur.execute('''
            INSERT INTO nemusic(userid,nickname,viptype,likedcount,content) VALUES(?,?,?,?,?)
            ''',(i[1],i[2],i[3],i[4],i[5]))
        except:
            print('插入%d失败'%int(i[0])+1)
    conn.commit()
    print(conn.total_changes-counter,'新插入')


def queryTable():
    return cur.execute('''
        SELECT userid,nickname,viptype,likedcount,content FROM nemusic;
    ''')

def closeDB():
    conn.close()