import pandas as pd
from django.shortcuts import HttpResponse
from django.db import connection

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

    roi_wheres = f"""
        {field_name}.{field_name} IS NOT NULL
    """
    roi_wheres.append(roi_wheres)

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

big_query = """
WITH dataset_path_cte AS (
    SELECT id
    FROM datasets
    WHERE dataset_path = '$$dataset_path$$'
),
""" + "".join(roi_ctes) + "".join(stat_ctes) + """
select * from (
SELECT
    s.subject as subject_name,
""" + "".join(roi_selects) + "".join(stat_selects) + """
FROM subjects s
""" + "".join(roi_joins) + "".join(stat_joins) + """
WHERE """ + " OR ".join(roi_wheres) + " OR " + " OR ".join(stat_wheres) + """
) as sub_q_1;
"""




# query = """
# WITH dataset_path_cte AS (
#     SELECT id
#     FROM datasets
#     WHERE dataset_path = '$$dataset_path$$'
# ),
# roi_2mm AS (
#     SELECT
#         da.file_path as roi_2mm,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'roi'
#     AND da.coordinate_system = '2mm'
# ),
# roi_1mm AS (
#     SELECT
#         da.file_path as roi_1mm,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'roi'
#     AND da.coordinate_system = '1mm'
# ),
# roi_original AS (
#     SELECT
#         da.file_path as roi_original,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'roi'
#     AND da.coordinate_system = 'original'
# ),
# avgRFz_2mm AS (
#     SELECT
#         da.file_path as avgRFz_2mm,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'connectivity'
#     AND da.statistic = 'avgRFz'
#     AND da.coordinate_system = '2mm'
# ),
# avgR_2mm AS (
#     SELECT
#         da.file_path as avgR_2mm,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'connectivity'
#     AND da.statistic = 'avgR'
#     AND da.coordinate_system = '2mm'
# ),
# t_stat_2mm AS (
#     SELECT
#         da.file_path as t_stat_2mm,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'connectivity'
#     AND da.statistic = 't'
#     AND da.coordinate_system = '2mm'
# ),
# avgRFz_1mm AS (
#     SELECT
#         da.file_path as avgRFz_1mm,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'connectivity'
#     AND da.statistic = 'avgRFz'
#     AND da.coordinate_system = '1mm'
# ),
# avgR_1mm AS (
#     SELECT
#         da.file_path as avgR_1mm,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'connectivity'
#     AND da.statistic = 'avgR'
#     AND da.coordinate_system = '1mm'
# ),
# t_stat_1mm AS (
#     SELECT
#         da.file_path as t_stat_1mm,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'connectivity'
#     AND da.statistic = 't'
#     AND da.coordinate_system = '1mm'
# ),
# surfLhAvgRFz_2mm AS (
#     SELECT
#         da.file_path as surfLhAvgRFz_2mm,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'connectivity'
#     AND da.statistic = 'surfLhAvgRFz'
#     AND da.coordinate_system = '2mm'
# ),
# strucSeed_2mm AS (
#     SELECT
#         da.file_path as strucSeed_2mm,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'connectivity'
#     AND da.statistic = 'strucSeed'
#     AND da.coordinate_system = '2mm'
# ),
# surfRhAvgRFz_2mm AS (
#     SELECT
#         da.file_path as surfRhAvgRFz_2mm,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'connectivity'
#     AND da.statistic = 'surfRhAvgRFz'
#     AND da.coordinate_system = '2mm'
# ),
# varR_2mm AS (
#     SELECT
#         da.file_path as varR_2mm,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'connectivity'
#     AND da.statistic = 'varR'
#     AND da.coordinate_system = '2mm'
# ),
# surfLhAvgR_2mm AS (
#     SELECT
#         da.file_path as surfLhAvgR_2mm,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'connectivity'
#     AND da.statistic = 'surfLhAvgR'
#     AND da.coordinate_system = '2mm'
# ),
# surfRhAvgR_2mm AS (
#     SELECT
#         da.file_path as surfRhAvgR_2mm,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'connectivity'
#     AND da.statistic = 'surfRhAvgR'
#     AND da.coordinate_system = '2mm'
# ),
# surfLhAvgRFz_1mm AS (
#     SELECT
#         da.file_path as surfLhAvgRFz_1mm,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'connectivity'
#     AND da.statistic = 'surfLhAvgRFz'
#     AND da.coordinate_system = '1mm'
# ),
# strucSeed_1mm AS (
#     SELECT
#         da.file_path as strucSeed_1mm,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'connectivity'
#     AND da.statistic = 'strucSeed'
#     AND da.coordinate_system = '1mm'
# ),
# surfRhAvgRFz_1mm AS (
#     SELECT
#         da.file_path as surfRhAvgRFz_1mm,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'connectivity'
#     AND da.statistic = 'surfRhAvgRFz'
#     AND da.coordinate_system = '1mm'
# ),
# varR_1mm AS (
#     SELECT
#         da.file_path as varR_1mm,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'connectivity'
#     AND da.statistic = 'varR'
#     AND da.coordinate_system = '1mm'
# ),
# surfLhAvgR_1mm AS (
#     SELECT
#         da.file_path as surfLhAvgR_1mm,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'connectivity'
#     AND da.statistic = 'surfLhAvgR'
#     AND da.coordinate_system = '1mm'
# ),
# surfRhAvgR_1mm AS (
#     SELECT
#         da.file_path as surfRhAvgR_1mm,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'connectivity'
#     AND da.statistic = 'surfRhAvgR'
#     AND da.coordinate_system = '1mm'
# ),


