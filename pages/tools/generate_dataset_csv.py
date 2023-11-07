import pandas as pd
from django.shortcuts import HttpResponse
from django.db import connection
import re 
# Define your queries
unique_conn_types = """
SELECT DISTINCT statistic, coordinate_system, hemisphere, connectome
FROM data_archives
WHERE type = 'connectivity'
"""

unique_roi_types = """
SELECT DISTINCT coordinate_system, hemisphere
FROM data_archives
WHERE type = 'roi'
"""

roi_ctes = []
roi_selects = []
roi_joins = []
roi_wheres = []

# Use a with statement to ensure the cursor is closed after use
with connection.cursor() as cursor:
    cursor.execute(unique_roi_types)
    unique_roi_rows = cursor.fetchall()

# Iterate over the fetched results
for coordinate_system, hemisphere in unique_roi_rows:
    display_hemisphere = "" if hemisphere == "unknown" else hemisphere
    field_name = f"roi_{coordinate_system}{display_hemisphere}"
    roi_cte = f"""
        {field_name} AS (
            SELECT
                da.file_path AS {field_name},
                s.id AS subject_id
            FROM subjects s
            LEFT JOIN data_archives da ON da.subject_id = s.id
            INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
            WHERE da.type = 'roi'
            AND da.coordinate_system = '{coordinate_system}'
            AND da.hemisphere = '{hemisphere}'
        ),
    """
    roi_ctes.append(roi_cte)

    roi_select = f"""
        {field_name}.{field_name},
    """
    roi_selects.append(roi_select)

    roi_join = f"""
        LEFT JOIN {field_name} ON {field_name}.subject_id = s.id
    """
    roi_joins.append(roi_join)

    roi_where = f"""
        {field_name}.{field_name} IS NOT NULL
    """
    roi_wheres.append(roi_where)

stat_ctes = []
stat_selects = []
stat_joins = []
stat_wheres = []

# Fetch the unique connection types in a similar way
with connection.cursor() as cursor:
    cursor.execute(unique_conn_types)
    unique_conn_rows = cursor.fetchall()

# Iterate over the fetched results
for statistic, coordinate_system, hemisphere, connectome in unique_conn_rows:
    display_hemisphere = "" if hemisphere == "unknown" else hemisphere
    field_name = f"{statistic}_{coordinate_system}{display_hemisphere}_{connectome}"
    conn_cte = f"""
        {field_name} AS (
            SELECT
                da.file_path AS {field_name},
                s.id AS subject_id
            FROM subjects s
            LEFT JOIN data_archives da ON da.subject_id = s.id
            INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
            WHERE da.type = 'connectivity'
            AND da.statistic = '{statistic}'
            AND da.coordinate_system = '{coordinate_system}'
            AND da.hemisphere = '{hemisphere}'
            AND da.connectome = '{connectome}'
        ),
    """
    stat_ctes.append(conn_cte)

    stat_select = f"""
        {field_name}.{field_name},
    """
    stat_selects.append(stat_select)

    stat_join = f"""
        LEFT JOIN {field_name} ON {field_name}.subject_id = s.id
    """
    stat_joins.append(stat_join)

    stat_where = f"""
        {field_name}.{field_name} IS NOT NULL
    """
    stat_wheres.append(stat_where)

# Function to remove last comma and any trailing whitespace
def remove_trailing_comma_and_whitespace(string):
    # This regular expression looks for a comma followed by any amount of whitespace
    # at the end of the string and replaces it with an empty string
    return re.sub(r',\s*$', '', string)

# Build the common table expressions (CTEs) without the final comma and trailing whitespace
cte_combined = "".join(roi_ctes) + "".join(stat_ctes)
cte_combined = remove_trailing_comma_and_whitespace(cte_combined)

# Build the select statements without the final comma and trailing whitespace
select_combined = "".join(roi_selects) + "".join(stat_selects)
select_combined = remove_trailing_comma_and_whitespace(select_combined)
# Combine everything into the final big query
big_query = f"""
WITH dataset_path_cte AS (
    SELECT id
    FROM datasets
    WHERE dataset_path = '$$dataset_path$$'
),
{cte_combined}
SELECT * FROM (
    SELECT
        s.subject as subject_name,
        {select_combined}
    FROM subjects s
    {"".join(roi_joins)}{"".join(stat_joins)}
    WHERE {" OR ".join(roi_wheres)} OR {" OR ".join(stat_wheres)}
) as sub_q_1;
"""

def generate_dataset_csv(request, dataset_path):
    if dataset_path == '':
        return HttpResponse('Dataset path not specified', status=400)
    # Replace the placeholder with the actual dataset path in the SQL query
    formatted_query = big_query.replace('$$dataset_path$$', dataset_path)
    # return HttpResponse(formatted_query, content_type='text/plain', status=200)
    # Execute the query and fetch data
    with connection.cursor() as cursor:
        cursor.execute(formatted_query)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        df = pd.DataFrame(rows, columns=columns)

    # Exclude columns that are entirely Null/None
    df = df.dropna(axis='columns', how='all')
    
    # Concatenate '/data/nimlab/dl_archive/NIMLAB_DATABASE' to all columns except 'subject_name'
    prefix = '/data/nimlab/NIMLAB_DATABASE'
    for column in df.columns:
        if column != 'subject_name':
            df[column] = df[column].apply(lambda x: f'{prefix}{x}' if pd.notnull(x) else x)

    # Convert DataFrame to CSV
    response = HttpResponse(content_type='text/csv')
    dataset_name = dataset_path.replace("/published_datasets/", "")
    response['Content-Disposition'] = f'attachment; filename="{dataset_name}_dataset.csv"'

    # Write the CSV data to the response object
    df.to_csv(path_or_buf=response, index=False)

    return response

