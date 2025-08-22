import csv
import os
import shutil
import tempfile

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files import File
from vote.models import Candidate, ScientificAssociation

degree_mapping = {
    'کارشناسی': 'BSc',
    'کارشناسی ارشد': 'MSc',
    'دکتری': 'PhD'
}


class Command(BaseCommand):
    help = 'Import candidates from CSV'

    def add_arguments(self, parser):
        # Define an argument to accept the CSV file path
        parser.add_argument('csv_file', type=str, help='The CSV file to import')

        # Optionally, you can add another argument to define the base path for file uploads
        parser.add_argument('--base_path', type=str, help='Base path for file uploads')
        parser.add_argument('--create_associations', type=bool, default=True, help="Should this script Create needed"
                                                                                  "Scientific Associations or throw"
                                                                                  "exception when the association"
                                                                                  "is not found")
        parser.add_argument('--rembg', action='store_true', help="remove background for personal and election photos")
        parser.add_argument('--whitebg', action='store_true', help="add white background to all images")

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']
        base_path = kwargs['base_path']
        remove_bg = kwargs['rembg']
        white_bg = kwargs['whitebg']
        if remove_bg:
            from rembg import remove, new_session
            session = new_session()
        if white_bg:
            from PIL import Image

        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                print(row["#"])
                try:
                    # Fetch the scientific association by name
                    association_name = row['انجمن_علمی']
                    association = ScientificAssociation.objects.filter(name=association_name).first()
                    if not association:
                        if kwargs['create_associations']:

                            association = ScientificAssociation(name=association_name)
                            association.save()
                        else:
                            raise ScientificAssociation.DoesNotExist(f"Scientific Association {association_name} not found.exiting")

                    # if row['مقطع_تحصیلی'] in degree_mapping:
                    #     education_level =  degree_mapping[row['مقطع_تحصیلی']],
                    # else:
                    #     education_level = None

                    # Create or update the candidate
                    candidate, created = Candidate.objects.update_or_create(
                        student_number=row['شماره_دانشجویی'],
                        national_id=row['کد_ملی'],
                        candidate_code=row['کدـانتخاباتی'],
                        defaults={
                            'first_name': row['نام'],
                            'last_name': row['نام_خانوادگی'],
                            # 'gender': 'M' if row['جنسیت'] == 'مرد' else 'F',
                            'phone_number': row['تلفن_همراه'],
                            'field_of_study': row['رشته_تحصیلی'],
                            'education_level': row['مقطع_تحصیلی'],
                            'scientific_association': association,
                        }
                    )
                    candidate.save()

                    # Handle file fields, if the file path is provided in the CSV
                    file_fields = {
                        'previous_semester_transcript': row['کارنامه_تحصیلی_ترم_قبل'],
                        'one_year_plan_for_association': row['برنامه_یکساله_برای_انجمن'],
                        'student_id_card': row['کارت_دانشجویی'],
                        'personal_photo': row['عکس_پرسنلی'],
                        'election_photo': row['عکس_انتخاباتی'],
                        'resume': row['رزومه_تحصیلی/کاری']
                    }

                    # Prepare a dictionary for form data
                    form_data = {}
                    file_data = {}


                    for field, file_name in file_fields.items():
                        if file_name and base_path:
                            # Sanitize the file name to prevent path traversal
                            file_path = os.path.join(base_path, row['#'], file_name)
                            if os.path.exists(file_path):
                                field_name = candidate._meta.get_field(field)
                                if (not remove_bg and not white_bg) or field not in ["personal_photo","election_photo"]:
                                    # shutil.copy2(file_path, destination_file_path)
                                    # Open the copied file and wrap it with Django File
                                    f = open(file_path, 'rb')
                                    django_file = File(f, name=file_name)
                                elif remove_bg and field in ["personal_photo","election_photo"]:
                                    new_file_name = file_name.replace(".jpg",".png").replace(".jpeg",".png")
                                    new_file_path = os.path.join(base_path, "temp", new_file_name)
                                    with open(file_path, 'rb') as i:
                                        with open(new_file_path, 'wb') as o:
                                            input = i.read()
                                            output = remove(input, session=session, bgcolor=(255, 255, 255, 255))
                                            o.write(output)
                                    f = open(new_file_path, 'rb')
                                    django_file = File(f, name=new_file_name)
                                elif white_bg and field in ["personal_photo", "election_photo"]:
                                    # new_file_name = file_name.replace(".jpg", ".png").replace(".jpeg", ".png")
                                    new_file_path = os.path.join(base_path, "temp", file_name).replace(".png",".jpg")
                                    new_file_name = file_name.replace(".png",".jpg")
                                    # Open the PNG image
                                    png_image = Image.open(file_path)
                                    # Create a new white background image with the same size as the PNG
                                    background = Image.new('RGB', png_image.size, (255, 255, 255))
                                    # Paste the PNG image onto the white background (handling transparency)
                                    background.paste(png_image, (0, 0), png_image)
                                    # Save the result as a JPG
                                    background.save(new_file_path, 'JPEG')
                                    f = open(new_file_path, 'rb')
                                    django_file = File(f, name=new_file_name)


                                # Assign the file to the appropriate field
                                setattr(candidate, field, django_file)
                                # Save the instance
                                candidate.save()
                                f.close()
                        else:
                            setattr(candidate, field, None)
                            candidate.save()

                    # self.stdout.write(self.style.SUCCESS(f'Successfully imported candidate {candidate}'))

                except ScientificAssociation.DoesNotExist:
                    self.stdout.write(self.style.ERROR(
                        f'Association {association_name} does not exist. Skipping candidate {row["نام"]} {row["نام_خانوادگی"]}'))
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error importing candidate {row["نام"]} {row["نام_خانوادگی"]}: {e}'))
