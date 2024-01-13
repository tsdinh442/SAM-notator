"""
This file is part of SAM-notator.

SAM-notator is based on Segment-Anything, https://github.com/facebookresearch/segment-anything, which is licensed under the Apache License, Version 2.0.
See the LICENSE file for the full license text.
"""

import tkinter as tk
from object_selector import Samnotator


if __name__ == "__main__":
    annotation_path = 'output/'
    root = tk.Tk()
    app = Samnotator(root, annotation_path)
    root.mainloop()