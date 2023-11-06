# forms.py
from django import forms
from django.db.models import Q  # This is where you import Q
from django.db import models
from pages.models import Dataset, Tag, Author, Contact, CitationSrc, CitationTo, NiftiImage

class DatasetSearchForm(forms.Form):
    dataset_name = forms.ModelMultipleChoiceField(
        queryset=Dataset.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Dataset Name"
    )
    BIDSVersion = forms.CharField(required=False)
    DatasetType = forms.ModelMultipleChoiceField(
        queryset=Dataset.objects.values_list('DatasetType', flat=True).distinct(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Dataset Type"
    )
    creation_date = forms.CharField(required=False)
    comments = forms.CharField(required=False)
    tag = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Tags"
    )
    author_email = forms.ModelMultipleChoiceField(
        queryset=Author.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Author Email"
    )
    contact_email = forms.ModelMultipleChoiceField(
        queryset=Contact.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Contact Email"
    )
    citation = forms.CharField(required=False)
    path = forms.CharField(required=False)
    type = forms.ModelMultipleChoiceField(
        queryset=NiftiImage.objects.values_list('type', flat=True).distinct(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Type"
    )
    md5 = forms.CharField(required=False)
    roi_size = forms.IntegerField(required=False)
    mask = forms.CharField(required=False)

    def search(self):
        datasets = Dataset.objects.all()

        if self.cleaned_data['dataset_name']:
            datasets = datasets.filter(dataset_name__icontains=self.cleaned_data['dataset_name'])
        if self.cleaned_data['BIDSVersion']:
            datasets = datasets.filter(BIDSVersion__icontains=self.cleaned_data['BIDSVersion'])
        if self.cleaned_data['DatasetType']:
            datasets = datasets.filter(DatasetType__icontains=self.cleaned_data['DatasetType'])
        if self.cleaned_data['creation_date']:
            datasets = datasets.filter(creation_date__icontains=self.cleaned_data['creation_date'])
        if self.cleaned_data['comments']:
            datasets = datasets.filter(comments__icontains=self.cleaned_data['comments'])

        # Search related models
        if self.cleaned_data['tag']:
            datasets = datasets.filter(tags__tag__icontains=self.cleaned_data['tag'])
        if self.cleaned_data['author_email']:
            datasets = datasets.filter(authors__author_email__icontains=self.cleaned_data['author_email'])
        if self.cleaned_data['contact_email']:
            datasets = datasets.filter(contacts__contact_email__icontains=self.cleaned_data['contact_email'])
        if self.cleaned_data['citation']:
            datasets = datasets.filter(
                Q(citations_src__citation__icontains=self.cleaned_data['citation']) |
                Q(citations_to__citation__icontains=self.cleaned_data['citation'])
            )
        if self.cleaned_data['path']:
            datasets = datasets.filter(nifti_images__path__icontains=self.cleaned_data['path'])
        if self.cleaned_data['type']:
            datasets = datasets.filter(nifti_images__type__icontains=self.cleaned_data['type'])
        if self.cleaned_data['md5']:
            datasets = datasets.filter(nifti_images__md5__icontains=self.cleaned_data['md5'])
        if self.cleaned_data['roi_size'] is not None:
            datasets = datasets.filter(nifti_images__roi_size=self.cleaned_data['roi_size'])
        if self.cleaned_data['mask']:
            datasets = datasets.filter(nifti_images__mask__icontains=self.cleaned_data['mask'])

        return datasets.distinct()
