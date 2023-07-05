import os
from datetime import datetime
import sys
sys.path.append('./src')
sys.path.append('./src/secrets')
import credentials    # Skript zum Verwalten von Anmeldeinformationen und API-Schlüsseln
import config
import userhandler
import exporthandler  # Skript zum Verarbeiten und Formatieren der Canned Responses
import filehandler    # Skript zum Laden und Speichern von Dateien
import jirahandler  # Skript zum Verwalten von Jira ServiceDesk-Operationen
import wikihandler    # Skript zum Verwalten von Confluence (Wiki)-Operationen
import timemanager as timeManager
import dbmanager as dbManager

if __name__ == "__main__":
    now = datetime.now()
    suffix = now.strftime('-%Y-%m-%d')

    # filehandler.json_repair_DEV()

    fresh_download = userhandler.input_timeout("Start fresh download of Canned Responses from WU ServiceDesk (JIRA)? [Y/N]")


    ## JIRA CR Download ##
    if not fresh_download and os.path.exists(config.jira_unsorted_dir):
        print("Canned Response already downloaded today, skipping download.")
        jira_cr_result = filehandler.load_latest_file(config.jira_unsorted_file_name)
    else:
        fresh_download = True
        # Herunterladen der Canned Responses aus Jira ServiceDesk
        print("Canned Responses downloading from Jira Servicedesk, please wait…")
        jira_cr_result = jirahandler.get_cr()
        if len(jira_cr_result) > 0:
            for cr in jira_cr_result:
                if "templateId" not in cr.keys():
                    cr["templateId"] = exporthandler.get_templateId(cr["serverId"])
            filehandler.safe_json_file(jira_cr_result, json_file_name= config.jira_unsorted_file_name, path_to_file=config.jira_unsorted_dir)
            timeManager.compare_same_src(src="jira")
            print("Formatting Canned Responses Export, please wait…")
            jira_cr_formatted = exporthandler.format_exports(jira_cr_result)
            print("Saving Canned Responses to JSON file, please wait…")
            filehandler.safe_json_file(jira_cr_formatted, json_file_name=config.jira_categorized_file_name, path_to_file=config.jira_categorized_dir)           
                

    fresh_download = userhandler.input_timeout("Start fresh download of Canned Responses from WU Wiki (Confluence)? [Y/N]")
    ## WIKI CR Download ##
    if not fresh_download and os.path.exists("data/wiki-exports/unsorted-exports/wiki-cr-export"+suffix+".json"):
        print("Canned Response already downloaded today, skipping download from WU Wiki.")
        wiki_cr_result = filehandler.load_latest_file(config.wiki_unsorted_file_name, config.wiki_unsorted_dir)
        if filehandler.load_latest_file(config.wiki_categorized_file_name, config.wiki_categorized_dir) == False:
            wiki_cr_formatted = exporthandler.format_exports(wiki_cr_result, "wiki")
            filehandler.safe_json_file(wiki_cr_formatted, config.wiki_categorized_file_name, config.wiki_categorized_dir)
    else:
        fresh_download = True
        print("Canned Response downloading, please wait…")
        wiki_cr_result = wikihandler.export_wiki_cr_pages(spaceKey=config.initial_spaceKey)
        filehandler.safe_json_file(wiki_cr_result, config.wiki_unsorted_file_name, config.wiki_unsorted_dir)
        timeManager.compare_same_src(src="wiki")
        wiki_cr_result = exporthandler.add_templateId() # add serverId from Jira CRs to Wiki CRs
        if len(wiki_cr_result) > 0:
            wiki_cr_formatted = exporthandler.format_exports(wiki_cr_result, "wiki")
            filehandler.safe_json_file(wiki_cr_formatted, config.wiki_categorized_file_name, config.wiki_categorized_dir)

        else:
            # Exportieren von Canned Responses aus Confluence (Wiki) als JSON- und CSV-Datei
            print("Creating Wiki Pages for categorical Canned Responses, please wait…")
            # upload to confluence on pageId set in config.initial_pageId
            cr_formatted = filehandler.load_latest_file(config.jira_categorized_file_name, config.jira_categorized_dir)
            wikihandler.create_categorized_pages(cr_formatted)
            wikihandler.update_pages(cr_formatted)
            wiki_cr_result = wikihandler.export_wiki_cr_pages(spaceKey=config.initial_spaceKey)
            wiki_cr_result = exporthandler.add_templateId()
            if len(wiki_cr_result) > 0:
                wiki_cr_formatted = exporthandler.format_exports(wiki_cr_result, "wiki")
                filehandler.safe_json_file(wiki_cr_formatted, config.wiki_categorized_file_name, config.wiki_categorized_dir)
            else:
                print("Serverdaten wurden zwar scheinbar erfolgreich in Confluence hochgeladen, konnten aber danach nicht mehr heruntergeladen werden. Um Datenverlust zu verhindern stoppt das Programm.")
                exit(1)

  
    # Run the synchronization
    dbManager.sync_data()
    # Export the updated data to Jira
    dbManager.db_jira_export()
    # Export the updated data to Confluence
    dbManager.db_wiki_export()
    # Merge the Jira export with the database export
    dbManager.merge_jira_export_with_db()
    # Merge the Confluence export with the database export
    dbManager.merge_wiki_export_with_db()
    

    # check if CR templateText in jira is up to date with wiki-cr-export
    # exporthandler.compare_cr_exports()

    # # # Exportieren von Canned Responses aus Confluence (Wiki) als JSON- und CSV-Datei
    # # print("Creating Wiki Pages for categorical Canned Responses, please wait…")
    # # # upload to confluence on pageId set in config.initial_pageId
    # # cr_formatted = filehandler.load_latest_file("canned-responses", path_to_file="data/jira-exports/")
    # # wikihandler.create_categorized_pages(cr_formatted)
    # # wikihandler.update_pages(cr_formatted)
    
    # # Vorbereiten der neuen Canned Responses von Confluence (Wiki) für Jira ServiceDesk
    # exporthandler.digest_exported_cr_pages("wiki2jira")
    
    # Übertragen von Canned Responses von Confluence (Wiki) zu Jira ServiceDesk
    # jirahandler.wiki_cr_to_jira()
    

    # ## resync wiki pages with updated canned responses that are uploaded to JIRA server
    # new_json_data_for_wiki_pages = filehandler.load_latest_file(config.wiki_categorized_file_name, config.wiki_categorized_dir)
    # # wikihandler.update_pages(new_json_data_for_wiki_pages)


    # # Bereinigen von temporären Dateien und Verzeichnissen
    # # filehandler.cleanup()