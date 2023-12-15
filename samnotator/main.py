import tkinter as tk
from object_selector import Samnotator


if __name__ == "__main__":
    annotation_path = 'output/annotaions.txt'
    root = tk.Tk()
    app = Samnotator(root, annotation_path)
    root.mainloop()