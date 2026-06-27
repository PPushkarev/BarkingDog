# scripts/download_datasets.py
import urllib.request
from pathlib import Path

EXTERNAL_DATASETS = {
    "garak_injections": "https://raw.githubusercontent.com/NVIDIA/garak/main/garak/data/injections.txt",
    "garak_dan": "https://raw.githubusercontent.com/NVIDIA/garak/main/garak/data/dan.txt"
}


def main():
    external_dir = Path(__file__).parent.parent / "dataset" / "external"
    external_dir.mkdir(parents=True, exist_ok=True)

    print("=== BarkingDog Offline Dataset Fetcher ===")
    for name, url in EXTERNAL_DATASETS.items():
        # Saving with '_filtered.csv' suffix so loader.py picks it up automatically
        target_path = external_dir / f"{name}_filtered.csv"
        print(f"[*] Downloading {name}...")

        try:
            response = urllib.request.urlopen(url)
            content = response.read().decode('utf-8')
        except Exception as e:
            print(f"[!] Failed to download {name}: {e}")
            continue

        lines = content.splitlines()
        # Filter out empty lines and comments
        valid_payloads = [line.strip() for line in lines if line.strip() and not line.startswith("#")]

        if valid_payloads:
            # Format as CSV with 'prompt' column header
            with open(target_path, "w", encoding="utf-8") as f:
                f.write("prompt\n")
                for payload in valid_payloads:
                    # Escape quotes to prevent CSV parsing errors
                    safe_payload = payload.replace('"', '""')
                    f.write(f'"{safe_payload}"\n')
            print(f"  [+] Saved {len(valid_payloads)} payloads to {target_path.name}")
        else:
            print(f"  [-] No payloads found in {name}.")


if __name__ == "__main__":
    main()