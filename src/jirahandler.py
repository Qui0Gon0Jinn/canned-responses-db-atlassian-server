from typing import List, Set, Dict, Any, Union
from datetime import datetime
import time
import requests
import os
from ssl import SSLCertVerificationError, SSLError, OPENSSL_VERSION
import urllib3
import signal
# from inputimeout import inputimeout, TimeoutOccurred

import config
import exporthandler
import wikihandler
import filehandler
import userhandler
from config import jira_host as base_url
from config import verify_ssl_requests
verify_ssl = verify_ssl_requests
print("verify_ssl_requests: %s" % verify_ssl)

def add_timestamp(json_data):
    timestamp = datetime.now().isoformat()
    for obj in json_data:
        obj["last_checked"] = timestamp
    return json_data

def validate_request(session: requests.Session, response: requests.Response) -> bool:
    status = response.status_code
    if status in [200, 204]:
        print("Request successful with status: ", status)
        return session, response
    elif status == 404:
        print("Target not found, Error code: ", status)
    elif status == 401:
        print("Fobidden, login first...")
    elif status == 415:
        print("Wrong media type, Server error code: ", status)
    elif status == 500:
        print("Internal Server Error, Server error code: ", status)
    else:
        print("Unknown error with response: ", response)
    return False

def check_login_status(session: requests.Session, headers: Dict = None) -> bool:
    url = config.jira_auth_url
    if headers is None:
        jira_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "username": os.getenv('JIRA_USER'),
        "Authorization": "Bearer " + os.getenv("JIRA_PAT")
        }
    response = session.get(url=url, headers=jira_headers, verify=verify_ssl)
    return validate_request(session, response)

def login_request(session: requests.Session) -> Any:
    url = config.jira_auth_url
    auth_payload = {
        "username": os.getenv('JIRA_USER'),
        "password": os.getenv('JIRA_PAT')
    }
    auth_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    response = session.post(url=url, data=auth_payload, headers=auth_headers, verify=verify_ssl)
    return validate_request(session, response)

def logout_request(session: requests.Session, headers: Dict = None) -> bool:
    url = config.jira_auth_url
    response = session.delete(url=url, headers=headers, verify=verify_ssl)
    if not validate_request(session, response):
        print("Error while logging out!")
    elif response.status == 204:
        print("Logout from JIRA successfull!")
    # return validate_request(session, response)
    
def jira_export_request(session: requests.Session, headers: Dict = None) -> Any:
    url = config.jira_cr_export_url
    if headers is None:
        headers = {
            "username": os.getenv('JIRA_USER'),
            "password": os.getenv('JIRA_PAT')
        }
    response = session.get(url=url, headers=headers, verify=verify_ssl)
    return validate_request(session, response)

def jira_import_request(session: requests.Session, headers: Dict = None, payload: Dict = None) -> Any:
    url = config.jira_cr_import_url
    if headers is None:
        headers = {
            "username": os.getenv('JIRA_USER'),
            "password": os.getenv('JIRA_PAT')
        }
    if payload is None:
        print("No payload for jira import request!")
    response = session.post(url=url, headers=headers, json=payload, verify=verify_ssl)
    status = response.status_code
    if status == (200 or 204):
        print("Upload successful")
        return {"status": status, "result": "Logged out successfully"}
    elif status == 415:
        print("Error from JIRA: Wrong media type")
        raise TypeError("Wrong media type")
    elif status == 500:
        print("Server error from JIRA, ErrorCode: ",status)
        raise ConnectionAbortedError
    return validate_request(session, response)
    

def delete_single_cr(session: requests.Session, headers: Dict = None, templateId=None):
    pass

def delete_all_cr(session: requests.Session, headers: Dict = None):
    url = config.jira_cr_bulkdelete_url
    pass

def add_single_cr(session: requests.Session, headers: Dict = None, params=None, payload=None):
    pass

def edit_single_cr(session: requests.Session, headers: Dict = None):
    pass


