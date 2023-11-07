# django models.py 
from django.db import models

class Dataset(models.Model):
    dataset_name = models.CharField(max_length=255, unique=True)
    BIDSVersion = models.CharField(max_length=255, blank=True, null=True)
    DatasetType = models.CharField(max_length=255, blank=True, null=True)
    creation_date = models.CharField(max_length=255, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    dataset_path = models.CharField(max_length=255, blank=True, null=True)

    # No direct ForeignKey fields to Tag, Author, Contact anymore; they are defined in the related models

    class Meta:
        db_table = 'datasets'

    def __str__(self):
        return self.dataset_name

# The Tag model now has a ManyToManyField linking it to Dataset
class Tag(models.Model):
    tag = models.CharField(max_length=255, blank=True, null=True)
    datasets = models.ManyToManyField(Dataset, related_name='tags', db_table='dataset_tag_association')

    class Meta:
        db_table = 'tags'

    def __str__(self):
        return self.tag

# The Author model now has a ManyToManyField linking it to Dataset
class Author(models.Model):
    author_email = models.CharField(max_length=255)
    datasets = models.ManyToManyField(Dataset, related_name='authors', db_table='dataset_author_association')

    class Meta:
        db_table = 'authors'

    def __str__(self):
        return self.author_email

# The Contact model now has a ManyToManyField linking it to Dataset
class Contact(models.Model):
    contact_email = models.CharField(max_length=255)
    datasets = models.ManyToManyField(Dataset, related_name='contacts', db_table='dataset_contact_association')

    class Meta:
        db_table = 'contacts'

    def __str__(self):
        return self.contact_email

class CitationSrc(models.Model):
    citation = models.TextField()
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='citations_src')

    class Meta:
        db_table = 'citations_src'
    def __str__(self):
        return self.citation

class CitationTo(models.Model):
    citation = models.TextField()
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='citations_to')

    class Meta:
        db_table = 'citations_to'

class Subject(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='subjects')
    subject_label = models.CharField(max_length=255)  # Assuming you want to rename 'subject' to 'subject_label'
    file_path = models.CharField(max_length=255)

    class Meta:
        db_table = 'subjects'

    def __str__(self):
        return self.subject_label

class DataArchive(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='data_archives')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='data_archives')
    type = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.CharField(max_length=255)
    file_extension = models.CharField(max_length=255, blank=True, null=True)
    coordinate_system = models.CharField(max_length=255, blank=True, null=True)
    connectome = models.CharField(max_length=255, blank=True, null=True)
    hemisphere = models.CharField(max_length=255, blank=True, null=True)
    statistic = models.CharField(max_length=255, blank=True, null=True)
    file_metadata_path = models.CharField(max_length=255, blank=True, null=True)
    md5 = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'data_archives'

    def __str__(self):
        return f"{self.type} - {self.file_path}"

