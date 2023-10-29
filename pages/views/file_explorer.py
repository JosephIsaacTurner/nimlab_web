import os
from django.conf import settings
from django.http import HttpResponse, FileResponse
from django.shortcuts import render

def file_explorer(request, path=''):
    base_dir = os.path.join(settings.STATICFILES_DIRS[0], 'published_datasets')

    # Full path to the directory or file
    full_path = os.path.join(base_dir, path)

    # Check if the path is a file
    if os.path.isfile(full_path):
        return FileResponse(open(full_path, 'rb'))

    # Otherwise, assume it's a directory and list its contents
    entries = os.listdir(full_path)

    files = []
    directories = []

    for entry in entries:
        if os.path.isfile(os.path.join(full_path, entry)):
            files.append(entry)
        else:
            directories.append(entry)

    return render(request, 'pages/file_explorer.html', {'path': path, 'files': files, 'directories': directories})