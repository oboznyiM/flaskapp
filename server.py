import os
from flask import Flask
from database import db, User
from auth import authorize_user
from routes import health, get_favourite_coffee, get_coffee_leaderboard, set_favourite_coffee

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{os.getenv("MYSQL_USERNAME")}:{os.getenv("MYSQL_PASSWORD")}@{os.getenv("MYSQL_HOST")}:{os.getenv("MYSQL_PORT")}/coffeeshop'
db.init_app(app)

app.add_url_rule('/health', view_func=health, methods=['GET'])
app.add_url_rule('/v1/coffee/favourite', view_func=get_favourite_coffee, methods=['GET'])
app.add_url_rule('/v1/admin/coffee/favourite/leaderboard', view_func=get_coffee_leaderboard, methods=['GET'])
app.add_url_rule('/v1/coffee/favourite', view_func=set_favourite_coffee, methods=['POST'])

if __name__ == '__main__':
    app.run(host='localhost', port=8080)
