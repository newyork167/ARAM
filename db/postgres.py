
import psycopg2.extras


class PGdb:
    host = ''
    user = ''
    password = ''
    database = ''
    con = None

    def __init__(self, database, host, user, password):
      self.host = host
      self.database = database
      self.user = user
      self.password = password
      self.__connect_to_db()

    def __connect_to_db(self):
        try:
            self.con = psycopg2.connect(database=self.database,
                                   host=self.host,
                                   user=self.user,
                                   password=self.password)

        except psycopg2.DatabaseError as e:
            print('Error %s' % e)
            return False

        return self.con

    def close_db(self):
         if not self.con.closed:
            self.con.close()

    # Executes query
    # :param query:
    # :return: list of query results
    def query_db(self, query):
        try:
            self.__connect_to_db()
            cur = self.con.cursor()
            cur.execute(query)
            results = cur.fetchall()

        except psycopg2.DatabaseError as e:
            print('Error %s' % e)
            return False
        finally:
            self.close_db()
        return results

    # Updates database
    # :param con:
    # :param query:
    # :return: Boolean with success
    def update_db(self, query):
        try:
            self.__connect_to_db()
            cur = self.con.cursor()
            cur.execute(query)
            self.con.commit()
        except psycopg2.DatabaseError as e:
            print('Error %s' % e)
            return False
        finally:
            self.close_db()
        return True
