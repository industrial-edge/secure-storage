# Implementation

- [Implementation](#implementation)
  - [Overview](#overview)
  - [Example Python implementation](#example-python-implementation)
    - [Retrieving the certificate and token](#retrieving-the-certificate-and-token)
    - [Using the Secure Storage API](#using-the-secure-storage-api)

## Overview

The process of using Secure Storage is described in the [Secure Storage documentation](https://docs.eu1.edge.siemens.cloud/apis_and_references/apis/api-how-tos/secure-storage.html). The implementation will depend on your choice of programming language and the availability and feature set of the necessary libraries or modules.

## Example Python implementation

### Retrieving the certificate and token

In order to call the Secure Storage API, the x509 certificate and JWT have to be retrieved from the pre-defined location on the Edge Device.

```python
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
```

A particularity when using the Python "requests" module is that the certificate has to be read from a file.

### Using the Secure Storage API

Using the Secure Storage mechanism then amounts to calling the Secure Storage API (as documented in the [IED Secure Storage API Documentation](https://docs.eu1.edge.siemens.cloud/apis_and_references/apis/ied/secure-storage-api-2.0.0.html)) using the provided client certificate and using the JWT in the API call header. Obtaining existing key-value pairs from Secure Storage happens through a GET request:

```python
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
```

And submitting a new key-value pair is done through a POST request:

```python
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
```