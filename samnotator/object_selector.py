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

            image = cv2.imread(self.file_paths[self.current_image_index])
            self.image = self.resize_image(image)

            self.show_additional_buttons()

            self.display_image()

    def resize_image(self, image):

        height, width, _ = image.shape
        self.ratio = width / height
        # define new image height
        self.HEIGHT = 600
        self.WIDTH = int(self.HEIGHT * self.ratio)

        return cv2.resize(image, (self.WIDTH, self.HEIGHT))

    def display_image(self, image=None):
        if self.image is not None:
            if image is None:
                image = self.image

            # Convert image from BGR to RGB for Tkinter
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

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
        self.anns = None
        self.masks = []
        self.contours = []
        # init button
        self.mask_button = tk.Button(root, text="Mask Generator", command=self.mask_generator)

        self.canvas.bind("<Button-1>", self.object_selector)
        self.canvas.bind("<Button-2>", self.object_deselector)


    def show_additional_buttons(self):
        self.mask_button.config(state='normal')
        self.mask_button.pack(side=tk.LEFT, padx=5, pady=10)
        super().show_additional_buttons()


    def mask_generator(self):

        image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.anns = mask_generator.generate(image)

        for idx, ann in enumerate(self.anns):
            mask = ann['segmentation']
            #mask = np.uint8(ann['segmentation']) * 255
            #cv2.imwrite(f'output/{idx}.jpg', mask)
            self.masks.append(mask)

        self.mask_button.config(state='disabled')
        self.masking()


    def object_selector(self, event):

        if self.anns is not None:
            x, y = event.x, event.y
            print(x, y)
            #x = int(x * self.ratio)
            #y = int(y * self.ratio)

            #x = int(self.canvas.canvasx(event.x) * self.ratio)
            #y = int(self.canvas.canvasy(event.y) * self.ratio)
            #print(x, y)

            masked_image = np.copy(self.masked_image)
            for mask in self.masks:
                if 0 <= y < mask.shape[0] and 0 <= x < mask.shape[1]:
                    if mask[y, x]:
                        if not any(np.array_equal(mask, arr) for arr in self.contours):
                            self.contours.append(mask)
                            self.draw_contours(masked_image)
                            break


    def object_deselector(self, event):
        print('right clicked')
        if len(self.contours) > 0:
            x, y = event.x, event.y

            #x = int(x * self.ratio)
            #y = int(y * self.ratio)

            masked_image = np.copy(self.masked_image)
            for mask in self.contours:
                if 0 <= y < mask.shape[0] and 0 <= x < mask.shape[1]:
                    if mask[y, x]:
                        # Iterate over the list and delete matching arrays
                        contours_copy = self.contours.copy()  # Create a copy to avoid modifying the list during iteration
                        for arr in contours_copy:
                            if isinstance(arr, np.ndarray):
                                if np.array_equal(arr, mask):
                                    print(True)
                                    self.contours.remove(arr)
                            elif any(isinstance(subarr, np.ndarray) and np.array_equal(subarr, mask) for subarr in arr):
                                print(True)
                                self.contours.remove(arr)
                                self.draw_contours(masked_image)
                                break


    def draw_contours(self, masked):

        if len(self.contours) > 0:
            for mask in self.contours:
                #mask = np.uint8(mask) * 255
                #contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                #cv2.drawContours(masked, contours, -1, (0, 0, 0), thickness=3)
                color = np.random.random_integers(0, 255, 3)
                #color_mask[mask] = color
                masked[mask] = color

            self.display_image(masked)


    def masking(self):

        if self.masks is not None:
            self.masked_image = np.copy(self.image)
            color_mask = np.zeros_like(self.image)

            for mask in self.masks:
                color = np.random.random_integers(0, 255, 3)
                color_mask[mask] = color

            # define opacity value
            opacity = 0.5

            # Add the colored polygon to the original image with opacity
            cv2.addWeighted(color_mask, opacity, self.masked_image, 1 - opacity, 0, self.masked_image)

        self.display_image(self.masked_image)






