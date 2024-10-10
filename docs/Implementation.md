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
SOCKET_PATH = "unix:/var/run/edgedevice/edgeapiagent.sock"
SPIFFE_ID = os.environ.get("EDGE_SPIFFE_ID", "spiffe://iert.siemens.com/edge-service")

x509_source = spiffe.X509Source(socket_path=SOCKET_PATH)

# get x509 certificate and JSON Web Token for Secure Storage API
with spiffe.WorkloadApiClient(socket_path=SOCKET_PATH) as client:
    try:
        x509_svid = client.fetch_x509_svid()
        jwt_svid = client.fetch_jwt_svid(audience=[SPIFFE_ID])
    except spiffe.exceptions.WorkloadApiError as e:
        print(f"SPIFFE Workload API Error: {e}")

```

A particularity when using the Python "requests" module is that the certificate has to be read from a file, so the file is first saved within the container to be then read later

```python
# certificate and key have to be saved to file as Python requests module doesn't accept raw input
with open("tmp/cert.pem", "wb") as f:
    f.write(
        x509_svid.cert_chain[0].public_bytes(
            encoding=cryptography.hazmat.primitives.serialization.Encoding.PEM
        )
    )

with open("tmp/key.key", "wb") as f:
    f.write(
        x509_svid.private_key.private_bytes(
            encoding=cryptography.hazmat.primitives.serialization.Encoding.PEM,
            format=cryptography.hazmat.primitives.serialization.PrivateFormat.PKCS8,
            encryption_algorithm=cryptography.hazmat.primitives.serialization.NoEncryption(),
        )
    )
```

### Using the Secure Storage API

Using the Secure Storage mechanism then amounts to calling the Secure Storage API (as documented in the [IED Secure Storage API Documentation](https://docs.eu1.edge.siemens.cloud/apis_and_references/apis/ied/secure-storage-api-2.0.0.html)) using the provided client certificate and using the JWT in the API call header.

```python
HEADERS = {
    "accept": "*/*",
    "Content-Type": "application/json",
    "Authorization": f"JWT {jwt_svid.token}",
}
```

Obtaining existing key-value pairs from Secure Storage happens through a GET request:

```python
if request.method == "GET":
        response = requests.request(
            "GET",
            (BASE_URL + "/keys"),
            headers=HEADERS,
            cert=("tmp/cert.pem", "tmp/key.key"),
            verify=False,
        ).json()

        if not response["securestoragekeys"]:
            return Response({})
        for element in response["securestoragekeys"]:
            response_call = requests.request(
                "GET",
                (BASE_URL + "/keys/" + element),
                headers=HEADERS,
                cert=("tmp/cert.pem", "tmp/key.key"),
                verify=False,
            ).json()
            key_value_pairs.append(response_call)
        return Response(json.dumps(key_value_pairs))
```

And submitting a new key-value pair is done through a POST request:

```python
if request.method == "POST":
        data = json.loads(request.data)
        body = json.dumps(data)
        if (
            not "key" in data
            or not "value" in data
            or data["key"] == ""
            or data["value"] == ""
        ):
            return Response(
                json.dumps({"errors": [{"message": "You must specify key and value"}]}),
                status=400,
            )

        response_post = requests.request(
            "POST",
            (BASE_URL + "/keys"),
            data=body,
            headers=HEADERS,
            cert=("tmp/cert.pem", "tmp/key.key"),
            verify=False,
        )
        if response_post.status_code == 201:
            return Response("Successfully added a member", status=201)
        else:
            return Response(
                json.dumps(response_post.json()), status=response_post.status_code
            )
```