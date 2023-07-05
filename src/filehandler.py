import json
import os
import datetime
import time
import csv
import glob

import config

cwd = os.getcwd()

def add_date_suffix(file_name, target_suffix="-YYYY-MM-DD"):
    now = datetime.datetime.now()
    if str.upper(target_suffix).endswith("YYYY-MM-DD"):
        suffix = now.strftime('-%Y-%m-%d')
        if suffix not in file_name:
            file_name += suffix
    elif "servicedesk" in target_suffix:
        suffix = now.strftime('-%d.%m.%Y')
        if suffix not in file_name:
            file_name += suffix
    return file_name

def check_extension(file_name, extension=".json"):
    if not file_name.endswith(extension):
        file_name += extension
    return file_name

def get_path_to_file(file_base_name):
    if file_base_name is config.jira_unsorted_file_name:
        path_to_file = config.jira_unsorted_dir
    elif file_base_name is config.jira_categorized_file_name:
        path_to_file = config.jira_categorized_dir
    elif file_base_name is config.wiki_unsorted_file_name:
        path_to_file = config.wiki_unsorted_dir
    elif file_base_name is config.wiki_categorized_file_name:
        path_to_file = config.wiki_categorized_dir
    elif file_base_name == config.wiki_page_structure:
        path_to_file = config.wiki_page_structure_dir
    elif file_base_name == config.updated_cr_wiki2jira_file_name:
        path_to_file = config.updated_cr_wiki2jira_dir
    elif file_base_name == config.updated_cr_jira2wiki_file_name:
        path_to_file = config.updated_cr_jira2wiki_dir
    return path_to_file
    

def open_json_file(json_file_name, path_to_file=None):
    if path_to_file is None:
        path_to_file = get_path_to_file(json_file_name)
        
    now = datetime.datetime.now()
    suffix = now.strftime('-%Y-%m-%d')
    if suffix not in json_file_name and ".json" not in json_file_name:
        json_file_name += suffix
    if "/" not in json_file_name:
        json_file_name = check_extension(json_file_name)
        json_file_path =  path_to_file + json_file_name
    else:
        json_file_name = check_extension(json_file_name)
        json_file_path = json_file_name
        
    with open(os.path.join(cwd, json_file_path), encoding="utf-8", errors="ignore") as file:
        data = json.load(file)
        # print(data)
    return data

def find_latest_file(directory_path):
    today = datetime.date.today().strftime("%Y-%m-%d")
    files = glob.glob(os.path.join(directory_path, f"*-{today}"))
    if not files:
        files = glob.glob(os.path.join(directory_path, "*-*-*"))
        if not files:
            return None
        return max(files, key=os.path.getctime)
    return max(files, key=os.path.getctime)


def load_latest_file(file_base_name, path_to_file=None, suffix=None):
    if path_to_file is None:
        path_to_file = get_path_to_file(file_base_name)
    if suffix is None:
        suffix = "-" + datetime.datetime.today().strftime("%Y-%m-%d")
    elif isinstance(suffix, str) and not suffix.startswith("-"):
        suffix = "-" + datetime.datetime.strptime(suffix, "%Y-%m-%d")
        print(suffix)
    try:
        file_base_name = add_date_suffix(file_base_name)
        latest_file = find_latest_file(path_to_file)
        latest_file = os.path.basename(latest_file)
        if latest_file is not None:
            return open_json_file(latest_file, path_to_file)
        else:
            return open_json_file(file_base_name, path_to_file)
    except Exception as e:
        print(f"Failed to load latest file {file_base_name} with suffix {suffix} in {path_to_file} with Error: {e}")
        return False
    
    
    

# def json2csv(json_data, csv_file_name=config.updated_cr_file_name, csv_file_path=config.updated_cr_dir):
#     ## also see Jira Admin Docu for importing csv files at https://confluence.atlassian.com/adminjiraserver0820/importing-data-from-csv-1095777338.html
    
