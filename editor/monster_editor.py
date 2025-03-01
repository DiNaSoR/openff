import os
from PIL import Image, ImageTk
import tkinter as tk

class MonsterEditor:
    def display_monster_sprite(self, monster):
        """Display the monster sprite in the sprite frame."""
        # Clear the sprite display frame first
        for widget in self.sprite_frame.winfo_children():
            widget.destroy()
            
        try:
            # Get the sprite info from the monster data
            sprite_info = monster.get('sprite', {"sheet": "monsters1", "row": 0, "col": 0})
            sheet_name = sprite_info.get("sheet", "monsters1")
            row = sprite_info.get("row", 0)
            col = sprite_info.get("col", 0)
            
            # Load the sprite sheet - adjust the path as needed
            sprite_sheet_path = os.path.join(self.app.project_path, 'assets', 'images', f'{sheet_name}.png')
            if not os.path.exists(sprite_sheet_path):
                print(f"Sprite sheet not found: {sprite_sheet_path}")
                # Try alternative paths
                alt_paths = [
                    os.path.join(self.app.project_path, 'img', f'{sheet_name}.png'),
                    os.path.join(self.app.project_path, 'images', f'{sheet_name}.png'),
                    os.path.join(self.app.project_path, 'resources', 'images', f'{sheet_name}.png'),
                    os.path.join(self.app.project_path, 'assets', f'{sheet_name}.png')
                ]
                
                for alt_path in alt_paths:
                    if os.path.exists(alt_path):
                        sprite_sheet_path = alt_path
                        print(f"Found sprite sheet at alternative path: {alt_path}")
                        break
            
            if not os.path.exists(sprite_sheet_path):
                # If still not found, use a placeholder image or display message
                print(f"Could not find sprite sheet for {sheet_name}. Using default.")
                label = tk.Label(self.sprite_frame, text="Sprite not found")
                label.pack(padx=10, pady=10)
                return
                
            # Load the image
            original_sheet = Image.open(sprite_sheet_path)
            
            # Define cell size - adjust based on your sprite sheet
            cell_width = 32  # Default sprite width
            cell_height = 32  # Default sprite height
            
            # Calculate the position in the sheet
            x = col * cell_width
            y = row * cell_height
            
            # Extract the sprite from the sheet
            sprite = original_sheet.crop((x, y, x + cell_width, y + cell_height))
            
            # Resize the sprite for better display (optional)
            sprite = sprite.resize((96, 96), Image.LANCZOS)
            
            # Convert to PhotoImage for Tkinter display
            self.current_sprite_image = ImageTk.PhotoImage(sprite)
            
            # Display the sprite
            sprite_label = tk.Label(self.sprite_frame, image=self.current_sprite_image)
            sprite_label.image = self.current_sprite_image  # Keep a reference
            sprite_label.pack(padx=10, pady=10)
            
            # Add sprite info below the image
            info_text = f"Sheet: {sheet_name}, Row: {row}, Col: {col}"
            info_label = tk.Label(self.sprite_frame, text=info_text, font=("Arial", 9))
            info_label.pack(padx=5, pady=5)
            
        except Exception as e:
            print(f"Error displaying sprite: {str(e)}")
            # Display error message in the sprite frame
            error_label = tk.Label(self.sprite_frame, text=f"Error loading sprite:\n{str(e)}")
            error_label.pack(padx=10, pady=10) 