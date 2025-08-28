import os
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class ImageGridScreenshot:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Image Grid Screenshot Tool")
        self.root.geometry("400x300")
        self.root.resizable(True, True)
        self.image_path = None
        self.zoom_factor = tk.DoubleVar(value=2.0)
        self.grid_rows = tk.IntVar(value=5)
        self.grid_cols = tk.IntVar(value=5)
        
        self.create_gui()
        
    def create_gui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(main_frame, text="Image Selection:", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))        
        self.image_label = ttk.Label(main_frame, text="No image selected", foreground="gray")
        self.image_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        ttk.Button(main_frame, text="Select Image", command=self.select_image).grid(row=2, column=0, sticky=tk.W, pady=(0, 20))
        ttk.Label(main_frame, text="Zoom Settings:", font=("Arial", 12, "bold")).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))        
        ttk.Label(main_frame, text="Zoom Factor:").grid(row=4, column=0, sticky=tk.W, pady=2)
        zoom_spinbox = ttk.Spinbox(main_frame, from_=0.1, to=10.0, increment=0.1, textvariable=self.zoom_factor, width=10)
        zoom_spinbox.grid(row=4, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(main_frame, text="Grid Settings:", font=("Arial", 12, "bold")).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(20, 10))        
        ttk.Label(main_frame, text="Grid Rows:").grid(row=6, column=0, sticky=tk.W, pady=2)
        rows_spinbox = ttk.Spinbox(main_frame, from_=1, to=20, textvariable=self.grid_rows, width=10)
        rows_spinbox.grid(row=6, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(main_frame, text="Grid Columns:").grid(row=7, column=0, sticky=tk.W, pady=2)
        cols_spinbox = ttk.Spinbox(main_frame, from_=1, to=20, textvariable=self.grid_cols, width=10)
        cols_spinbox.grid(row=7, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        process_btn = ttk.Button(main_frame, text="Process Image", command=self.process_image_gui)
        process_btn.grid(row=8, column=0, columnspan=2, pady=30)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
                ("All files", "*.*")
            ]
        )       
        if file_path:
            self.image_path = file_path
            filename = os.path.basename(file_path)
            self.image_label.config(text=f"Selected: {filename}", foreground="black")
        
        return file_path
    
    def create_output_folder(self, image_path):
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        folder_name = f"{base_name}_grid_screenshots"
        
        image_dir = os.path.dirname(image_path)
        output_path = os.path.join(image_dir, folder_name)
        
        if not os.path.exists(output_path):
            os.makedirs(output_path)        
        return output_path
    
    def zoom_image(self, image, zoom_factor):
        original_width, original_height = image.size
        new_width = int(original_width * zoom_factor)
        new_height = int(original_height * zoom_factor)     
        zoomed_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        return zoomed_image
    
    def split_into_grid(self, image, output_folder):
        width, height = image.size
        rows = self.grid_rows.get()
        cols = self.grid_cols.get()      
        grid_width = width // cols
        grid_height = height // rows
        
        print(f"Image size: {width}x{height}")
        print(f"Grid: {rows}x{cols}")
        print(f"Grid cell size: {grid_width}x{grid_height}")
        print(f"Saving grid pieces to: {output_folder}")
        
        for row in range(rows):
            for col in range(cols):
                left = col * grid_width
                top = row * grid_height
                right = left + grid_width
                bottom = top + grid_height
                
                if col == cols - 1:  
                    right = width
                if row == rows - 1:  
                    bottom = height
                
                grid_piece = image.crop((left, top, right, bottom))      
                filename = f"grid_{row+1:02d}_{col+1:02d}.png"
                filepath = os.path.join(output_folder, filename)
                grid_piece.save(filepath, "PNG")
                cell_width_px = right - left
                cell_height_px = bottom - top
                
                print(f"Saved: {filename} ({cell_width_px}x{cell_height_px} px)")
        return True
    
    def process_image_gui(self):
        if not self.image_path:
            messagebox.showerror("Error", "Please select an image first!")
            return
        
        try:
            zoom_factor = self.zoom_factor.get()
            if zoom_factor <= 0:
                messagebox.showerror("Error", "Zoom factor must be greater than 0!")
                return
            
            rows = self.grid_rows.get()
            cols = self.grid_cols.get()            
            if rows <= 0 or cols <= 0:
                messagebox.showerror("Error", "Grid rows and columns must be greater than 0!")
                return
            
            output_folder = self.process_image(self.image_path, zoom_factor)            
            if output_folder:
                total_pieces = rows * cols
                messagebox.showinfo(
                    "Success", 
                    f"Successfully created {total_pieces} grid screenshots!\n"
                    f"Grid: {rows}x{cols}\n"
                    f"Location: {output_folder}"
                )          
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def process_image(self, image_path, zoom_factor):
        try:
            print(f"Opening image: {image_path}")
            image = Image.open(image_path)
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            print(f"Original image size: {image.size}")
            print(f"Applying zoom factor: {zoom_factor}x")
            zoomed_image = self.zoom_image(image, zoom_factor)
            print(f"Zoomed image size: {zoomed_image.size}")
            
            output_folder = self.create_output_folder(image_path)           
            success = self.split_into_grid(zoomed_image, output_folder)
            
            if success:
                return output_folder
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            raise e        
        return None
    
    def run(self):
        self.root.mainloop()

def main():
    print("Image Grid Screenshot Tool")
    print("=" * 30)
    print("Features:")
    print("- Custom zoom factor")
    print("- Adjustable grid size (rows x columns)")
    print("- Automatic grid splitting and saving")
    print("- Output saved in same directory as source image")
    print()
    print("Requirements: pip install pillow")
    print()
    
    try:
        app = ImageGridScreenshot()
        app.run()
    except ImportError as e:
        print(f"ERROR: Missing required library: {e}")
        print("Install requirements with: pip install pillow")

if __name__ == "__main__":
    main()