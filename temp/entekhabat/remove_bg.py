import csv
import os
from rembg import remove, new_session
session = new_session()

csv_file_path = "ثبت نام انتخابات متمرکز انجمن های علمی دانشجویی (1).csv"
temp_csv_path = "new_images.csv"

def rembg_func(input_filename, output_filename):
    try:
        with open(input_filename, 'rb') as i:
            with open(output_filename, 'wb') as o:
                input = i.read()
                # output = remove(input, session=session, bgcolor=(255, 255, 255, 255))
                output = remove(input, session=session)
                o.write(output)
    except FileNotFoundError:
        pass

# Read the CSV and update the row
with open(csv_file_path, newline='', encoding='utf-8') as csvfile, \
        open(temp_csv_path, 'w', newline='', encoding='utf-8') as temp_csvfile:
    reader = csv.DictReader(csvfile)
    fieldnames = reader.fieldnames

    writer = csv.DictWriter(temp_csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        personal_photo = row['عکس_پرسنلی']
        election_photo = row['عکس_انتخاباتی']
        update_data = {}
        if personal_photo and personal_photo != "":
            print(row["#"], personal_photo)
            personal_file_path = os.path.join(row['#'], personal_photo)
            new_personal_file_path = personal_file_path.replace(".png","_new.png").replace(".jpg","_new.png").replace(".jpeg","_new.png")
            rembg_func(personal_file_path,new_personal_file_path)
            update_data['عکس_پرسنلی'] = row['عکس_پرسنلی'].replace(".png","_new.png").replace(".jpg","_new.png").replace(".jpeg","_new.png")
        if election_photo and election_photo != "":
            print(row["#"], election_photo)
            election_file_path = os.path.join(row['#'], election_photo)
            new_election_file_path = election_file_path.replace(".png","_new.png").replace(".jpg","_new.png").replace(".jpeg","_new.png")
            rembg_func(election_file_path,new_election_file_path)
            update_data['عکس_انتخاباتی'] = row['عکس_انتخاباتی'].replace(".png","_new.png").replace(".jpg","_new.png").replace(".jpeg","_new.png")

        row.update(update_data)
        writer.writerow(row)

# Replace the original file with the updated one
# os.replace(temp_csv_path, csv_file_path)
