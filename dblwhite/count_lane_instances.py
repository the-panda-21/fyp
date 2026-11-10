import json
import time
from pathlib import Path
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count

# ========== CONFIGURATION ==========

JSON_DIR = Path("/Users/ak/Documents/FYP/code/berkley_dataset/100k/test")
WORKERS = cpu_count()


# ========== PROCESS FILE ==========

def process_json(json_path):
    count = 0

    try:
        with open(json_path, "r") as f:
            data = json.load(f)

        for frame in data.get("frames", []):
            for obj in frame.get("objects", []):

                # ONLY count solid double-white markings
                if (
                    obj.get("category") == "lane/double white"
                    and obj.get("attributes", {}).get("style") == "solid"
                ):
                    count += 1

        return json_path.stem, count, None

    except Exception as e:
        return json_path.stem, 0, str(e)


# ========== MAIN ==========

def main():
    start = time.time()

    json_files = list(JSON_DIR.rglob("*.json"))

    print(f"Total JSON files found: {len(json_files):,}")
    print(f"Workers: {WORKERS}")
    print("Scanning...\n")

    total_instances = 0
    matching_images = []
    errors = 0

    with ProcessPoolExecutor(max_workers=WORKERS) as executor:
        for filename, count, error in executor.map(process_json, json_files):

            if error:
                errors += 1

            elif count > 0:
                total_instances += count
                matching_images.append(filename + ".jpg")

    # Save matching image filenames
    matching_images.sort()

    output_txt = JSON_DIR / "bdd100k_double_white_solid.txt"

    with open(output_txt, "w") as f:
        f.write("\n".join(matching_images))

    print("\n========== RESULTS ==========")
    print(f"Total JSON files scanned: {len(json_files):,}")
    print(f"Solid double-white instances: {total_instances:,}")
    print(f"Unique images containing them: {len(matching_images):,}")
    print(f"Errors: {errors}")
    print(f"Saved filenames to: {output_txt}")
    print(f"Total time: {time.time() - start:.2f} seconds")


if __name__ == "__main__":
    main()