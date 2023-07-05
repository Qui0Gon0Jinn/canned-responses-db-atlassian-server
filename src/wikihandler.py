import os
import json
import requests
import re
import time
import datetime
# from datetime import datetime

import config
import exporthandler
import filehandler
import jirahandler
import config
# import html

existing_subpage_titles = list()
existing_subpages = list()
parent_pages = list()
wiki_exports = list()

def add_timestamp_to_wiki_export(wiki_export):
    # Get the current timestamp in ISO format
    timestamp = datetime.datetime.now().isoformat()

    # Loop through all the items in the wiki export
    for item in wiki_export:
        # Add the timestamp to the item under the key "last_checked"
        item["last_checked"] = timestamp

    # Return the updated wiki export
    return wiki_export

def wiki_request(method="GET", url="https://wiki.wu.ac.at/rest/api/content"):
    headers = {
        "Authorization": 'Bearer ' + str(os.getenv('WIKI_TOKEN'))
    }
    try:
        response = requests.request(method, url, headers=headers, timeout=30)
        json_data = response.json()
        return json_data
    except TimeoutError:
        print("TimeoutError while Wiki Request")
    except requests.exceptions.HTTPError as err:
        if response.status_code == 403:
            print("Zugriff auf den Server verweigert. Bitte prüfen Sie die Zugangsdaten.")
        else:
            print(f"Fehler beim Zugriff auf die API. Fehlercode: {err.response.status_code}")

def get_wiki_subpages(parent_pageId=config.initial_parent_pageId):
    global existing_subpages
    subpages = []
    url = "https://wiki.wu.ac.at/rest/api/content/search?cql=parent=" + str(parent_pageId)
    response = wiki_request(url=url)
    for subpage in response["results"]:
        page_obj = {
            "pageId": subpage["id"],
            "title": subpage["title"]
        }
        if page_obj not in subpages:
            subpages.append(page_obj)
        if page_obj not in existing_subpages:
            existing_subpages.append(page_obj)
    subpages = [dict(t) for t in (tuple(d.items()) for d in subpages)]
    existing_subpages = [dict(t) for t in (tuple(d.items()) for d in existing_subpages)]
    return subpages

def collect_existing_pages(spaceKey=config.initial_spaceKey):
    global existing_subpages
    global existing_subpage_titles
    get_wiki_subpages()
    print_counter = 1
    max_depth = 3
    print("Collecting existing pages, this may take a while…")
    for i in range(max_depth):
        for subpage in existing_subpages:
            pageId = subpage["pageId"]
            title = subpage["title"] 
            if title not in existing_subpage_titles:
                existing_subpage_titles.append(title)
            new_subpage = get_wiki_subpages(pageId)
            if subpage not in existing_subpages:
                existing_subpages.extend(new_subpage)
                if len(existing_subpage_titles) % print_counter == 0:
                    print(str(len(existing_subpage_titles)) + " new Pages collected, please wait…")
    existing_subpage_titles = list(set(existing_subpage_titles))
    existing_subpages = [dict(t) for t in (tuple(d.items()) for d in existing_subpages)]
    print("Subpages successfully collected, please wait…")
    return existing_subpage_titles

def get_wiki_page_id(page_title=None, spaceKey=config.initial_spaceKey):
    
    for page in existing_subpages:
        if page["title"] == page_title:
            return page["pageId"]
    params = {"spaceKey": spaceKey, "title": page_title}
    # url = "https://wiki.wu.ac.at/rest/api/content" + "?spaceKey=" + spaceKey + "&title=" + page_title
    url = "https://wiki.wu.ac.at/rest/api/content"
    headers = {
        "Authorization": 'Bearer '+ str(os.getenv('WIKI_TOKEN'))
    }
    response = requests.request("GET", url, headers=headers, params=params)
    if "results" in response.json() and response.status_code == 200:
        if len(response.json()["results"]) > 0:
            pageId = response.json()["results"][0]["id"]
            return pageId
    else:
        print("Page with Title '", page_title, "' not found in Wiki, pls check Title")



