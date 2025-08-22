from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Field, Row, Column
from django import forms
from django.contrib.auth.forms import AuthenticationForm

from vote.models import Voter, ScientificAssociation, Candidate

# from django_recaptcha.fields import ReCaptchaField
# from django_recaptcha.widgets import ReCaptchaV2Checkbox
from turnstile.fields import TurnstileField

# class CustomAuthenticationForm(AuthenticationForm):
#     recaptcha = ReCaptchaField(widget=ReCaptchaV2Checkbox(
#         attrs={
#             'hl': 'fa',
#         }))

class CustomAuthenticationForm(AuthenticationForm):
    turnstile = TurnstileField()


class VoterForm(forms.ModelForm):
    class Meta:
        model = Voter
        fields = [
            'first_name', 'last_name', 'gender', 'fathers_name',
            'education_level', 'scientific_association', 'national_id',
            'field_of_study', 'email', 'student_number',
            'phone'
            # 'phone', 'otp', 'verified', 'voted', 'otp_sent'
        ]
        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'gender': 'جنسیت',
            'fathers_name': "نام پدر",
            'education_level': 'سطح تحصیلات(مقطع)',
            'scientific_association': 'انجمن',
            'national_id': 'کد ملی',
            'field_of_study': 'رشته تحصیلی',
            'email': 'آدرس ایمیل',
            'student_number': 'شماره دانشجویی',
            'phone': 'شماره تلفن همراه',
            # 'otp': 'One-Time Password (OTP)',
            # 'verified': 'Verified',
            # 'voted': 'Has Voted',
            # 'otp_sent': 'OTP Sent Count'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'

        # # Dynamically generate wrapper classes based on field names
        # field_wrappers = {}
        # for field_name in self.fields:
        #     field_wrappers[field_name] = Field(
        #         field_name,
        #         css_class='input-group  input-group-outline my-3'
        #     )
        # self.helper.layout = Layout(*field_wrappers.values())

        self.helper.layout = Layout(
            Row(
                Column(Field('first_name', wrapper_class='input-group  input-group-outline my-3'),
                       css_class='form-group col-md-6 mb-0'),
                Column(Field('last_name', wrapper_class='input-group  input-group-outline my-3'),
                       css_class='form-group col-md-6 mb-0'),
                css_class='form-row',
            ),

            Row(
                Column('gender', css_class='form-group col-md-4 mb-0'),

                Column('education_level', css_class='form-group col-md-4 mb-0'),
                Column('scientific_association', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column(Field('fathers_name', wrapper_class='input-group  input-group-outline my-3'),
                       css_class='form-group col-md-6 mb-0'),
                Column(Field('national_id', wrapper_class='input-group  input-group-outline my-3'),
                       css_class='form-group col-md-6 mb-0'),

                css_class='form-row'
            ),
            Row(
                Column(Field('field_of_study', wrapper_class='input-group  input-group-outline my-3'),
                       css_class='form-group col-md-6 mb-0'),
                Column(Field('student_number', wrapper_class='input-group  input-group-outline my-3'),
                       css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column(Field('email', wrapper_class='input-group  input-group-outline my-3'),
                       css_class='form-group col-md-6 mb-0'),
                Column(Field('phone', wrapper_class='input-group  input-group-outline my-3'),
                       css_class='form-group col-md-6 mb-0'),

                css_class='form-row'
            ),

            Submit('submit', 'ذخیره')
        )


    def validate_phone(self, phone):
        if not phone.startswith('09') or len(phone) != 11 or not phone.isdigit():
            return False
        return True


    def validate_iranian_national_id(self, national_id):
        # Check if the national ID is exactly 10 digits
        if not national_id.isdigit() or len(national_id) != 10:
            return False

        check = int(national_id[9])  # The last digit is the check digit
        sum_digits = sum(int(num) * (10 - index) for index, num in enumerate(national_id[:9]))
        remainder = sum_digits % 11

        # Check if the check digit is valid
        if (remainder < 2 and check == remainder) or (remainder >= 2 and check == 11 - remainder):
            return True
        return False

    def validate_student_id_14_digits(self, student_number):
        # Validation for 14-digit student number starting with 399 to 403
        return len(student_number) == 14 and student_number[:3].isdigit() and 399 <= int(student_number[:3]) <= 403

    def validate_student_id_9_digits(self, student_number):
        # Validation for 9-digit student number starting with 91 to 98
        return (len(student_number) == 9 and student_number[:2].isdigit() and 91 <= int(student_number[:2]) <= 98) or \
                (len(student_number) == 9 and student_number[:3].isdigit() and int(student_number[:3]) == 403)

    def clean(self):
        cleaned_data = super().clean()
        national_id = cleaned_data.get('national_id')
        student_number = cleaned_data.get('student_number')
        phone = cleaned_data.get('phone')

        if not self.validate_phone(phone):
            raise forms.ValidationError('فرمت شماره تلفن نامعتبر است. باید با 09 شروع شود و 11 رقم باشد.')
        # Validate National ID
        if not self.validate_iranian_national_id(national_id):
            raise forms.ValidationError('کد ملی نامعتبر است.')

        # Validate Student Number
        if not (
                self.validate_student_id_14_digits(student_number) or self.validate_student_id_9_digits(
                student_number)):
            raise forms.ValidationError('شماره دانشجویی نامعتبر است.')

        return cleaned_data
    # Dynamically create a layout with custom classes for each field
    # self.helper.layout = Layout(
    #     *[
    #             FloatingField(field_name,wrapper_class='input-group  input-group-outline my-3')
    #         for field_name in self.fields
    #     ]
    # )
    # # Automatically apply classes to div wrappers for each field
    # for field_name, field in self.fields.items():
    #     field.widget.attrs['class'] = 'form-control'  # Add Bootstrap form-control class to inputs
    #     # Set the class for the surrounding div
    #     self.helper[field_name].wrap_together('div', css_class='input-group  input-group-outline my-3')

    # Add a submit button at the end
    # self.helper.add_input(Submit('submit', 'Send'))

    # self.helper.add_input(Submit('submit', 'Submit'))


class ScientificAssociationForm(forms.ModelForm):
    class Meta:
        model = ScientificAssociation
        fields = ['name', 'description', 'established_year', 'logo']
        labels = {
            'name': 'نام انجمن',
            'description': 'توضیحات',
            'established_year': 'سال تاسیس',
            'logo': 'لوگو',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            Row(
                Column(Field('name', wrapper_class='input-group  input-group-outline my-3'),
                       css_class='form-group col-md-6 mb-0'),
                Column(Field('established_year', wrapper_class='input-group  input-group-outline my-3'),
                       css_class='form-group col-md-6 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column(Field('description', wrapper_class='input-group  input-group-outline my-3'),
                       css_class='form-group col-md-12 mb-0'),
                Column(Field('logo', wrapper_class='input-group  input-group-outline my-3'),
                       css_class='form-group col-md-12 mb-0'),
                css_class='form-row',
            ),
            Submit('submit', 'Save')
        )


class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = [
            'first_name', 'last_name','candidate_code', 'gender', 'student_number',
            'education_level', 'field_of_study', 'scientific_association',
            'national_id', 'phone_number', 'previous_semester_transcript',
            'one_year_plan_for_association', 'student_id_card', 'personal_photo',
            'election_photo', 'resume'
        ]
        labels = {
            'first_name': 'نام کوچک',
            'last_name': 'نام خانوادگی',
            'candidate_code': 'کد انتخاباتی',
            'gender': 'جنسیت',
            'student_number': 'شماره دانشجویی',
            'education_level': 'سطح تحصیلات(مقطع)',
            'field_of_study': 'رشته تحصیلی',
            'scientific_association': 'انجمن علمی',
            'national_id': 'کد ملی',
            'phone_number': 'شماره تلفن همراه',
            'previous_semester_transcript': 'عکس کارنامه ترم قبل',
            'one_year_plan_for_association': 'عکس برنامه یکساله انجمن',
            'student_id_card': 'عکس کارت دانشجویی',
            'personal_photo': 'عکس پرسنلی',
            'election_photo': 'عکس انتخاباتی',
            'resume': 'رزومه',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            Row(
                Column(Field('first_name', wrapper_class='input-group  input-group-outline my-3'),
                       css_class='form-group col-md-4 mb-0'),
                Column(Field('last_name', wrapper_class='input-group  input-group-outline my-3'),
                       css_class='form-group col-md-4 mb-0'),
                Column(Field('candidate_code', wrapper_class='input-group  input-group-outline my-3'),
                       css_class='form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            Row(
                Column('gender', css_class='form-group col-md-6 mb-0'),
                Column('education_level', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column(Field('field_of_study', wrapper_class='input-group  input-group-outline my-3'),
                       css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column(Field('student_number', wrapper_class='input-group  input-group-outline my-3'),
                       css_class='form-group col-md-6 mb-0'),
                Column(Field('national_id', wrapper_class='input-group  input-group-outline my-3'),
                       css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column(Field('phone_number', wrapper_class='input-group  input-group-outline my-3'),
                       css_class='form-group col-md-6 mb-0'),
                Column(Field('scientific_association', wrapper_class='input-group  input-group-outline my-3'),
                       css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column(Field('previous_semester_transcript', wrapper_class='input-group  input-group-outline my-3'),
                       css_class='form-group col-md-6 mb-0'),
                Column(Field('one_year_plan_for_association', wrapper_class='input-group  input-group-outline my-3'),
                       css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column(Field('student_id_card', wrapper_class='input-group  input-group-outline my-3'),
                       css_class='form-group col-md-6 mb-0'),
                Column(Field('personal_photo', wrapper_class='input-group  input-group-outline my-3'),
                       css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column(Field('election_photo', wrapper_class='input-group  input-group-outline my-3'),
                       css_class='form-group col-md-6 mb-0'),
                Column(Field('resume', wrapper_class='input-group  input-group-outline my-3'),
                       css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Save')
        )