#     csv_file_name = add_date_suffix(csv_file_name, target_suffix="servicedesk")
#     csv_file_name = check_extension(csv_file_name, extension=".csv")
#     csv_target = csv_file_path + csv_file_name
#     fieldnames = ["name", "content", "scope", "scopeParam", "favourite"]
#     with open(csv_target, mode='w', newline='', encoding='utf-8-sig') as csvfile:
#         writer = csv.writer(csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_NONNUMERIC, lineterminator='\r\n', escapechar='"', doublequote=True)
#         writer.writerow(fieldnames)
#         # writer.writerow(fieldnames)
#         for item in json_data:
#             row = {
#                 "name": item.get("name", ""),
#                 "content": item.get("templateText", ""),
#                 "scope": item.get("templateScope", ""),
#                 "scopeParam": item.get("projectKey") if item.get("templateScope") == "PROJECT" else item.get("ownerUserKey") if item.get("templateScope") == "USER" else "",
#                 "favourite": ""
#             }
#             writer.writerow([row[field] if ',' not in row[field] else f"'{row[field]}'" for field in fieldnames])
#     print("CSV File written and saved in 'jira-imports' directory")
    
        

def safe_json_file(data, json_file_name="canned-responses", path_to_file=config.jira_categorized_dir):
    # add suffix and extension to file name
    json_file_name = add_date_suffix(json_file_name)
    json_file_name = check_extension(json_file_name)
    json_file_path =  path_to_file + json_file_name

    # create directory if it does not exist
    if not os.path.exists("data/jira-exports/json-response"):
        os.makedirs(os.path.join(cwd, path_to_file))

    # if file with the same name already exists, overwrite it
    if os.path.isfile(os.path.join(cwd, json_file_path)):
        with open(os.path.join(cwd, json_file_path), "w", encoding="utf-8") as outfile:
            json.dump(data, outfile, ensure_ascii=False, indent=4)
    else:
        with open(os.path.join(cwd, json_file_path), "w+", encoding="utf-8") as outfile:
            json.dump(data, outfile, ensure_ascii=False, indent=4)


def delete_target(file_path='', filter_file_name='',filter_file_type='', directory_path='', suffix_datetime=''):
    # get current date in the format "-YYYY-MM-DD"
    if suffix_datetime == "today":
        suffix_datetime = datetime.datetime.now().strftime("-%Y-%m-%d")
    # loop through files in directory
    for file in os.listdir(directory_path):
        # check if file matches filter parameters
        if file.endswith(filter_file_type) and filter_file_name in file and suffix_datetime in file:
            # construct full file path
            file_path = os.path.join(directory_path, file)
            # remove file
            os.remove(file_path)

def cleanup():
    # shutil.rmtree(os.path.join(cwd, "data/jira-exports/json-response"))
    # cleanup extracted data in json files in data directory
    # if there are more than 10 Files in one of the directories, cleanup json Files older than 30 days
    files_to_keep = 3
    days_to_keep = 30
    if len(os.listdir(os.path.join(cwd, "data/jira-exports"))) > files_to_keep:
        now = time.time()
        paths_to_cleanup = ["data/jira-exports"]
        for path in paths_to_cleanup:
            for filename in os.listdir(os.path.join(cwd, path)):
                filestamp = os.stat(os.path.join(path, filename)).st_mtime
                filecompare = now - days_to_keep * 86400
                if filestamp < filecompare:
                    os.remove(os.path.join(path, filename))



### DEV json file repair ###
def get_substring_after_last_underscore(string):
    index = string.rfind('_')
    if index != -1:
        return string[index+1:]
    else:
        return ''


def json_repair_DEV(file_path="data/wiki-exports/unsorted-exports/"):
    data = open_json_file("wiki-cr-export", file_path)
    i = 3
    for cr in data:
        cr["templateId"] = i
        if "serverId" in cr.keys():
            cr.pop("serverId")
        i += 1
        # string = cr["serverId"]
        # index = string.rfind('_')
        # if index != -1:
            # cr["templateId"] = get_substring_after_last_underscore(cr.pop("serverId"))  
        # else:
        #     cr["templateId"] = 0
    # print(data)
    safe_json_file(data, "wiki-cr-export", file_path)
        
