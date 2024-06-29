import json
import os
import sys
import requests

if not hasattr(sys, '_MEIPASS'):
    qkdgtk_module_dir = os.path.dirname(__file__)
else:
    qkdgtk_module_dir = os.path.dirname(sys.executable)

def get_full_path(relative_path):
    # if not inside pyinstaller bundle
    return os.path.join(qkdgtk_module_dir, relative_path)

def qkd_get_config():
    with open(get_full_path('config.json')) as f:
        config = json.load(f)
    return config

def qkd_get_myself():
    return qkd_get_config()['myname']

def qkd_get_locations():
    return qkd_get_config()['locations']

def qkd_get_location_names():
    locations = [location['name'] for location in qkd_get_locations()]
    return locations

def qkd_get_destinations():
    config = qkd_get_config()
    locations = config['locations']
    locations = [location['name'] for location in locations]
    myself = config['myname']
    locations.remove(myself)
    return locations

def qkd_get_key_custom_params(destination, source, cert_path, key_path, cacert_path, pem_password, type, id=""):    
    if not os.path.isabs(cert_path):
        cert_path = get_full_path(cert_path)
    if not os.path.isabs(key_path):
        key_path = get_full_path(key_path)
    if not os.path.isabs(cacert_path):
        cacert_path = get_full_path(cacert_path)

    if type == 'Request':
        url = f"https://{source}/api/v1/keys/{destination}/enc_keys"

        response = requests.get(
            url,
            cert=(cert_path, key_path),
            verify=False,
            headers={
                'Content-Type': 'application/json'
            },
            data=data_json if type == 'Response' else None
        )
    else:
        url = f"https://{source}/api/v1/keys/{destination}/dec_keys"
        data_payload = {
            "key_IDs": [
                {
                    "key_ID": id
                }
            ]
        }
        data_json = json.dumps(data_payload)
    
        response = requests.post(
            url,
            cert=(cert_path, key_path),
            verify=False,
            headers={
                'Content-Type': 'application/json'
            },
            data=data_json
        )

    # Check the response
    if response.status_code == 200:
        result = response.text
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

    # print(result)
    return result

def qkd_get_key_with_type(destination, type, id=""):
    config = qkd_get_config()
    
    myself = config['myname']
    locations = config['locations']
    assert myself in [location['name'] for location in locations], "Local name not found in locations"
    assert destination in [location['name'] for location in locations], "Destination name not found in locations"

    source = [location['ipport'] for location in locations if location['name'] == myself][0]
    destination = [location['endpoint'] for location in locations if location['name'] == destination][0]

    cert_path = config['cert']
    key_path = config['key']
    cacert_path = config['cacert']
    pem_password = config['pempassword']

    return qkd_get_key_custom_params(destination, source, cert_path, key_path, cacert_path, pem_password, type, id)

def qkd_get_key(destination):
    return qkd_get_key_with_type(destination, 'Request')

def qkd_get_key_resp(destination, id):
    return qkd_get_key_with_type(destination, 'Response', id)
