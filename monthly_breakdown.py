import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import sqlite3
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import webbrowser
import os
from datetime import datetime
from theme import ThemeManager

class MonthlyBreakdown(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        
        # Initialize Monthly Breakdown page similar to your previous MonthlyBreakdown layout
        self.frame = ttk.Frame(self, style='Card.TFrame')
        
        # Create controls frame
        self.controls_frame = ttk.Frame(self.frame, style='Card.TFrame')
        self.controls_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Create month and year selection
        self.create_date_selection()
        
        # Create content frame with two columns
        self.content_frame = ttk.Frame(self.frame, style='Card.TFrame')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create left frame for table
        self.table_frame = ttk.Frame(self.content_frame, style='Card.TFrame')
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Create right frame for pie chart
        self.chart_frame = ttk.Frame(self.content_frame, style='Card.TFrame')
        self.chart_frame.pack(fill=tk.BOTH, expand=True)
        
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
        
        # Update button
        ttk.Button(
            self.controls_frame,
            text="Update",
            command=self.load_data,
            style='Primary.TButton'
        ).pack(side=tk.LEFT, padx=20)
    
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
    
    def create_pie_chart(self):
        # Create a button to show the pie chart
        self.chart_button = ttk.Button(
            self.chart_frame,
            text="Show Pie Chart",
            command=self.show_pie_chart,
            style='Secondary.TButton'
        )
        self.chart_button.grid(row=0, column=0, pady=10)
        
        # Configure grid weights
        self.chart_frame.grid_rowconfigure(0, weight=1)
        self.chart_frame.grid_columnconfigure(0, weight=1)
    
    def load_data(self):
        try:
            month = int(self.month_var.get())
            year = int(self.year_var.get())
            
            conn = sqlite3.connect('financial_data.db')
            cursor = conn.cursor()
            
            # Get all categories
            cursor.execute('SELECT name FROM categories')
            categories = [row[0] for row in cursor.fetchall()]
            
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # For each category, get budget and actual spending
            for category in categories:
                # Get actual spending
                cursor.execute('''
                    SELECT COALESCE(SUM(amount), 0)
                    FROM transactions
                    WHERE category = ? AND month = ? AND year = ?
                ''', (category, month, year))
                actual = cursor.fetchone()[0]
                
                # TODO: Get budget from budget table
                # For now, using a placeholder budget
                budget = 1000
                
                # Calculate difference
                difference = actual - budget
                
                # Add to treeview
                self.tree.insert('', 'end', values=(
                    category,
                    f"${budget:,.2f}",
                    f"${actual:,.2f}",
                    f"${difference:,.2f}"
                ))
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading data: {str(e)}")
    
    def show_pie_chart(self):
        try:
            # Get data from treeview
            categories = []
            amounts = []
            
            for item in self.tree.get_children():
                values = self.tree.item(item)['values']
                category = values[0]
                amount = float(values[2].replace('$', '').replace(',', ''))
                
                if amount > 0:  # Only include categories with spending
                    categories.append(category)
                    amounts.append(amount)
            
            # Create pie chart
            fig = go.Figure(data=[go.Pie(
                labels=categories,
                values=amounts,
                hole=.3
            )])
            
            # Update layout
            fig.update_layout(
                title=f"Spending by Category - {self.month_var.get()}/{self.year_var.get()}",
                showlegend=True
            )
            
            # Save and show the chart
            html_file = 'monthly_breakdown.html'
            fig.write_html(html_file)
            webbrowser.open('file://' + os.path.realpath(html_file))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error creating pie chart: {str(e)}") 