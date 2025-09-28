import numpy as np
import json
from pathlib import Path
import os


def mock_handled_images():
	json_path = Path(os.getenv("PROJECT_ROOT")) / "tests" / "mock_data" / "handed_image.json"
	with open(json_path, 'r') as file:
		handled_images = json.load(file)

	restored = [
		{k: (np.array(v) if isinstance(v, list) else v) for k, v in d.items()}
		for d in handled_images
	]

	return restored
