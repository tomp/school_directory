from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^adults/$', views.adult_index, name='adult_index'),
    url(r'^students/$', views.student_index, name='student_index'),
    url(r'^families/$', views.family_index, name='family_index'),
    url(r'^classes/$', views.class_index, name='class_index'),
    url(r'^$', views.index, name='index'),
]
