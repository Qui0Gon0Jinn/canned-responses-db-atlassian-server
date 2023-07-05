import json
import os
import re

import config
import filehandler
import jirahandler
import wikihandler


cat_templates = {}
transformed_cat_templates = {}
transformed_cat_templates["categorized-projects"] = cat_templates

def get_templateId(cr_item):
    if isinstance(cr_item, dict) and "serverId" in cr_item:
        templateId = cr_item["serverId"].split('_')
        templateId = int(templateId[-1])
        return templateId
    elif isinstance(cr_item, str):
        templateId = cr_item.split('_')
        templateId = int(templateId[-1])
        return templateId

def get_serverId_without_templateId():
    jira_cr = filehandler.load_latest_file(config.jira_unsorted_file_name)
    for cr in jira_cr[-1:]:
        # serverId aus dem letzten Eintrag
        server_only_Id = cr["serverId"].split("_")[0]
    return server_only_Id

def next_server_Id(filename=config.jira_unsorted_file_name, serverId_string=''):
    if len(serverId_string) > 0:
        index = serverId_string.rfind('_')
        if index != -1:
            serverId_only = serverId_string[:index]
            next_templateId = int(serverId_string[index+1:]) + 1
            next_serverId = str(serverId_only) + "_" + str(next_templateId)
            return next_serverId
    server_only_Id = ""
    max_templateId = 1
    unsorted_cr = filehandler.load_latest_file(filename)
    for cr in unsorted_cr:
        # serverId = cr["serverId"]
        if "serverId" in cr.keys():
            server_only_Id = cr["serverId"].split("_")[0]
            templateId = int(cr["serverId"].split("_")[1])
            if templateId >= max_templateId:
                max_templateId = templateId + 1
        elif "templateId" in cr.keys():
            if re.match("^[0-9]+$", str(cr["templateId"])):
                templateId = int(cr["templateId"])
                if templateId >= max_templateId:
                    max_templateId = templateId + 1                
    next_serverId = server_only_Id + "_" + str(max_templateId)
    return next_serverId

def remove_spaces_for_categories(string):
    pattern = r"\s*::\s*"
    match = re.search(pattern, string)
    if match:
        return re.sub(pattern, "::", string)
    else:
        return string

def build_cr_item(obj):
    obj["name"] = remove_spaces_for_categories(obj["name"])
    if "templateScope" in obj.keys():
        if obj["templateScope"] == "PROJECT":
            cr_key = obj["projectKey"]
            cr_item = obj
        elif obj["templateScope"] == "GLOBAL":
            cr_key = "GLOBAL"
            cr_item = obj
            cr_item.update({"projectKey": "GLOBAL"})
    else:            
        if obj["projectKey"] == "GLOBAL":
            cr_key = "GLOBAL"
            cr_item = obj
            cr_item.update({"projectKey": "GLOBAL"})
        else:
            cr_key = obj["projectKey"]
            cr_item = obj
    # cr_key = ""
    # cr_item = ""
    # if "templateScope" not in obj.keys():
    #     cr_item = {"scopeParameter": obj["projectKey"], "name": obj["name"],
    #                     "content": obj["templateText"], "favourite": ""}
    #     cr_key = obj["projectKey"]
    # else:
    #     if obj["templateScope"] == "PROJECT":
    #         cr_item = {"scopeParameter": obj["projectKey"], "name": obj["name"],
    #                         "content": obj["templateText"], "favourite": ""}
    #         cr_key = obj["projectKey"]
    #     elif obj["templateScope"] == "USER":
    #         cr_item = {"scopeParameter": obj["ownerUserKey"], "name": obj["name"],
    #                         "content": obj["templateText"], "favourite": ""}
    #         cr_key = obj["ownerUserKey"]
    #     elif obj["templateScope"] == "GLOBAL":
    #         cr_item = {"scopeParameter": obj["templateScope"], "name": obj["name"],
    #                         "content": obj["templateText"], "favourite": ""}
    #         cr_key = obj["name"]
    return cr_key, cr_item