def prepare_cr(json_data):
    # table_headers = config.wiki_cr_page_table_headers
    obj = json_data
    obj["templateText"] = re.sub(r'<([^>]+)>', r'[\1]', obj["templateText"])
    obj["templateText"] = obj["templateText"].replace("\r\n", "<br/>")
    obj["templateText"] = obj["templateText"].replace("'", "\'")
    obj["templateText"] = obj["templateText"].replace("&", "&amp;")
    obj["name"] = obj["name"].replace("&", "&amp;")
    # table = "<p class=\"auto-cursor-target\"><br/></p><table><colgroup><col/><col/><col/><col/></colgroup><tbody><tr><th scope=\"col\">" + table_headers[0] + "</th><th scope=\"col\">" + table_headers[1] + "</th><th scope=\"col\">" + table_headers[2] + "</th><th scope=\"col\">" + table_headers[3] + "</th><th scope=\"col\">" + table_headers[4] + "</th><th scope=\"col\">" + table_headers[5] + "</th></tr>"
    # if isinstance(obj["templateId"], int):
    #     table += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(obj["name"], obj["templateText"], "", "", obj["projectKey"], obj["templateId"])
    # else:
    #     table += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(obj["name"], obj["templateText"], "", "", obj["projectKey"], "TODO: get templateID")
    # table += "</tbody></table><p class=\"auto-cursor-target\"><br/></p>"
    # return table
    return obj["templateText"]

def update_body(body, new_cr_table):
    new_body = new_cr_table
    return new_body

def update_page(json_data, spaceKey=config.initial_spaceKey, pageId=config.initial_parent_pageId):
    if pageId is None:
        page_title = json_data['name'] + ' - ' + json_data['projectKey'] + ' - CR'
        pageId = get_wiki_page_id(page_title=page_title)
    url = "https://wiki.wu.ac.at/rest/api/content/" + str(pageId) + "?spaceKey=" + spaceKey + "&expand=version,body.storage"
    token = 'Bearer ' + str(os.getenv('WIKI_TOKEN'))
    headers = {
        'Authorization': token
    }
    response = requests.request("GET", url, headers=headers)
    response = response.json()
    body = response["body"]["storage"]["value"]
    new_cr_table = prepare_cr(json_data)
    new_body = update_body(body, new_cr_table)
    # url = 'https://wiki.wu.ac.at/rest/api/content/' + str(pageId) + "?spaceKey=" + spaceKey
    url = 'https://wiki.wu.ac.at/rest/api/content/' + str(pageId) + "?expand=version,body.storage"
    new_version = response["version"]["number"] + 1
    payload = json.dumps({
        "type": "page",
        "title": response["title"],
        "version": {"number": new_version},
        "space": {"key": spaceKey},
        "body": {
            "storage": {
                "value": new_body,
                "representation": "storage"
            }
        }
    }, ensure_ascii=False).encode(encoding="utf-8")
    headers.update({"Content-Type": "application/json"})
    response = requests.request("PUT", url, headers=headers, data=payload)
    if response.status_code == 200:
        response = response.json()
        print(response["title"] + " - Page successfully updated")
        time.sleep(config.wiki_request_pause_time)
    else:
        print(json_data["name"] + " - Page update failed\n" + response.text)

