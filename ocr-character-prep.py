import os
import cv2
import numpy as np
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class CharacterExtractor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Character Grid Extractor")
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        self.image_path = None
        
        self.create_gui()
        
    def create_gui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(main_frame, text="Character Grid Extractor", font=("Arial", 16, "bold")).grid(row=0, column=0, pady=(0, 20))
        
        self.image_label = ttk.Label(main_frame, text="No image selected", foreground="gray")
        self.image_label.grid(row=1, column=0, pady=(0, 10))
        
        ttk.Button(main_frame, text="Select Character Grid Image", command=self.select_image, width=25).grid(row=2, column=0, pady=(0, 20))
        
        self.process_btn = ttk.Button(main_frame, text="Extract Characters", command=self.extract_characters, width=25, state="disabled")
        self.process_btn.grid(row=3, column=0, pady=(0, 10))
        
        self.status_label = ttk.Label(main_frame, text="Select an image to start", foreground="blue")
        self.status_label.grid(row=4, column=0)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Select character grid image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.image_path = file_path
            filename = os.path.basename(file_path)
            self.image_label.config(text=f"Selected: {filename}", foreground="black")
            self.process_btn.config(state="normal")
            self.status_label.config(text="Ready to extract characters", foreground="green")
    
    def detect_grid_lines(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, 10)
        
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
        
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
        
        return horizontal_lines, vertical_lines
    
    def find_grid_coordinates(self, horizontal_lines, vertical_lines):
        horizontal_sum = np.sum(horizontal_lines, axis=1)
        h_peaks = []
        for i in range(1, len(horizontal_sum)-1):
            if horizontal_sum[i] > np.mean(horizontal_sum) * 2:
                if not h_peaks or i - h_peaks[-1] > 20:  
                    h_peaks.append(i)
        
        vertical_sum = np.sum(vertical_lines, axis=0)
        v_peaks = []
        for i in range(1, len(vertical_sum)-1):
            if vertical_sum[i] > np.mean(vertical_sum) * 2:
                if not v_peaks or i - v_peaks[-1] > 20:  
                    v_peaks.append(i)
        
        return sorted(h_peaks), sorted(v_peaks)
    
    def extract_character_cells(self, image, h_lines, v_lines):
        characters = []
        cell_count = 0
        
        # Create output folder
        base_name = os.path.splitext(os.path.basename(self.image_path))[0]
        output_folder = os.path.join(os.path.dirname(self.image_path), f"{base_name}_characters")
        
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        print(f"Found {len(h_lines)-1} rows and {len(v_lines)-1} columns")
        print(f"Extracting characters to: {output_folder}")
        
        for row in range(len(h_lines) - 1):
            for col in range(len(v_lines) - 1):
                y1 = h_lines[row] + 2
                y2 = h_lines[row + 1] - 2
                x1 = v_lines[col] + 2
                x2 = v_lines[col + 1] - 2
                
                cell = image[y1:y2, x1:x2]
                
                if cell.size > 0:
                    cell_pil = Image.fromarray(cv2.cvtColor(cell, cv2.COLOR_BGR2RGB))
                    
                    cell_count += 1
                    filename = f"char_{cell_count:03d}.png"
                    filepath = os.path.join(output_folder, filename)
                    cell_pil.save(filepath)
                    
                    print(f"Saved: {filename} (Size: {cell.shape[1]}x{cell.shape[0]})")
        
        return output_folder, cell_count
    
    def extract_characters(self):
        if not self.image_path:
            messagebox.showerror("Error", "Please select an image first!")
            return
        
        try:
            self.status_label.config(text="Processing image...", foreground="orange")
            self.root.update()
            
            image = cv2.imread(self.image_path)
            if image is None:
                messagebox.showerror("Error", "Could not load the image!")
                return
            
            print(f"Processing image: {self.image_path}")
            print(f"Image size: {image.shape[1]}x{image.shape[0]}")
            
            self.status_label.config(text="Detecting grid lines...", foreground="orange")
            self.root.update()
            
            horizontal_lines, vertical_lines = self.detect_grid_lines(image)
            
            h_coords, v_coords = self.find_grid_coordinates(horizontal_lines, vertical_lines)
            
            if len(h_coords) < 2 or len(v_coords) < 2:
                messagebox.showerror("Error", "Could not detect grid lines properly!\nMake sure the image has clear grid lines.")
                return
            
            self.status_label.config(text="Extracting characters...", foreground="orange")
            self.root.update()
            
            output_folder, char_count = self.extract_character_cells(image, h_coords, v_coords)
            
            # Success message
            self.status_label.config(text=f"Extracted {char_count} characters successfully!", foreground="green")
            
            messagebox.showinfo(
                "Success!",
                f"Successfully extracted {char_count} characters!\n\n"
                f"Characters saved to:\n{output_folder}"
            )
            
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            print(error_msg)
            messagebox.showerror("Error", error_msg)
            self.status_label.config(text="Error occurred during processing", foreground="red")
    
    def run(self):
        self.root.mainloop()

def main():
    print("Character Grid Extractor")
    print("=" * 25)
    print("This tool extracts individual characters from grid images.")
    print("Requirements: pip install opencv-python pillow")
    print()
    
    try:
        app = CharacterExtractor()
        app.run()
    except ImportError as e:
        if "cv2" in str(e):
            print("ERROR: OpenCV is required for grid detection.")
            print("Install it with: pip install opencv-python")
        else:
            print(f"ERROR: Missing required library: {e}")
            print("Install requirements with: pip install opencv-python pillow")

if __name__ == "__main__":
    main()