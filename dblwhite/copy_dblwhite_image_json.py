import shutil
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# ========== CONFIGURATION ==========

# Original BDD100K training images (70,000 JPG files)
IMAGE_SOURCE_DIR = Path("/Users/ak/Documents/FYP/code/berkley_dataset/100k_images/test")

# Original BDD100K training JSON annotations
JSON_SOURCE_DIR = Path("/Users/ak/Documents/FYP/code/berkley_dataset/100k/test")

# TXT containing the 2,092 matching JPG filenames
TXT_FILE = Path("/Users/ak/Documents/FYP/code/berkley_dataset/100k/test/bdd100k_double_white_solid.txt")

# Destination folder
OUTPUT_DIR = Path("/Users/ak/Documents/FYP/code/berkley_dataset/dblwhite/from_test")

# Multithreading
WORKERS = 8

# ========== OUTPUT FOLDERS ==========

IMAGE_OUTPUT_DIR = OUTPUT_DIR / "images"
JSON_OUTPUT_DIR = OUTPUT_DIR / "annotations"


# ========== COPY FUNCTION ==========

def copy_files(filename):

    # Convert filename to corresponding JSON filename
    image_name = Path(filename).name
    json_name = Path(image_name).with_suffix(".json").name

    image_source = IMAGE_SOURCE_DIR / image_name
    json_source = JSON_SOURCE_DIR / json_name

    image_destination = IMAGE_OUTPUT_DIR / image_name
    json_destination = JSON_OUTPUT_DIR / json_name

    # Check both files exist before copying
    if not image_source.is_file():
        return "missing_image", image_name

    if not json_source.is_file():
        return "missing_json", json_name

    try:
        shutil.copy2(image_source, image_destination)
        shutil.copy2(json_source, json_destination)

        return "copied", image_name

    except Exception as e:
        return "error", f"{image_name}: {e}"


# ========== MAIN ==========

def main():

    start_time = time.time()

    IMAGE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    JSON_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Read TXT file
    with open(TXT_FILE, "r") as f:
        filenames = [
            line.strip()
            for line in f
            if line.strip()
        ]

    # Remove duplicates
    filenames = list(dict.fromkeys(filenames))

    print(f"Total unique images: {len(filenames):,}")
    print(f"Image source: {IMAGE_SOURCE_DIR}")
    print(f"JSON source: {JSON_SOURCE_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Workers: {WORKERS}\n")

    copied = 0
    missing_images = []
    missing_json = []
    errors = []

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:

        futures = [
            executor.submit(copy_files, filename)
            for filename in filenames
        ]

        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Copying images + JSON",
            unit="pair"
        ):

            status, info = future.result()

            if status == "copied":
                copied += 1

            elif status == "missing_image":
                missing_images.append(info)

            elif status == "missing_json":
                missing_json.append(info)

            else:
                errors.append(info)

    elapsed = time.time() - start_time

    print("\n========== RESULTS ==========")
    print(f"Requested image/JSON pairs: {len(filenames):,}")
    print(f"Successfully copied pairs: {copied:,}")
    print(f"Missing images: {len(missing_images):,}")
    print(f"Missing JSON files: {len(missing_json):,}")
    print(f"Copy errors: {len(errors):,}")
    print(f"Total time: {elapsed:.2f} seconds")
    print(f"Output: {OUTPUT_DIR}")

    # Save error reports
    for report_name, items in [
        ("missing_images.txt", missing_images),
        ("missing_json.txt", missing_json),
        ("copy_errors.txt", errors),
    ]:
        if items:
            (OUTPUT_DIR / report_name).write_text(
                "\n".join(items) + "\n"
            )


if __name__ == "__main__":
    main()