# surfLhAvgRFz_fs5 AS (
#     SELECT
#         da.file_path as surfLhAvgRFz_fs5,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'connectivity'
#     AND da.statistic = 'surfLhAvgRFz'
#     AND da.coordinate_system = 'fs5'
# ),
# strucSeed_fs5 AS (
#     SELECT
#         da.file_path as strucSeed_fs5,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'connectivity'
#     AND da.statistic = 'strucSeed'
#     AND da.coordinate_system = 'fs5'
# ),
# surfRhAvgRFz_fs5 AS (
#     SELECT
#         da.file_path as surfRhAvgRFz_fs5,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'connectivity'
#     AND da.statistic = 'surfRhAvgRFz'
#     AND da.coordinate_system = 'fs5'
# ),
# varR_fs5 AS (
#     SELECT
#         da.file_path as varR_fs5,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'connectivity'
#     AND da.statistic = 'varR'
#     AND da.coordinate_system = 'fs5'
# ),
# surfLhAvgR_fs5 AS (
#     SELECT
#         da.file_path as surfLhAvgR_fs5,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'connectivity'
#     AND da.statistic = 'surfLhAvgR'
#     AND da.coordinate_system = 'fs5'
# ),
# surfRhAvgR_fs5 AS (
#     SELECT
#         da.file_path as surfRhAvgR_fs5,
#         s.id as subject_id
#     FROM subjects s
#     LEFT JOIN data_archives da ON da.subject_id = s.id
#     INNER JOIN dataset_path_cte d ON d.id = s.dataset_id
#     WHERE da.type = 'connectivity'
#     AND da.statistic = 'surfRhAvgR'
#     AND da.coordinate_system = 'fs5'
# )

