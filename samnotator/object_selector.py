import tkinter
import cv2
import os
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
from sam import mask_generator, predictor
from pycocotools import mask as maskUtils


def get_random_colors(number_of_colors):
    random_colors = np.random.randint(0, 256, size=(number_of_colors, 3))
    return random_colors

class Image_Displayer:
    def __init__(self, root):

        self.root = root
        self.root.title('Image')

        self.image = None
        self.number_of_images = 0
        self.file_paths = None
        self.file_names = []
        self.current_image_index = 0

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

        self.number_of_images = len(self.file_paths)
        self.file_names = [os.path.basename(file_path) for file_path in self.root.tk.splitlist(self.file_paths)]

        if self.file_paths:

            self.resize_image()

            self.show_additional_buttons()

            self.display_image(self.image)


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


    def display_image(self, image):

        if image is not None:
            #image = self.image

            # Convert image from BGR to RGB for Tkinter
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            #image_rgb = image

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
            self.display_image(self.image)


    def show_prev_image(self):
        self.current_image_index -= 1
        self.check_image_index()

        if self.current_image_index < len(self.file_paths):
            self.resize_image()
            self.display_image(self.image)

class Interface(Image_Displayer):

    def __init__(self, root):
        super().__init__(root)
        self.selected_class = None

    def validate_input(self):
        """
        validating if inputs are integers greater than 0
        :return: None
        """
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
        """
        displaying the entry box asking users to enter how many classes there are
        :return:
        """
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
        """
        display entry boxes for users to enter the name of each class
        :return:
        """

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
        """
        :return:
        """

        self.canvas.delete('all')
        self.canvas.config()

        # hide not-needed buttons
        self.num_of_classes_label.pack_forget()
        self.num_of_classes_entry_box.pack_forget()
        self.num_of_classes_button.pack_forget()

    def show_additional_buttons(self):

        self.save_button.pack(side=tk.LEFT, padx=5, pady=10)
        self.drop_down_display()

        super().show_additional_buttons()


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

    def get_classes(self, classes):

        # get the name of each class
        self.classes = [cls.get() for cls in classes]

        self.hide_buttons()
        self.load_image()

    def update_class(self, *args):
        current_class = self.selected_class.get()
        self.current_class = self.classes.index(current_class)


class Samnotator(Interface):

    def __init__(self, root, annotation_path):

        super().__init__(root)
        self.colors = []
        self.anns = None
        self.mask = None
        self.masks = []
        self.masked_image = None
        self.contours = []
        self.annotated_images = []

        self.input_points = []
        self.input_labels = []

        # init buttons
        self.save_button = tk.Button(root, text="Save Annotations", command=self.write_annotations)
        self.add_button = tk.Button(self.root, text="Add", command=lambda: self.add_annotations(self.mask))

        self.load_button.pack_forget()

        self.front_page()

        self.annotation_path = annotation_path

    def load_image(self):
        super().load_image()
        self.annotated_images = [None] * self.number_of_images
        self.contours = [None] * self.number_of_images

    def display_image(self, image):
        super().display_image(image)
        self.canvas.bind("<Button-1>", self.selector)
        self.canvas.bind("<Button-2>", self.deselector)

    def get_classes(self, classes):

        super().get_classes(classes)

        # initialize annotations for each class with an empty list
        self.contours = [{idx: [] for idx in range(len(self.classes))} for i in range(self.number_of_images)]

        # assign a random color for each class
        self.colors = get_random_colors(len(self.classes))

    def draw_contours(self, mask):

        if self.annotated_images[self.current_image_index] is not None:
            image = np.copy(self.annotated_images[self.current_image_index])
        else:
            image = np.copy(self.image)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(image, contours, -1, (0, 0, 255), thickness=2)
        self.display_image(image)

    def selector(self, event):

        x, y = event.x, event.y
        self.input_points.append([x, y])
        self.input_labels.append(1)

        self.segment()

    def deselector(self, event):

        x, y = event.x, event.y

        self.input_points.append([x, y])
        self.input_labels.append(0)

        self.segment()

    def segment(self):

        input_point = np.array(self.input_points)
        input_label = np.array(self.input_labels)

        predictor.set_image(self.image)

        if len(input_point) == 1:
            masks, self.scores, self.logits = predictor.predict(
                point_coords=input_point,
                point_labels=input_label,
                multimask_output=True,
            )

        elif len(input_point) > 1:
            mask_input = self.logits[np.argmax(self.scores), :, :]  # Choose the model's best mask
            masks, _, _ = predictor.predict(
                point_coords=input_point,
                point_labels=input_label,
                mask_input=mask_input[None, :, :],
                multimask_output=False,
            )

        if len(input_point) == 0:
            self.mask = None
        else:
            self.mask = np.uint8(masks[0]) * 255

        self.draw_contours(self.mask)
        self.add_button.pack(side=tk.LEFT, padx=5, pady=10)


    def add_annotations(self, mask):
        if mask is not None:
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            self.contours[self.current_image_index][self.current_class].append(contours[0])

            # reset mask, input points and labels
            self.input_points = []
            self.input_labels = []
            self.mask = None
            color = tuple(int(c) for c in self.colors[self.current_class])

            if self.annotated_images[self.current_image_index] is not None:
                image = self.annotated_images[self.current_image_index]
            else:
                image = np.copy(self.image)

            cv2.drawContours(image, contours, -1, color=color, thickness=2)

            self.annotated_images[self.current_image_index] = image

            self.display_image(image)


    def write_annotations(self):


        for idx, item in enumerate(self.contours):
            file_name = self.file_names[idx]
            file_name = file_name.split('.')[0]
            file_name += '.txt'
            with open(self.annotation_path + file_name, 'w') as f:
                for cls, contours in item.items():
                    for contour in contours:
                        f.write(str(cls) + ' ')
                        # Get the bounding box coordinates of the contour
                        x, y, w, h = cv2.boundingRect(contour)
                        # Convert the coordinates to YOLO format and write to file
                        f.write('{:.6f} {:.6f} {:.6f} {:.6f}\n'.format((x + w / 2) / self.image.shape[1],
                                                                         (y + h / 2) / self.image.shape[0],
                                                                         w / self.image.shape[1],
                                                                         h / self.image.shape[0]))

    def show_next_image(self):
        self.current_image_index += 1
        self.check_image_index()

        if self.current_image_index < len(self.file_paths):
            self.resize_image()
            if self.annotated_images[self.current_image_index] is not None:
                self.display_image(self.annotated_images[self.current_image_index])
            else:
                self.display_image(self.image)


    def show_prev_image(self):
        self.current_image_index -= 1
        self.check_image_index()

        if self.current_image_index < len(self.file_paths):
            self.resize_image()
            if self.annotated_images[self.current_image_index] is not None:
                self.display_image(self.annotated_images[self.current_image_index])
            else:
                self.display_image(self.image)
