import os
import glob
import numpy as np
import pandas as pd
import xarray as xr

# =========================================================
# SETTINGS
# =========================================================

input_folder = r"C:\Users\sciglob\OneDrive - UMBC\4. SciGlob\Panndora_456\Lab_pandora\26_Aug_12_paper\Topomi"

output_csv = os.path.join(input_folder, "TROPOMI_OFFL_O3_Izana_5km_QA05.csv")

izana_lat = 28.3090
izana_lon = -16.4994

radius_km = 5.0
minimum_qa = 0.5

DU_CONVERSION = 2242.0


# =========================================================
# HAVERSINE DISTANCE
# =========================================================

def haversine_distance_km(lat1, lon1, lat2, lon2):
    R = 6371.0

    lat1_rad = np.deg2rad(lat1)
    lon1_rad = np.deg2rad(lon1)
    lat2_rad = np.deg2rad(lat2)
    lon2_rad = np.deg2rad(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2.0) ** 2
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))

    return R * c


# =========================================================
# FIND ALL OFFL O3 FILES
# =========================================================

files = sorted(glob.glob(os.path.join(input_folder, "S5P_OFFL_L2__O3*.nc")))

print("Number of OFFL O3 files found:", len(files))


# =========================================================
# PROCESS FILES
# =========================================================

summary_records = []

for file_path in files:
    print()
    print("Processing:", os.path.basename(file_path))

    try:
        ds = xr.open_dataset(file_path, group="PRODUCT")

        lat = ds["latitude"].values[0]
        lon = ds["longitude"].values[0]
        o3_mol_m2 = ds["ozone_total_vertical_column"].values[0]
        qa = ds["qa_value"].values[0]

        time_utc_scanline = ds["time_utc"].values[0]

        distance_km = haversine_distance_km(izana_lat, izana_lon, lat, lon)

        valid_mask = np.isfinite(lat) & np.isfinite(lon) & np.isfinite(o3_mol_m2) & np.isfinite(qa) & (distance_km <= radius_km) & (qa >= minimum_qa)

        selected_indices = np.where(valid_mask)

        if len(selected_indices[0]) == 0:
            print("No valid pixels found within radius and QA limits.")

            summary_records.append({
                "file_name": os.path.basename(file_path),
                "overpass_time_utc": pd.NaT,
                "number_of_pixels": 0,
                "mean_latitude": np.nan,
                "mean_longitude": np.nan,
                "closest_distance_km": np.nan,
                "farthest_distance_km": np.nan,
                "mean_qa": np.nan,
                "minimum_qa": np.nan,
                "maximum_qa": np.nan,
                "o3_min_du": np.nan,
                "o3_max_du": np.nan,
                "o3_mean_du": np.nan,
                "o3_median_du": np.nan,
                "o3_std_du": np.nan
            })

            ds.close()
            continue

        selected_lat = lat[valid_mask]
        selected_lon = lon[valid_mask]
        selected_o3_du = o3_mol_m2[valid_mask] * DU_CONVERSION
        selected_qa = qa[valid_mask]
        selected_distance = distance_km[valid_mask]

        selected_scanline_indices = selected_indices[0]

        selected_times = []

        for scanline_index in selected_scanline_indices:
            time_value = time_utc_scanline[scanline_index]
            parsed_time = pd.to_datetime(time_value, utc=True, errors="coerce")

            if not pd.isna(parsed_time):
                selected_times.append(parsed_time)

        if len(selected_times) > 0:
            selected_times = pd.DatetimeIndex(selected_times)
            overpass_time_utc = selected_times.min() + (selected_times.max() - selected_times.min()) / 2
        else:
            overpass_time_utc = pd.NaT

        record = {
            "file_name": os.path.basename(file_path),
            "overpass_time_utc": overpass_time_utc,
            "number_of_pixels": len(selected_o3_du),
            "mean_latitude": np.mean(selected_lat),
            "mean_longitude": np.mean(selected_lon),
            "closest_distance_km": np.min(selected_distance),
            "farthest_distance_km": np.max(selected_distance),
            "mean_qa": np.mean(selected_qa),
            "minimum_qa": np.min(selected_qa),
            "maximum_qa": np.max(selected_qa),
            "o3_min_du": np.min(selected_o3_du),
            "o3_max_du": np.max(selected_o3_du),
            "o3_mean_du": np.mean(selected_o3_du),
            "o3_median_du": np.median(selected_o3_du),
            "o3_std_du": np.std(selected_o3_du)
        }

        summary_records.append(record)

        print("Valid pixels:", record["number_of_pixels"])
        print("Overpass UTC:", record["overpass_time_utc"])
        print("Closest distance [km]:", record["closest_distance_km"])
        print("Mean QA:", record["mean_qa"])
        print("O3 minimum [DU]:", record["o3_min_du"])
        print("O3 maximum [DU]:", record["o3_max_du"])
        print("O3 mean [DU]:", record["o3_mean_du"])

        ds.close()

    except Exception as e:
        print("ERROR:", e)


# =========================================================
# CREATE SUMMARY DATAFRAME
# =========================================================

summary_df = pd.DataFrame(summary_records)

summary_df = summary_df.sort_values("overpass_time_utc").reset_index(drop=True)


# =========================================================
# FORMAT TIME
# =========================================================

if "overpass_time_utc" in summary_df.columns:
    summary_df["overpass_time_utc"] = pd.to_datetime(summary_df["overpass_time_utc"], utc=True, errors="coerce")


# =========================================================
# SAVE CSV
# =========================================================

summary_df.to_csv(output_csv, index=False)

print()
print("=========================================")
print("PROCESSING COMPLETE")
print("=========================================")
print("Files processed:", len(files))
print("Summary rows:", len(summary_df))
print("Output file:")
print(output_csv)


# =========================================================
# DISPLAY RESULTS
# =========================================================

print()
print(summary_df)
