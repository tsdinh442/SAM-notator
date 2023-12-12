import tkinter
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from sam import mask_generator

class Image_Displayer:
    def __init__(self, root):

        self.root = root
        self.root.title('Image')

        self.image = None

        self.canvas = tkinter.Canvas(root, width=800, height=600, bg='white')
        self.canvas.pack()

        self.load_button = tk.Button(root, text="Select Images", command=self.load_image)
        self.load_button.pack(side=tk.LEFT, padx=5, pady=10)

        self.next_button = tk.Button(self.root, text="Next", command=self.show_next_image)
        self.next_button.pack_forget()

        self.prev_button = tk.Button(self.root, text="Previous", command=self.show_prev_image)
        self.prev_button.pack_forget()

    def load_image(self):
        self.file_paths = filedialog.askopenfilenames(title="Select Images",
                                                      filetypes=[("Image files", "*.png *.jpg *.jpeg")])

        if self.file_paths:
            self.current_image_index = 0
            self.show_additional_buttons()
            self.fit_image_to_frame()
            self.display_image()

    def fit_image_to_frame(self):

        image = cv2.imread(self.file_paths[self.current_image_index])

        # fit the image to the canvas
        image_height, image_width, _ = image.shape
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()

        scale = width / image_width
        self.image = cv2.resize(image, (int(image_width * scale), int(image_height * scale)))

    def display_image(self):
        if self.image is not None:
            # Convert image from BGR to RGB for Tkinter
            image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)

            # Convert to PhotoImage format
            image_tk = Image.fromarray(image_rgb)
            image_tk = ImageTk.PhotoImage(image_tk)

            # Update canvas
            self.canvas.config()
            self.canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
            self.canvas.image = image_tk

    def show_additional_buttons(self):
        self.check_image_index()
        self.next_button.pack(side=tk.RIGHT, padx=5, pady=10)
        self.prev_button.pack(side=tk.RIGHT, padx=5, pady=10)

    def check_image_index(self):

        self.prev_button.config(state='normal')
        self.next_button.config(state='normal')

        if self.current_image_index == 0:
            if self.current_image_index == len(self.file_paths) - 1:
                self.next_button.config(state='disabled')
            self.prev_button.config(state='disabled')

        elif self.current_image_index == len(self.file_paths) - 1:
            self.next_button.config(state='disabled')

    def show_next_image(self):
        self.current_image_index += 1
        self.check_image_index()

        # self.polygons_image = np.copy(self.image)
        if self.current_image_index < len(self.file_paths):
            self.fit_image_to_frame()
            self.display_image()

    def show_prev_image(self):
        self.current_image_index -= 1
        self.check_image_index()

        if self.current_image_index < len(self.file_paths):
            self.fit_image_to_frame()
            self.display_image()

class Mask_Displayer(Image_Displayer):

    def __init__(self, root):

        super().__init__(root)
        self.mask = None
        self.mask_button = tk.Button(root, text="Mask Generator", command=self.mask_generator)


    def show_additional_buttons(self):

        self.mask_button.pack(side=tk.LEFT, padx=5, pady=10)
        super().show_additional_buttons()

    def mask_generator(self):

        image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.mask = mask_generator.generate(image)
        
    def display_mask(self):
        pass




