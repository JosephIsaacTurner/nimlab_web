import os
from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import render
from django.db.models import Q
from pages.models import Dataset

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
    # This recursive helper function fetches contents of the given directory, excluding dotfiles/directories
    contents = {'files': [], 'directories': {}}
    try:
        with os.scandir(path) as it:
            for entry in it:
                if entry.name.startswith('.'):
                    # Skip dotfiles and hidden directories
                    continue
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
            'display_path': path if path else root_dir,
            'path': path, 'empty_directory': True,
            'root_dir': root_dir
        }
        return render(request, 'pages/file_explorer.html', context)

    # Check if the path is a file
    if os.path.isfile(full_path):
        return FileResponse(open(full_path, 'rb'))

    # Decide what to display based on whether we're at the root directory
    if not path:
        # At the root, list only non-hidden subdirectories
        directories = [d for d in os.listdir(full_path) if os.path.isdir(os.path.join(full_path, d)) and not d.startswith('.')]
        contents = {'files': [], 'directories': {d: {} for d in directories}}
    else:
        # Not at the root, recursively list all contents
        contents = get_directory_contents(full_path)

    empty_directory = not contents['files'] and not any(contents['directories'])
    if path:
        path = path.rstrip('/ ').rstrip() + '/'

    # Sort the 'files' and 'directories' arrays alphabetically
    sorted_files = sorted(contents['files'])
    sorted_directories = sorted(contents['directories'])
    if not path:
        # Create a dictionary with directory names as keys and another dictionary with dataset_name and in_database as values
        directory_info = {}

        for directory in sorted_directories:
            # Construct the full path to match with dataset_path in the database
            full_directory_path = os.path.join(path, directory) if path else directory
            # Query the database to check if the directory corresponds to a dataset_path
            test_path = "/published_datasets/" + full_directory_path
            in_database = Dataset.objects.filter(dataset_path=test_path).exists()
            # Get the dataset name if in the database, else use the directory name
            dataset_name = Dataset.objects.get(dataset_path=test_path).dataset_path.replace("/published_datasets/","") if in_database else directory
            
            # Update the directory info dictionary
            directory_info[directory] = {
                'dataset_name': dataset_name,
                'in_database': in_database
            }
        download_csv = False
    else:
        if Dataset.objects.filter(dataset_path=os.path.join(root_dir+path)).exists():
            download_csv = True
        else:
            download_csv = False

    sorted_contents = {
        'files': sorted_files,
        'directories': sorted_directories
    }


    context = {
        'download_csv': download_csv,
        'display_path': path if path else root_dir,
        'path': path,
        'contents': contents,
        'sorted_contents': sorted_contents,
        'empty_directory': empty_directory,
        'root_dir': root_dir,
        'directory_info': directory_info
    }

    return render(request, 'pages/file_explorer.html', context)