def create_category_template(obj):
    cr_key, cr_item = build_cr_item(obj)
    category_template = {}
    categories = obj["name"].split("::")
    category_1 = categories[0].strip()
    category_2 = categories[1].strip()
    category_3 = None
    if len(categories) == 3:
        category_3 = categories[2].strip()
    if category_1 not in category_template:
        category_template[category_1] = {}
    if category_2 not in category_template[category_1]:
        category_template[category_1][category_2] = {}
    if cr_key not in cat_templates:
            cat_templates[cr_key] = {}
    if category_1 not in cat_templates[cr_key]:
        cat_templates[cr_key][category_1] = {}
    if category_3 is None:
        if category_2 not in category_template[category_1][category_2]:
            category_template[category_1][category_2] = []
        else:
            category_template[category_1]
        if category_2 not in cat_templates[cr_key][category_1]:
            cat_templates[cr_key][category_1][category_2] = {}
        else:
            cat_templates[cr_key][category_1][category_2] = cr_item
        category_template[category_1][category_2].append(cr_item)
    else:
        if category_2 not in cat_templates[cr_key][category_1]:
            cat_templates[cr_key][category_1][category_2] = {}
        if category_3 not in category_template[category_1][category_2]:
            category_template[category_1][category_2][category_3] = []
        if category_3 not in cat_templates[cr_key][category_1][category_2]:
            cat_templates[cr_key][category_1][category_2][category_3] = {}
        else:
            cat_templates[cr_key][category_1][category_2][category_3] = cr_item
        category_template[category_1][category_2][category_3].append(cr_item)
    return category_template

def categorize(obj):
    categories = obj["name"].split("::")
    for cat in categories:
        cat.strip()
    categories = obj["name"].split("::")
    cat_1 = categories[0].strip()
    cat_2 = categories[1].strip()
    cat_3 = None
    if len(categories) == 3:
        cat_3 = categories[2].strip()
    cr_key, cr_item = build_cr_item(obj)
    if len(categories) == 3:
        if cat_1 not in cat_templates[cr_key].keys():
            cat_templates[cr_key][cat_1] = {} 
        if cat_2 not in cat_templates[cr_key][cat_1].keys():
            cat_templates[cr_key][cat_1][cat_2] = {}
        if cat_3 not in cat_templates[cr_key][cat_1][cat_2].keys():
            cat_templates[cr_key][cat_1][cat_2][cat_3] = ()
        if len(cat_templates[cr_key][cat_1][cat_2][cat_3]) == 0:
            cat_templates[cr_key][cat_1][cat_2][cat_3] = cr_item
        else:
            print("Doubled CR with same 3rd category")
            print(cr_item["name"])
    elif len(categories) == 2:
        if cat_1 not in cat_templates[cr_key].keys():
            cat_templates[cr_key][cat_1] = {} 
        if cat_2 not in cat_templates[cr_key][cat_1].keys():
            cat_templates[cr_key][cat_1][cat_2] = {}
        if len(cat_templates[cr_key][cat_1][cat_2]) == 0:
            cat_templates[cr_key][cat_1][cat_2] = cr_item
        else:
            print("Doubled CR with same 2nd category")
            print(cr_item["name"])
    else:
        print("Canned Responses with 4 subcategorizations can not be processed at this moment.")
        raise IndexError

