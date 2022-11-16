from flask import Flask, render_template, request, Response
import json
import os
import requests
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app._static_folder = os.path.abspath("templates/static/")

with open("/var/run/edgedevice/certsips.json", 'r') as certsip:
    data = json.load(certsip)
    DEVICE_IP = data["edge-ips"]
    API_PATH = data["secure-storage-api-path"]


BASE_URL = "https://" + DEVICE_IP + API_PATH
HEADERS = {
    'accept': '*/*',
    'Content-Type': 'application/json'
}


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/members", methods=['GET', 'POST'])
def members():
    key_value_pairs = []
    if request.method == 'GET':
        response = requests.request(
            "GET", (BASE_URL + "/keys"), headers=HEADERS, verify=False).json()
        if not response["securestoragekeys"]:
            return Response({})
        for element in response["securestoragekeys"]:
            response_call = requests.request(
                "GET", (BASE_URL + "/keys/" + element), headers=HEADERS, verify=False).json()
            key_value_pairs.append(response_call)
        return Response(json.dumps(key_value_pairs))

    if request.method == 'POST':
        data = json.loads(request.data)
        body = json.dumps(data)
        if not 'key' in data or not 'value' in data or data['key'] == '' or data['value'] == '':
            return Response(json.dumps({
                "errors": [
                    {
                        "message": "You must specify key and value"
                    }
                ]
            }), status=400)

        response_post = requests.request(
            "POST", (BASE_URL + "/keys"), data=body, headers=HEADERS, verify=False)
        if response_post.status_code == 201:
            return Response('Successfully added a member', status=201)
        else:
            return Response(json.dumps(response_post.json()), status=response_post.status_code)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
