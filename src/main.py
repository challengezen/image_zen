import tkinter as tk
from tkinter import filedialog, Label, Button, messagebox, OptionMenu, StringVar
from PIL import Image, ImageTk
from gradio_client import Client, handle_file
import os

# Initialize Gradio client
client = Client("levihsu/OOTDiffusion")


class PhotoUploaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Uploader and Processor")

        # Set the dimensions to match the Pixel 8 screen size (1080 x 2400 px)
        self.root.geometry("360x800")  # Approximate dimensions for mobile UI
        self.root.config(bg="white")  # Set white background

        self.photo1_path = None
        self.photo2_path = None

        # Dropdown for garment category
        self.category_var = StringVar(value="Upper-body")  # Default value
        self.category_label = Label(root, text="Select Garment Category", bg="white", font=("Arial", 14))
        self.category_label.grid(row=0, column=0, columnspan=2, pady=10)
        self.category_menu = OptionMenu(root, self.category_var, "Upper-body", "Lower-body", "Dress")
        self.category_menu.config(bg="blue", fg="white", font=("Arial", 12))
        self.category_menu.grid(row=1, column=0, columnspan=2, pady=5)

        # Photo 1 (Person Image)
        self.photo1_label = Label(root, text="Upload Person Image", width=30, height=2, bg="white", font=("Arial", 14))
        self.photo1_label.grid(row=2, column=0, pady=10)
        self.photo1_button = Button(root, text="Choose Person Image", command=self.upload_photo1, bg="blue", fg="white",
                                    font=("Arial", 12))
        self.photo1_button.grid(row=3, column=0, pady=5)
        self.photo1_canvas = Label(root, bg="white")  # Preview area for photo 1
        self.photo1_canvas.grid(row=4, column=0, pady=10)

        # Photo 2 (Garment Image)
        self.photo2_label = Label(root, text="Upload Garment Image", width=30, height=2, bg="white", font=("Arial", 14))
        self.photo2_label.grid(row=2, column=1, pady=10)
        self.photo2_button = Button(root, text="Choose Garment Image", command=self.upload_photo2, bg="blue",
                                    fg="white", font=("Arial", 12))
        self.photo2_button.grid(row=3, column=1, pady=5)
        self.photo2_canvas = Label(root, bg="white")  # Preview area for photo 2
        self.photo2_canvas.grid(row=4, column=1, pady=10)

        # Send button
        self.send_button = Button(root, text="Process with AI", command=self.send_to_api, state=tk.DISABLED, bg="blue",
                                  fg="white", font=("Arial", 14))
        self.send_button.grid(row=5, column=0, columnspan=2, pady=20)

        # Output image
        self.output_label = Label(root, text="Output Image", bg="white", font=("Arial", 14))
        self.output_label.grid(row=6, column=0, columnspan=2, pady=10)
        self.output_canvas = Label(root, bg="white")
        self.output_canvas.grid(row=7, column=0, columnspan=2, pady=10)

    def upload_photo1(self):
        self.photo1_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
        if self.photo1_path:
            self.photo1_label.config(text=f"Selected: {os.path.basename(self.photo1_path)}")
            self.display_image(self.photo1_path, self.photo1_canvas, 200)
        self.check_ready()

    def upload_photo2(self):
        self.photo2_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
        if self.photo2_path:
            self.photo2_label.config(text=f"Selected: {os.path.basename(self.photo2_path)}")
            self.display_image(self.photo2_path, self.photo2_canvas, 200)
        self.check_ready()

    def check_ready(self):
        if self.photo1_path and self.photo2_path:
            self.send_button.config(state=tk.NORMAL)

    def display_image(self, image_path, canvas, size):
        try:
            img = Image.open(image_path)
            img.thumbnail((size, size))
            photo = ImageTk.PhotoImage(img)
            canvas.config(image=photo)
            canvas.image = photo
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display image: {str(e)}")

    def send_to_api(self):
        try:
            if not os.path.exists(self.photo1_path) or not os.path.exists(self.photo2_path):
                raise FileNotFoundError("One or both files are missing.")

            category = self.category_var.get()  # Get selected category
            print(f"Category: {category}")
            print(f"Sending files:\n Person Image: {self.photo1_path}\n Garment Image: {self.photo2_path}")

            # Prepare API request
            inputs = {
                "vton_img": handle_file(self.photo1_path),
                "garm_img": handle_file(self.photo2_path),
                "category": category,  # Add category
                "n_samples": 1,
                "n_steps": 20,
                "image_scale": 2,
                "seed": -1
            }

            # Send API request
            result = client.predict(api_name="/process_dc", **inputs)

            print("API Response:", result)

            if isinstance(result, list) and len(result) > 0:
                image_path = result[0].get("image")
                if not image_path or not os.path.exists(image_path):
                    raise ValueError(f"Image file not found: {image_path}")

                # Load the output image
                output_image = Image.open(image_path)
            else:
                raise ValueError(f"Unexpected response format: {result}")

            # Display the output image
            output_image.thumbnail((200, 200))
            output_photo = ImageTk.PhotoImage(output_image)
            self.output_canvas.config(image=output_photo)
            self.output_canvas.image = output_photo

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            print(f"Error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoUploaderApp(root)
    root.mainloop()