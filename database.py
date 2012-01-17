from pg8000 import DBAPI
import urlparse, os

if __name__ == "__main__":
    url = urlparse.urlparse(os.environ['DATABASE_URL'])
    config = {
        'NAME':     url.path[1:],
        'USER':     url.username,
        'PASSWORD': url.password,
        'HOST':     url.hostname,
        'PORT':     url.port
    }

    conn = DBAPI.connect(host=config['HOST'], user=config['USER'], password=config['PASSWORD'], database=config["NAME"])
    cur = conn.cursor()

    for query in file('db.sql').read().split(';'):
      cur.execute(query + ";")

    conn.commit()
    conn.close()
