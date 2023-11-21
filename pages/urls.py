from django.urls import path, re_path

from .views import *
from .tools.generate_dataset_csv import generate_dataset_csv

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("usage/", usage_page_view, name="usage"),
    path("about/", usage_page_view, name="about"),
    re_path(r'^file_explorer/(?P<path>.*)$', file_explorer, name='file_explorer'),
    re_path(r'^file_viewer/(?P<path>.*)$', file_viewer, name='file_viewer'),
    path("search_datasets/", search_datasets, name='search_datasets'),
    path("generate_csv/<path:dataset_path>/", generate_dataset_csv, name='generate_csv'),
]