# select * from (
# SELECT
#     s.subject as subject_name,
#     roi_2mm.roi_2mm,
#     roi_1mm.roi_1mm,
#     roi_original.roi_original,
#     avgRFz_2mm.avgRFz_2mm,
#     avgR_2mm.avgR_2mm,
#     t_stat_2mm.t_stat_2mm,
#     avgRFz_1mm.avgRFz_1mm,
#     avgR_1mm.avgR_1mm,
#     t_stat_1mm.t_stat_1mm,
#     surfLhAvgRFz_2mm.surfLhAvgRFz_2mm,
#     strucSeed_2mm.strucSeed_2mm,
#     surfRhAvgRFz_2mm.surfRhAvgRFz_2mm,
#     varR_2mm.varR_2mm,
#     surfLhAvgR_2mm.surfLhAvgR_2mm,
#     surfRhAvgR_2mm.surfRhAvgR_2mm,
#     surfLhAvgRFz_1mm.surfLhAvgRFz_1mm,
#     strucSeed_1mm.strucSeed_1mm,
#     surfRhAvgRFz_1mm.surfRhAvgRFz_1mm,
#     varR_1mm.varR_1mm,
#     surfLhAvgR_1mm.surfLhAvgR_1mm,
#     surfRhAvgR_1mm.surfRhAvgR_1mm,
#     surfLhAvgRFz_fs5.surfLhAvgRFz_fs5,
#     strucSeed_fs5.strucSeed_fs5,
#     surfRhAvgRFz_fs5.surfRhAvgRFz_fs5,
#     varR_fs5.varR_fs5,
#     surfLhAvgR_fs5.surfLhAvgR_fs5,
#     surfRhAvgR_fs5.surfRhAvgR_fs5
# FROM subjects s
# LEFT JOIN roi_2mm ON roi_2mm.subject_id = s.id
# LEFT JOIN roi_1mm ON roi_1mm.subject_id = s.id
# LEFT JOIN roi_original ON roi_original.subject_id = s.id
# LEFT JOIN avgRFz_2mm ON avgRFz_2mm.subject_id = s.id
# LEFT JOIN avgR_2mm ON avgR_2mm.subject_id = s.id
# LEFT JOIN t_stat_2mm ON t_stat_2mm.subject_id = s.id
# LEFT JOIN avgRFz_1mm ON avgRFz_1mm.subject_id = s.id
# LEFT JOIN avgR_1mm ON avgR_1mm.subject_id = s.id
# LEFT JOIN t_stat_1mm ON t_stat_1mm.subject_id = s.id
# LEFT JOIN surfLhAvgRFz_2mm ON surfLhAvgRFz_2mm.subject_id = s.id
# LEFT JOIN strucSeed_2mm ON strucSeed_2mm.subject_id = s.id
# LEFT JOIN surfRhAvgRFz_2mm ON surfRhAvgRFz_2mm.subject_id = s.id
# LEFT JOIN varR_2mm ON varR_2mm.subject_id = s.id
# LEFT JOIN surfLhAvgR_2mm ON surfLhAvgR_2mm.subject_id = s.id
# LEFT JOIN surfRhAvgR_2mm ON surfRhAvgR_2mm.subject_id = s.id
# LEFT JOIN surfLhAvgRFz_1mm ON surfLhAvgRFz_1mm.subject_id = s.id
# LEFT JOIN strucSeed_1mm ON strucSeed_1mm.subject_id = s.id
# LEFT JOIN surfRhAvgRFz_1mm ON surfRhAvgRFz_1mm.subject_id = s.id
# LEFT JOIN varR_1mm ON varR_1mm.subject_id = s.id
# LEFT JOIN surfLhAvgR_1mm ON surfLhAvgR_1mm.subject_id = s.id
# LEFT JOIN surfRhAvgR_1mm ON surfRhAvgR_1mm.subject_id = s.id
# LEFT JOIN surfLhAvgRFz_fs5 ON surfLhAvgRFz_fs5.subject_id = s.id
# LEFT JOIN strucSeed_fs5 ON strucSeed_fs5.subject_id = s.id
# LEFT JOIN surfRhAvgRFz_fs5 ON surfRhAvgRFz_fs5.subject_id = s.id
# LEFT JOIN varR_fs5 ON varR_fs5.subject_id = s.id
# LEFT JOIN surfLhAvgR_fs5 ON surfLhAvgR_fs5.subject_id = s.id
# LEFT JOIN surfRhAvgR_fs5 ON surfRhAvgR_fs5.subject_id = s.id

