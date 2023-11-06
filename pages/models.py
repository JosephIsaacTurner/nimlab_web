# django models.py 
from django.db import models

class Dataset(models.Model):
    name = models.CharField(max_length=255, unique=True)
    bids_version = models.CharField(max_length=255, blank=True, null=True)
    dataset_type = models.CharField(max_length=255, blank=True, null=True)
    creation_date = models.CharField(max_length=255, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    tag = models.CharField(max_length=255, blank=True, null=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='tags')

class Author(models.Model):
    author_email = models.CharField(max_length=255)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='authors')

class Contact(models.Model):
    contact_email = models.CharField(max_length=255)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='contacts')

class CitationSrc(models.Model):
    citation = models.TextField()
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='citations_src')

class CitationTo(models.Model):
    citation = models.TextField()
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='citations_to')

class NiftiImage(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='nifti_images')
    path = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    md5 = models.CharField(max_length=255, blank=True, null=True)
    roi_size = models.IntegerField(blank=True, null=True)
    mask = models.CharField(max_length=255, blank=True, null=True)

class NiftiLinearized(models.Model):
    nifti_image = models.ForeignKey(NiftiImage, on_delete=models.CASCADE, related_name='nifti_linearized')
    voxel_id = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
