from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

from .models import Student, Adult, Family, OLSClass

def index(request):
    return HttpResponse("Welcome! You've safely arrived at the contacts index!")

def adult_index(request):
    return HttpResponse("Welcome! You've safely arrived at the adult index!")

def student_index(request):
    students 
    return HttpResponse("Welcome! You've safely arrived at the student index!")

def family_index(request):
    families = []
    for family in Family.objects.all():
        familyinfo = {
                'students': [],
                'parents': family.parent_names(),
                'email': '(no email)',
                'address': ['(no address)'],
                'phone_numbers': family.phone_numbers(),
                'emails': family.emails(),
                }
        if family.address is not None:
                familyinfo['address'] = family.address.multiline()
        for student in family.student_set.all():
            familyinfo['students'].append({
                'firstname': student.firstname,
                'lastname': student.lastname,
                'grade': student.olsclass.grade,
                })
        families.append(familyinfo)
    template = loader.get_template('contacts/family_index.html')
    context = RequestContext(request, {'families': families })
    return HttpResponse(template.render(context))

def class_index(request):
    classes = []
    for idx, olsclass in enumerate(OLSClass.objects.all()):
        classinfo = {
                'tag': olsclass.tag(),
                'grade': olsclass.grade,
                'teacher': olsclass.teacher_name(),
                'aide': olsclass.aide_name(),
                'classmom': olsclass.classmom_name(),
                'students': [] }
        for student in olsclass.student_set.all():
            classinfo['students'].append(student.name())
        if len(classinfo['students']) > 0:
            classes.append(classinfo)
            if idx % 3 == 0:
                classinfo['classes'] = 'clear'
            else:
                classinfo['classes'] = ""
    template = loader.get_template('contacts/classes_index.html')
    context = RequestContext(request, {'classes': classes })
    return HttpResponse(template.render(context))