def format_exports(json_data, export_source="jira"):
    cr_dict = {}
    sub_projects = {}
    if export_source == "jira":
        for cr in json_data:
            if "templateId" not in cr.keys():
                cr["templateId"] = ""
            if "serverId" in cr.keys():
                cr["templateId"] = get_templateId(cr["serverId"])
            if cr["templateScope"] not in cr_dict and cr["templateScope"] != "GLOBAL":
                cr_dict.update({cr["templateScope"]: {}})
            
            if "::" in cr["name"] and cr["templateScope"] == "PROJECT":
                if cr["projectKey"] not in cat_templates.keys():
                    cat_templates[cr["projectKey"]] = {} 
                cat_cr = create_category_template(cr)
                sub_projects.update({cr["projectKey"]: cat_cr})
            elif "::" in cr["name"] and cr["templateScope"] == "GLOBAL":
                if "GLOBAL" not in cat_templates.keys():
                    cat_templates["GLOBAL"] = {} 
                cat_cr = create_category_template(cr)
                sub_projects.update({"GLOBAL": cat_cr})
            # elif "::" in cr["name"] and cr["templateScope"] == "USER":
            #     if cr["ownerUserKey"] not in cat_templates.keys():
            #         cat_templates[cr["ownerUserKey"]] = {}
            #     cat_cr = create_category_template(cr)
            #     sub_projects.update({cr["ownerUserKey"]: cat_cr})
            elif "::" not in cr["name"]:
                if cr["templateScope"] == "USER":
                    if cr["ownerUserKey"] not in cr_dict[cr["templateScope"]]:
                        cr_dict[cr["templateScope"]].update({cr["ownerUserKey"]:[]})
                    cr_item = {"name": cr["name"], "templateText": cr["templateText"], "chatbotAnswerDE": "", "chatbotAnswerEN": "", "projectKey": "USER", "templateId": get_templateId(cr["serverId"]), "pageId": False}
                    cr_dict[cr["templateScope"]][cr["ownerUserKey"]].append(cr_item)
                elif cr["templateScope"] == "PROJECT":
                    if cr["projectKey"] not in cr_dict[cr["templateScope"]]:
                        cr_dict[cr["templateScope"]].update({cr["projectKey"]:[]})
                    cr_item = {"name": cr["name"], "templateText": cr["templateText"], "chatbotAnswerDE": "", "chatbotAnswerEN": "", "projectKey": cr["projectKey"], "templateId": get_templateId(cr["serverId"]), "pageId": False}
                    # cr_item = {"scopeParameter": cr["projectKey"], "name": cr["name"],
                    #         "content": cr["templateText"], "favourite": ""}
                    cr_dict[cr["templateScope"]][cr["projectKey"]].append(cr_item)        
                else:
                    if "GLOBAL" not in cr_dict.keys():
                        cr_dict.update({"GLOBAL":[]})
                    if "PROJECT" not in cr_dict.keys():
                        cr_dict.update({"PROJECT": {}})
                    if cr["templateScope"] not in cr_dict["PROJECT"] and cr["templateScope"] != "GLOBAL":
                        cr_dict.update({"PROJECT": {cr["templateScope"]:[]}})
                    cr_item = {"name": cr["name"], "templateText": cr["templateText"], "chatbotAnswerDE": "", "chatbotAnswerEN": "", "projectKey": cr["templateScope"], "templateId": get_templateId(cr["serverId"]), "pageId": False}
                    # cr_item = {"scopeParameter": cr["templateScope"], "name": cr["name"],
                    #         "content": cr["templateText"], "favourite": ""}
                    if cr["templateScope"] == "GLOBAL":
                        cr_dict["GLOBAL"].append(cr_item)
                    else:
                        cr_dict["PROJECT"][cr["templateScope"]].append(cr_item)
    elif export_source == "wiki":
        if "GLOBAL" not in cat_templates.keys():
            cat_templates["GLOBAL"] = {}
        if "GLOBAL" not in cr_dict.keys():
            cr_dict["GLOBAL"] = []
        if "PROJECT" not in cr_dict.keys():
            cr_dict["PROJECT"] = {}
        for cr in json_data:
            if "PROJECT" not in cat_templates.keys():
                cat_templates[cr["projectKey"]] = {}
            # if "serverId" in cr.keys():
                # cr.pop("serverId")
            if "::" in cr["name"] and "projectKey" in cr.keys():
                if cr["projectKey"] == "GLOBAL":
                    cat_cr = create_category_template(cr)
                    sub_projects.update({"GLOBAL": cat_cr})
                else:
                    cat_cr = create_category_template(cr)
                    sub_projects.update({cr["projectKey"]: cat_cr})
            elif "::" not in cr["name"]:
                if cr["projectKey"] == "GLOBAL":
                    cr_item = {"name": cr["name"], "templateText": cr["templateText"], "chatbotAnswerDE": "", "chatbotAnswerEN": "", "projectKey": "USER", "templateId": cr["templateId"], "pageId": cr["pageId"]}
                    cr_dict["GLOBAL"].append(cr_item)
                else:
                    if cr["projectKey"] not in cr_dict["PROJECT"]:
                        cr_dict["PROJECT"][cr["projectKey"]] = []
                    cr_item = {"name": cr["name"], "templateText": cr["templateText"], "chatbotAnswerDE": "", "chatbotAnswerEN": "", "projectKey": "USER", "templateId": cr["templateId"], "pageId": cr["pageId"]}
                    cr_dict["PROJECT"][cr["projectKey"]].append(cr_item)
                    
    for cr in json_data:
        if "templateScope" in cr.keys():
            if "::" in cr["name"] and cr["templateScope"] == "PROJECT":
                categorize(cr)
            elif "::" in cr["name"] and cr["templateScope"] == "GLOBAL":
                categorize(cr)
        elif export_source == "wiki":
            if "::" in cr["name"]:
                categorize(cr)
    cr_dict.update(transformed_cat_templates)
    return cr_dict

