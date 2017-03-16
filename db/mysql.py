
import MySQLdb
import warnings


def connect_to_db(host, user, passwd, db):
    try:
        db = MySQLdb.connect(host=host,
                             user=user,
                             passwd=passwd,
                             db=db)
        return db
    except Exception as e:
        print(str(e))
        raise


def update_db(db, query):
    try:
        cur = db.cursor()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            cur.execute(query)
        db.commit()
    except MySQLdb.Error as e:
        db.rollback()
        print("MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
        raise

    db.close()


def query_db(db, query):
    try:
        cur = db.cursor()
        cur.execute(query)
        results = cur.fetchall()

        db.close()

        return results
    except MySQLdb.Error as e:
        try:
            print("MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
            db.close()
            return
        except IndexError:
            print("MySQL Error: %s" % str(e))
            db.close()
            raise
