import os

# Folder containing the images
folder_path = "red_P"

# Get list of files
files = os.listdir(folder_path)

# Optional: sort files so numbering stays consistent
files.sort()

count = 1

for file in files:
    old_path = os.path.join(folder_path, file)

    # Skip if not a file
    if not os.path.isfile(old_path):
        continue

    # Get file extension (.jpg, .png etc.)
    ext = os.path.splitext(file)[1]

    new_name = f"red_image_{count}{ext}"
    new_path = os.path.join(folder_path, new_name)

    os.rename(old_path, new_path)

    print(f"{file} -> {new_name}")

    count += 1