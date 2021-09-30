from flask import Flask, request, jsonify

app = Flask(__name__)


def itemgetter(*names):
    return lambda mapping: tuple(
        -mapping[name[1:]] if name.startswith("-") else mapping[name] for name in names
    )


def cost(fuels, t):
    if t == "gasfired":
        p = fuels.get("gas(euro/MWh)")
    elif t == "turbojet":
        p = fuels.get("kerosine(euro/MWh)")
    else:
        p = 0
    return p


@app.route("/productionplan", methods=["POST"])
def foo():
    if request.is_json:
        data = request.json
        data_r = []
        fuels = data.get("fuels")
        load = data.get("load")
        powerplants = []
        for pp in data.get("powerplants"):
            pp["cost"] = cost(fuels, pp.get("type"))
            powerplants.append(pp)
        powerplants = sorted(
            data.get("powerplants"),
            key=itemgetter("efficiency", "cost"),
            reverse=True,
        )
        for d in powerplants:
            if d.get("pmax") <= load:
                if d.get("type") == "windturbine":
                    e = d.get("pmax") * fuels.get("wind(%)") / 100
                elif d.get("type") == "gasfired":
                    e = d.get("pmax") - d.get("pmin")
                else:
                    e = d.get("pmax")
                p = int(e)
                load -= int(e)
            else:
                p = load
                load = 0
            data_r.append(
                {
                    "name": d.get("name"),
                    "p": p,
                }
            )
    else:
        data_r = {"error": "Wrong json data format"}
    return jsonify(data_r)


if __name__ == "__main__":
    app.run(debug=False, port=8888)
