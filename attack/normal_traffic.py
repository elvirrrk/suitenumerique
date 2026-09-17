import json
import random
import time

from drive_api import *

REALM_PATH = "../docker/auth/realm.json"

def load_users():
    with open(REALM_PATH, "r") as file:
        realms = json.load(file)

    drive = next(realm for realm in realms if realm["realm"] == "drive")

    return [
        {
            "username": user["username"],
            "email": user["email"],
            "password": user["credentials"][0]["value"]
        }
        for user in drive["users"]
    ]

def main():

    users = load_users()

    for user in users:
        user["token"] = login(user["username"], user["password"])
        get_items(user["token"])

    for _ in range(100):
        user = random.choice(users)
        numbers = random.randint(1, 3)
        
        for _ in range(numbers):

            action = random.choices(
                [ "open_folder", "download", "share", "permission"],
                weights = [40, 30, 20, 10]
            )[0]

            print (f"{user["username"]}: {action}")

            items = get_items(user["token"])
            files = [i for i in items if i["type"] == "file"]
            folders = [i for i in items if i["type"] == "folder"]

            if action == "open_folder" and folders:
                folder = random.choice(folders)
                open_folder(user["token"], folder["id"])
                
            elif action == "download" and files:
                file = random.choice(files)
                download_file( user["token"], file["url"], file["filename"] )

            elif action in ("share", "permission") and files:
                target = random.choice([ u for u in users if u["username"] != user["username"] ])
                found = find_user( user["token"], target["email"] )
                if not found:
                    continue
                target_id = found[0]["id"]
                file = random.choice(files)

                role = random.choices(
                    ["reader", "editor", "administrator", "owner"],
                    weights=[60, 30, 8, 2]
                )[0]

                access = add_access( user["token"], file["id"], target_id, ROLE_READER)
                
                if action == "permission" and access:
                    update_access( user["token"], file["id"], target_id, access["id"], role)

            time.sleep(random.uniform(0.05, 0.3))

        time.sleep(random.uniform(0.2, 1))
        
if __name__ == "__main__":
    main()