def jira_admin_request(sync_direction="jira_export"):
    global verify_ssl
    jira_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "username": os.getenv('JIRA_USER'),
        "Authorization": "Bearer " + os.getenv("JIRA_PAT")
    }
    if sync_direction == "jira_export":
        url = config.jira_cr_export_url
    elif sync_direction == "jira_import":
        url = config.jira_cr_import_url
        if os.path.exists(config.updated_cr_wiki2jira_dir + config.updated_cr_wiki2jira_file_name + datetime.datetime.now().strftime('-%Y-%m-%d')+'.json'):
            cr_payload = filehandler.open_json_file(config.updated_cr_wiki2jira_file_name, path_to_file=config.updated_cr_wiki2jira_dir)
        else:
            exporthandler.digest_exported_cr_pages()
            cr_payload = filehandler.open_json_file(config.updated_cr_wiki2jira_file_name, path_to_file=config.updated_cr_wiki2jira_dir)
        cr_payload = digest_json_for_jira_import(cr_payload)
        items_per_request = 100
        list_of_chunks = list()
        if len(cr_payload) > items_per_request:
            list_of_chunks = [cr_payload[i:i+items_per_request] for i in range(0, len(cr_payload), items_per_request)]
    elif sync_direction == "delete_all":
        pass
    else:
        raise ValueError("Invalid sync_direction, expected 'jira_export' or 'jira_import'")
    with requests.Session() as session:
        try:
            # response = session.get(url=auth_url, headers=jira_headers, verify=verify_ssl)
            session, response = check_login_status(session)
            status = response.status_code
        except requests.exceptions.SSLError:
            verify_ssl = ask_user_verify_SSL()
            # response = session.get(url=auth_url, headers=jira_headers, verify=verify_ssl)
            session, response = check_login_status(session)
            status = response.status_code
            print(status)
        if status != (200 or 204):
            print("Need to login to JIRA first")
            # response = session.post(url=auth_url, data=auth_payload, headers=jira_headers, verify=verify_ssl)
            session, response = login_request(session)
            jira_headers.update({"Cookie": digest_session_cookie(session)})

        if sync_direction == "jira_export":
            # response = session.get(url=export_url, headers=jira_headers, verify=verify_ssl)
            # session.delete(auth_url, headers=jira_headers, verify=verify_ssl)
            session, response = jira_export_request(session, jira_headers)
            json_export = response.json()
            json_export = add_timestamp(json_export)
            # TODO: Überprüfe Kodierung der Sonderzeichen (utf-8) von json_export
            logout_request(session, jira_headers)
            return json_export
            
        elif sync_direction == "jira_import":
            if len(cr_payload) <= items_per_request:
                payload = cr_payload
                # Send the request to import the json file
                # response = session.post(url=import_url, headers=jira_headers, json=payload, verify=verify_ssl)
                session, response = jira_import_request(session, jira_headers, payload)
                status = response.status_code
                print(response.status_code)
                if status == (200 or 204):
                    # session.delete(auth_url, headers=jira_headers, verify=verify_ssl)
                    logout_request(session, jira_headers)
                    return {"status": status, "result": "Logged out successfully"}
                
            elif len(cr_payload) > items_per_request:
                re_run_post_request_chunks = list()
                try:
                    request_sleep = 60 # 20 seconds sleep between requests
                    for cr_payload_chunked in list_of_chunks:
                        payload = cr_payload_chunked
                        try:
                            # response = session.post(url=import_url, headers=jira_headers, json=payload, verify=verify_ssl)
                            session, response = jira_import_request(session, jira_headers, payload)
                        except Exception as error:
                            print("Upload failed at payload_chunk ",list_of_chunks.index(cr_payload))
                            print("Saving CR import chunk for re-run after 2 minutes sleep.")
                            print(f"Upload failed with Error: {error}")                       
                            time.sleep(120)
                        status = response.status_code
                        print(response.status_code)
                        if status in [200, 204]:
                            print(list_of_chunks.index(cr_payload_chunked)+1,"/",len(list_of_chunks)," Upload successful")
                            time.sleep(request_sleep)
                        elif status == 415:
                            print("Error from JIRA: Wrong media type, saving chunk for re-run")
                            re_run_post_request_chunks.append(cr_payload_chunked)
                            # raise TypeError("Wrong media type")
                            print("Upload failed at payload_chunk ",list_of_chunks.index(cr_payload))
                            print("Saving CR import chunk for re-run after 3 minutes sleep.")
                            print("Next chunk post request in 1 minute.")
                            time.sleep(60)
                        elif status == 500:
                            print("Server error from JIRA, ErrorCode: ",status)
                            print(response.text)
                            re_run_post_request_chunks.append(cr_payload_chunked)
                            # raise ConnectionAbortedError
                            print("Upload failed at payload_chunk ",list_of_chunks.index(cr_payload))
                            print("Saving CR import chunk for re-run after 3 minutes sleep.")
                            print("Next chunk post request in 1 minute.")
                            time.sleep(60)
                except:
                    print("Error from Server, Error: ",status)
                    print("waiting for 3 minutes...")
                    time.sleep(180)
                    for cr_payload_chunked in re_run_post_request_chunks:
                        payload = cr_payload_chunked
                        # response = session.post(url=import_url, headers=jira_headers, json=payload, verify=verify_ssl)
                        session, response = jira_import_request(session, jira_headers, payload)
                        status = response.status_code
                        print(response.status_code)
                        if status in [200, 204]:
                            print(list_of_chunks.index(cr_payload_chunked)+1,"/",len(list_of_chunks)," Upload successful")
                            time.sleep(request_sleep)
                        elif status == 415:
                            print("Error from JIRA: Wrong media type, failed 2nd try, no next try in this run")
                            re_run_post_request_chunks.append(cr_payload_chunked)
                            print("Upload failed at payload_chunk ",list_of_chunks.index(cr_payload))
                            print("Next chunk post request in 1 minute.")
                            time.sleep(60)
                        elif status == 500:
                            print("Server error from JIRA, ErrorCode: ",status)
                            print(response.text)
                            re_run_post_request_chunks.append(cr_payload_chunked)
                            print("Upload failed at 2nd run, no next try, payload_chunk ",list_of_chunks.index(cr_payload))
                            print("Next chunk post request in 1 minute.")
                            time.sleep(60)
                if status == (200 or 204):
                    print("All Uploads successful, logging out...")
                    # response = session.delete(auth_url, headers=jira_headers, verify=verify_ssl)
                    session, response = logout_request(session, jira_headers)
                else:
                    print("Unknown Error importing data from JIRA")
                    logout_request(session, jira_headers)
                    # raise ConnectionError("Error importing data from JIRA")

           
