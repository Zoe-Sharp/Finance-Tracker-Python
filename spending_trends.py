import tkinter as tk
from tkinter import ttk
import sqlite3
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import webbrowser
import os
from datetime import datetime
import pandas as pd
from theme import ThemeManager

class SpendingTrends:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, style='Card.TFrame')
        
        # Create controls frame
        self.controls_frame = ttk.Frame(self.frame, style='Card.TFrame')
        self.controls_frame.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        
        # Create filters
        self.create_filters()
        
        # Create graph type selection
        self.create_graph_type_selection()
        
        # Create chart frame
        self.chart_frame = ttk.Frame(self.frame, style='Card.TFrame')
        self.chart_frame.grid(row=1, column=0, sticky='nsew')
        
        # Configure grid weights
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        # Create update button
        ttk.Button(
            self.controls_frame,
            text="Update Chart",
            command=self.update_chart,
            style='Primary.TButton'
        ).grid(row=0, column=4, padx=20)
        
        # Initialize variables
        self.graph_type = tk.StringVar(value="line")
        self.selected_categories = []
        
        # Load initial data
        self.update_chart()
    
    def create_filters(self):
        # Year filter
        ttk.Label(self.controls_frame, text="Year:", style='Body.TLabel').grid(row=0, column=0, padx=5)
        self.year_var = tk.StringVar()
        self.year_combo = ttk.Combobox(
            self.controls_frame,
            textvariable=self.year_var,
            values=[str(i) for i in range(2020, datetime.now().year + 1)],
            state='readonly',
            width=5
        )
        self.year_combo.grid(row=0, column=1, padx=5)
        self.year_combo.set(str(datetime.now().year))
        
        # Category filter
        ttk.Label(self.controls_frame, text="Categories:", style='Body.TLabel').grid(row=0, column=2, padx=5)
        self.category_frame = ttk.Frame(self.controls_frame, style='Card.TFrame')
        self.category_frame.grid(row=0, column=3, padx=5)
        
        # Load categories
        self.load_categories()
    
    def create_graph_type_selection(self):
        ttk.Label(self.controls_frame, text="Graph Type:", style='Body.TLabel').grid(row=0, column=5, padx=5)
        self.graph_type_combo = ttk.Combobox(
            self.controls_frame,
            textvariable=self.graph_type,
            values=["line", "bar", "scatter"],
            state='readonly',
            width=10
        )
        self.graph_type_combo.grid(row=0, column=6, padx=5)
    
    def load_categories(self):
        try:
            conn = sqlite3.connect('financial_data.db')
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM categories')
            categories = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            # Create checkboxes for each category
            for i, category in enumerate(categories):
                var = tk.BooleanVar(value=True)
                self.selected_categories.append((category, var))
                ttk.Checkbutton(
                    self.category_frame,
                    text=category,
                    variable=var,
                    style='TCheckbutton'
                ).grid(row=0, column=i, padx=2)
        
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error loading categories: {str(e)}")
    
    def update_chart(self):
        try:
            year = int(self.year_var.get())
            
            # Get selected categories
            selected = [cat for cat, var in self.selected_categories if var.get()]
            
            if not selected:
                tk.messagebox.showwarning("Warning", "Please select at least one category")
                return
            
            # Get data from database
            conn = sqlite3.connect('financial_data.db')
            cursor = conn.cursor()
            
            # Create DataFrame to store results
            data = []
            
            for category in selected:
                cursor.execute('''
                    SELECT month, SUM(amount) as total
                    FROM transactions
                    WHERE category = ? AND year = ?
                    GROUP BY month
                    ORDER BY month
                ''', (category, year))
                
                results = cursor.fetchall()
                for month, total in results:
                    data.append({
                        'month': month,
                        'category': category,
                        'amount': total
                    })
            
            conn.close()
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Create figure
            fig = go.Figure()
            
            # Add traces for each category
            for category in selected:
                category_data = df[df['category'] == category]
                
                if self.graph_type.get() == "line":
                    fig.add_trace(go.Scatter(
                        x=category_data['month'],
                        y=category_data['amount'],
                        name=category,
                        mode='lines+markers'
                    ))
                elif self.graph_type.get() == "bar":
                    fig.add_trace(go.Bar(
                        x=category_data['month'],
                        y=category_data['amount'],
                        name=category
                    ))
                else:  # scatter
                    fig.add_trace(go.Scatter(
                        x=category_data['month'],
                        y=category_data['amount'],
                        name=category,
                        mode='markers'
                    ))
            
            # Update layout
            fig.update_layout(
                title=f"Spending Trends - {year}",
                xaxis_title="Month",
                yaxis_title="Amount ($)",
                showlegend=True,
                xaxis=dict(
                    tickmode='array',
                    tickvals=list(range(1, 13)),
                    ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                )
            )
            
            # Save and show the chart
            html_file = 'spending_trends.html'
            fig.write_html(html_file)
            webbrowser.open('file://' + os.path.realpath(html_file))
            
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error updating chart: {str(e)}") 