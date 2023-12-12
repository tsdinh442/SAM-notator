import tkinter as tk
from object_selector import Image_Displayer


if __name__ == "__main__":
    #car_detector = 'models/car-detector.pt'  # replace your model here
    #model = YOLO(car_detector)
    root = tk.Tk()
    app = Image_Displayer(root)
    root.mainloop()