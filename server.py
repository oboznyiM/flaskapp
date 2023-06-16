from flask import Flask, request, jsonify

app = Flask(__name__)

users = {
    "user": {
        "favourite_coffee": None
    }
}
AUTH_HEADER = "Basic dXNlcjplYTY1NDU0MS00MjZhLTQwOWMtYTFiMy00NTk3YTBlY2JmZWU="

coffee_leaderboard = {}


def is_authorized(request):
    return True
#    print(request.headers.get('Authorization'))
#    return request.headers.get('Authorization') == AUTH_HEADER

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"message": "hello!"}), 200
   
@app.route('/v1/coffee/favourite', methods=['GET'])
def get_favourite_coffee():
    if not is_authorized(request):
        return jsonify({"message": "Unauthorized"}), 401

    return jsonify({"favourite_coffee": users["user"]['favourite_coffee']}), 200


@app.route('/v1/admin/coffee/favourite/leaderboard', methods=['GET'])
def get_coffee_leaderboard():
    if not is_authorized(request):
        return jsonify({"message": "Unauthorized"}), 401

    leaderboard = sorted(coffee_leaderboard.items(), key=lambda x: x[1], reverse=True)
    return jsonify({"leaderboard": leaderboard}), 200


@app.route('/v1/coffee/favourite', methods=['POST'])
def set_favourite_coffee():
    if not is_authorized(request):
        return jsonify({"message": "Unauthorized"}), 401

    coffee = request.json.get('coffee')

    users["user"]['favourite_coffee'] = coffee

    if coffee not in coffee_leaderboard:
        coffee_leaderboard[coffee] = 0
    coffee_leaderboard[coffee] += 1

    return jsonify({"message": "Favourite coffee set successfully"}), 200

if __name__ == '__main__':
    app.run(host='localhost', port=8080)