# def uniq_sort_list(unsorted_list: list[dict], sort_key: str = "serverId", regard_order: bool = True) -> list[dict]:
def uniq_sort_list(unsorted_list, sort_key="serverId", regard_order=True, reverse=False):
    if len(unsorted_list):
        # remove duplicates
        if regard_order:
            # unsorted_list = [x for i, x in enumerate(unsorted_list) if x not in unsorted_list[:i]]
            unsorted_list = [dict(t) for t in (tuple(d.items()) for d in unsorted_list)]
        else:
            unsorted_list = list(set(unsorted_list)) #remove duplicates without regard to the order
        # if sort_key == "serverId":
        #     unsorted_list = sorted(unsorted_list, key=lambda x: x[sort_key])
        if isinstance(unsorted_list[0], dict):
            if sort_key in unsorted_list[0].keys():
                sorted_list = sorted(unsorted_list, key=lambda x: x[sort_key])
            elif sort_key not in unsorted_list[0].keys():
                print("Sorting Key ", sort_key, " not found in given list... returning list with removed duplicates, sorted by the contained values")
                sorted_list = sorted(unsorted_list, key=lambda x: list(x.values()))
        elif isinstance(unsorted_list, list):
            sorted_list = sorted(unsorted_list)
        
        return sorted_list
    else:
        print("Empty list, no need for removing clones and nothing to sort.")
        return unsorted_list
    

def add_templateId():
    commands_get_templateId = ["", None, "get_templateID", "get templateID", "get_templateId", "get templateId", "<br />", "TODO: get templateID"]
    jira_cr_list = filehandler.load_latest_file(config.jira_unsorted_file_name, config.jira_unsorted_dir)
    wiki_cr_list = filehandler.load_latest_file(config.wiki_unsorted_file_name, config.wiki_unsorted_dir)
    for wiki_cr in wiki_cr_list:
        for jira_cr in jira_cr_list:
            if wiki_cr["templateId"] in commands_get_templateId:
                if wiki_cr["name"] == jira_cr["name"] and wiki_cr["projectKey"] == "GLOBAL" and jira_cr["templateScope"] == "GLOBAL":
                    wiki_cr["templateId"] = get_templateId(jira_cr["serverId"])
                elif wiki_cr["name"] == jira_cr["name"] and wiki_cr["projectKey"] == jira_cr["projectKey"]:
                    wiki_cr["templateId"] = get_templateId(jira_cr["serverId"])
                else:
                    wiki_cr["templateId"] = "get_templateId"
    filehandler.safe_json_file(wiki_cr_list, config.wiki_unsorted_file_name, config.wiki_unsorted_dir)
    return wiki_cr_list

