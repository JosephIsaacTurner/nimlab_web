# forms.py
from django import forms
from django.db.models import Q  # This is where you import Q
from django.db import models
from pages.models import Dataset, Tag, Author, Contact, CitationSrc, CitationTo, NiftiImage

class DatasetSearchForm(forms.Form):
    dataset_id = forms.ModelMultipleChoiceField(
        queryset=Dataset.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Dataset Name"
    )
    # BIDSVersion = forms.CharField(required=False)
    # dataset_path = forms.ModelMultipleChoiceField(
    #     queryset=Dataset.objects.values_list('directory_path', flat=True).distinct(),
    #     widget=forms.CheckboxSelectMultiple,
    #     required=False,
    #     label="Dataset Directory"
    # )
    DatasetType = forms.ModelMultipleChoiceField(
        queryset=Dataset.objects.values_list('DatasetType', flat=True).distinct(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Dataset Type"
    )
    # creation_date = forms.CharField(required=False)
    comments = forms.CharField(required=False)
    tag = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all().order_by('tag').distinct('tag'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Tags"
    )
    author_email = forms.ModelMultipleChoiceField(
        queryset=Author.objects.distinct(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Author Email"
    )
    contact_email = forms.ModelMultipleChoiceField(
        queryset=Contact.objects.distinct(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Contact Email"
    )
    citation = forms.CharField(required=False)
    # path = forms.CharField(required=False)
    # type = forms.ModelMultipleChoiceField(
    #     queryset=NiftiImage.objects.values_list('type', flat=True).distinct(),
    #     widget=forms.CheckboxSelectMultiple,
    #     required=False,
    #     label="Type"
    # )
    # md5 = forms.CharField(required=False)
    # roi_size = forms.IntegerField(required=False)
    # mask = forms.CharField(required=False)
    dataset_path = forms.MultipleChoiceField(
        choices=[],  # You can dynamically populate this in the __init__ method
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Dataset Directory"
    )

    def __init__(self, *args, **kwargs):
        super(DatasetSearchForm, self).__init__(*args, **kwargs)
        self.fields['dataset_path'].choices = Dataset.objects.values_list('directory_path', 'directory_path').distinct()


    def search(self):
        datasets = Dataset.objects.all()
        if self.cleaned_data['dataset_path']:
            directory_paths_query = Q(directory_path__in=self.cleaned_data['dataset_path'])
            datasets = datasets.filter(directory_paths_query)
        if self.cleaned_data['dataset_id']:
            ids_query = Q(id__in=self.cleaned_data['dataset_id'])
            datasets = datasets.filter(ids_query)
        # if self.cleaned_data['dataset_path']:
        #     directory_paths_query = Q(directory_path__in=self.cleaned_data['dataset_path'])
        #     datasets = datasets.filter(directory_paths_query)
        # if self.cleaned_data['dataset_name']:
        #     datasets = datasets.filter(dataset_name__icontains=self.cleaned_data['dataset_name'])
        # if self.cleaned_data['BIDSVersion']:
        #     datasets = datasets.filter(BIDSVersion__icontains=self.cleaned_data['BIDSVersion'])
        if self.cleaned_data['DatasetType']:
            dataset_type_query = Q()
            for dataset_type in self.cleaned_data['DatasetType']:
                dataset_type_query |= Q(DatasetType=dataset_type)
            datasets = datasets.filter(dataset_type_query)
        # if self.cleaned_data['dataset_path']:
        #     directory_paths_query = Q()
        #     for directory_path in self.cleaned_data['dataset_path']:
        #         directory_paths_query |= Q(directory_path=directory_path)
        #     datasets = datasets.filter(directory_paths_query)
        # if self.cleaned_data['creation_date']:
        #     datasets = datasets.filter(creation_date__icontains=self.cleaned_data['creation_date'])
        if self.cleaned_data['comments']:
            datasets = datasets.filter(comments__icontains=self.cleaned_data['comments'])

        # Search related models
        if self.cleaned_data['tag']:
            tag_query = Q()
            for tag in self.cleaned_data['tag']:
                tag_query |= Q(tags__in=[tag])
            datasets = datasets.filter(tag_query)
        if self.cleaned_data['author_email']:
            author_email_query = Q()
            for author_email in self.cleaned_data['author_email']:
                author_email_query |= Q(authors__in=[author_email])
            datasets = datasets.filter(author_email_query)
        # if self.cleaned_data['contact_email']:
        #     datasets = datasets.filter(contacts__contact_email__icontains=self.cleaned_data['contact_email'])
        if self.cleaned_data['contact_email']:
            contact_email_query = Q()
            for contact_email in self.cleaned_data['contact_email']:
                contact_email_query |= Q(contacts__in=[contact_email])
            datasets = datasets.filter(contact_email_query)

        # if self.cleaned_data['path']:
        #     datasets = datasets.filter(nifti_images__path__icontains=self.cleaned_data['path'])
        # if self.cleaned_data['type']:
        #     datasets = datasets.filter(nifti_images__type__icontains=self.cleaned_data['type'])
        # if self.cleaned_data['md5']:
        #     datasets = datasets.filter(nifti_images__md5__icontains=self.cleaned_data['md5'])
        # if self.cleaned_data['roi_size'] is not None:
        #     datasets = datasets.filter(nifti_images__roi_size=self.cleaned_data['roi_size'])
        # if self.cleaned_data['mask']:
        #     datasets = datasets.filter(nifti_images__mask__icontains=self.cleaned_data['mask'])

        return datasets.distinct()
