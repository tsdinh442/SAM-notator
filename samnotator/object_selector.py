import tkinter
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
from sam import mask_generator, predictor
from pycocotools import mask as maskUtils


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

            self.resize_image()

            self.show_additional_buttons()

            self.display_image()


    def resize_image(self):

        image = cv2.imread(self.file_paths[self.current_image_index])

        height, width, _ = image.shape

        self.ratio = width / height
        # define new image height
        self.HEIGHT = 600
        self.WIDTH = int(self.HEIGHT * self.ratio)

        self.image = cv2.resize(image, (self.WIDTH, self.HEIGHT))


    def show_additional_buttons(self):
        self.check_image_index()
        self.next_button.pack(side=tk.RIGHT, padx=5, pady=10)
        self.prev_button.pack(side=tk.RIGHT, padx=5, pady=10)


    def display_image(self, image=None):

        if self.image is not None:
            if image is None:
                image = self.image

            # Convert image from BGR to RGB for Tkinter
            #image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_rgb = image

            # Convert to PhotoImage format
            image_tk = Image.fromarray(image_rgb)
            image_tk = ImageTk.PhotoImage(image_tk)

            # Update canvas
            self.canvas.config()
            self.canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
            self.canvas.image = image_tk


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
            self.resize_image()
            self.display_image()


    def show_prev_image(self):
        self.current_image_index -= 1
        self.check_image_index()

        if self.current_image_index < len(self.file_paths):
            self.resize_image()
            self.display_image()

