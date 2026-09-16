from drive_api import *

def main():

    drive_token = login("drive", "drive")
    mark_token = login("mark", "pass")
    miles_token = login("miles", "pass")

    if not drive_token or not mark_token or not miles_token:
        print("Login failed.")
        return

    print("\n=== ITEMS ===")

    get_items(mark_token)
    get_items(miles_token)
    items = get_items(drive_token)

    if not items:
        print("No items available.")
        return

    for item in items:
        print(
            f"{item['type']:6} "
            f"{item['title']} "
            f"{item['id']}"
        )

    print("\n=== NORMAL ACTIVITY ===")
    
    for item in items:
        if item["type"] == "file":
            download_file(drive_token, item["url"], item["filename"])
    
        elif item["type"] == "folder":
            children = open_folder(drive_token, item["id"])
            for child in children:
                if child["type"] == "file":
                    download_file(drive_token, child["url"], child["filename"])

    files = [item for item in items if item["type"] == "file"]

    if not files:
        print("No file available for permission tests.")
        return

    test_file = files[0]
    item_id = test_file["id"]

    download_file(mark_token, test_file["url"], test_file["filename"])

    print("\n=== LINK CONFIGURATION ===")

    update_link_configuration(drive_token, item_id, LINK_PUBLIC, ROLE_READER)

    print("\n=== USERS ===")

    mark = find_user(drive_token, "mark.down@plain.text")
    miles = find_user(drive_token, "miles.ahead@roadmap.fwd")

    if not mark:
        print("Mark not found.")
        return

    if not miles:
        print("Miles not found.")
        return

    mark_id = mark[0]["id"]
    miles_id = miles[0]["id"]

    print(f"Mark ID : {mark_id}")
    print(f"Miles ID: {miles_id}")

    print("\n=== ADD ACCESS ===")

    add_access(drive_token, item_id, mark_id, ROLE_READER)

    miles_access = add_access(drive_token, item_id, miles_id, ROLE_READER)
    if miles_access is None:
        return
    access_id = miles_access["id"]
    
    print("\n=== PERMISSION ESCALATION ===")

    update_access(mark_token, item_id, mark_id, access_id, ROLE_EDITOR)
    update_access(mark_token, item_id, miles_id, access_id, ROLE_EDITOR)
    update_access(drive_token, item_id, miles_id, access_id, ROLE_EDITOR)
    update_access(drive_token, item_id, miles_id, access_id, ROLE_ADMIN)
    update_access(drive_token, item_id, miles_id, access_id, ROLE_OWNER)

if __name__ == "__main__":
    main()