def get_cr():
    jira_exports = jira_admin_request(sync_direction="jira_export")
    jira_exports = [dict(t) for t in (tuple(d.items()) for d in jira_exports)]
    jira_exports = sorted(jira_exports, key=lambda x: x["serverId"])
    # if len(request_result) > 0:
        # filehandler.safe_json_file(request_result,"unsorted-cr-export", config.jira_unsorted_dir)
    return jira_exports

def ask_user_verify_SSL(default=config.verify_ssl_requests, timeout=10):
    global verify_ssl
    user_input = userhandler.input_timeout("The SSL certificate could not be authenticated. Do you want to try with http:// instead? [Y/n]: ", default, timeout)
    print("requesting with http://", user_input)
    if user_input:
        verify_ssl = False
        config.verify_ssl_requests = False
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    else:
        verify_ssl = True
        config.verify_ssl_requests = True
        print("No request without SSLError possible. Stopping script...")
        quit()
    return verify_ssl



def digest_session_cookie(session):
    key = list(session.cookies.get_dict().keys())[0]
    value = session.cookies.get_dict()[key]
    cookie_value = key + "=" + value
    return cookie_value



def digest_json_for_jira_import(json_data):
    for cr in json_data:
        if "serverId" not in cr.keys():
            cr["serverId"] = exporthandler.next_server_Id()
        # for key, value in list(cr.items()):
        #     if key == "serverId":
        #         cr.pop(key)
        #     # elif key == "ownerUserKey" or key == "projectKey":
        #     #     cr["scopeParam"] = cr.pop(key)
        #     # elif key == "templateScope":
        #     #     cr["scope"] = cr.pop(key)
        #     elif key == "name":
        #         continue
    return json_data



def wiki_cr_to_jira():
    jira_admin_request(sync_direction="jira_import")

def compare_json_objects(obj1, obj2):
    for key, value in obj1.items():
        if key != "serverId" and key != "last_checked":
            if key not in obj2 or obj2[key] != value:
                return True
    return False

def compare_json_files(file1, file2):
    json_data1 = filehandler.open_json_file(file1)
    json_data2 = filehandler.open_json_file(file2)
    
    new_json_data = []
    
    for obj1 in json_data1:
        match_found = False
        for obj2 in json_data2:
            if obj1["serverId"] == obj2["serverId"]:
                match_found = True
                if compare_json_objects(obj1, obj2):
                    obj1["last_checked"] = datetime.datetime.now().isoformat()
                    if "last_change" not in obj1:
                        obj1["last_change"] = obj1["last_checked"]
                elif "last_change" in obj2:
                    obj1["last_change"] = obj2["last_change"]
                break
        if not match_found:
            obj1["last_checked"] = datetime.datetime.now().isoformat()
            if "last_change" not in obj1:
                obj1["last_change"] = obj1["last_checked"]
        new_json_data.append(obj1)
    
    filehandler.safe_json_file(new_json_data, "merged_jira_export.json", "jira-export")