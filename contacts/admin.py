from django.contrib import admin

from .models import Student, Adult, Guardian, Family, Address, OLSClass

admin.site.register(Student)
admin.site.register(Adult)
admin.site.register(Guardian)
admin.site.register(Address)
admin.site.register(OLSClass)

class StudentInline(admin.TabularInline):
    model = Student
    extra = 0

class GuardianInline(admin.TabularInline):
    model = Guardian
    extra = 0

class FamilyAdmin(admin.ModelAdmin):
    readonly_fields = ('name',)
    fields = ('name', 'private', 'address', 'email')
    inlines = [StudentInline, GuardianInline]

admin.site.register(Family, FamilyAdmin)

