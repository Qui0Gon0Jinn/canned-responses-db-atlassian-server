import os
import subprocess


def process_file(file, output_file):
    with open(file, 'r') as f:
        content = f.read()

    output_file.write(f"# File: {file}\n")
    output_file.write(content)
    output_file.write("\n\n")


def process_directory(directory, output_file, processed_files):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                if file_path not in processed_files and not is_excluded(file_path):
                    process_file(file_path, output_file)
                    processed_files.add(file_path)
                    process_directory(os.path.dirname(file_path), output_file, processed_files)


def is_excluded(file_path):
    exclusions = ["secrets/", "credentials.py"]
    for exclusion in exclusions:
        if exclusion in file_path:
            return True
    return False


def collect_code():
    output_file_name = "output_collected_code.txt"
    processed_files = set()

    with open(output_file_name, 'w') as output_file:
        process_file("src/main.py", output_file)
        processed_files.add("src/main.py")
        process_directory("src", output_file, processed_files)

    convert_to_pdf = input("Möchten Sie die TXT-Datei als PDF speichern? (j/n): ")
    if convert_to_pdf.lower() in ["j", "y"]:
        convert_to_pdf_pdfkit(output_file_name)


def convert_to_pdf_pdfkit(txt_file):
    pdf_file = txt_file.replace(".txt", ".pdf")
    try:
        subprocess.run(["pdfkit", txt_file, pdf_file], check=True)
        print(f"Die PDF-Datei '{pdf_file}' wurde erfolgreich erstellt.")
    except FileNotFoundError:
        print("Das 'pdfkit'-Modul wurde nicht gefunden. Stellen Sie sicher, dass es installiert ist.")
    except subprocess.CalledProcessError:
        print("Ein Fehler ist beim Erstellen der PDF-Datei aufgetreten.")


collect_code()
