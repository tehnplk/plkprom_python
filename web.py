from flask import Flask, jsonify, json, render_template
import requests
import json
import os

token_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'token.txt')

app = Flask(__name__)


def read_token():
    with open(token_file, "r") as f:
        token = f.read()
        return token.strip()


def check(cid):
    endpoint = f"https://cvp1.moph.go.th/api/ImmunizationTarget?cid={cid}"
    r = requests.get(endpoint, headers=headers, verify=False)
    return r.json()


@app.route("/view/<cid>")
def index(cid):
    data = check(cid)
    return render_template("index.html", result=data)


@app.route("/api/<cid>")
def api(cid):
    data = check(cid)
    return data


if __name__ == '__main__':
    requests.urllib3.disable_warnings()
    token = read_token()
    headers = {"Authorization": f"Bearer {token}"}

    app.run(debug=True, port=5000)
