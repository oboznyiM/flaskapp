from flask import request, jsonify
from database import db, User
from auth import authorize_user
from email_service import send_email

def health():
    return jsonify({"message": "hello!"}), 200

def get_favourite_coffee():
    username = authorize_user()
    if username is None:
        return jsonify({"error": "unauthorized"}), 401
    user = User.query.filter_by(username=username).first()
    return jsonify({"favourite_coffee": user.favourite_coffee}), 200

def get_coffee_leaderboard():
    leaderboard = db.session.query(User.favourite_coffee, db.func.count(User.favourite_coffee)) \
                                .group_by(User.favourite_coffee)                                \
                                .order_by(db.func.count(User.favourite_coffee).desc())          \
                                .limit(3)                                                       \
                                .all()
    leaderboard = [{"coffee": coffee, "count": count} for coffee, count in leaderboard]
    return jsonify({"leaderboard": leaderboard}), 200

def set_favourite_coffee():
    username = authorize_user()
    if username is None:
        return jsonify({"error": "unauthorized"}), 401
    coffee = request.json.get('coffee')
    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User(username=username, favourite_coffee=coffee)
        db.session.add(user)
    else:
        user.favourite_coffee = coffee
    send_email("kek", "lol", "top")
    db.session.commit()

    return jsonify({"message": "Favourite coffee set successfully"}), 200
