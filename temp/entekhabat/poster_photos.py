import csv
import os
import shutil

csv_file_path = "jome.csv"
os.makedirs("poster", exist_ok=True)
# Read the CSV and update the row
with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    fieldnames = reader.fieldnames
    print(fieldnames)
    for row in reader:
        personal_photo = row['عکس_پرسنلی']
        election_photo = row['عکس_انتخاباتی']
        sa_name = row['انجمن_علمی']
        person_name = row['نام_خانوادگی'] + " - " + row['نام']
        os.makedirs(f"poster/{sa_name}", exist_ok=True)
        try:
            if election_photo:
                shutil.copy2(os.path.join(row['#'], election_photo), os.path.join("poster",sa_name, person_name+".png"))
            elif personal_photo:
                shutil.copy2(os.path.join(row['#'], personal_photo),
                             os.path.join("poster", sa_name, person_name+".png"))
            else:
                print(sa_name," | ",person_name)
        except FileNotFoundError as e:
            print(f"Exception for {sa_name} | {person_name}: {e}")


# Replace the original file with the updated one
# os.replace(temp_csv_path, csv_file_path)
