import psycopg2


def get_connection():
    conn = psycopg2.connect(dbname="fifa_tournament", user="nitin", password="temp", host="localhost")
    return conn
