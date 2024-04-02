import os
from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import render
from django.db.models import Q
from pages.models import Dataset
import markdown
import json
from django.db import connection
from django.contrib.auth.decorators import login_required

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

def is_file(path):
    """Check if the path is a file."""
    return os.path.isfile(path)

def check_path_exists(path):
    """Check if the given path exists."""
    return os.path.exists(path)

def get_directory_contents(path):
    # This recursive helper function fetches contents of the given directory, excluding dotfiles/directories
    contents = {'files': [], 'directories': {}, 'text_content':{}}
    try:
        with os.scandir(path) as it:
            for entry in it:
                if entry.name.startswith('.'):
                    # Skip dotfiles and hidden directories
                    continue
                if entry.is_file():
                    # Check the file extension and read the content if it's .txt, .md, or .json
                    if entry.name.endswith(('.txt', '.md', '.json')):
                        with open(entry.path, 'r', encoding='utf-8') as file:
                            if entry.name.endswith('.json'):
                                try:
                                    # Attempt to parse and store the JSON data
                                    file_content = json.dumps(json.load(file), indent=4, sort_keys=True)
                                except json.JSONDecodeError:
                                    # If JSON is not formatted correctly, append the file name instead
                                    contents['files'].append(entry.name)
                                    continue  # Skip the rest of the loop for this file
                            else:
                                # Read the content of the file for .txt and .md
                                file_content = file.read()

                            contents['text_content'][entry.name] = file_content
                    else:
                        # If the file does not have one of the specified extensions, just append the file name
                        contents['files'].append(entry.name)
                elif entry.is_dir():
                    # recurse into directory
                    if any(substring.lower() in entry.name.lower() for substring in ["grafman", "mgh","trash"]):
                        pass
                    else:
                        contents['directories'][entry.name] = get_directory_contents(entry.path)
    except PermissionError:
        # Handle any permissions errors
        pass
    return contents

def list_directories(base_path, exclude_hidden=True, excluded_substrings=None):
    """List directories in the base path, optionally excluding hidden and specified directories."""
    if excluded_substrings is None:
        excluded_substrings = []
    directories = [
        d for d in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, d))
        and (not exclude_hidden or not d.startswith('.'))
        and all(substring.lower() not in d.lower() for substring in excluded_substrings)
    ]
    return directories

def directory_in_database(path):
    """
    Check if the directory is represented in the database, case-insensitively,
    and return a tuple of a boolean indicating if a match is found and the actual
    dataset_path from the database if a match is found.
    """
    # Extract the last part of the path to use in comparisons
    if path:
        path = os.path.normpath(path)
        path = os.path.basename(path)
    
    prefixes = [
        '/volume1/NIMLAB_DATABASE/published_datasets/',
        '/volume1/NIMLAB_DATABASE/control_datasets/'
    ]

    test_paths = [prefix + path for prefix in prefixes]

    # Craft the SQL query, using placeholders for parameters
    sql = """
    SELECT
        dataset_path, dataset_name
    FROM 
        datasets
    WHERE
        LOWER(dataset_path) = LOWER(%s)
        OR
        LOWER(dataset_path) = LOWER(%s)
    LIMIT 1;
    """

    with connection.cursor() as cursor:
        cursor.execute(sql, [test_paths[0], test_paths[1]])
        query_result = cursor.fetchone()

    if query_result:
        return True, query_result[0], query_result[1]
    else:
        return False, None, None

def get_directory_info(directory, path):
    """
    Get information about the directory to display, utilizing the directory_in_database
    function to check for the directory's presence in the database in a case-insensitive manner.
    """
    # Prepare the full directory path for case-insensitive comparison
    full_directory_path = os.path.join(path, directory).strip("/")

    # Check for the directory's presence in the database case-insensitively
    in_database, dataset_path, dataset_name = directory_in_database(full_directory_path)

    if not in_database:
        dataset_name = directory
        dataset_path = full_directory_path

    return {
        'dataset_name': dataset_name,
        'path_in_drive': full_directory_path,
        'path_in_db': dataset_path if in_database else '',
        'in_database': in_database
    }

@login_required
def file_explorer(request, path=''):
    """View function to explore files and directories."""
    root_dir = 'published_datasets'
    base_dir = os.path.join(settings.MEDIA_ROOT, root_dir)
    full_path = os.path.join(base_dir, path)

    if not check_path_exists(full_path):
        return render(request, 'pages/file_explorer.html', {
            'display_path': path if path else root_dir,
            'path': path, 'empty_directory': True,
            'root_dir': root_dir
        })

    if is_file(full_path):
        return FileResponse(open(full_path, 'rb'))

    contents = {'files': [], 'directories': {}}
    if not path:
        directories = list_directories(full_path, excluded_substrings=["grafman", "mgh", "trash"])
        contents['directories'] = {d: {} for d in directories}
    else:
        contents = get_directory_contents(full_path)

    directory_info = {d: get_directory_info(d, path) for d in contents['directories']}

    context = {
        'download_csv': directory_in_database(path)[0],
        'dataset_path_in_db': directory_in_database(path)[1],
        'display_path': path if path else root_dir,
        'path': path,
        'contents': contents,
        'empty_directory': not contents['files'] and not any(contents['directories']),
        'root_dir': root_dir,
        'directory_info': directory_info
    }

    return render(request, 'pages/file_explorer.html', context)