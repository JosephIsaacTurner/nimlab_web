# django models.py 
from django.db import models

class Dataset(models.Model):
    dataset_name = models.CharField(max_length=255, unique=True)
    BIDSVersion = models.CharField(max_length=255, blank=True, null=True)
    DatasetType = models.CharField(max_length=255, blank=True, null=True)
    creation_date = models.CharField(max_length=255, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'datasets'

    def __str__(self):
        return self.dataset_name

class Tag(models.Model):
    tag = models.CharField(max_length=255, blank=True, null=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='tags')

    class Meta:
        db_table = 'tags'
    def __str__(self):
        return self.tag

class Author(models.Model):
    author_email = models.CharField(max_length=255)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='authors')

    class Meta:
        db_table = 'authors'
    def __str__(self):
        return self.author_email

class Contact(models.Model):
    contact_email = models.CharField(max_length=255)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='contacts')

    class Meta:
        db_table = 'contacts'

class CitationSrc(models.Model):
    citation = models.TextField()
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='citations_src')

    class Meta:
        db_table = 'citations_src'

class CitationTo(models.Model):
    citation = models.TextField()
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='citations_to')

    class Meta:
        db_table = 'citations_to'

class NiftiImage(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='nifti_images')
    path = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    md5 = models.CharField(max_length=255, blank=True, null=True)
    roi_size = models.IntegerField(blank=True, null=True)
    mask = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'nifti_images'

class NiftiLinearized(models.Model):
    nifti_image = models.ForeignKey(NiftiImage, on_delete=models.CASCADE, related_name='nifti_linearized')
    voxel_id = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
