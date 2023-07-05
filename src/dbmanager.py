import os
import json
from datetime import datetime

jira_dir = "data/jira-exports/unsorted-exports/"
confluence_dir = "data/wiki-exports/unsorted-exports/"
database_dir = "data/database/"

def get_newest_file(path):
    files = [f for f in os.listdir(path) if f.endswith(".json")]
    if not files:
        return None
    return max(files)

def get_last_change(file):
    try:
        return datetime.strptime(file[-14:-5], "%Y-%m-%d")
    except ValueError:
        return None

def sanitize_text(text):
    # Perform sanitization tasks (e.g., remove HTML tags, convert special characters)
    # Implement the code to sanitize the text
    pass

def sync_data():
    # Get the two newest Jira files
    jira_files = sorted([f for f in os.listdir(jira_dir) if f.endswith(".json")])
    jira_newest_files = jira_files[-2:]
    jira_newest_files = [os.path.join(jira_dir, f) for f in jira_newest_files]

    # Get the two newest Confluence files
    confluence_files = sorted([f for f in os.listdir(confluence_dir) if f.endswith(".json")])
    confluence_newest_files = confluence_files[-2:]
    confluence_newest_files = [os.path.join(confluence_dir, f) for f in confluence_newest_files]

    # Load the data from the two newest Jira files
    jira_data = []
    for file in jira_newest_files:
        with open(file, "r") as jira_file:
            jira_data.extend(json.load(jira_file))

    # Load the data from the two newest Confluence files
    confluence_data = []
    for file in confluence_newest_files:
        with open(file, "r") as confluence_file:
            confluence_data.extend(json.load(confluence_file))

    # Compare the last change dates
    jira_last_change = max((get_last_change(f) for f in jira_newest_files if get_last_change(f) is not None), default=None)
    confluence_last_change = max((get_last_change(f) for f in confluence_newest_files if get_last_change(f) is not None), default=None)

    def merge_data(jira_data, confluence_data):
        merged_data = []
        for jira_item in jira_data:
            template_id = jira_item.get("templateId")
            confluence_item = next((item for item in confluence_data if item.get("templateId") == template_id), None)
            if confluence_item:
                merged_item = {
                    "name": jira_item.get("name", ""),
                    "templateText": jira_item.get("templateText", ""),
                    "clearText": "",
                    "jiraSyntax": "",
                    "wikiSyntax": "",
                    "chatbotAnswerDE": "",
                    "chatbotAnswerEN": "",
                    "projectKey": confluence_item.get("projectKey", ""),
                    "templateId": template_id,
                    "pageId": confluence_item.get("pageId", ""),
                    "serverId": jira_item.get("serverId", confluence_item.get("serverId")),
                    "templateScope": jira_item.get("templateScope", ""),
                    "last_update": {
                        "creation_date": "",
                        "creator_user": "",
                        "created_on": "wiki",
                        "last_change": "",
                        "last_editor": "",
                        "last_changed_on": ""
                    }
                }
                merged_data.append(merged_item)
            else:
                merged_data.append(jira_item)
        for confluence_item in confluence_data:
            if not any(item.get("templateId") == confluence_item.get("templateId") for item in merged_data):
                merged_data.append(confluence_item)
        return merged_data

    merged_data = merge_data(jira_data, confluence_data)

    def sanitize_and_convert_text(data):
        for item in data:
            item["templateText"] = sanitize_text(item.get("templateText", ""))
            item["clearText"] = ""
            item["jiraSyntax"] = ""
            item["wikiSyntax"] = ""
            item["chatbotAnswerDE"] = ""
            item["chatbotAnswerEN"] = ""
            item["templateScope"] = ""
            item["last_update"] = {
                "creation_date": "",
                "creator_user": "",
                "created_on": "wiki",
                "last_change": "",
                "last_editor": "",
                "last_changed_on": ""
            }

    sanitize_and_convert_text(merged_data)

    def convert_datetime_to_string(date_time):
        return date_time.strftime("%B %d, %Y")

    def update_last_update_information(data):
        for item in data:
            last_update = item.get("last_update")
            if last_update:
                if not last_update.get("creation_date"):
                    last_update["creation_date"] = convert_datetime_to_string(datetime.now())
                if not last_update.get("last_change"):
                    last_update["last_change"] = convert_datetime_to_string(datetime.now())
                if not last_update.get("created_on"):
                    last_update["created_on"] = "wiki"
                if not last_update.get("last_changed_on"):
                    if item.get("last_changed_on") == "jira":
                        last_update["last_changed_on"] = "jira"
                    else:
                        last_update["last_changed_on"] = "wiki"

    update_last_update_information(merged_data)

    database_filename = f"db-cr-{datetime.now().strftime('%Y-%m-%d')}.json"
    database_path = os.path.join(database_dir, database_filename)

    with open(database_path, "w") as current_database_file:
        json.dump(merged_data, current_database_file, indent=4, default=str)




