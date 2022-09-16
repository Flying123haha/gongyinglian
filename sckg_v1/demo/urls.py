from django.urls import path
from django.conf.urls import url
from .views import index,search_entity,search_relation,show_overview,showdetail,question_answering
urlpatterns = [
    url(r'^$',index),
    url(r'search_entity',search_entity),
    url(r'^overview',show_overview),
    url(r'^search_relation',search_relation),
    url(r'^detail',showdetail),
    url(r'^overview',show_overview),
    url(r'qa', question_answering)

    # path('',index)
]