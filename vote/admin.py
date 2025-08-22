from django.contrib import admin

from .models import OTP

class OTPAdmin(admin.ModelAdmin):
    list_display = ('id', 'voter', 'otp_token', 'created_at', 'otp_sent', 'is_used', 'check_if_used')
    list_filter = ('is_used', 'voter')
    search_fields = ('voter__username', 'otp_token')
    ordering = ('-created_at', 'voter')

    def check_if_used(self, obj):
        return "Used" if obj.is_used else "Not Used"
    check_if_used.short_description = "Used?"

admin.site.register(OTP, OTPAdmin)