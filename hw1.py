import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class PhotoEnhancerApp(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        parent.title("Homework 1: Image Adjuster")
        parent.geometry("800x600")

        self.grid(row=0, column=0, sticky="nsew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Frame for images
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, sticky="nsew")
        self.top_frame.rowconfigure(0, weight=1)
        self.top_frame.columnconfigure(0, weight=1)

        self.load_button = ctk.CTkButton(self.top_frame, corner_radius=10, text="Load Image", font=("Arial", 12),
                                         command=self.load_image, fg_color="#5989d7", width=120)
        self.load_button.grid(row=0, column=0)

        # Frame for images
        self.image_frame = ctk.CTkFrame(self)
        self.image_frame.grid(row=1, column=0, sticky="nsew")
        self.image_frame.columnconfigure(0, weight=1)
        self.image_frame.columnconfigure(1, weight=1)

        # Labels to display images side by side
        self.original_label = ctk.CTkLabel(self.image_frame, text="Original Image")
        self.original_label.grid(row=0, column=0, sticky="nsew")

        self.original_temp = ctk.CTkLabel(self.image_frame, text="")
        self.original_temp.grid(row=1, column=0, padx=10)

        self.processed_label = ctk.CTkLabel(self.image_frame, text="Processed Image")
        self.processed_label.grid(row=0, column=1, sticky="nsew")

        self.processed_temp = ctk.CTkLabel(self.image_frame, text="")
        self.processed_temp.grid(row=1, column=1, padx=10)


        # Frame for histograms
        self.histogram_frame = ctk.CTkFrame(self)
        self.histogram_frame.grid(row=2, column=0, sticky="nsew")
        self.histogram_frame.columnconfigure(0, weight=1)
        self.histogram_frame.columnconfigure(1, weight=1)

        # Frames to hold histogram canvases
        self.original_hist_frame = ctk.CTkFrame(self.histogram_frame)
        self.original_hist_frame.grid(row=0, column=0, padx=10, pady=20)

        self.processed_hist_frame = ctk.CTkFrame(self.histogram_frame)
        self.processed_hist_frame.grid(row=0, column=1, padx=10, pady=20)

        # Hold the original and processed images
        self.original_image = None
        self.processed_image = None
        self.original_canvas = None
        self.processed_canvas = None

        # Sliders Frame
        self.sliders_frame = ctk.CTkFrame(self)
        self.sliders_frame.grid(row=0, column=1, sticky="nsew")

        self.brightness_label = ctk.CTkLabel(self.sliders_frame, text="Brightness")
        self.brightness_label.grid(row=0, column=0)

        self.brightness_slider = ctk.CTkSlider(self.sliders_frame, from_=-100, to=100, command=self.update_brightness)
        self.brightness_slider.grid(row=1, column=0)

        self.contrast_label = ctk.CTkLabel(self.sliders_frame, text="Contrast")
        self.contrast_label.grid(row=2, column=0)

        self.contrast_slider = ctk.CTkSlider(self.sliders_frame, from_=-100, to=100, command=self.update_contrast)
        self.contrast_slider.grid(row=3, column=0)

        self.save_button = ctk.CTkButton(self.sliders_frame, text="Save Processed Image", font=("Arial", 12),
                                         fg_color="#5989d7", command=self.save_processed_image, state="disabled")
        self.save_button.grid(row=4, column=0, padx=10, pady=(70, 10))


    def load_image(self):
        """
        Open a file dialog to choose an image. Read it with OpenCV and display.
        Enable processing buttons after loading.
        """
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not file_path:
            return

        image = cv2.imread(file_path)
        if image is None:
            messagebox.showerror("Error", "Failed to load image.")
            return

        self.original_image = image
        self.processed_image = image.copy()

        self.display_image(image, self.original_temp)
        self.display_image(image, self.processed_temp)

        self.display_histogram(image, self.original_hist_frame,"Original Image Histogram")
        self.display_histogram(image, self.processed_hist_frame,"Processed Image Histogram")

        self.save_button.configure(state="normal")

    def display_image(self, img, label: ctk.CTkLabel):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)

        pil_img = pil_img.resize((400, 300), Image.LANCZOS)

        ctk_img = ctk.CTkImage(
            light_image=pil_img,
            dark_image=pil_img,
            size=(400, 300)
        )

        label.configure(image=ctk_img, text="")
        label.image = ctk_img

    def display_histogram(self, img, frame: ctk.CTkFrame, title: str):
        """
        Display histogram of the image inside a CTkFrame.
        """
        # Clear previous histogram
        for widget in frame.winfo_children():
            widget.destroy()

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        pixels = gray.ravel()

        fig, ax = plt.subplots(figsize=(4, 2))
        ax.hist(pixels, bins=256, range=(0, 256), color='black', alpha=0.7)
        ax.set_xlim([0, 256])
        ax.set_xlabel("Pixel Intensity")
        ax.set_ylabel("Frequency")
        ax.set_title(title)
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_brightness(self, value):
        self.after_idle(self.apply_brightness_contrast)

    def update_contrast(self, value):
        self.after_idle(self.apply_brightness_contrast)

    def apply_brightness_contrast(self):
        if self.original_image is None:
            return

        brightness = self.brightness_slider.get()
        contrast = self.contrast_slider.get()

        # Map contrast slider (-100 → 100) to alpha (0.0 → ~3.0)
        alpha = max(0.0, 1 + (contrast / 50))
        beta = brightness

        adjusted = cv2.convertScaleAbs(
            self.original_image,
            alpha=alpha,
            beta=beta
        )

        self.processed_image = adjusted

        # Update processed image
        self.display_image(adjusted, self.processed_temp)

        self.display_histogram(adjusted, self.processed_hist_frame,"Processed Image Histogram")

    def save_processed_image(self):
        if self.processed_image is None:
            messagebox.showwarning("No Image", "There is no processed image to save.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG Image", "*.png"),
                ("JPEG Image", "*.jpg *.jpeg"),
                ("Bitmap Image", "*.bmp")
            ]
        )

        if not file_path:
            return  # User cancelled

        try:
            success = cv2.imwrite(file_path, self.processed_image)
            if not success:
                raise IOError("cv2.imwrite failed")

            messagebox.showinfo("Saved", "Image saved successfully!")

        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save image:\n{e}")


def main():
    root = ctk.CTk()
    app = PhotoEnhancerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
