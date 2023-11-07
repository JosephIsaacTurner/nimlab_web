# forms.py
from django import forms
from django.db.models import Q  # This is where you import Q
from django.db import models
from pages.models import Dataset, Tag, Author, Contact, CitationSrc, CitationTo
class DatasetSearchForm(forms.Form):
    dataset_id = forms.ModelMultipleChoiceField(
        queryset=Dataset.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Dataset Name"
    )
    dataset_path = forms.MultipleChoiceField(
        choices=[],  # You can dynamically populate this in the __init__ method
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Dataset Directory"
    )

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

    def __init__(self, *args, **kwargs):
        super(DatasetSearchForm, self).__init__(*args, **kwargs)
        self.fields['dataset_path'].choices = Dataset.objects.values_list('dataset_path', 'dataset_path').distinct()


    def search(self):
        datasets = Dataset.objects.all()
        if self.cleaned_data['dataset_path']:
            dataset_paths_query = Q(dataset_path__in=self.cleaned_data['dataset_path'])
            datasets = datasets.filter(dataset_paths_query)
        if self.cleaned_data['dataset_id']:
            ids_query = Q(id__in=self.cleaned_data['dataset_id'])
            datasets = datasets.filter(ids_query)
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
        if self.cleaned_data['contact_email']:
            contact_email_query = Q()
            for contact_email in self.cleaned_data['contact_email']:
                contact_email_query |= Q(contacts__in=[contact_email])
            datasets = datasets.filter(contact_email_query)
        return datasets.distinct()