import os
import json
from datetime import datetime

jira_dir = "data/jira-exports/unsorted-exports/"
confluence_dir = "data/wiki-exports/unsorted-exports/"
database_dir = "data/database/"

# Existing code...

def db_jira_export():
    # Get the latest db-cr.json file
    database_files = sorted([f for f in os.listdir(database_dir) if f.startswith("db-cr-") and f.endswith(".json")])
    latest_database_file = database_files[-1]
    latest_database_path = os.path.join(database_dir, latest_database_file)

    # Load the data from the latest db-cr.json file
    with open(latest_database_path, "r") as database_file:
        db_data = json.load(database_file)

    jira_export_files = sorted([f for f in os.listdir(jira_dir) if f.startswith("jira-cr-export-") and f.endswith(".json")])
    latest_jira_export_file = jira_export_files[-1]
    latest_jira_export_path = os.path.join(jira_dir, latest_jira_export_file)

    # Load the data from the latest jira export file
    with open(latest_jira_export_path, "r") as jira_export_file:
        jira_export_data = json.load(jira_export_file)

    # Create a mapping of serverId to updated data
    server_id_mapping = {}
    for item in db_data:
        server_id = item.get("serverId")
        server_id_mapping[server_id] = item

    # Update the jira export data with the new values
    for item in jira_export_data:
        server_id = item.get("serverId")
        updated_data = server_id_mapping.get(server_id)
        if updated_data:
            item.update(updated_data)

    # Save the updated jira export data back to the file
    with open(latest_jira_export_path, "w") as jira_export_file:
        json.dump(jira_export_data, jira_export_file, indent=4)

def db_wiki_export():
    # Get the latest db-cr.json file
    database_files = sorted([f for f in os.listdir(database_dir) if f.startswith("db-cr-") and f.endswith(".json")])
    latest_database_file = database_files[-1]
    latest_database_path = os.path.join(database_dir, latest_database_file)

    # Load the data from the latest db-cr.json file
    with open(latest_database_path, "r") as database_file:
        db_data = json.load(database_file)

    wiki_export_files = sorted([f for f in os.listdir(confluence_dir) if f.startswith("wiki-cr-export-") and f.endswith(".json")])
    latest_wiki_export_file = wiki_export_files[-1]
    latest_wiki_export_path = os.path.join(confluence_dir, latest_wiki_export_file)

    # Load the data from the latest wiki export file
    with open(latest_wiki_export_path, "r") as wiki_export_file:
        wiki_export_data = json.load(wiki_export_file)

    # Create a mapping of serverId to updated data
    server_id_mapping = {}
    for item in db_data:
        server_id = item.get("serverId")
        server_id_mapping[server_id] = item

    # Update the wiki export data with the new values
    for item in wiki_export_data:
        server_id = item.get("serverId")
        updated_data = server_id_mapping.get(server_id)
        if updated_data:
            item.update(updated_data)

    # Save the updated wiki export data back to the file
    with open(latest_wiki_export_path, "w") as wiki_export_file:
        json.dump(wiki_export_data, wiki_export_file, indent=4)




