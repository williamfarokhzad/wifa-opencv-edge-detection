# OpenCV Edge Detection: Tune Canny Thresholds in Python

[Full WIFA Robotics lesson](https://wifarobotics.com/learn/opencv-edge-detection/)

Use three grayscale scenes with known boundary locations to see when OpenCV Canny keeps a weak edge and when it finds noise. The project runs offline after installation. It uses no camera, robot or downloaded image dataset.

## From a new folder

Install Python 3.12. Download this repository as a ZIP from GitHub and extract it, or clone it with Git:

```sh
git clone https://github.com/williamfarokhzad/wifa-opencv-edge-detection.git
cd wifa-opencv-edge-detection
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, replace the last three lines with:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Use `.\.venv\Scripts\python.exe` wherever an example below says `python` if you did not activate the environment. The headless OpenCV wheel has no GUI, so this project prints JSON and optionally saves a PNG. No display window is required.

## Run the comparisons

```sh
python -m examples.compare
python edge_lab.py --scene steps --low 60 --high 220 --output edges.png
python edge_lab.py --image edges.png --low 40 --high 90
python -m unittest discover -s tests -v
```

For a real photo, replace the input with a saved image you can use. Running the example on its own edge PNG demonstrates the file input path only; an edge map is not a recommended input for inspection. Remove the old output or choose a new name before rerunning the save command.

| Scene | Thresholds, blur | Expected in the pinned environment |
| --- | --- | --- |
| Two isolated steps | 60/120, off | Both boundary bands cover 88 of 88 rows |
| Two isolated steps | 60/220, off | Weak band covers 0 rows; strong band covers 88 |
| Connected edge | 60/220, off | Weak lower band covers 37 of 37 selected rows |
| Connected edge | 180/220, off | Weak lower band covers 0 rows |
| Noisy step | 45/95, off | 4,797 off-band pixels over 88 rows |
| Noisy step | 45/95, 5 × 5 | 0 off-band pixels; 88 boundary rows retained |

Thresholds act on internal derivative magnitudes, not image brightness or a percentage. A strong gradient seeds an edge; a weaker surviving gradient can be retained when it connects to that seed. The output map identifies candidate boundaries, not complete objects. The summaries allow a narrow band around each known synthetic boundary and ignore four rows at the top and bottom. Real photos omit these truth metrics.

## Troubleshooting

* **No edges:** on `steps` start with 60/120 and no blur. On your image, lower the high threshold in controlled steps or check whether the edge is visible at the source resolution.
* **Too many edges:** compare the same thresholds with and without a 5 × 5 blur. Look for lost fine detail as well as fewer speckles.
* **Cannot import cv2:** install with the same interpreter used to run the script. Use a new virtual environment if another OpenCV wheel already supplies `cv2`.
* **Image error or existing output:** check the input path and use a new PNG name. The program does not overwrite a file.
* **Numbers differ:** confirm the pinned packages and use the included synthetic scenes before trying other photos.

## Files and reproducibility

`edge_lab.py` contains the simulator and CLI. `examples/compare.py` runs the six comparisons. Tests check geometry, hysteresis, noise reduction, brightness offset and file I/O. `diagrams/render.py` is the editable figure source and uses Pillow 13.0.0 as an optional authoring dependency. Install it with `python -m pip install Pillow==13.0.0` and run `python -m diagrams.render` from the project root. If the script cannot find the DejaVu Sans fonts, install them and set `EDGE_LAB_FONTS` to the directory containing the regular and bold TTF files.

The numbers above describe synthetic images only. Camera motion, lens blur, reflective surfaces and illumination changes can cause missed edges and false positives. Validate on saved production-like frames with independently labeled features before using the method for inspection. Do not connect this example to motion control.

References: [OpenCV Canny tutorial](https://docs.opencv.org/4.x/da/d22/tutorial_py_canny.html), [OpenCV GaussianBlur API](https://docs.opencv.org/4.x/d4/d86/group__imgproc__filter.html), [OpenCV Python wheel instructions](https://pypi.org/project/opencv-python-headless/).
