import os

verify_ssl_requests = True

##### Exported Data Files Configuration #####
### File Names ###
jira_unsorted_file_name = "jira-cr-export"
jira_categorized_file_name = "jira-cr-categorized"
# jira_updated_file_name = "jira-cr-update"
wiki_unsorted_file_name = "wiki-cr-export"
wiki_page_structure = "wiki-page-structure"
wiki_categorized_file_name = "wiki-cr-categorized"
# updated_cr_file_name = "updated-canned-responses" #file for jira import
updated_cr_wiki2jira_file_name = "updated-cr-wiki2jira"
updated_cr_jira2wiki_file_name = "updated-cr-jira2wiki"
### Directory Paths ###
project_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
jira_unsorted_dir = os.path.join(project_base_dir, "data", "jira-exports", "unsorted-exports/")
# jira_categorized_dir = os.path.join(project_base_dir, "data", "jira-exports", "categorized-exports/")
jira_categorized_dir = os.path.join(project_base_dir, "data", "jira-exports", "categorized-exports/")
wiki_unsorted_dir = os.path.join(project_base_dir, "data", "wiki-exports", "unsorted-exports/")
wiki_page_structure_dir = os.path.join(project_base_dir, "data", "wiki-exports/")
wiki_categorized_dir = os.path.join(project_base_dir, "data", "wiki-exports", "categorized-exports/")
# updated_cr_dir = os.path.join(project_base_dir, "data", "updated-canned-responses/")
updated_cr_wiki2jira_dir = os.path.join(project_base_dir, "data", "updated-canned-responses", "wiki2jira/")
updated_cr_jira2wiki_dir = os.path.join(project_base_dir, "data", "updated-canned-responses", "jira2wiki/")



##### JIRA Configuration #####
# jira_host = "support-dev.wu.ac.at"
jira_host = "support.wu.ac.at"
if not jira_host.startswith("https://"):
    jira_host = "https://" + jira_host
if jira_host.endswith("/"):
    jira_host = jira_host[:-1]
if not jira_host.endswith("/"):
    # authentification
    # jira_login_url = jira_host + "/login.jsp"
    jira_auth_url = jira_host + "/rest/auth/session"
    # canned responses manage templates
    jira_cr_management_url = jira_host + "/rest/comment-templates/1.0/backup"
    jira_cr_export_url = jira_cr_management_url  + "/export"
    jira_cr_import_url = jira_cr_management_url + "/import"
    jira_cr_bulkdelete_url = jira_cr_management_url + "/delete"
    # canned responses manage single template
    jira_add_single_cr_url = jira_host + "/secure/add-template.jspa" # POST
    jira_edit_single_cr_url = jira_host + "/edit-template.jspa" # POST & params to identify correct template - see canned-responses-handler/data/.EXAMPLES/Single-CR-manipulation-support-dev.wu.ac.at.har
    # or another example: "https://support-dev.wu.ac.at/edit-template!default.jspa?templateType=GENERAL&templateId=365668&projectKey=&inline=true&decorator=dialog&_=1683834532841"
    jira_delete_single_cr_url = jira_host + "/rest/comment-templates/1.0/template" # DELETE with params ?templateType=GENERAL&templateId=365669&projectKey=  (projectKey is '' in GLOBAL)
    # or another example: "https://support-dev.wu.ac.at/rest/comment-templates/1.0/template?templateType=GENERAL&templateId=365669&projectKey="

# PROD
# jira_cr_export_url = "https://support.wu.ac.at/rest/comment-templates/1.0/backup/export"
# jira_host = "https://support.wu.ac.at/"



##### WIKI Configuration #####
wiki_base_url = "https://wiki.wu.ac.at/"
wiki_request_pause_time = 2
## Page configuration CR Export Table ##
# initial_parent_pageId = 271159296 # parent page id for CR-Export Collection in WIKI space ServiceDesk (spaceKey=SD)
initial_parent_pageId_table = 271174501 # table initial parent page id for CR-Export Collection in WIKI space ServiceDesk
initial_parent_pageId = 271175005 # v2 initial parent page
initial_spaceKey = "CR" # PROD only
# initial_parent_pageId = 271173641 # DEV only - parent page for DEV CR export
# initial_spaceKey = "~fscholz" # DEV only

wiki_cr_page_table_headers = ["Name of Canned Response in Jira ServiceDesk", "Canned Response Content", "Chatbot Answer - DE", "Chatbot Answer - EN", "projectKey", "templateId"]
## Json Export Configuration ##
wiki_cr_export_json_keys = ["name", "templateText", "chatbotAnswerDE", "chatbotAnswerEN", "projectKey", "templateId"]

