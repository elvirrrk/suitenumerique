import time

from drive_api import *


def get_files(token):
    items = get_items(token)
    files = [item for item in items if item["type"] == "file"]

    for item in items:
        if item["type"] == "folder":
            children = open_folder(token, item["id"])

            if children:
                files += [child for child in children if child["type"] == "file"]

    return files


def mass_download(token, files):
    print("\n=== MASS DOWNLOAD ATTACK ===")

    for i in range(65):
        file = files[i % len(files)]
        print(f"[{i + 1}/65] download {file['filename']}")
        download_file(token, file["url"], file["filename"])


def permission_denial_attack(attacker_token, victim_files):
    print("\n=== PERMISSION DENIAL ATTACK ===")

    targets = victim_files[:5]

    for i in range(10):
        file = targets[i % len(targets)]

        print(f"[{i + 1}/10] unauthorized download {file['filename']}")
        download_file(attacker_token, file["url"], file["filename"])

        time.sleep(0.1)


def permission_change_attack(owner_token, target_id, files):
    print("\n=== PERMISSION CHANGE ATTACK ===")

    targets = files[:5]

    for file in targets:
        access = add_access(owner_token, file["id"], target_id, ROLE_READER)

        if not access:
            continue

        access_id = access["id"]

        update_access(owner_token, file["id"], target_id, access_id, ROLE_EDITOR)
        update_access(owner_token, file["id"], target_id, access_id, ROLE_READER)


def self_grant_attack(owner_token, attacker_token, attacker_id, file):
    print("\n=== SELF GRANT ATTACK ===")

    access = add_access(owner_token, file["id"], attacker_id, ROLE_EDITOR)

    if not access:
        print("Could not create attacker access")
        return

    print("Attacker tries to grant OWNER to himself")

    update_access(
        attacker_token,
        file["id"],
        attacker_id,
        access["id"],
        ROLE_OWNER
    )


def main():
    drive_token = login("drive", "drive")
    mark_token = login("mark", "pass")

    if not drive_token or not mark_token:
        print("Login failed")
        return

    get_items(mark_token)

    files = get_files(drive_token)

    mark = find_user(drive_token, "mark.down@plain.text")

    if not mark:
        print("Mark not found")
        return

    mark_id = mark[0]["id"]

    print("\n==============================")
    print("        ATTACK DEMO")
    print("==============================")

    mass_download(drive_token, files)

    permission_denial_attack(mark_token, files)

    permission_change_attack(drive_token, mark_id, files)

    self_grant_attack(drive_token, mark_token, mark_id, files[0])

    print("\n=== DEMO DONE ===")


if __name__ == "__main__":
    main()
