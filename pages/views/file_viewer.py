import os
from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import render
import os
from django.http import Http404
from django.conf import settings
from django.shortcuts import render

from django.shortcuts import redirect

from django.contrib.auth.decorators import login_required
from accounts.decorators import is_cleared

@is_cleared
def file_viewer(request, path=''):
    # This function is used to view files in the browser
    # It checks to see if the file is a nifti file, and if so, it will display it in the browser
    # Otherwise, it will redirect to the file_explorer view
    root_dir = 'published_datasets'
    base_dir = os.path.join(settings.STATICFILES_DIRS[0], root_dir)
    
    # Construct the absolute path to the file
    file_path = os.path.join(base_dir, path)

    # Check if path is valid and contains a file
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise Http404("File not found.")

    # Check file extension type
    _, file_extension = os.path.splitext(file_path)

    is_nifti = False
    if file_extension == ".gz":
        # Further check for .nii.gz files (as it's a double extension)
        _, prev_extension = os.path.splitext(os.path.splitext(file_path)[0])
        if prev_extension == ".nii":
            is_nifti = True

    if not is_nifti:
        # Redirect to file_explorer with the path
        return redirect('file_explorer', path=path)

    file_path = file_path.replace("/app/", "")
    context = {
        "message": "hello world",
        "file_type": file_extension,
        "file_path": file_path,
        "is_nifti": is_nifti,
        "dataset_path": path.split("/")[0],
        "display_path": path
    }

    return render(
        request,
        'pages/file_viewer.html',
        context
    )