def merge_jira_export_with_db():
    # Get the latest db-cr.json file
    database_files = sorted([f for f in os.listdir(database_dir) if f.startswith("db-cr-") and f.endswith(".json")])
    latest_database_file = database_files[-1]
    latest_database_path = os.path.join(database_dir, latest_database_file)

    # Load the data from the latest db-cr.json file
    with open(latest_database_path, "r") as database_file:
        db_data = json.load(database_file)

    jira_export_files = sorted([f for f in os.listdir(jira_dir) if f.startswith("jira-cr-export-") and f.endswith(".json")])
    latest_jira_export_file = jira_export_files[-1]
    latest_jira_export_path = os.path.join(jira_dir, latest_jira_export_file)

    # Load the data from the latest jira export file
    with open(latest_jira_export_path, "r") as jira_export_file:
        jira_export_data = json.load(jira_export_file)

    # Create a mapping of serverId to updated data
    server_id_mapping = {}
    for item in db_data:
        server_id = item.get("serverId")
        server_id_mapping[server_id] = item

    # Update the jira export data with the new values
    for item in jira_export_data:
        server_id = item.get("serverId")
        updated_data = server_id_mapping.get(server_id)
        if updated_data:
            updated_item = {}
            for key in ["serverId", "name", "templateScope", "templateText", "projectKey", "ownerUserKey"]:
                updated_item[key] = updated_data.get(key)
            item.update(updated_item)

    # Save the updated jira export data to a new file
    jira_export_output_path = os.path.join(database_dir, "exports/db-export-jira.json")
    jira_export_output_data = [
        {
            "serverId": item.get("serverId"),
            "name": item.get("name"),
            "templateScope": item.get("templateScope"),
            "templateText": item.get("templateText"),
            "projectKey": item.get("projectKey"),
            "ownerUserKey": item.get("ownerUserKey")
        }
        for item in jira_export_data
    ]
    with open(jira_export_output_path, "w") as jira_export_output_file:
        json.dump(jira_export_output_data, jira_export_output_file, indent=4)


def merge_wiki_export_with_db():
    # Get the latest db-cr.json file
    database_files = sorted([f for f in os.listdir(database_dir) if f.startswith("db-cr-") and f.endswith(".json")])
    latest_database_file = database_files[-1]
    latest_database_path = os.path.join(database_dir, latest_database_file)

    # Load the data from the latest db-cr.json file
    with open(latest_database_path, "r") as database_file:
        db_data = json.load(database_file)

    wiki_export_files = sorted([f for f in os.listdir(confluence_dir) if f.startswith("wiki-cr-export-") and f.endswith(".json")])
    latest_wiki_export_file = wiki_export_files[-1]
    latest_wiki_export_path = os.path.join(confluence_dir, latest_wiki_export_file)

    # Load the data from the latest wiki export file
    with open(latest_wiki_export_path, "r") as wiki_export_file:
        wiki_export_data = json.load(wiki_export_file)

    # Create a mapping of serverId to updated data
    server_id_mapping = {}
    for item in db_data:
        server_id = item.get("serverId")
        server_id_mapping[server_id] = item

    # Update the wiki export data with the new values
    for item in wiki_export_data:
        server_id = item.get("serverId")
        updated_data = server_id_mapping.get(server_id)
        if updated_data:
            item.update({key: updated_data[key] for key in ["serverId", "name", "templateScope", "templateText", "pageId"]})

    # Save the updated wiki export data to a new file
    wiki_export_output_path = os.path.join(database_dir, "exports/db-export-wiki.json")
    with open(wiki_export_output_path, "w") as wiki_export_output_file:
        json.dump(wiki_export_data, wiki_export_output_file, indent=4)

