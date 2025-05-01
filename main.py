import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import sqlite3
import datetime
from monthly_breakdown import MonthlyBreakdown
from transaction_manager import TransactionManager
from net_worth import NetWorth
from theme import ThemeManager


class FinancialApp:
    def __init__(self, root):

        self.create_db()
        self.root = root
        self.root.title("Financial Management System")
        self.root.geometry("1200x800")
        
        # Apply theme
        ThemeManager.apply_theme(self.root)

        # Create header
        self.create_header()

        # Create main container (Frame) for all pages
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)  # Full window frame below the header
        
        # Initialize pages
        self.home_page = HomePage(self.main_frame, self)
        self.monthly_breakdown_page = MonthlyBreakdown(self.main_frame, self)
        self.networth_page = NetWorth(self.main_frame, self)
        
        # Show the home page initially
        self.show_page(self.home_page)

    def create_db(self):
        # create a db if it doesnt exist
        conn = sqlite3.connect("financial_data.db") 
        cursor = conn.cursor()

        # create transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                description TEXT,
                amount REAL,
                category TEXT,
                payee TEXT,
                month REAL,
                year REAL
            )
            """)
        
        # Create 'networth' table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS networth (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            asset_name TEXT,
            amount REAL,
            type TEXT
        )
        """)

        # Check if any rows already exist
        cursor.execute("SELECT COUNT(*) FROM networth")
        row_count = cursor.fetchone()[0]

        if row_count == 0:
            networth_categories = [
                ('Cash', 'asset'),
                ('Savings Account', 'asset'),
                ('Student Loan', 'liability'),        
            ]

            for catergory in networth_categories:
                cursor.execute("""
                INSERT INTO networth (date, asset_name, amount, type)
                VALUES (?, ?, ?, ?) 
                """, (datetime.datetime.now().date(), catergory[0], 0, catergory[1]))

        # Create 'settings' table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            type TEXT,
            budget REAL
        )
        """)

        # Check if any rows already exist
        cursor.execute("SELECT COUNT(*) FROM categories")
        row_count = cursor.fetchone()[0]

        # Only add categories if db is empty
        if row_count == 0:
            # Categories and budget 
            catergories = [
                ("Utilities", "Expenses", 70),
                ("Transport", "Expenses", 100),
                ("Fuel", "Expenses", 160),
                ("Groceries", "Expenses", 300),
                ("Healthcare", "Expenses", 40),
                ("Rent", "Expenses", 628),
                ("Shopping", "Spending", 200),
                ("Food", "Spending", 150),
                ("Entertainment", "Spending", 50),
                ("Alcohol", "Spending", 100),
                ("Sports Gear","Spending",0),
                ("Outdoor Activites", "Spending", 100),
                ("Fitness", "Spending", 60),
                ("Other", "Spending", 0),
                ("Salary", "Income", 3300),
                ("Other Income", "Income", 0),
                ("Employee Shares - IN", "Income", 800),
                ("Super Savings", "Assets", 1000),
                ("Short Term Savings", "Assets", 300),
                ("Investments", "Assets", 100),
                ("Employee Shares - OUT", "Assets", 800)
            ]

            for catergory in catergories:
                cursor.execute("""
                INSERT INTO categories (name, type, budget)
                VALUES (?, ?, ?)
                """, (catergory[0], catergory[1], catergory[2]))


        # Save (commit) the changes and close the connection
        conn.commit()
        conn.close()


    def create_header(self):
        # Create header frame
        self.header_frame = ttk.Frame(self.root, style='Main.TFrame')
        self.header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))  # Pack at the top of the window
        
        # Title in left corner
        title_label = ttk.Label(
            self.header_frame,
            text="Financial Management System",
            style='Heading.TLabel'
        )
        title_label.pack(side=tk.LEFT)

        # Load and display logo from images folder
        logo_image = Image.open("images/ZAP Logo.png")
        logo_image = logo_image.resize((72, 35))
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = ttk.Label(
            self.header_frame,
            image=logo_photo,
            style='Body.TLabel'
        )
        logo_label.image = logo_photo  # Keep a reference to prevent garbage collection
        logo_label.pack(side=tk.RIGHT)

    def show_page(self, page):
        # Hide all children of main_frame (pages)
        for widget in self.main_frame.winfo_children():
            widget.pack_forget()  # Hide all current widgets in the frame
        
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
        
        # Create and place buttons in 2x2 grisd
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
        TransactionManager(self)

    def show_monthly_breakdown(self):
        self.app.show_page(self.app.monthly_breakdown_page)

    def show_spending_trends(self):
        # Logic to show spending trends page
        pass

    def show_net_worth(self):
        self.app.show_page(self.app.networth_page)


if __name__ == "__main__":
    root = tk.Tk()
    app = FinancialApp(root)
    root.mainloop()
