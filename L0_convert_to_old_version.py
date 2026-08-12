import os
import re


# ============================================================
# SETTINGS
# ============================================================

input_file = r"C:\Users\sciglob\Desktop\New folder\Blick-OFP-v1.8.75_src\Blick\data\L0\pandora315\Pandora315s1_GreenbeltMD_20260430_L0.txt"

output_file = r"C:\Users\sciglob\Desktop\New folder\Blick-OFP-v1.8.75_src\Blick\data\L0\pandora315\Pandora315s1_GreenbeltMD_20260430_L0_old.txt"

# ============================================================
# COLUMNS TO REMOVE
# ============================================================

# Original L0 columns to remove:
#   Column 23 = Humidity inside spectrometer box
#   Column 24 = Temperature inside spectrometer box
#   Column 25 = Pressure inside spectrometer box

# Convert 1-based column numbers to Python 0-based indices.
remove_indices = {22, 23, 24}


# ============================================================
# HEADER UPDATE FUNCTION
# ============================================================

def update_header_line(line):
    """
    Convert the new 27-metadata-column L0 header to the older
    24-metadata-column format.

    Removes header definitions for columns 23-25 and shifts
    subsequent column numbers down by 3.
    """

    stripped = line.strip()

    # --------------------------------------------------------
    # Remove the three new metadata descriptions
    # --------------------------------------------------------

    if stripped.startswith("Column 23:"):
        return None

    if stripped.startswith("Column 24:"):
        return None

    if stripped.startswith("Column 25:"):
        return None


    # --------------------------------------------------------
    # Single-column definitions
    #
    # Column 26 -> Column 23
    # Column 27 -> Column 24
    # --------------------------------------------------------

    match = re.match(r"^Column\s+(\d+):(.*)$", stripped)

    if match:
        column_number = int(match.group(1))
        description = match.group(2)

        if column_number > 25:
            column_number -= 3

        return "Column {}:{}\n".format(
            column_number,
            description
        )


    # --------------------------------------------------------
    # Column ranges
    #
    # Columns 28-2079   -> Columns 25-2076
    # Columns 2080-4131 -> Columns 2077-4128
    # --------------------------------------------------------

    match = re.match(
        r"^Columns\s+(\d+)-(\d+):(.*)$",
        stripped
    )

    if match:
        start_column = int(match.group(1))
        end_column = int(match.group(2))
        description = match.group(3)

        if start_column > 25:
            start_column -= 3

        if end_column > 25:
            end_column -= 3

        return "Columns {}-{}:{}\n".format(
            start_column,
            end_column,
            description
        )


    return line


# ============================================================
# CONVERT FILE
# ============================================================

measurement_count = 0
comment_count = 0
other_count = 0


# Use text mode, not binary mode.
#
# latin-1 is useful here because it maps every byte 1:1 and
# therefore avoids decoding failures from older Pandora files
# containing characters such as the degree symbol.
with open(
    input_file,
    "r",
    encoding="latin-1",
    newline=""
) as infile:

    with open(
        output_file,
        "w",
        encoding="latin-1",
        newline=""
    ) as outfile:

        for line in infile:

            # =================================================
            # HEADER
            # =================================================

            if line.startswith("Column ") or line.startswith("Columns "):

                updated_line = update_header_line(line)

                if updated_line is not None:
                    outfile.write(updated_line)

                continue


            # =================================================
            # SPLIT LINE
            # =================================================

            parts = line.split()


            # =================================================
            # COMMENT / INFO ROWS
            # =================================================
            #
            # Column 5 = "#"
            #
            # Example:
            #
            # FM 20260430T050523.6Z 1 1 # INFO ...
            #
            # These are NOT normal measurement records.
            # Leave the entire line untouched.
            # =================================================

            if len(parts) >= 5 and parts[4] == "#":

                outfile.write(line)

                comment_count += 1

                continue


            # =================================================
            # ACTUAL MEASUREMENT ROWS
            # =================================================
            #
            # New format:
            #
            # 1-27    = metadata
            # 28-2079 = raw spectrum
            # 2080+   = uncertainty
            #
            # A proper spectral measurement therefore has
            # thousands of fields.
            #
            # Using >100 fields prevents us from accidentally
            # modifying an unrelated metadata/header line.
            # =================================================

            if len(parts) > 100:

                original_column_count = len(parts)

                new_parts = [
                    value
                    for index, value in enumerate(parts)
                    if index not in remove_indices
                ]

                new_column_count = len(new_parts)


                # ---------------------------------------------
                # Safety check
                # ---------------------------------------------

                if new_column_count != original_column_count - 3:

                    raise RuntimeError(
                        "Unexpected column removal. "
                        "Original={}, New={}".format(
                            original_column_count,
                            new_column_count
                        )
                    )


                outfile.write(" ".join(new_parts) + "\n")

                measurement_count += 1

                continue


            # =================================================
            # EVERYTHING ELSE
            # =================================================

            outfile.write(line)

            other_count += 1


# ============================================================
# REPORT
# ============================================================

print("==============================================")
print("L0 conversion complete")
print("==============================================")

print("\nInput file:")
print(input_file)

print("\nOutput file:")
print(output_file)

print("\nMeasurement rows converted:")
print(measurement_count)

print("\nComment/INFO rows preserved:")
print(comment_count)

print("\nOther lines preserved:")
print(other_count)

print("\nRemoved original columns:")
print("23 = Humidity inside spectrometer box")
print("24 = Temperature inside spectrometer box")
print("25 = Pressure inside spectrometer box")

print("\nExpected converted header:")
print("Column 23 = Scale factor")
print("Column 24 = Uncertainty indicator")
print("Columns 25-2076 = Mean raw counts")
print("Columns 2077-4128 = Uncertainty")

print("\nDone.")
