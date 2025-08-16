import os

import psycopg2


def get_connection():
    #     conn = psycopg2.connect(dbname="fifa_tournament", user="nitin", password="temp", host="localhost")
    return psycopg2.connect(
        dbname=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        host=os.environ.get("POSTGRES_HOST"),
        port=os.environ.get("POSTGRES_PORT", "5432"),
    )
