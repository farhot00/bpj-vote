from django.contrib import admin
from vote.models import Candidate, ScientificAssociation,Voter,Vote
from django.contrib.auth.admin import UserAdmin
from main.models import User, SentSMS, SentEmail

admin.site.register(User, UserAdmin)


class SaveWithUserMixin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        # Pass the user to the model's save method
        obj.save(user=request.user)
        super().save_model(request, obj, form, change)
@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'gender', 'scientific_association', 'created_by', 'created_at', 'updated_at')
    search_fields = ('first_name', 'last_name', 'scientific_association__name')

@admin.register(ScientificAssociation)
class ScientificAssociationAdmin(admin.ModelAdmin):
    list_display = ('name', 'established_year', 'created_by', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'gender', 'fathers_name', 'education_level', 'scientific_association', 'student_number', 'phone', 'voted', 'created_by', 'created_at', 'updated_at',"confirmed_information")
    search_fields = ('first_name', 'last_name', 'student_number', 'phone')

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('voter', 'candidate', 'created_by', 'created_at', 'updated_at','ip_address','user_agent','device')
    search_fields = ('voter__first_name', 'voter__last_name', 'candidate__first_name', 'candidate__last_name')


admin.site.register(SentSMS)
admin.site.register(SentEmail)