class Samnotator(Image_Displayer):

    def __init__(self, root, annotation_path):

        super().__init__(root)
        self.anns = None
        self.masks = []
        self.masked_image = None
        self.contours = {}
        self.selected_masks = {}

        # init buttons
        self.mask_button = tk.Button(root, text="Mask Generator", command=self.generating_mask)
        self.save_button = tk.Button(root, text="Save Annotations", command=self.write_annotations)

        self.load_button.pack_forget()

        self.front_page()

        #self.canvas.bind("<Button-1>", self.object_selector)
        #self.canvas.bind("<Button-2>", self.object_deselector)

        self.annotation_path = annotation_path

        self.canvas.bind("<Button-1>", self.segment)


    def validate_input(self):
        '''
        validating if inputs are integers greater than 0
        :return: None
        '''
        try:
            # Try to convert the entered value to an integer
            value = int(self.num_of_classes_input.get())
            # Check if the value is greater than 0
            if value > 0:
                self.number_of_classes = value
                self.second_page()
            else:
                self.num_of_classes_input.set("Invalid input.")

        except ValueError:
            self.num_of_classes_input.set("Invalid input.")


    def front_page(self):
        '''
        displaying the entry box asking users to enter how many classes there are
        :return:
        '''
        # set default number of parking types
        self.number_of_classes = 1

        # label of the entry box
        self.num_of_classes_label = tk.Label(self.root, text="How many classes? ")
        self.num_of_classes_label.pack(side=tk.LEFT, padx=5, pady=10)

        # define entry box
        self.num_of_classes_input = tk.StringVar()
        self.num_of_classes_entry_box = tk.Entry(self.root, textvariable=self.num_of_classes_input)
        self.num_of_classes_entry_box.pack(side=tk.LEFT, padx=5, pady=10)

        # Submit button
        self.num_of_classes_button = tk.Button(self.root, text="Enter", command=self.validate_input)
        self.num_of_classes_button.pack(side=tk.LEFT, padx=5, pady=10)

    def second_page(self):
        '''
        display entry boxes for users to enter the name of each class
        :return:
        '''
        self.canvas.create_text(100, 30, text='Enter the name of each class', font=('Arial', 12), fill="black",
                                anchor=tk.NW)
        # define the location of each box
        starting_position_x, starting_position_y = 100, 50

        classes = []

        for i in range(self.number_of_classes):
            # display the label of each entry box
            label = tk.Label(self.canvas, text=f'Class {i + 1}: ')
            self.canvas.create_window(starting_position_x, starting_position_y + (i + 1) * 50,
                                      window=label, anchor=tk.NW)

            # diplay each entry box
            user_input = tk.StringVar()
            entry_box = tk.Entry(self.canvas, textvariable=user_input)
            self.canvas.create_window(starting_position_x + 100, starting_position_y + (i + 1) * 50,
                                      window=entry_box, anchor=tk.NW)
            classes.append(user_input)

            # dsiplay the submit button
            submit_button = tk.Button(self.canvas, text='Submit', command=lambda: self.get_classes(classes))
            self.canvas.create_window(starting_position_x, starting_position_y + (self.number_of_classes + 1) * 50,
                                      window=submit_button, anchor=tk.NW)

    def hide_buttons(self):
        '''
        display a button to select images
        :return:
        '''

        self.canvas.delete('all')
        self.canvas.config()
        #self.load_button.pack(side=tk.LEFT, padx=5, pady=10)

        # hide not-needed buttons
        self.num_of_classes_label.pack_forget()
        self.num_of_classes_entry_box.pack_forget()
        self.num_of_classes_button.pack_forget()


    def get_classes(self, classes):
        self.classes = [cls.get() for cls in classes]

        # initialize annotations for each class with an empty list
        self.selected_masks = {cls: [] for cls in self.classes}
        self.contours = {cls: [] for cls in self.classes}
        self.hide_buttons()
        self.load_image()

    def drop_down_display(self):

        # create labels
        dropdown_label = tk.Label(self.root, text="Select a class: ")
        dropdown_label.pack(side=tk.LEFT, padx=5, pady=10)

        # Create a StringVar to store the selected option
        self.selected_class = tk.StringVar()
        self.selected_class.trace_add("write", self.update_class)

        # Create a Combobox
        dropdown = ttk.Combobox(self.root, textvariable=self.selected_class)

        # Set options for the dropdown
        dropdown['values'] = self.classes

        # Set a default value for the dropdown
        dropdown.set(self.classes[0])

        # Place the dropdown on the window
        dropdown.pack(side=tk.LEFT, padx=5, pady=20)


    def update_class(self, *args):
        self.current_class = self.selected_class.get()
        if self.masked_image is not None:
            self.draw_contours(np.copy(self.masked_image))


    def show_additional_buttons(self):
        #self.mask_button.config(state='normal')
        self.mask_button.pack(side=tk.LEFT, padx=5, pady=10)
        self.save_button.pack(side=tk.LEFT, padx=5, pady=10)
        #if len(self.contours) > 0:
            #self.save_button.config(state='normal')
        #self.save_button.config(state='disabled')

        super().show_additional_buttons()


    def object_selector(self, event):

        masked_image = np.copy(self.masked_image)
        if self.anns is not None:
            x, y = event.x, event.y

            if 0 <= y < self.masks[0].shape[0] and 0 <= x < self.masks[0].shape[1]:
                for mask in self.masks:
                    if mask[y, x]:
                        m = np.uint8(mask) * 255
                        contours, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        if not any(np.array_equal(contours, arr) for arr in self.contours[self.current_class]):
                            self.contours[self.current_class].append(contours)
                            self.selected_masks[self.current_class].append(mask)
                            break

        self.draw_contours(masked_image)
        self.save_button.config(state='normal')

    def object_deselector(self, event):
        masked_image = np.copy(self.masked_image)
        if len(self.contours[self.current_class]) > 0:
            x, y = event.x, event.y

            if 0 <= y < self.masks[0].shape[0] and 0 <= x < self.masks[0].shape[1]:

                selected_masks = self.selected_masks[self.current_class]
                for idx, mask in enumerate(selected_masks):
                    if mask[y, x]:
                        self.contours[self.current_class].pop(idx)
                        break


        self.draw_contours(masked_image)
        if len(self.contours[self.current_class]) > 0:
            self.save_button.config(state='normal')

    def draw_contours(self, masked):

        if len(self.contours[self.current_class]) > 0:
            for contours in self.contours[self.current_class]:
                #mask = np.uint8(mask) * 255
                #contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(masked, contours, -1, (0, 0, 255), thickness=2)
                #self.annotations[self.current_class].append(contours)

        self.display_image(masked)

    def generating_mask(self):

        image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.anns = mask_generator.generate(image)

        for idx, ann in enumerate(self.anns):
            mask = ann['segmentation']
            self.masks.append(mask)

        self.drop_down_display()
        self.masking()

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
        #self.canvas.bind("<Button-1>", self.object_selector)
        #self.canvas.bind("<Button-2>", self.object_deselector)

    def segment(self, event):

        x, y = event.x, event.y

        input_point = np.array([[x, y]])
        input_label = np.array([1])

        predictor.set_image(self.image)

        masks, scores, logits = predictor.predict(
            point_coords=input_point,
            point_labels=input_label,
            multimask_output=True,
        )

        print(x, y)

        self.display_image(masks[0])

    def write_annotations(self):

        txt = ''
        with open(self.annotation_path, 'w') as f:
            for cls, masks in self.contours.items():
                mask = self.selected_masks[cls][0]
                for contours in masks:
                    f.write(str(self.classes.index(cls)) + ' ')
                    for contour in contours:
                        # Get the bounding box coordinates of the contour
                        x, y, w, h = cv2.boundingRect(contour)
                        # Convert the coordinates to YOLO format and write to file
                        f.write('{:.6f} {:.6f} {:.6f} {:.6f}\n'.format((x + w / 2) / mask.shape[1],
                                                                         (y + h / 2) / mask.shape[0],
                                                                         w / mask.shape[1],
                                                                         h / mask.shape[0]))



