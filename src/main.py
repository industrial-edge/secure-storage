import flask
import json
import os
import sys
import requests
import spiffe
import cryptography
import logging

requests.packages.urllib3.disable_warnings()  # ignore insecure connection warnings

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

app = flask.Flask(__name__)
app._static_folder = os.path.abspath("templates/static/")

BASE_URL = "https://edge-iot-core.proxy-redirect:8443/b.service/api/v2/secure-storage"
SOCKET_PATH = "unix:///var/run/edgedevice/edgeapiagent.sock"
SPIFFE_ID = os.environ.get("EDGE_SPIFFE_ID", "spiffe://iert.siemens.com/edge-service")

CERTS_PATH = "/tmp/spiffe.pem"
KEY_PATH = "/tmp/spiffe.key"

def get_ss() -> tuple[dict, int]:
    """Get x509 cert and jwt for Secure Storage."""

    with spiffe.WorkloadApiClient(socket_path=SOCKET_PATH) as client:
        try:
            x509_svid = client.fetch_x509_svid()
            jwt_svid = client.fetch_jwt_svid(audience=[SPIFFE_ID])
        except spiffe.exceptions.WorkloadApiError as e:
            logger.error("SPIFFE Workload API Error: %s", e)
            return {
                "errors": [
                    {
                        "message": f"SPIFFE Workload API Error: {e}",
                        "logref": "",  # cSpell:disable-line
                        "code": "edge.spiffeWorkloadApiError",
                    }
                ]
            }

    x509_svid.save(CERTS_PATH, KEY_PATH, encoding=cryptography.hazmat.primitives.serialization.Encoding.PEM)

    return {"jwt": f"JWT {jwt_svid.token}", "spiffe_id": str(jwt_svid.spiffe_id)}

@app.route("/")
def home():
    return flask.render_template("index.html")


@app.route("/members", methods=["GET", "POST"])
def members():
    key_value_pairs = []
    ss_obj = get_ss()

    if "errors" in ss_obj:
        return ss_obj, 400

    auth_token = ss_obj["jwt"]
    
    if flask.request.method == "GET":

        response = requests.request(
            "GET",
            (BASE_URL + "/keys"),
            headers={
                "accept": "*/*",
                "Content-Type": "application/json",
                "Authorization": auth_token,
            },
            cert=(CERTS_PATH, KEY_PATH),
            verify=False,
        ).json()

        if not response["securestoragekeys"]:
            return flask.Response({})
        for element in response["securestoragekeys"]:
            response_call = requests.request(
                "GET",
                (BASE_URL + "/keys/" + element),
                headers={
                    "accept": "*/*",
                    "Content-Type": "application/json",
                    "Authorization": auth_token,
                },
                cert=(CERTS_PATH, KEY_PATH),
                verify=False,
            ).json()
            key_value_pairs.append(response_call)
        return flask.Response(json.dumps(key_value_pairs))

    if flask.request.method == "POST":
        data = json.loads(flask.request.data)
        body = json.dumps(data)
        if (
            not "key" in data
            or not "value" in data
            or data["key"] == ""
            or data["value"] == ""
        ):
            return flask.Response(
                json.dumps({"errors": [{"message": "You must specify key and value"}]}),
                status=400,
            )

        response_post = requests.request(
            "POST",
            (BASE_URL + "/keys"),
            data=body,
            headers={
                "accept": "*/*",
                "Content-Type": "application/json",
                "Authorization": auth_token,
            },
            cert=(CERTS_PATH, KEY_PATH),
            verify=False,
        )
        if response_post.status_code == 201:
            return flask.Response("Successfully added a member", status=201)
        else:
            return flask.Response(
                json.dumps(response_post.json()), status=response_post.status_code
            )

if __name__ == '__main__':  
   app.run(host="0.0.0.0")