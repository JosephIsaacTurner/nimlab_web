import os
# import hashlib
import numpy as np
import pandas as pd
from bids import BIDSLayout

FSL_MNI152_2MM_AFFINE = np.array(
    [
        [-2.0, 0.0, 0.0, 90.0],
        [0.0, 2.0, 0.0, -126.0],
        [0.0, 0.0, 2.0, -72.0],
        [0.0, 0.0, 0.0, 1.0],
    ]
)

FSL_MNI152_1MM_AFFINE = np.array(
    [
        [-1.0, 0.0, 0.0, 90.0],
        [0.0, 1.0, 0.0, -126.0],
        [0.0, 0.0, 1.0, -72.0],
        [0.0, 0.0, 0.0, 1.0],
    ]
)

FSAVERAGE_SHAPES = {"fs5": (10242,), "fs6": (40962,), "fs7": (163842,)}

FSAVERAGE_NAMES = {
    "fs5": "fsaverage5",
    "fs6": "fsaverage6",
    "fs7": "fsaverage7",
}


# def hash_file(path):
#     hasher = hashlib.md5()
#     with open(path, "rb") as afile:
#         buf = afile.read()
#         hasher.update(buf)
#     return hasher.hexdigest()

def generate_dataset_csv(project_path, project_name, vol_spaces, surf_spaces, lesion_type):
    """
    Generate ready-to-use csv within the dataset for safety.
    """

    # Default values for entities
    defaults = {
        "coordinateSystem": "2mm",
        "hemisphere": "L",
    }

    # Load BIDSLayout and dataframe
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(parent_dir, 'connectivity_config.json')
    
    archive_df = BIDSLayout(
        project_path,
        validate=False,
        config=config_path,
    ).to_df()
    
    # Apply default values to the dataframe
    for key, value in defaults.items():
        if key not in archive_df.columns:
            archive_df[key] = value
        else:
            archive_df[key].fillna(value, inplace=True)
    
    # Filter files with statistics and valid extensions
    conn_files = archive_df[
        (~archive_df["statistic"].isna())
        & archive_df["extension"].isin([
            ".nii.gz", ".gii", ".mat", ".trk.gz", ".connectivity.mat",
            ".txt", ".connectogram.txt", ".node", ".edge", ".trk.gz.tdi.nii.gz"
        ])
    ]
    print(archive_df.columns)
    conn_csv = pd.DataFrame()
    conn_csv["dataset"] = [project_name] * len(conn_files["subject"].unique())
    conn_csv["subject"] = conn_files["subject"].unique()

    # Get original ROI columns
    if lesion_type == "volume":
        conn_csv["orig_roi_vol"] = list(
            archive_df["path"][
                (archive_df["datatype"] == "roi")
                & (
                    (archive_df["extension"] == ".nii.gz")
                    | (archive_df["extension"] == ".gii")
                )
                & (archive_df["coordinateSystem"] == "original")
            ]
        )
    elif lesion_type == "surface":
        conn_csv["orig_roi_surf_lh"] = list(
            archive_df["path"][
                (archive_df["datatype"] == "roi")
                & (
                    (archive_df["extension"] == ".nii.gz")
                    | (archive_df["extension"] == ".gii")
                )
                & (archive_df["coordinateSystem"] == "original")
                & (archive_df["hemisphere"] == "L")
            ]
        )
        conn_csv["orig_roi_surf_rh"] = list(
            archive_df["path"][
                (archive_df["datatype"] == "roi")
                & (
                    (archive_df["extension"] == ".nii.gz")
                    | (archive_df["extension"] == ".gii")
                )
                & (archive_df["coordinateSystem"] == "original")
                & (archive_df["hemisphere"] == "R")
            ]
        )

    # Get resliced/resampled ROI columns
    for space in vol_spaces["input"]:
        conn_csv[f"roi_{space}"] = list(
            archive_df["path"][
                (archive_df["datatype"] == "roi")
                & (archive_df["extension"] == ".nii.gz")
                & (archive_df["coordinateSystem"] == space)
            ]
        )
    for space in surf_spaces["input"]:
        for hemisphere in ["L", "R"]:
            conn_csv[f"roi_{space}_{hemisphere}"] = list(
                archive_df["path"][
                    (archive_df["datatype"] == "roi")
                    & (archive_df["extension"] == ".gii")
                    & (archive_df["coordinateSystem"] == space)
                    & (archive_df["hemisphere"] == hemisphere)
                ]
            )

    for s in conn_files["statistic"].unique():
        files = list(
            conn_files["path"][
                (conn_files["statistic"] == s) & (conn_files["extension"] != ".json")
            ]
        )
        conn_csv[s] = files

    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Define the path for the new csv file within the script's directory
    csv_file_path = os.path.join(script_dir, f"{project_name}_filelist.csv")

    # Write the DataFrame to a CSV file in the script's directory
    conn_csv.to_csv(csv_file_path, index=False)

if __name__ == "__main__":
    
    project_path = "/app/static/published_datasets/joutsa_2022_nature_medicine_addiction_remission_rochester_lesions_yeo1000/"
    project_name = "juho_addiction_rochester_lesions_yeo1000"
    vol_spaces = {"input": ["2mm"], "output": ["2mm"]}
    surf_spaces = {"input": ["fs5"], "output": ["fs5"]}
    lesion_type = "volume" # or surface
    generate_dataset_csv(project_path, project_name, vol_spaces, surf_spaces, lesion_type)
    print("done")