# WHERE roi_2mm.roi_2mm IS NOT NULL 
#    OR roi_1mm.roi_1mm IS NOT NULL 
#    OR roi_original.roi_original IS NOT NULL 
#    OR avgRFz_2mm.avgRFz_2mm IS NOT NULL
#    OR avgR_2mm.avgR_2mm IS NOT NULL
#    OR t_stat_2mm.t_stat_2mm IS NOT NULL
#    OR avgRFz_1mm.avgRFz_1mm IS NOT NULL
#    OR avgR_1mm.avgR_1mm IS NOT NULL
#    OR t_stat_1mm.t_stat_1mm IS NOT NULL
#    OR surfLhAvgRFz_2mm.surfLhAvgRFz_2mm IS NOT NULL
#    OR strucSeed_2mm.strucSeed_2mm IS NOT NULL
#    OR surfRhAvgRFz_2mm.surfRhAvgRFz_2mm IS NOT NULL
#    OR varR_2mm.varR_2mm IS NOT NULL
#    OR surfLhAvgR_2mm.surfLhAvgR_2mm IS NOT NULL
#    OR surfRhAvgR_2mm.surfRhAvgR_2mm IS NOT NULL
#    OR surfLhAvgRFz_1mm.surfLhAvgRFz_1mm IS NOT NULL
#    OR strucSeed_1mm.strucSeed_1mm IS NOT NULL
#    OR surfRhAvgRFz_1mm.surfRhAvgRFz_1mm IS NOT NULL
#    OR varR_1mm.varR_1mm IS NOT NULL
#    OR surfLhAvgR_1mm.surfLhAvgR_1mm IS NOT NULL
#    OR surfRhAvgR_1mm.surfRhAvgR_1mm IS NOT NULL
#    OR surfLhAvgRFz_fs5.surfLhAvgRFz_fs5 IS NOT NULL
#    OR strucSeed_fs5.strucSeed_fs5 IS NOT NULL
#    OR surfRhAvgRFz_fs5.surfRhAvgRFz_fs5 IS NOT NULL
#    OR varR_fs5.varR_fs5 IS NOT NULL
#    OR surfLhAvgR_fs5.surfLhAvgR_fs5 IS NOT NULL
#    OR surfRhAvgR_fs5.surfRhAvgR_fs5 IS NOT null) as sub_q_1;
# """

def generate_dataset_csv(request, dataset_path):
    if dataset_path == '':
        return HttpResponse('Dataset path not specified', status=400)
    # Replace the placeholder with the actual dataset path in the SQL query
    formatted_query = big_query.replace('$$dataset_path$$', dataset_path)
    return HttpResponse(formatted_query, content_type='text/plain', status=200)
    # # Execute the query and fetch data
    # with connection.cursor() as cursor:
    #     cursor.execute(formatted_query)
    #     rows = cursor.fetchall()
    #     columns = [col[0] for col in cursor.description]
    #     df = pd.DataFrame(rows, columns=columns)

    # # Exclude columns that are entirely Null/None
    # df = df.dropna(axis='columns', how='all')
    
    # # Concatenate '/data/nimlab/dl_archive/NIMLAB_DATABASE' to all columns except 'subject_name'
    # prefix = '/data/nimlab/NIMLAB_DATABASE'
    # for column in df.columns:
    #     if column != 'subject_name':
    #         df[column] = df[column].apply(lambda x: f'{prefix}{x}' if pd.notnull(x) else x)

    # # Convert DataFrame to CSV
    # response = HttpResponse(content_type='text/csv')
    # dataset_name = dataset_path.replace("/published_datasets/", "")
    # response['Content-Disposition'] = f'attachment; filename="{dataset_name}_dataset.csv"'

    # # Write the CSV data to the response object
    # df.to_csv(path_or_buf=response, index=False)

    # return response

