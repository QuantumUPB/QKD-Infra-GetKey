import subprocess
import json
import platform

def qkd_get_myself():
    with open('config.json') as f:
        config = json.load(f)
    return config['myname']

def qkd_get_locations():
    with open('config.json') as f:
        config = json.load(f)
    locations = config['locations']
    locations = [location['name'] for location in locations]
    return locations

def qkd_get_destinations():
    with open('config.json') as f:
        config = json.load(f)
    locations = config['locations']
    locations = [location['name'] for location in locations]
    myself = config['myname']
    locations.remove(myself)
    return locations

def qkd_get_key_custom_params(destination, source, cert_path, key_path, cacert_path, pem_password, type, id=""):
    if type == 'Request':    
        script_path = './qkd_get_raw.sh'
    elif type == 'Response':
        script_path = './qkd_get_raw_id.sh'
    else:
        return "Invalid type"

    def fix_windows_path(path):
        path = path.replace('\\', '/')
        if len(path) > 1 and path[1] == ':':
            drive_letter = path[0]
            drive_letter_lower = drive_letter.lower()
            path = path.replace(f'{drive_letter}:/', f'/mnt/{drive_letter_lower}/')
        return path
    
    if platform.system() == 'Windows':
        cert_path = fix_windows_path(cert_path)
        key_path = fix_windows_path(key_path)
        cacert_path = fix_windows_path(cacert_path)
        script_path = fix_windows_path(script_path)

        if type == 'Request':
            params = [cert_path, key_path, cacert_path, source, destination, pem_password]
        else:
            params = [cert_path, key_path, cacert_path, source, destination, pem_password, id]

        try:
            process = subprocess.Popen([
                    'wsl', 'bash', script_path, 
                    *params
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                result = stdout.strip() 
            else:
                result = f"Error: {stderr.strip()}" 
        except Exception as e:
            result = f"Exception occurred: {str(e)}"
    else:
        if type == 'Request':
            params = [cert_path, key_path, cacert_path, source, destination, pem_password]
        else:
            params = [cert_path, key_path, cacert_path, source, destination, pem_password, id]

        try:
            process = subprocess.Popen([
                    'bash', 'qkd_get_raw.sh', 
                    *params
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                result = stdout.strip()
            else:
                result = f"Error: {stderr.strip()}"
        except Exception as e:
            result = f"Exception occurred: {str(e)}"
    
    # print(result)
    return result

def qkd_get_key_with_type(destination, type, id=""):
    with open('config.json') as f:
        config = json.load(f)
    
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
