# scripts/build.py

import os
import subprocess
import shutil
from pathlib import Path


def export_html(input_path: str, output_dir: str) -> None:
    output_path = os.path.join(output_dir, "eda.html")
    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        "marimo", "export", "html-wasm",
        "--mode", "run",
        "--no-show-code",
        input_path,
        "-o", output_path,
    ]
    subprocess.run(cmd, check=True)
    print(f"✅ Exported to {output_path}")

def copy_data(output_dir: str) -> None:
    src_data_path = Path(__file__).parent.parent / "data"
    dst_data_path = Path(output_dir) / "data"

    if src_data_path.exists():
        shutil.copytree(src_data_path, dst_data_path, dirs_exist_ok=True)
        print(f"✅ Copied data folder to {dst_data_path}")
    else:
        print("⚠️ No data folder found to copy.")


def generate_index(output_dir: str) -> None:
    index_html = f"""
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <title>EDA Report</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      </head>
      <body style="font-family: sans-serif; padding: 2rem;">
        <h1>EDA Report</h1>
        <a href="eda.html">Open eda.py notebook</a>
      </body>
    </html>
    """
    with open(os.path.join(output_dir, "index.html"), "w") as f:
        f.write(index_html.strip())
    print("✅ index.html created")


def main():
    export_html("eda.py", "_site")
    copy_data("_site")
    generate_index("_site")


if __name__ == "__main__":
    main()
