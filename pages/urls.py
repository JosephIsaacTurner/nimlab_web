from django.urls import path, re_path

from .views import *

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("about/", AboutPageView.as_view(), name="about"),
    re_path(r'^file_explorer/(?P<path>.*)$', file_explorer, name='file_explorer'),
    re_path(r'^file_viewer/(?P<path>.*)$', file_viewer, name='file_viewer'),
    path("search_datasets/", search_datasets, name='search_datasets'),  # <-- new line for search page
]

