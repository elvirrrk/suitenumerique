import requests

KEYCLOAK_URL = "http://localhost:8080"
API_URL = "http://localhost:8071/api/v1.0"
ITEMS_URL = f"{API_URL}/items"

LINK_RESTRICTED = "restricted"
LINK_AUTHENTICATED = "authenticated"
LINK_PUBLIC = "public"

ROLE_READER = "reader"
ROLE_EDITOR = "editor"
ROLE_ADMIN = "administrator"
ROLE_OWNER = "owner"

# def get_file_by_name(token, filename):
# def read_file(token, filename):
# def delete_file(token, filename):

def login(username, password):
    url = f"{KEYCLOAK_URL}/realms/drive/protocol/openid-connect/token"

    data = {
        "client_id" : "admin-cli",
        "username": username,
        "password": password,
        "grant_type": "password",
        "scope": "openid" # utilisable par OpenID Connect
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        return response.json()["access_token"] # convertit json en objet python
    
    print(f"Error {response.status_code}: {response.json()["error_description"]}")
    return None

def get_items(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "page": 1,
        "page_size": 100,
        "is_creator_me": "true",
        "ordering": "-type,title"
    }

    response = requests.get(ITEMS_URL, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()["results"]

    print(f"Failed to get items: {response.status_code}")
    return []

def download_file(token, url, filename):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print(f"Download: {filename}")
        # with open(filename, "wb") as f: # binary write mdoe
        #     f.write(response.content)
    else:
        print(f"Failed to download file. Status code: {response.status_code}")
    return response

def open_folder(token, id):   
    url = f"{ITEMS_URL}/{id}/children"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print(f"Open folder: {id}")
        return response.json()["results"]

    print(f"Failed to open folder: {response.status_code}")
    return 

def update_link_configuration(token, id, link_reach, link_role):  
    url = f"{ITEMS_URL}/{id}/link-configuration/"

    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    data = {
        "link_reach": link_reach,
        "link_role": link_role
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code == 200:
        print(f"Link configuration updated: {link_reach}")
    else:
        print(f"Failed to update link configuration: {response.status_code}")
    return response

def find_user(token, email):
    url = f"{API_URL}/users/"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "q": email
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()

    print(f"Failed to find user: {response.status_code}")
    return None

def add_access(token, id, user_id, role):
    url = f"{ITEMS_URL}/{id}/accesses/"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to get accesses: {response.status_code}")
        return None

    accesses = response.json()

    for access in accesses:
        if access["user"]["id"] == user_id:
            print(f"User already has access: {access['role']}")
            return access

    data = {
        "user_id": user_id,
        "role": role
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print(f"Access added: {role}")
        return response.json()

    print(f"Failed to add access: {response.status_code}")
    return None

def update_access(token, item_id, user_id, access_id, role):
    url = f"{ITEMS_URL}/{item_id}/accesses/{access_id}/"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    data = {
        "user_id": user_id,
        "role": role
    }

    response = requests.patch(url, headers=headers, json=data)

    if response.status_code == 200:
        print(f"Updated access: {role}")
        return response.json()

    print(f"Failed to update access: {response.status_code}")
    return None    