def compare_cr_exports():
    # Sync Fall 0: add missing templateIds to wiki_cr
    # Sync Fall 1: (daily + manual) neue Wiki Seite --> neue Jira CR
    # Sync Fall 2: (daily) neue Jira CR --> neue Wiki Seite
    # Sync Fall 3: (daily + manual) updated content on Wiki page --> update single Jira CR by template_id
    # Sync Fall 4: (daily) Wiki page removed --> delete single CR or all project CRs in Jira
    # Sync Fall 5: (manual) updated Jira CR content --> update single Wiki page for single CR
    # Sync Fall 6: (manual) updated Jira CR content --> update project Wiki page for all CRs of a jira project

    jira_cr_list = filehandler.load_latest_file(config.jira_unsorted_file_name, config.jira_unsorted_dir)
    wiki_cr_list = filehandler.load_latest_file(config.wiki_unsorted_file_name, config.wiki_unsorted_dir)
    wiki_max_templateId = get_templateId(next_server_Id(filename=config.wiki_unsorted_file_name))
    jira_max_templateId = get_templateId(next_server_Id(filename=config.jira_unsorted_file_name))
    
    update_cr_wiki2jira = list()
    update_cr_jira2wiki = list()
    updated_wiki_page = False
    # Sync Fall 0: add missing templateIds to wiki_cr
    # add missing templateIds to wiki_cr_list
    for wiki_cr in wiki_cr_list:
        if not re.match("^[0-9]+$", str(wiki_cr["templateId"])):
            updated_wiki_page = True
            wiki_cr["templateId"] = max(wiki_max_templateId, jira_max_templateId) + 1
            wiki_max_templateId = wiki_cr["templateId"]
            update_cr_jira2wiki.append(wiki_cr)
            wikihandler.update_page(wiki_cr, spaceKey=config.initial_spaceKey, pageId=wiki_cr["pageId"])
    # filehandler.safe_json_file(update_cr_jira2wiki, config.updated_cr_jira2wiki_file_name)
    if updated_wiki_page:
        wiki_cr_list = wikihandler.export_wiki_cr_pages(spaceKey=config.initial_spaceKey)
        wiki_max_templateId = get_templateId(next_server_Id(filename=config.wiki_unsorted_file_name))
    wiki_templateId_set = set()
    for wiki_cr in wiki_cr_list:
        wiki_templateId_set.add(wiki_cr["templateId"])
    jira_templateId_set = set()
    for jira_cr in jira_cr_list:
        if "templateId" in jira_cr.keys():
            jira_templateId_set.add(jira_cr["templateId"])
        elif "serverId" in jira_cr.keys():
            current_templateId = get_templateId(jira_cr["serverId"])
            jira_templateId_set.add(current_templateId)

    # Sync Fall 1
    if wiki_max_templateId > jira_max_templateId:
        new_wiki_templateIds = wiki_templateId_set.difference(jira_templateId_set)
        new_templateId = wiki_max_templateId + 1
        for wiki_cr in wiki_cr_list:
            if wiki_cr["templateId"] in new_wiki_templateIds:
                if not re.match("^[0-9]+$", str(wiki_cr["templateId"])):
                    while new_templateId in (wiki_templateId_set or jira_templateId_set):
                        new_templateId += 1
                    wiki_cr["templateId"] = new_templateId
                    new_templateId += 1
                new_cr_obj = digest_exported_cr_pages(mode="wiki2jira-partial-sync", cr_obj=wiki_cr)
                update_cr_wiki2jira.append(new_cr_obj)
        filehandler.safe_json_file(update_cr_wiki2jira, config.updated_cr_wiki2jira_file_name)
        filehandler.safe_json_file(wiki_cr_list, config.wiki_unsorted_file_name)
        filehandler.safe_json_file(update_cr_jira2wiki, config.updated_cr_jira2wiki_file_name)
    
    # Sync Fall 2
    # elif wiki_max_templateId < jira_max_templateId:
    #     new_jira_templateIds = jira_templateId_set.difference(wiki_templateId_set)
    #     new_templateId = jira_max_templateId + 1
    #     for jira_cr in jira_cr_list:
    #         if jira_cr["templateId"] in new_jira_templateIds:
    #             if not re.match("^[0-9]+$", str(jira_cr["templateId"])):
    #                 while new_templateId in (wiki_templateId_set or jira_templateId_set):
    #                     new_templateId += 1
    #                 jira_cr["templateId"] = new_templateId
    #             new_cr_obj = digest_exported_cr_pages(mode="wiki2jira-partial-sync", cr_obj=wiki_cr)
    #             update_cr_jira2wiki.append(new_cr_obj)
    #     filehandler.safe_json_file(update_cr_wiki2jira, config.updated_cr_wiki2jira_file_name)
    #     # filehandler.safe_json_file(wiki_cr_list, config.wiki_unsorted_file_name)
    #     filehandler.safe_json_file(update_cr_jira2wiki, config.updated_cr_jira2wiki_file_name)
    
    # Sync Fall 3
    # elif wiki_max_templateId == jira_max_templateId:
    #     for wiki_cr in wiki_cr_list:
    #         for jira_cr in jira_cr_list:
    #             server_only_Id = jira_cr["serverId"].split("_")[0]
    #             if jira_cr["templateScope"] == "PROJECT":
    #                 if wiki_cr["name"] == jira_cr["name"] and wiki_cr["projectKey"] == jira_cr["projectKey"] and wiki_cr["templateText"] == jira_cr["templateText"]:
    #                     wiki_cr["serverId"] = jira_cr["serverId"]
    #                 elif wiki_cr["name"] == jira_cr["name"] and wiki_cr["projectKey"] == jira_cr["projectKey"]:
    #                     wiki_cr["serverId"] = jira_cr["serverId"]
    #                     jira_cr["templateText"] = wiki_cr["templateText"]
    #                 elif "templateId" in wiki_cr.keys():
    #                     wiki_cr["serverId"] = server_only_Id + "_" + str(wiki_cr["templateId"])
    #                 else:
    #                     wiki_cr["serverId"] = serverId
    #             elif jira_cr["templateScope"] == "GLOBAL":
    #                 if wiki_cr["name"] == jira_cr["name"]:
    #                     wiki_cr["serverId"] = jira_cr["serverId"]
    #                     if wiki_cr["templateText"] != jira_cr["templateText"]:
    #                         jira_cr["templateText"] = wiki_cr["templateText"]
    #                 elif "templateId" in wiki_cr.keys():
    #                     wiki_cr["serverId"] = server_only_Id + "_" + str(wiki_cr["templateId"])
    #                 else:
    #                     wiki_cr["serverId"] = serverId
    #             if "_" in serverId:
    #                 serverId = next_server_Id(serverId_string=serverId)
    else:
        for wiki_cr in wiki_cr_list:
            for jira_cr in jira_cr_list:
                server_only_Id = jira_cr["serverId"].split("_")[0]
                if jira_cr["templateScope"] == "PROJECT":
                    if wiki_cr["name"] == jira_cr["name"] and wiki_cr["projectKey"] == jira_cr["projectKey"] and wiki_cr["templateText"] == jira_cr["templateText"]:
                        wiki_cr["serverId"] = jira_cr["serverId"]
                    elif wiki_cr["name"] == jira_cr["name"] and wiki_cr["projectKey"] == jira_cr["projectKey"]:
                        wiki_cr["serverId"] = jira_cr["serverId"]
                        jira_cr["templateText"] = wiki_cr["templateText"]
                    elif "templateId" in wiki_cr.keys():
                        wiki_cr["serverId"] = server_only_Id + "_" + str(wiki_cr["templateId"])
                    else:
                        wiki_cr["serverId"] = serverId
                elif jira_cr["templateScope"] == "GLOBAL":
                    if wiki_cr["name"] == jira_cr["name"]:
                        wiki_cr["serverId"] = jira_cr["serverId"]
                        if wiki_cr["templateText"] != jira_cr["templateText"]:
                            jira_cr["templateText"] = wiki_cr["templateText"]
                    elif "templateId" in wiki_cr.keys():
                        wiki_cr["serverId"] = server_only_Id + "_" + str(wiki_cr["templateId"])
                    else:
                        wiki_cr["serverId"] = serverId
                if "_" in serverId:
                    serverId = next_server_Id(serverId_string=serverId)
            if "chatbotAnswerDE" not in wiki_cr.keys():
                wiki_cr["chatbotAnswerDE"] = ""
            if "chatbotAnswerEN" not in wiki_cr.keys():
                wiki_cr["chatbotAnswerEN"] = ""

    # if (len(jira_cr_list) and len(wiki_cr_list)) > 0: 
    #     serverId = next_server_Id()
    #     for wiki_cr in wiki_cr_list:
    #         for jira_cr in jira_cr_list:
    #             server_only_Id = jira_cr["serverId"].split("_")[0]
    #             if jira_cr["templateScope"] == "PROJECT":
    #                 if wiki_cr["name"] == jira_cr["name"] and wiki_cr["projectKey"] == jira_cr["projectKey"] and wiki_cr["templateText"] == jira_cr["templateText"]:
    #                     wiki_cr["serverId"] = jira_cr["serverId"]
    #                 elif wiki_cr["name"] == jira_cr["name"] and wiki_cr["projectKey"] == jira_cr["projectKey"]:
    #                     wiki_cr["serverId"] = jira_cr["serverId"]
    #                     jira_cr["templateText"] = wiki_cr["templateText"]
    #                 elif "templateId" in wiki_cr.keys():
    #                     wiki_cr["serverId"] = server_only_Id + "_" + str(wiki_cr["templateId"])
    #                 else:
    #                     wiki_cr["serverId"] = serverId
    #             elif jira_cr["templateScope"] == "GLOBAL":
    #                 if wiki_cr["name"] == jira_cr["name"]:
    #                     wiki_cr["serverId"] = jira_cr["serverId"]
    #                     if wiki_cr["templateText"] != jira_cr["templateText"]:
    #                         jira_cr["templateText"] = wiki_cr["templateText"]
    #                 elif "templateId" in wiki_cr.keys():
    #                     wiki_cr["serverId"] = server_only_Id + "_" + str(wiki_cr["templateId"])
    #                 else:
    #                     wiki_cr["serverId"] = serverId
    #             if "_" in serverId:
    #                 serverId = next_server_Id(serverId_string=serverId)
    #         if "chatbotAnswerDE" not in wiki_cr.keys():
    #             wiki_cr["chatbotAnswerDE"] = ""
    #         if "chatbotAnswerEN" not in wiki_cr.keys():
    #             wiki_cr["chatbotAnswerEN"] = ""
            
    # jira_cr_list = uniq_sort_list(jira_cr_list)
    # wiki_cr_list = uniq_sort_list(wiki_cr_list)
    # jira_cr_list = [x for i, x in enumerate(jira_cr_list) if x not in jira_cr_list[:i]]
    # wiki_cr_list = [y for j, y in enumerate(wiki_cr_list) if y not in wiki_cr_list[:j]]
    # wiki_exports = sorted(wiki_exports, key=lambda x: x["serverId"])
    # filehandler.safe_json_file(jira_cr_list, config.jira, config.jira_unsorted_dir)
    # filehandler.safe_json_file(wiki_cr_list, config.wiki_unsorted_file_name, config.wiki_unsorted_dir)
    
    # filehandler.safe_json_file(wiki_cr_list, config.wiki_unsorted_file_name, config.wiki_unsorted_dir)