def update_pages(json_data, spaceKey=config.initial_spaceKey):
    for scope in json_data:
        if scope == "categorized-projects":
            for project in json_data[scope]:
                for cat1 in json_data[scope][project]:
                    if "projectKey" in json_data[scope][project][cat1].keys():
                        page_title = cat1 + " - " + project + " - CR"
                        pageId = get_wiki_page_id(page_title, spaceKey=spaceKey)
                        update_page(json_data[scope][project][cat1], spaceKey=spaceKey,pageId=pageId)
                    else:
                        for cat2 in json_data[scope][project][cat1]:
                            if "projectKey" in json_data[scope][project][cat1][cat2].keys():
                                page_title = cat2 + " - " + cat1 + " - " + project + " - CR"
                                pageId = get_wiki_page_id(page_title, spaceKey=spaceKey)
                                update_page(json_data[scope][project][cat1][cat2], spaceKey=spaceKey,pageId=pageId)
                            else:
                                for cat3 in json_data[scope][project][cat1][cat2]:
                                    if "projectKey" in json_data[scope][project][cat1][cat2][cat3].keys():
                                        page_title = cat3 + " - " + cat2 + " - " + cat1 + " - " + project + " - CR"
                                        pageId = get_wiki_page_id(page_title, spaceKey=spaceKey)
                                        update_page(json_data[scope][project][cat1][cat2][cat3], spaceKey=spaceKey,pageId=pageId)
                                    else:
                                        print("Canned Response with a category depth of 4 is not supported")
        # if scope == "PROJECT" or scope == "GLOBAL":
        if scope == "PROJECT":
            for project in json_data[scope]:
                for cr in json_data[scope][project]:
                    if "::" not in cr["name"]:
                        page_title = cr["name"] + " - " + project + " - CR"
                        pageId = get_wiki_page_id(page_title, spaceKey=spaceKey)                
                        update_page(cr, spaceKey=spaceKey, pageId=pageId)
        if scope == "GLOBAL":
            for cr in json_data[scope]:
                    if "::" not in cr["name"]:
                        page_title = cr["name"] + " - " + "GLOBAL" + " - CR"
                        pageId = get_wiki_page_id(page_title, spaceKey=spaceKey)                
                        update_page(cr, spaceKey=spaceKey, pageId=pageId)

def get_wiki_cr_content(spaceKey=config.initial_spaceKey, pageId=config.initial_parent_pageId):
    url = "https://wiki.wu.ac.at/rest/api/content/" + str(pageId) + "?spaceKey=" + spaceKey + "&expand=version,body.storage"
    token = 'Bearer ' + str(os.getenv('WIKI_TOKEN'))
    headers = {
        'Authorization': token
    }
    response = requests.request("GET", url, headers=headers)
    response = response.json()
    body = response["body"]["storage"]["value"]
    time.sleep(config.wiki_request_pause_time)
    return body


# def prepare_single_cr(cr_obj):
#     table = '<p class="auto-cursor-target"><br /></p><table><colgroup><col /><col /><col /><col /></colgroup><tbody><tr><th scope="col">scopeParameter</th><th scope="col">CR Name</th><th scope="col">Content</th><th scope="col">Anmerkungen</th></tr>'
#     if (">" or "<") in cr_obj["content"]:
#         cr_obj["content"] = cr_obj["content"].replace("<", "&lt;")
#         cr_obj["content"] = cr_obj["content"].replace(">","&gt;")
#         cr_obj["content"] = cr_obj["content"].replace("&", "&amp;")
#         print("> or < found")

#     table += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(*cr_obj.values())
#     table += '</tbody></table><p class="auto-cursor-target"><br /></p>'
#     return table

def get_projectKey_from_title(string):
    pattern = r"([A-Z]+)[\s-]*CR$"
    match = re.search(pattern, string)
    if match:
        return match.group(1)
    else:
        return ""

def get_category(string):
    project_key = get_projectKey_from_title(string)
    if project_key is None:
        return None
    pattern = re.compile(r"(?<=- )" + ".+?(?<= -" + project_key + " - CR)", re.IGNORECASE)
    match = pattern.search(string)
    if match:
        return match.group()
    else:
        return ""
    
