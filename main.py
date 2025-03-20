import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from monthly_breakdown import MonthlyBreakdown  # Assuming you have the MonthlyBreakdown class in a separate file
from theme import ThemeManager

class FinancialApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Financial Management System")
        self.root.geometry("1200x800")
        
        # Apply theme
        ThemeManager.apply_theme(self.root)
        
        # Create main container (Frame) for all pages
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)  # Full window frame
        
        # Create header
        self.create_header()
        
        # Initialize pages
        self.home_page = HomePage(self.main_frame, self)
        self.monthly_breakdown_page = MonthlyBreakdown(self.main_frame, self)
        
        # Show the home page initially
        self.show_page(self.home_page)

    def create_header(self):
        # Create header frame
        header_frame = ttk.Frame(self.main_frame, style='Main.TFrame')
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # Title in left corner
        title_label = ttk.Label(
            header_frame,
            text="Financial Management System",
            style='Heading.TLabel'
        )
        title_label.pack(side=tk.LEFT)
        
        # Load and display logo from images folder
        logo_image = Image.open("images/ZAP Logo.png")
        logo_image = logo_image.resize((72, 35))
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = ttk.Label(
            header_frame,
            image=logo_photo,
            style='Body.TLabel'
        )
        logo_label.image = logo_photo
        logo_label.pack(side=tk.RIGHT)

    def show_page(self, page):
        # Hide the current page by destroying its widgets
        for widget in self.main_frame.winfo_children():
            widget.pack_forget()  # Use pack_forget to hide widgets
            
        # Show the selected page
        page.pack(fill=tk.BOTH, expand=True)

class HomePage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        
        # Create button grid
        self.create_button_grid()

    def create_button_grid(self):
        # Create a frame for the button grid that will fill the remaining space
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Configure the button frame's grid
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_rowconfigure(1, weight=1)
        
        # Create buttons
        buttons = [
            ("Add New Month", self.add_new_month, 'Secondary.TButton'),
            ("Monthly Breakdown", self.show_monthly_breakdown, 'Secondary.TButton'),
            ("Spending Trends", self.show_spending_trends, 'Secondary.TButton'),
            ("Net Worth", self.show_net_worth, 'Secondary.TButton')
        ]
        
        # Create and place buttons in 2x2 grid
        for i, (text, command, style) in enumerate(buttons):
            # Create a frame for each button to allow for padding
            button_container = ttk.Frame(button_frame)
            row = i // 2
            col = i % 2
            button_container.grid(row=row, column=col, sticky='nsew', padx=10, pady=10)
            button_container.grid_columnconfigure(0, weight=1)
            button_container.grid_rowconfigure(0, weight=1)
            
            # Create the button inside the container
            btn = ttk.Button(
                button_container,
                text=text,
                command=command,
                style=style
            )
            btn.grid(row=0, column=0, sticky='nsew')

    def add_new_month(self):
        # This still opens in a new window as it's a modal dialog
        pass

    def show_monthly_breakdown(self):
        self.app.show_page(self.app.monthly_breakdown_page)

    def show_spending_trends(self):
        # Logic to show spending trends page
        pass

    def show_net_worth(self):
        # Logic to show net worth page
        pass



if __name__ == "__main__":
    root = tk.Tk()
    app = FinancialApp(root)
    root.mainloop() 