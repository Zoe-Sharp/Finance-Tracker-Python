import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import calendar


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
        # Query available months and years from the database
        try:
            conn = sqlite3.connect('financial_data.db')
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT month, year FROM transactions ORDER BY year, month')
            results = cursor.fetchall()
            conn.close()
            # Build sets of available months and years
            available_months = sorted(set(int(row[0]) for row in results))
            available_years = sorted(set(int(row[1]) for row in results))
        except Exception as e:
            available_months = list(range(1, 13))
            available_years = list(range(2020, 2026))

        # Month selection
        ttk.Label(self.controls_frame, text="Month:", style='Body.TLabel').pack(side=tk.LEFT, padx=5)
        self.month_var = tk.StringVar()
        month_names = [calendar.month_abbr[m].upper() for m in available_months]
        self.month_map = {calendar.month_abbr[m].upper(): m for m in available_months}
        self.month_combo = ttk.Combobox(
            self.controls_frame,
            textvariable=self.month_var,
            values=month_names,
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
            values=[str(y) for y in available_years],
            state='readonly',
            width=5
        )
        self.year_combo.pack(side=tk.LEFT, padx=5)

        # Set default to latest available month/year if possible
        now = datetime.now()
        default_year = str(now.year) if now.year in available_years else str(available_years[-1]) if available_years else ''
        default_month_num = now.month if now.month in available_months else (available_months[-1] if available_months else 1)
        default_month = calendar.month_abbr[default_month_num].upper()
        self.month_combo.set(default_month)
        self.year_combo.set(default_year)
        
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
        columns = ('category', 'budget', 'actual', 'difference')
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show='headings', height=20)

        self.tree.heading('category', text='Category')
        self.tree.heading('budget', text='Budget')
        self.tree.heading('actual', text='Actual')
        self.tree.heading('difference', text='% Difference')

        self.tree.column('category', width=200, anchor='w')
        self.tree.column('budget', width=100, anchor='center')
        self.tree.column('actual', width=100, anchor='center')
        self.tree.column('difference', width=120, anchor='center')

        style = ttk.Style()
    
        # Fix header row styling
        style.configure("Treeview.Heading", 
                        background="#0072C6",  # Blue header
                        foreground="white", 
                        font=("Helvetica", 10, "bold"),
                        borderwidth=1)

        # Remove hover effect (highlight) on headings
        style.map("Treeview.Heading",
                background=[('active', '#0072C6')],  # Same color as normal
                relief=[('active', 'flat')])

        # General row styling
        style.configure("Treeview", 
                        font=("Helvetica", 10),
                        rowheight=28,
                        borderwidth=0,
                        relief="flat")

        scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)
    
    def load_data(self):
        try:
            # Convert month name to number
            month = self.month_map[self.month_var.get()]
            year = int(self.year_var.get())

            conn = sqlite3.connect('financial_data.db')
            cursor = conn.cursor()

            self.create_table()

            for item in self.tree.get_children():
                self.tree.delete(item)

            # Get all categories and their types
            cursor.execute("SELECT name, budget, type FROM categories")
            all_categories = cursor.fetchall()

            section_data = {}
            for name, budget, cat_type in all_categories:
                # Get actual total
                cursor.execute('''
                    SELECT COALESCE(SUM(amount), 0)
                    FROM transactions
                    WHERE category = ? AND month = ? AND year = ?
                ''', (name, month, year))
                actual = abs(cursor.fetchone()[0])
                diff_percent = ((actual - budget) / budget * 100) if budget != 0 else 0

                if cat_type not in section_data:
                    section_data[cat_type] = []

                section_data[cat_type].append({
                    "category": name,
                    "budget": budget,
                    "actual": actual,
                    "diff": diff_percent
                })

            # Insert into treeview with formatting
            for section in ['Income', 'Expenses', 'Spending', 'Assets']:
                if section not in section_data:
                    continue

                self.tree.insert('', 'end', values=(f'{section}', '', '', ''), tags=('section',))

                total_budget = 0
                total_actual = 0

                for entry in section_data[section]:
                    total_budget += entry["budget"]
                    total_actual += entry["actual"]
                    self.tree.insert('', 'end', values=(
                        entry["category"],
                        f"${entry['budget']:,.2f}",
                        f"${entry['actual']:,.2f}",
                        f"{entry['diff']:.0f}%" 
                    ))

                total_diff = ((total_actual - total_budget) / total_budget * 100) if total_budget != 0 else 0
                self.tree.insert('', 'end', values=('Total', f"${total_budget:,.2f}", f"${total_actual:,.2f}", f"{total_diff:.0f}%"), tags=('total',))


            # Calculate totals for Spending, Expenses, Assets
            type_amounts = {"Spending": 0, "Expenses": 0, "Assets": 0}

            for section in section_data:
                total_actual = sum(entry["actual"] for entry in section_data[section])
                if section in type_amounts:
                    type_amounts[section] = total_actual
    
            # Show pie chart
            self.show_pie_chart(type_amounts)


            conn.close()
            self.apply_treeview_styles()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")

    def apply_treeview_styles(self):
        self.tree.tag_configure('section', font=('Helvetica', 10, 'bold'), background='#e6f0ff')
        self.tree.tag_configure('total', font=('Helvetica', 10, 'bold'), background='#d9ead3')

    
    def show_pie_chart(self, amounts):
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Define categories and values
        categories = ["Spending", "Expenses", "Assets"]
        values = [amounts.get(cat, 0) for cat in categories]

        # Avoid zero-only chart
        if all(v == 0 for v in values):
            ttk.Label(self.chart_frame, text="No data available", style="Body.TLabel").pack()
            return

        # Create pie chart
        fig, ax = plt.subplots(figsize=(4, 4))
        colors = ['#FF9999', '#66B3FF', '#99FF99']
        ax.pie(
            values, 
            labels=categories, 
            autopct='%1.1f%%', 
            startangle=90,
            colors=colors,
            wedgeprops={'edgecolor': 'white'}
        )
        ax.set_title("Spending vs Expenses vs Assets", fontsize=10)
        ax.axis('equal')

        # Display chart in chart_frame
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

            

    
