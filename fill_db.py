import os
import pymysql

host = os.getenv('MYSQL_HOST')
port = int(os.getenv('MYSQL_PORT'))
username = os.getenv('MYSQL_USERNAME')
password = os.getenv('MYSQL_PASSWORD')

connection = pymysql.connect(
    host=host,
    port=port,
    user=username,
    password=password
)

try:
    with connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS coffeeshop;")
        cursor.execute("USE coffeeshop;")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(255) UNIQUE NOT NULL,
                favourite_coffee VARCHAR(255)
            );
        """)
        cursor.execute("""
            INSERT INTO user (username, favourite_coffee)
            VALUES
                ('user', 'Latte'),
                ('user1', 'Espresso'),
                ('user2', 'Cappuccino'),
                ('user3', 'Latte');
        """)

    connection.commit()

finally:
    connection.close()
