# This work has been implemented by Alin-Bogdan Popa and Bogdan-Calin Ciobanu,
# under the supervision of prof. Pantelimon George Popescu, within the Quantum
# Team in the Computer Science and Engineering department,Faculty of Automatic
# Control and Computers, National University of Science and Technology
# POLITEHNICA Bucharest (C) 2024. In any type of usage of this code or released
# software, this notice shall be preserved without any changes.


import json
import os
import sys
import requests

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib

if not hasattr(sys, '_MEIPASS'):
    qkdgtk_module_dir = os.path.dirname(__file__)
else:
    qkdgtk_module_dir = os.path.dirname(sys.executable)

def get_full_path(relative_path):
    # if not inside pyinstaller bundle
    return os.path.join(qkdgtk_module_dir, relative_path)

_CONFIG = None


def qkd_get_config():
    global _CONFIG
    if _CONFIG is None:
        with open(get_full_path('config.toml'), 'rb') as f:
            _CONFIG = tomllib.load(f)
    return _CONFIG

def qkd_get_myself():
    """Return the consumer name defined in the configuration if present."""
    return qkd_get_config().get('consumer')

def qkd_get_locations():
    return qkd_get_config()['locations']

def qkd_get_location_names():
    locations = [location['name'] for location in qkd_get_locations()]
    return locations

def qkd_get_destinations():
    config = qkd_get_config()
    locations = [location['name'] for location in config['locations']]
    myself = config.get("location")
    if myself in locations:
        locations.remove(myself)
    return locations

def qkd_get_endpoint(destination):
    """Return the SAE endpoint for a destination name.

    Falls back to the destination name if no endpoint is defined.
    """
    for location in qkd_get_locations():
        if location.get('name') == destination:
            return location.get('endpoint', destination)
    return destination

def _self_report(node_id: str, name: str, number_of_keys: int, key_size: int = 256) -> None:
    """Report key retrieval details if self-reporting is enabled."""
    cfg = qkd_get_config()
    if not cfg.get("self_reporting", False):
        return

    endpoint = cfg.get("report_endpoint")
    if not endpoint:
        return

    payload = {
        "nodeId": node_id,
        "name": name,
        "numberOfKeys": number_of_keys,
        "keySize": key_size,
    }

    token = cfg.get("report_token")

    try:
        verify_tls = True
        if cfg.get("report_trust_self_signed", False):
            verify_tls = False

        headers = {"Content-Type": "application/json"}
        if token:
            headers["X-Auth-Token"] = f"Bearer {token}"

        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            verify=verify_tls,
        )
        if response.status_code >= 400:
            print(f"Reporting failed: {response.status_code} {response.text}")
    except Exception as exc:
        print(f"Reporting error: {exc}")

def qkd_get_key_custom_params(destination, kme, cert_path, key_path, cacert_path=None, pem_password="", type="Request", id=""):
    """Retrieve an encryption or decryption key from the specified KME.

    If ``cacert_path`` is not provided, the request is made without setting a
    custom CA certificate and TLS verification is disabled.
    """

    proto = "https"
    no_cert = False
    if cert_path == "":
        proto = "http"
        no_cert = True
        print("Warning: using an unsafe connection to the QKD, which might not work")

    if not os.path.isabs(cert_path):
        cert_path = get_full_path(cert_path)
    if not os.path.isabs(key_path):
        key_path = get_full_path(key_path)
    if cacert_path and not os.path.isabs(cacert_path):
        cacert_path = get_full_path(cacert_path)

    consumer = qkd_get_myself()

    request_kme = kme

    sae = qkd_get_endpoint(destination)

    if type == 'Request':
        if consumer:
            url = f"{proto}://{request_kme}/{consumer}/api/v1/keys/{sae}/enc_keys"
        else:
            url = f"{proto}://{request_kme}/api/v1/keys/{sae}/enc_keys"

        curl_parts = ["curl", "-Ss"]
        if not no_cert:
            cert_arg = f"{cert_path}:{pem_password}" if pem_password else cert_path
            curl_parts.extend(["--cert", cert_arg, "--key", key_path])
            if cacert_path:
                curl_parts.extend(["--cacert", cacert_path])
            else:
                curl_parts.append("-k")
        else:
            curl_parts.append("-k")
        curl_parts.append(url)
        print(" ".join(curl_parts))

        response = requests.get(
            url,
            cert=None if no_cert else (cert_path, key_path),
            verify=None if no_cert else (cacert_path or False),
            headers={
                'Content-Type': 'application/json'
            },
        )
    else:
        if consumer:
            url = f"{proto}://{request_kme}/{consumer}/api/v1/keys/{sae}/dec_keys"
        else:
            url = f"{proto}://{request_kme}/api/v1/keys/{sae}/dec_keys"
        data_payload = {
            "key_IDs": [
                {
                    "key_ID": id
                }
            ]
        }
        data_json = json.dumps(data_payload)

        curl_parts = ["curl", "-Ss"]
        if not no_cert:
            cert_arg = f"{cert_path}:{pem_password}" if pem_password else cert_path
            curl_parts.extend(["--cert", cert_arg, "--key", key_path])
            if cacert_path:
                curl_parts.extend(["--cacert", cacert_path])
            else:
                curl_parts.append("-k")
        else:
            curl_parts.append("-k")
        curl_parts.extend(["-X", "POST", "-H", "Content-Type:application/json", "-d", data_json, url])
        print(" ".join(curl_parts))

        response = requests.post(
            url,
            cert= None if no_cert else (cert_path, key_path),
            verify=None if no_cert else (cacert_path or False),
            headers={
                'Content-Type': 'application/json'
            },
            data=data_json
        )

    # Check the response
    if response.status_code == 200:
        result = response.text

        number_of_keys = 0
        key_size = 0
        try:
            parsed = json.loads(result)
            if isinstance(parsed, dict):
                number_of_keys = parsed.get("numberOfKeys") or len(parsed.get("keys", []))
                key_size = parsed.get("keySize") or 0
                if not key_size and parsed.get("keys"):
                    first_key = parsed.get("keys")[0]
                    if isinstance(first_key, str):
                        key_size = len(first_key)
            elif isinstance(parsed, list):
                number_of_keys = len(parsed)
        except Exception:
            pass

        cfg = qkd_get_config()
        _self_report(
            cfg.get("location", qkd_get_myself()),
            cfg.get("reporting_name", "infra-getkey"),
            int(number_of_keys) if number_of_keys else 0,
            int(key_size) if key_size else 0,
        )
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return "error: " + response.text

    # print(result)
    return result

def qkd_get_key_with_type(destination, type, id=""):
    config = qkd_get_config()

    locations = config['locations']

    kme_name = qkd_get_config().get("location")
    assert kme_name in [location['name'] for location in locations], "Local KME not found in locations"
    assert destination in [location['name'] for location in locations], "Destination name not found in locations"

    kme_ipport = [location['ipport'] for location in locations if location['name'] == kme_name][0]

    cert_path = config['cert']
    key_path = config['key']
    cacert_path = config.get('cacert')
    pem_password = config['pempassword']

    request_kme = kme_ipport

    return qkd_get_key_custom_params(destination, request_kme, cert_path, key_path, cacert_path, pem_password, type, id)

def qkd_get_key(destination):
    return qkd_get_key_with_type(destination, 'Request')

def qkd_get_key_resp(destination, id):
    return qkd_get_key_with_type(destination, 'Response', id)