def create_parent_page(title, spaceKey=config.initial_spaceKey, parent_page_id=config.initial_parent_pageId):
    if title in existing_subpage_titles:
        return print("Page '" + title + "' already exists, skipping creation")
    url = "https://wiki.wu.ac.at/rest/api/content"
    payload = json.dumps({
    "type": "page",
    "title": title,
    "ancestors": [
        {
            "id": parent_page_id
        }
    ],
    "space": {
        "key": spaceKey
    },
    "body": {
        "storage": {
        "value": "",
        "representation": "storage"
        }
    }
    })
    headers = {
    'Authorization': 'Bearer '+ str(os.getenv('WIKI_TOKEN')),
    'Content-Type': 'application/json',
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        pageId = response.json()["id"]
        print("Page created successfully with pageId: " + pageId)
        existing_subpage_titles.append(title)
        existing_subpages.append({"pageId": pageId, "title": title})

        time.sleep(config.wiki_request_pause_time)
        parent_page = {
                    "projectKey": get_projectKey_from_title(title),
                    "cannedResponseName": get_projectKey_from_title(title) + "::" + get_category(title),
                    "pageTitle": title,
                    "pageId": pageId
                }
        if parent_page not in parent_pages:
            parent_pages.append(parent_page)
    else:
        print(response.text)



# def create_page(json_data, parent_page_id=config.initial_parent_pageId, spaceKey=config.initial_spaceKey, page_title="Demo - CR"):
#     # body = '<p class="auto-cursor-target"><br /></p><table><colgroup><col /><col /><col /><col /></colgroup><tbody><tr><th scope="col">scopeParameter</th><th scope="col">CR Name</th><th scope="col">Content</th><th scope="col">Anmerkungen</th></tr>'
#     # body += "</tbody></table><h1>TODOs</h1><ac:task-list><ac:task><ac:task-id>649</ac:task-id><ac:task-status>incomplete</ac:task-status><ac:task-body>x</ac:task-body></ac:task></ac:task-list>"
#     body = prepare_single_cr(json_data)
#     # TODO: get body of wiki-page and replace only CR-Data
#     # body = body.replace(" & ", "&amp;")
#     url = "https://wiki.wu.ac.at/rest/api/content"
#     # title = " - CR"
#     payload = json.dumps({
#     "type": "page",
#     "title": page_title,
#     "ancestors": [
#         {
#             "id": parent_page_id
#         }
#     ],
#     "space": {
#         "key": spaceKey
#     },
#     "body": {
#         "storage": {
#         "value": body,
#         "representation": "storage"
#         }
#     }
#     })
#     headers = {
#     'Authorization': 'Bearer ' + os.getenv('WIKI_TOKEN'),
#     'Content-Type': 'application/json',
#     }

#     response = requests.request("POST", url, headers=headers, data=payload)
#     if response.status_code == 200:
#         print("Page created successfully\n" + response.json()["id"])
#     else:
#         print(response.text)

def create_categorized_pages(cr_formatted):
    existing_subpage_titles = collect_existing_pages(spaceKey=config.initial_spaceKey)
    for project in cr_formatted["categorized-projects"]:
        project_title = project + " - CR"
        if project_title not in existing_subpage_titles:
            create_parent_page(project_title, parent_page_id=config.initial_parent_pageId)
        if "projectKey" not in cr_formatted["categorized-projects"][project].keys():
            for cat1 in cr_formatted["categorized-projects"][project]:
                cat1_title = cat1 + " - " + project + " - CR"
                if cat1_title not in existing_subpage_titles:
                    create_parent_page(cat1_title, parent_page_id=get_wiki_page_id(project_title))
                if "projectKey" not in cr_formatted["categorized-projects"][project][cat1].keys():
                    for cat2 in cr_formatted["categorized-projects"][project][cat1]:
                        cat2_title = cat2 + " - " + cat1 + " - " + project + " - CR"
                        if cat2_title not in existing_subpage_titles:
                            create_parent_page(cat2_title, parent_page_id=get_wiki_page_id(cat1_title))
                        if "projectKey" not in cr_formatted["categorized-projects"][project][cat1][cat2].keys():
                            for cat3 in cr_formatted["categorized-projects"][project][cat1][cat2]:
                                cat3_title = cat3 + " - " + cat2 + " - " + cat1 + " - " + project + " - CR"
                                if cat3_title not in existing_subpage_titles:
                                    create_parent_page(cat3_title, parent_page_id=get_wiki_page_id(cat2_title))
    if "PROJECT" in cr_formatted.keys():
        for project in cr_formatted["PROJECT"]:
            project_title = project + " - CR"
            if project_title not in existing_subpage_titles:
                create_parent_page(project_title, parent_page_id=config.initial_parent_pageId)
            for cr in cr_formatted["PROJECT"][project]:
                if "::" not in cr["name"]:
                    cr_title = cr["name"] + " - " + project + " - CR"
                    if cr_title not in existing_subpage_titles:
                        create_parent_page(cr_title, parent_page_id=get_wiki_page_id(project_title))
    if "GLOBAL" in cr_formatted.keys() and "GLOBAL" not in cr_formatted["PROJECT"].keys():
        project_title = "GLOBAL - CR"
        if project_title not in existing_subpage_titles:
            create_parent_page(project_title, parent_page_id=config.initial_parent_pageId)
        for cr in cr_formatted["GLOBAL"]:
            if "::" not in cr["name"]:
                cr_title = cr["name"] + " - " + "GLOBAL" + " - CR"
                if cr_title not in existing_subpage_titles:
                    create_parent_page(cr_title, parent_page_id=get_wiki_page_id(project_title))


def replace_wiki_headers(list_of_headers):
    default_list_of_table_headers = config.wiki_cr_page_table_headers
    default_list_of_json_keys = config.wiki_cr_export_json_keys
    if list_of_headers == default_list_of_table_headers:
        return default_list_of_json_keys
    else:
        if len(list_of_headers) == len(default_list_of_table_headers) or set(list_of_headers) == set(default_list_of_table_headers):
            for i in range(len(list_of_headers)):
                if list_of_headers[i].lower() == "projectkey":
                    list_of_headers[i] = "projectKey"
                elif list_of_headers[i].lower().startswith("name"):
                    list_of_headers[i] = "name"
                elif list_of_headers[i].lower() == ("canned response content" or "canned cesponse text" or "template" or "templatetext"):
                    list_of_headers[i] = "templateText"
                elif list_of_headers[i] == "Chatbot Answer - DE" or list_of_headers[i].replace(" ", "").lower() == "chatbotanswer-de":
                    list_of_headers[i] = "chatbotAnswerDE"
                elif list_of_headers[i] == "Chatbot Answer - EN" or list_of_headers[i].replace(" ", "").lower() == "chatbotanswer-en":
                    list_of_headers[i] = "chatbotAnswerEN"
                elif list_of_headers[i] == "Anmerkungen":
                    list_of_headers[i] = "Anmerkungen"
            if list_of_headers == default_list_of_json_keys:
                return list_of_headers
            elif list_of_headers[0].lower() == "projectKey" and list_of_headers[1].lower().startswith("name") and "chatbot" in (list_of_headers[3].lower() and list_of_headers[4].lower()):
                print("New Table Headers in WIKI Page!")
                # TODO: what to do when headers are changed? - quick fix: return default json keys
        elif set(list_of_headers) == set(["Name / chatbotID", "Canned Response Content", "Chatbot Answer Content", "Anmerkungen"]):
            list_of_headers[0] = "name"
            list_of_headers[1] = "templateText"
            list_of_headers[2] = "chatbotAnswerDE"
            list_of_headers[3] = "chatbotAnswerEn"
            list_of_headers.append("projectKey")
            list_of_headers.append("templateId")
            return list_of_headers
        else:
            list_of_headers = default_list_of_json_keys
    return list_of_headers
            

def html_table_to_json(html):
    # Extrahiere die Table-Elemente
    table_start = html.find("<table")
    table_end = html.find("</table>")
    if table_start > -1:
        table_html = html[table_start:table_end + 8] # 8 für das schließende </table> tag
        table_rows = table_html.split("<tr>")[1:] # überspringe den table header row
        # Extrahiere die Table-Header
        header_row = table_rows[0].split("<th scope=\"col\">")
        table_headers = [h.split("</th>")[0] for h in header_row[1:]]
        table_headers = replace_wiki_headers(table_headers)
        # Extrahiere die Table-Inhalte
        rows = []
        for row in table_rows[1:]:
            row_data = {}
            row_cells = row.split("<td>")
            for i, cell in enumerate(row_cells[1:]):
                if len(table_headers[i]):
                    try:
                        row_data[table_headers[i]] = cell.split("</td>")[0].strip()
                    except:
                        pass
                else:
                    table_headers
            rows.append(row_data)

        return rows
    else:
        pass


def str_between(input_string, start_string, end_string):
    search_string = '(?<=' + start_string + ')(.*?)(?=' + end_string + ')'
    match = re.search(search_string, input_string)
    if match:
        return match.group(0)
    else:
        return False




def export_wiki_cr_pages(spaceKey=config.initial_spaceKey):
    global existing_subpages
    global parent_pages
    global wiki_exports
    existing_subpages = []
    wiki_exports = []
    print("Exporting wiki pages to JSON")
    collect_existing_pages(spaceKey=config.initial_spaceKey)
    i = 0
    for page in existing_subpages:
        i += 1
        if i < len(existing_subpages):
            cr_wiki_export = get_wiki_cr_content(spaceKey=spaceKey, pageId=page["pageId"])
            if isinstance(cr_wiki_export, str) and len(cr_wiki_export) > 0:
                # wiki_cr = html_table_to_json(cr_wiki_export)
                wiki_cr = cr_wiki_export
                if isinstance(wiki_cr, list):
                    wiki_cr[0]["pageId"] = page["pageId"]
                if wiki_cr is not None and isinstance(wiki_cr, list):
                    wiki_exports.append(wiki_cr[0])
            # else:
            #     parent_page = {
            #         "projectKey": get_projectKey_from_title(page["title"]),
            #         "cannedResponseName": get_projectKey_from_title(page["title"]) + "::" + get_category(page["title"]),
            #         "pageTitle": page["title"],
            #         "pageId": page["pageId"]
            #     }
            #     if parent_page not in parent_pages:
            #         parent_pages.append(parent_page)
            # print(wiki_cr)
            
    wiki_exports = [dict(t) for t in (tuple(d.items()) for d in wiki_exports)]
    # wiki_exports = [x for i, x in enumerate(wiki_exports) if x not in wiki_exports[:i]]
    # wiki_exports = list(set(wiki_exports)) #TypeError
    filehandler.safe_json_file(parent_pages, config.wiki_page_structure, config.wiki_page_structure_dir)
    
    # if len(parent_pages) > 0:
    #     filehandler.safe_json_file(parent_pages, config.wiki_page_structure, config.wiki_page_structure_dir)
    # if len(wiki_exports) > 0:
    #     filehandler.safe_json_file(wiki_exports, config.wiki_unsorted_file_name, config.wiki_unsorted_dir)
    return wiki_exports





    # Extract the date suffixes from the JSON file names
    # wiki_date_suffix = datetime.strptime(os.path.basename(filehandler.find_latest_file(config.wiki_unsorted_dir))[-15:-5],'%Y-%m-%d')
    # jira_latest_file = filehandler.find_latest_file(config.jira_unsorted_dir)
    # if jira_latest_file:
    #     jira_date_suffix = datetime.strptime(os.path.basename(jira_latest_file)[-15:-5], '%Y-%m-%d')
    # else:
    #     jira_date_suffix = 0
    # latest_file = os.path.basename(latest_file)
    # wiki_date_suffix = os.path.splitext(wiki_crs["filename"])[0][-10:]
    # jira_date_suffix = os.path.splitext(jira_crs["filename"])[0][-10:]

    # Check if the wiki file is newer than the jira file
    # if wiki_date_suffix > jira_date_suffix:
    print("Wiki CR is newer than Jira file")
    # Iterate over each wiki CR and update corresponding JIRA CRs
    for wiki_item in wiki_exports:
        if wiki_item["projectKey"] == "PROJECT":
            # Find matching JIRA PROJECT CRs
            matching_jira_items = [j for j in jira_crs if
                                j["name"] == wiki_item["name"] and
                                j["projectKey"] == wiki_item["projectKey"]]
        elif wiki_item["projectKey"] == "GLOBAL":
            matching_jira_items = [j for j in jira_crs if
                                j["name"] == wiki_item["name"] and
                                j["templateScope"] == "GLOBAL"]
        else:
            matching_jira_items = []
        # matching_jira_items = [j for j in jira_crs if
        #                     j["name"] == wiki_item["name"] and
        #                     j["templateScope"] == wiki_item["templateScope"] and
        #                     j["projectKey"] == wiki_item["projectKey"]]
        # Update matching JIRA CRs with new templateText value
        for matching_jira_item in matching_jira_items:
            if matching_jira_item["templateText"] != wiki_item["templateText"]:
                matching_jira_item["templateText"] = wiki_item["templateText"]
        for jira_item in jira_crs:
            # jira_item.pop("serverId")
            # jira_item["scope"] = jira_item.pop("templateScope")
            # if "serverId" in jira_item.keys():
            #     if jira_item["serverId"] not in server_id_set:
            #         server_id_set.add(jira_item["serverId"])
            if jira_item["templateScope"] == "USER" and "scopeParam" in jira_item.keys():
                jira_item["ownerUserKey"] = jira_item.pop("scopeParam")
            elif jira_item["templateScope"] == "PROJEKT" and "scopeParam" in jira_item.keys():
                jira_item["projectKey"] = jira_item.pop("scopeParam")
            elif jira_item["templateScope"] == "GLOBAL" and "scopeParam" in jira_item.keys():
                jira_item.pop("scopeParam")
            if jira_item["templateScope"] == "PROJEKT":
                if jira_item["name"] == wiki_item["name"] and jira_item["projectKey"] == wiki_item["projectKey"]:
                    jira_item["templateText"] = wiki_item["templateText"]

        # If there are no matching JIRA CRs, add a new one
        if not matching_jira_items:
            if "serverId" not in wiki_item.keys():
                next_server_id = exporthandler.next_server_Id()
                # if next_server_id not in server_id_set:
                #     wiki_item["serverId"] = next_server_id
                # else:
                #     next_server_id = max(template_id_set) + 1
            
            if "chatbotAnswer" in wiki_item.keys():
                wiki_item.pop("chatbotAnswer")
            if "templateScope" not in wiki_item.keys():
                if "projectKey" in wiki_item.keys():
                    wiki_item["templateScope"] = "PROJECT"
                else:
                    wiki_item["templateScope"] = "GLOBAL"
            jira_crs.append(wiki_item)

    
        # Save the updated JIRA CRs to a new file
    jira_crs = jirahandler.digest_json_for_jira_import(jira_crs)
    filehandler.safe_json_file(jira_crs, 'updated-jira-cr-import', 'data/jira-imports/')
    # if len(wiki_crs) > len(jira_crs):
    #     # Save the updated JIRA CRs to a new file
    #     jira_crs = jirahandler.digest_json_for_jira_import(jira_crs)
    #     filehandler.safe_json_file(jira_crs, 'updated-jira-cr-import', 'data/jira-imports/')
    # else:
    #     wiki_crs = jirahandler.digest_json_for_jira_import(wiki_crs)
    #     filehandler.safe_json_file(wiki_crs, 'updated-jira-cr-import', 'data/jira-imports/')

    
    # with open('updated-jira-cr-import.json', 'w') as f:
    #     json.dump(jira_crs, f)
    # filehandler.json2csv(jira_crs)