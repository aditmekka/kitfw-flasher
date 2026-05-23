import json
import zipfile
import tempfile
from pathlib import Path

from core.manifest import from_dict

class PackageLoader:

    def load(self, package_path):

        temp_dir = Path(
            tempfile.mkdtemp()
        )

        with zipfile.ZipFile(package_path) as z:
            z.extractall(temp_dir)

        manifest_file = (
            temp_dir / "manifest.json"
        )

        with open(
            manifest_file,
            encoding="utf-8"
        ) as f:

            manifest = from_dict(
                json.load(f)
            )

        return temp_dir, manifest