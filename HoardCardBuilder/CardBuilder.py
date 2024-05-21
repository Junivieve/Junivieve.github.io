import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont
import csv
import os
import requests
from io import BytesIO
import textwrap


class CardBuilder:
    def __init__(self, root):
        self.root = root
        self.root.title("Card Builder")

        self.card_width = 400
        self.card_height = 600

        # Set fonts
        self.font_subtitle = ImageFont.truetype("GermaniaOne-Regular.ttf", 20)
        self.font_title = ImageFont.truetype("GermaniaOne-Regular.ttf", 30)
        self.font_stats = ImageFont.truetype("GermaniaOne-Regular.ttf", 25)
        self.font_description = ImageFont.truetype("GermaniaOne-Regular.ttf", 16)

        self.text_color = "#1D3531"  # Set text color

        # Subtitle input
        tk.Label(root, text="Subtitle:").grid(row=0, column=0)
        self.subtitle_entry = tk.Entry(root)
        self.subtitle_entry.grid(row=0, column=1)

        # Title input
        tk.Label(root, text="Title:").grid(row=1, column=0)
        self.title_entry = tk.Entry(root)
        self.title_entry.grid(row=1, column=1)

        # Stats input
        tk.Label(root, text="Stats:").grid(row=2, column=0)
        self.stats_entry = tk.Entry(root)
        self.stats_entry.grid(row=2, column=1)

        # Description input
        tk.Label(root, text="Description:").grid(row=3, column=0)
        self.description_entry = tk.Entry(root)
        self.description_entry.grid(row=3, column=1)

        # Background image selection
        tk.Button(root, text="Select Background Image", command=self.select_background_image).grid(row=4, column=0,
                                                                                                   columnspan=2)

        # Icon image selection
        tk.Button(root, text="Select Icon Image", command=self.select_icon_image).grid(row=5, column=0, columnspan=2)

        # Create card button
        tk.Button(root, text="Create Card", command=self.create_card).grid(row=6, column=0, columnspan=2)

        # Generate cards from CSV button
        tk.Button(root, text="Generate Cards from CSV", command=self.generate_cards_from_csv).grid(row=7, column=0,
                                                                                                   columnspan=2)

        self.background_image_path = None
        self.icon_image_path = None

    def select_background_image(self):
        self.background_image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if self.background_image_path:
            messagebox.showinfo("Selected Background Image", f"Selected Background Image: {self.background_image_path}")
        else:
            messagebox.showwarning("No Image Selected", "Please select a background image to proceed.")

    def select_icon_image(self):
        self.icon_image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if self.icon_image_path:
            messagebox.showinfo("Selected Icon Image", f"Selected Icon Image: {self.icon_image_path}")
        else:
            messagebox.showwarning("No Image Selected", "Please select an icon image to proceed.")

    def create_card(self):
        self._create_card(
            self.subtitle_entry.get(),
            self.title_entry.get(),
            self.stats_entry.get(),
            self.description_entry.get(),
            self.background_image_path,
            self.icon_image_path,
            None
        )

    def _create_card(self, subtitle, title, stats, description, background_image_path, icon_image_path, save_filename,
                     save_directory=None):
        if not background_image_path:
            messagebox.showwarning("No Background Image", "Please select a background image first.")
            return

        if not icon_image_path:
            messagebox.showwarning("No Icon Image", "Please select an icon image first.")
            return

        # Load background image
        if background_image_path.startswith("http"):
            response = requests.get(background_image_path)
            card = Image.open(BytesIO(response.content)).resize((self.card_width, self.card_height))
        else:
            card = Image.open(background_image_path).resize((self.card_width, self.card_height))

        draw = ImageDraw.Draw(card)

        # Load and resize icon image
        if icon_image_path.startswith("http"):
            response = requests.get(icon_image_path)
            icon = Image.open(BytesIO(response.content))
        else:
            icon = Image.open(icon_image_path)

        icon_size = self.card_width // 2  # icon size is half of the card width
        icon = icon.resize((icon_size, icon_size))

        # Calculate text sizes
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=self.font_subtitle)
        subtitle_height = subtitle_bbox[3] - subtitle_bbox[1]

        title_bbox = draw.textbbox((0, 0), title, font=self.font_title)
        title_height = title_bbox[3] - title_bbox[1]

        stats_bbox = draw.textbbox((0, 0), stats, font=self.font_stats)
        stats_height = stats_bbox[3] - stats_bbox[1]

        # Calculate positions
        top_margin = 50  # Adjusted top margin for subtitle to move it down a bit
        element_spacing = 40  # Spacing between elements
        description_margin = 40  # Increased spacing for description

        subtitle_x = (self.card_width - subtitle_bbox[2]) / 2
        subtitle_y = top_margin

        icon_x = (self.card_width - icon_size) / 2
        icon_y = subtitle_y + subtitle_height + element_spacing

        title_x = (self.card_width - title_bbox[2]) / 2
        title_y = icon_y + icon_size + element_spacing

        stats_x = (self.card_width - stats_bbox[2]) / 2
        stats_y = title_y + title_height + element_spacing

        # Draw text and images
        draw.text((subtitle_x, subtitle_y), subtitle, fill=self.text_color, font=self.font_subtitle)
        card.paste(icon, (int(icon_x), int(icon_y)), icon.convert("RGBA"))
        draw.text((title_x, title_y), title, fill=self.text_color, font=self.font_title)
        draw.text((stats_x, stats_y), stats, fill=self.text_color, font=self.font_stats)

        # Wrap and draw the description text
        max_description_width = self.card_width - 40  # Card width minus 20px padding on each side
        wrapped_description = textwrap.fill(description,
                                            width=int(max_description_width / 10))  # Adjust width to wrap text

        description_bbox = draw.textbbox((0, 0), wrapped_description, font=self.font_description)
        description_x = (self.card_width - description_bbox[2]) / 2  # Centered
        description_y = stats_y + stats_height + description_margin

        draw.multiline_text((description_x, description_y), wrapped_description, fill=self.text_color,
                            font=self.font_description, align="center")

        # Save card
        if save_filename is None:
            save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")])
        else:
            if save_directory:
                save_path = os.path.join(save_directory, save_filename)
            else:
                save_path = save_filename

        if save_path:
            card.save(save_path.lower())
            # Do not open the card image automatically

    def generate_cards_from_csv(self):
        csv_file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not csv_file_path:
            messagebox.showwarning("No CSV File Selected", "Please select a CSV file to proceed.")
            return

        save_directory = filedialog.askdirectory()
        if not save_directory:
            messagebox.showwarning("No Save Directory Selected", "Please select a directory to save the cards.")
            return

        cards = []
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                subtitle = row.get('Subtitle', '')
                title = row.get('Title', '')
                stats = row.get('Stats', '')
                description = row.get('Description', '')
                background_image_path = row.get('BackgroundImage', '')
                icon_image_path = row.get('IconImage', '')
                filename = row.get('Filename', '')

                card_data = (subtitle, title, stats, description, background_image_path, icon_image_path, filename)
                cards.append(card_data)

        for card_data in cards:
            self._create_card(*card_data, save_directory=save_directory)

        messagebox.showinfo("Cards Created", f"All cards have been created and saved to '{save_directory}'")


if __name__ == "__main__":
    root = tk.Tk()
    app = CardBuilder(root)
    root.mainloop()
