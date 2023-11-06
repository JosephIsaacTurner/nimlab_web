import os
from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import render

# def file_explorer(request, path=''):
    # This function is used to view files in the browser
    # It takes in a path to a directory or a file; 
    # It will list all the subdirectories and files in the directory
    # However, I want to modify this function to display the contents of a dataset, including
    # all subdirectories and files within the dataset. Datasets are typically one level deeper
    # Than the root directory (published_datasets), and contain a dataset_description.json file
    # They have subject level directories, which contain connectivity/roi subdirs with files inside.
    # I want to show the structure of the whole dataset, including the subdirectories and included contents.
    # Example structure of the /published_datasets/ directory:
    # /published_datasets/
    # ├── dataset1/
    # │   ├── dataset_description.json
    # │   ├── sub01/
    # │   │   ├── connectivity/
    # │   │   │   ├── sub01_stat-t_conn.nii.gz
    # │   │   │   └── sub01_stat-t_conn.json
    # │   │   └── roi/
    # │   │       ├── sub01_LesionMask.nii.gz
    # │   │       └── sub01_LesionMask.json
    # │   └── sub02/
    # │       (and so on for other subdirectories and files)
    ### etc. 
    # Second type of structure of the /published_datasets/ directory:
    # This type of structure has multiple datasets within the upper level dataset directory
    # /published_datasets/
    # ├── dataset2/
    # │   ├── dataset_description.json
    # │   ├── sub_dataset1/
    # │   │   ├── sub01/
    # │   │   │   ├── connectivity/
    # │   │   │   │   ├── sub01_stat-t_conn.nii.gz
    # │   │   │   │   └── sub01_stat-t_conn.json
    # │   │   │   └── roi/
    # │   │   │       ├── sub01_LesionMask.nii.gz
    # │   │   │       └── sub01_LesionMask.json
    # │   │   └── sub02/
    # │   │       (and so on for other subdirectories and files)

def get_directory_contents(path):
    # This recursive helper function fetches contents of the given directory
    contents = {'files': [], 'directories': {}}
    try:
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file():
                    # append file name
                    contents['files'].append(entry.name)
                elif entry.is_dir():
                    # recurse into directory
                    contents['directories'][entry.name] = get_directory_contents(entry.path)
    except PermissionError:
        # Handle any permissions errors
        pass
    return contents

def file_explorer(request, path=''):
    root_dir = 'published_datasets'
    base_dir = os.path.join(settings.STATICFILES_DIRS[0], root_dir)

    # Full path to the directory or file
    full_path = os.path.join(base_dir, path)

    # Check if the path actually exists
    if not os.path.exists(full_path):
        context = {
            'display_path': path if path and path.strip() else root_dir,
            'path': path, 'empty_directory': True, 
            'root_dir': root_dir
        }
        return render(request, 'pages/file_explorer.html', context)

    # Check if the path is a file
    if os.path.isfile(full_path):
        return FileResponse(open(full_path, 'rb'))

    # Otherwise, assume it's a directory and list its contents recursively
    contents = get_directory_contents(full_path)

    empty_directory = not contents['files'] and not contents['directories']
    context = {
        'display_path': path if path and path.strip() else root_dir,
        'path': path, 'contents': contents, 'empty_directory': empty_directory,
        'root_dir': root_dir
    }
    return render(request, 'pages/file_explorer.html', context)
