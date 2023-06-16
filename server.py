import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

print(os.getenv("MYSQL_PASSWORD"))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{os.getenv("MYSQL_USERNAME")}:{os.getenv("MYSQL_PASSWORD")}@{os.getenv("MYSQL_HOST")}:{os.getenv("MYSQL_PORT")}/coffeeshop'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    favourite_coffee = db.Column(db.String(120))


def authorize_user(request):
    return request.headers.get('Authorization')
    
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"message": "hello!"}), 200

@app.route('/v1/coffee/favourite', methods=['GET'])
def get_favourite_coffee():
    username = authorize_user(request)
    if username is None:
        return jsonify({"error": "unauthorized"}), 401
    user = User.query.filter_by(username=username).first()
    return jsonify({"favourite_coffee": user.favourite_coffee}), 200

@app.route('/v1/admin/coffee/favourite/leaderboard', methods=['GET'])
def get_coffee_leaderboard():
    leaderboard = db.session.query(User.favourite_coffee, db.func.count(User.favourite_coffee)) \
                                .group_by(User.favourite_coffee)                                \
                                .order_by(db.func.count(User.favourite_coffee).desc())          \
                                .limit(3)                                                       \
                                .all()
    leaderboard = [{"coffee": coffee, "count": count} for coffee, count in leaderboard]
    return jsonify({"leaderboard": leaderboard}), 200

@app.route('/v1/coffee/favourite', methods=['POST'])
def set_favourite_coffee():
    username = authorize_user(request)
    if username is None:
        return jsonify({"error": "unauthorized"}), 401
    coffee = request.json.get('coffee')
    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User(username=username, favourite_coffee=coffee)
        db.session.add(user)
    else:
        user.favourite_coffee = coffee
    db.session.commit()

    return jsonify({"message": "Favourite coffee set successfully"}), 200

if __name__ == '__main__':
    app.run(host='localhost', port=8080)
