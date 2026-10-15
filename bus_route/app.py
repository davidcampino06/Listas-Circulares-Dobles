"""
Flask server that exposes the bus route (circular doubly linked list) to the frontend.
Run:  python app.py   and open  http://127.0.0.1:5000
"""

from flask import Flask, jsonify, render_template, request
from circular_route import create_sample_route

app = Flask(__name__)
route = create_sample_route()


def success():
    return jsonify({"ok": True, "state": route.state()})


def failure(message):
    return jsonify({"ok": False, "error": message, "state": route.state()}), 400


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/state")
def get_state():
    return success()


@app.route("/api/stops", methods=["POST"])
def add_stop():
    data = request.get_json()
    try:
        name = data["name"].strip()
        neighborhood = data["neighborhood"].strip()
        time_to_next = int(data["time_to_next"])
        passengers = int(data.get("passengers", 0))
        if not name or not neighborhood or time_to_next <= 0 or passengers < 0:
            return failure("Invalid data: check name, neighborhood, time (>0) and passengers (>=0)")
        position = data.get("position", "end")
        if position == "beginning":
            route.insert_at_beginning(name, neighborhood, time_to_next, passengers)
        elif position == "after":
            route.insert_after(data["reference"], name, neighborhood, time_to_next, passengers)
        else:
            route.insert_at_end(name, neighborhood, time_to_next, passengers)
        return success()
    except (KeyError, ValueError) as e:
        return failure(str(e))


@app.route("/api/stops/<name>", methods=["DELETE"])
def delete_stop(name):
    try:
        route.delete(name)
        return success()
    except ValueError as e:
        return failure(str(e))


@app.route("/api/bus/move", methods=["POST"])
def move_bus():
    try:
        route.move_bus()
        return success()
    except ValueError as e:
        return failure(str(e))


@app.route("/api/bus/direction", methods=["POST"])
def toggle_direction():
    route.toggle_direction()
    return success()


@app.route("/api/passengers", methods=["POST"])
def generate_passengers():
    route.generate_passengers()
    return success()


@app.route("/api/shortest-route")
def shortest_route():
    try:
        result = route.shortest_route(request.args["origin"], request.args["destination"])
        return jsonify({"ok": True, "result": result})
    except (KeyError, ValueError) as e:
        return failure(str(e))


@app.route("/api/reset", methods=["POST"])
def reset():
    global route
    route = create_sample_route()
    return success()


if __name__ == "__main__":
    app.run(debug=True)