def digest_exported_cr_pages(mode=None, cr_obj=None):
    if mode is None:
        wiki_crs = filehandler.load_latest_file(config.wiki_unsorted_file_name, config.wiki_unsorted_dir)
        jira_crs = filehandler.load_latest_file(config.jira_unsorted_file_name, config.jira_unsorted_dir)
        # jira_crs = filehandler.load_latest_file(config.updated_cr_file_name, config.updated_cr_dir)
        if jira_crs == False:
            jira_crs = filehandler.load_latest_file(config.jira_unsorted_file_name, config.jira_unsorted_dir)
        elif isinstance(jira_crs, dict):
            jira_crs = sorted(jira_crs, key=lambda x: x['serverId'])
        server_id_set = set()
        template_id_set = set()
        for jira_item in jira_crs:
            if "serverId" in jira_item.keys():
                item_server_id = jira_item["serverId"]
                server_id_set.add(item_server_id)
                template_id_set.add(int(get_templateId(item_server_id)))
    elif mode == "wiki2jira-partial-sync":
        if "templateId" in cr_obj.keys():
            serverId = get_serverId_without_templateId() + "_" + cr_obj["templateId"]
        if cr_obj["projectKey"] == "GLOBAL":
            new_cr_obj = {"serverId": serverId, "name": cr_obj["name"], "templateScope": "GLOBAL", "templateText": cr_obj["templateText"]}
            return new_cr_obj
        else:
            new_cr_obj = {"serverId": serverId, "name": cr_obj["name"], "templateScope": "PROJECT", "templateText": cr_obj["templateText"], "projectKey": cr_obj["projectKey"]}
            return new_cr_obj
    elif mode == "wiki2jira-complete-sync":
        new_crs = filehandler.load_latest_file(config.wiki_unsorted_file_name, config.wiki_unsorted_dir)
        cr_formatted_for_jira_import = []
        for cr in new_crs:
             # cr.pop("templateId")
             # cr.pop("chatbotAnswerDE")
             # cr.pop("chatbotAnswerEN")
            if "templateScope" in cr.keys():
                if cr["templateScope"] == "PROJECT":
                    new_cr_formatted = {
                        "serverId":cr["serverId"],
                        "name":cr["name"],
                        "templateScope":cr["templateScope"],
                        "templateText":cr["templateText"],
                        "projectKey":cr["projectKey"]
                    }
                elif cr["templateScope"] == "USER":
                    new_cr_formatted = {
                        "serverId":cr["serverId"],
                        "name":cr["name"],
                        "ownerUserKey":cr["ownerUserKey"],
                        "templateScope":cr["templateScope"],
                        "templateText":cr["templateText"]
                    }
            if cr["projectKey"] == "GLOBAL":
                new_cr_formatted = {
                    "serverId":cr["serverId"],
                    "name":cr["name"],
                    "templateScope":"GLOBAL",
                    "templateText":cr["templateText"]
                }
            else:
                new_cr_formatted = {
                        "serverId":cr["serverId"],
                        "name":cr["name"],
                        "templateScope":"PROJECT",
                        "templateText":cr["templateText"],
                        "projectKey":cr["projectKey"]
                }
            cr_formatted_for_jira_import.append(new_cr_formatted)
            
             
        
        filehandler.safe_json_file(cr_formatted_for_jira_import, config.updated_cr_file_name, config.updated_cr_dir)