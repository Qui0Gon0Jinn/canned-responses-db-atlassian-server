import os
import glob
import json
import datetime

def compare_same_src(src="jira"):
    if src == "jira":
        # Specify the directory and the file name patterns
        directory = "data/jira-exports/unsorted-exports/"
        file_pattern = "jira-cr-export-*.json"
        
        # Get the list of matching files in the directory
        file_list = glob.glob(os.path.join(directory, file_pattern))
        
        if len(file_list) < 2:
            print("At least two Jira export files are required for comparison.")
            return
        
        # Sort the file list based on the date in the file name
        file_list.sort(key=lambda x: datetime.datetime.strptime(x.split("-")[-1].split(".")[0], "%Y-%m-%d"))
        
        # Get the file paths for the two most recent files
        file1 = file_list[-2]
        file2 = file_list[-1]
        
        # Open and load the JSON data from the files
        with open(file1) as f1, open(file2) as f2:
            data1 = json.load(f1)
            data2 = json.load(f2)
        
        # Use the templateId as the primary key to compare records
        for id in data1:
            if id in data2:
                # Compare the values of the two records
                for key in data1[id]:
                    if key != "templateId" and key != "last_change":
                        if data1[id].get(key) != data2[id].get(key):
                            # Check if the "last_change" key exists
                            if "last_change" in data2[id]:
                                continue
                            
                            # Add the "last_change" field with the current date object
                            current_date = datetime.datetime.now().isoformat()
                            data2[id]["last_change"] = current_date
        
        # Save the updated records in the second file
        with open(file2, 'w') as f2:
            json.dump(data2, f2, indent=4)
    elif src == "wiki":
        # Specify the directory and the file name pattern for the wiki source
        directory = "data/wiki-exports/unsorted-exports/"
        file_pattern = "wiki-cr-export-*.json"

        # Get the list of matching files in the directory
        file_list = glob.glob(os.path.join(directory, file_pattern))

        if len(file_list) < 2:
            print("At least two Wiki export files are required for comparison.")
            return

        # Sort the file list based on the date in the file name
        file_list.sort(key=lambda x: datetime.datetime.strptime(x.split("-")[-1].split(".")[0], "%Y-%m-%d"))

        # Get the file paths for the two most recent files
        file1 = file_list[-2]
        file2 = file_list[-1]

        # Open and load the JSON data from the files
        with open(file1) as f1, open(file2) as f2:
            data1 = json.load(f1)
            data2 = json.load(f2)

        # Use the templateId as the primary key to compare records
        for id in data1:
            if id in data2:
                # Compare the values of the two records
                for key in data1[id]:
                    if key != "templateId" and key != "last_change":
                        if data1[id].get(key) != data2[id].get(key):
                            # Check if the "last_change" key exists
                            if "last_change" in data2[id]:
                                continue

                            # Add the "last_change" field with the current date object
                            current_date = datetime.datetime.now().isoformat()
                            data2[id]["last_change"] = current_date

        # Save the updated records in the second file
        with open(file2, 'w') as f2:
            json.dump(data2, f2, indent=4)





def compare_same_src(src="jira"):
    if src == "jira":
        folder_path = "data/jira-exports/unsorted-exports"
        files = os.listdir(folder_path)
        json_files = [f for f in files if f.endswith(".json")]

        if not json_files:
            print("No JSON files found in the specified folder.")
            return

        latest_file = max(json_files)
        json_files.remove(latest_file)

        with open(os.path.join(folder_path, latest_file)) as latest_f:
            latest_data = json.load(latest_f)

        for file in json_files:
            with open(os.path.join(folder_path, file)) as f:
                data = json.load(f)

            for template_id in latest_data:
                if template_id in data:
                    for key in latest_data[template_id]:
                        if key != "last_change" and key in data[template_id]:
                            if latest_data[template_id][key] != data[template_id][key]:
                                if "last_change" in data[template_id]:
                                    latest_date = latest_data[template_id]["last_change"]
                                    current_date = data[template_id]["last_change"]
                                    datetime_latest = datetime.datetime.fromisoformat(latest_date)
                                    datetime_current = datetime.datetime.fromisoformat(current_date)

                                    if datetime_current > datetime_latest:
                                        latest_data[template_id][key] = data[template_id][key]
                                else:
                                    latest_data[template_id][key] = data[template_id][key]

        # Save the updated data to the latest file
        with open(os.path.join(folder_path, latest_file), 'w') as latest_f:
            json.dump(latest_data, latest_f, indent=4)



def compare_json_for_db(data1, data2):
    # Check if the parameters are file paths or JSON data
    if isinstance(data1, str) and os.path.isfile(data1):
        with open(data1) as f1:
            data1 = json.load(f1)
    if isinstance(data2, str) and os.path.isfile(data2):
        with open(data2) as f2:
            data2 = json.load(f2)

    # Use primary key templateId to compare records
    for id in data1:
        if id in data2:
            # Compare the values of the two records
            for key in data1[id]:
                if key != "templateId" and key != "last_change":
                    if data1[id][key] != data2[id][key]:
                        # Compare the date objects
                        date1 = data1[id]["last_change"]
                        date2 = data2[id]["last_change"]
                        datetime1 = datetime.datetime.fromisoformat(date1)
                        datetime2 = datetime.datetime.fromisoformat(date2)

                        if datetime1 > datetime2:
                            data2[id][key] = data1[id][key]
                        elif datetime2 > datetime1:
                            data1[id][key] = data2[id][key]

    # If file paths were provided, save the updated records
    if isinstance(data1, str) and os.path.isfile(data1):
        with open(data1, 'w') as f1:
            json.dump(data1, f1, indent=4)
    if isinstance(data2, str) and os.path.isfile(data2):
        with open(data2, 'w') as f2:
            json.dump(data2, f2, indent=4)

