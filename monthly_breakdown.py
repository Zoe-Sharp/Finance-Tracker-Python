import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime


class MonthlyBreakdown(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        # Create main content frame (self.frame) within this page
        self.frame = ttk.Frame(self, style='Card.TFrame')
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)  # This ensures it displays properly

        # Create controls frame
        self.controls_frame = ttk.Frame(self.frame, style='Card.TFrame')
        self.controls_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
    
        # Create month and year selection
        self.create_date_selection()
        
        # Create content frame with two columns
        self.content_frame = ttk.Frame(self.frame, style='Card.TFrame')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create left frame for table
        self.table_frame = ttk.Frame(self.content_frame, style='Card.TFrame', width=600)
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=(0, 10), side='left')
        
        # Create right frame for pie chart
        self.chart_frame = ttk.Frame(self.content_frame, style='Card.TFrame', width=400)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=(0, 10), side='left')
        
        # Load initial data
        self.load_data()

    def create_date_selection(self):
        # Month selection
        ttk.Label(self.controls_frame, text="Month:", style='Body.TLabel').pack(side=tk.LEFT, padx=5)
        self.month_var = tk.StringVar()
        self.month_combo = ttk.Combobox(
            self.controls_frame,
            textvariable=self.month_var,
            values=[str(i) for i in range(1, 13)],
            state='readonly',
            width=5
        )
        self.month_combo.pack(side=tk.LEFT, padx=5)
        
        # Year selection
        ttk.Label(self.controls_frame, text="Year:", style='Body.TLabel').pack(side=tk.LEFT, padx=5)
        self.year_var = tk.StringVar()
        self.year_combo = ttk.Combobox(
            self.controls_frame,
            textvariable=self.year_var,
            values=[str(i) for i in range(2020, 2026)],
            state='readonly',
            width=5
        )
        self.year_combo.pack(side=tk.LEFT, padx=5)

        self.month_combo.set(str(datetime.now().month))
        self.year_combo.set(str(datetime.now().year))
        
        # Update button
        ttk.Button(
            self.controls_frame,
            text="Update",
            command=self.load_data,
            style='Primary.TButton'
        ).pack(side=tk.LEFT, padx=20)

        # Back home button
        ttk.Button(
            self.controls_frame,
            text="Back",
            command=self.return_home,
            style='Primary.TButton'
        ).pack(side=tk.RIGHT, padx=20)

    def return_home(self):
        self.app.show_page(self.app.home_page)  
        
    def create_table(self):
        # Create treeview
        columns = ('category', 'budget', 'actual', 'difference')
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show='headings')
        
        # Define headings
        self.tree.heading('category', text='Category')
        self.tree.heading('budget', text='Budget')
        self.tree.heading('actual', text='Actual')
        self.tree.heading('difference', text='Difference')
        
        # Define column widths
        self.tree.column('category', width=150)
        self.tree.column('budget', width=100)
        self.tree.column('actual', width=100)
        self.tree.column('difference', width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the treeview and scrollbar
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Configure grid weights
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)
    
    def load_data(self):
        try:
            month = int(self.month_var.get())
            year = int(self.year_var.get())
            
            conn = sqlite3.connect('financial_data.db')
            cursor = conn.cursor()

            # Create Table
            self.create_table()
            
            # Get all categories
            cursor.execute('SELECT name FROM categories')
            categories = [row[0] for row in cursor.fetchall()]
            
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            catergories_amounts = {}

            # For each category, get budget and actual spending
            for category in categories:
                # Get actual spending
                cursor.execute('''
                    SELECT COALESCE(SUM(amount), 0)
                    FROM transactions
                    WHERE category = ? AND month = ? AND year = ?
                ''', (category, month, year))
                actual = cursor.fetchone()[0]

                catergories_amounts[category] = actual
                
                # Get budget for each category
                cursor.execute("SELECT budget FROM categories WHERE name = ?", (category,))
                budget = cursor.fetchone()[0]
                
                # Calculate difference
                difference = actual - budget
                
                # Add to treeview
                self.tree.insert('', 'end', values=(
                    category,
                    f"${budget:,.2f}",
                    f"${actual:,.2f}",
                    f"${difference:,.2f}"
                ))

            # Get categories and types
            df = pd.read_sql_query("SELECT name, type FROM categories", conn)

            # Group by 'type' and aggregate names into a list
            grouped_df = df.groupby("type")["name"].apply(list).reset_index()

            type_amounts = {}
            for i, row in grouped_df.iterrows():
                type_name = row['type']
                category_list = row['name']
                amount_sum = 0
                for category in category_list:
                    amount_sum += catergories_amounts[category]

                type_amounts[type_name] = abs(amount_sum)

            conn.close()

            self.show_pie_chart(type_amounts)
            
        except Exception as e:
            print(str(e))
            messagebox.showerror("Error", f"Error loading data: {str(e)}")
    
    def show_pie_chart(self, amounts):
        # Clear previous chart widgets in case you want to refresh
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Get data from treeview
        categories = ["Spending", "Expenses", "Assets"]
        values = [amounts.get(category, 1) if amounts.get(category, 1) != 0 else 1 for category in categories]

        # Create a Matplotlib figure and pie chart
        fig, ax = plt.subplots()
        ax.pie(values, labels=categories, autopct='%1.1f%%', startangle=90)
        ax.set_title("Monthly Spending")
        ax.axis('equal')  # Makes sure pie is drawn as a circle

         # Embed into self.chart_frame
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
            
        

   
