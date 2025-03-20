import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import webbrowser
import os
from datetime import datetime
import pandas as pd
from theme import ThemeManager

class NetWorth:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, style='Card.TFrame')
        
        # Create controls frame
        self.controls_frame = ttk.Frame(self.frame, style='Card.TFrame')
        self.controls_frame.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        
        # Create update button
        ttk.Button(
            self.controls_frame,
            text="Update Net Worth",
            command=self.show_update_dialog,
            style='Primary.TButton'
        ).grid(row=0, column=0, padx=20)
        
        # Create chart frame
        self.chart_frame = ttk.Frame(self.frame, style='Card.TFrame')
        self.chart_frame.grid(row=1, column=0, sticky='nsew')
        
        # Configure grid weights
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        # Load initial data
        self.update_charts()
    
    def show_update_dialog(self):
        dialog = tk.Toplevel(self.frame)
        dialog.title("Update Net Worth")
        dialog.geometry("400x500")
        
        # Apply theme to dialog
        ThemeManager.apply_theme(dialog)
        
        # Create main container
        main_frame = ttk.Frame(dialog, style='Card.TFrame')
        main_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
        
        # Configure dialog grid weights
        dialog.grid_rowconfigure(0, weight=1)
        dialog.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)  # Space between assets and liabilities
        
        # Create entry fields
        entries = {}
        
        # Assets section
        ttk.Label(main_frame, text="Assets", style='Subheading.TLabel').grid(row=0, column=0, pady=(0, 10))
        
        asset_types = ["Cash", "Investments", "Real Estate", "Vehicles", "Other"]
        for i, asset_type in enumerate(asset_types):
            frame = ttk.Frame(main_frame, style='Card.TFrame')
            frame.grid(row=i+1, column=0, sticky='ew', pady=5)
            ttk.Label(frame, text=asset_type, style='Body.TLabel').grid(row=0, column=0)
            entry = ttk.Entry(frame)
            entry.grid(row=0, column=1, sticky='ew', padx=5)
            frame.grid_columnconfigure(1, weight=1)
            entries[asset_type] = entry
        
        # Liabilities section
        ttk.Label(main_frame, text="Liabilities", style='Subheading.TLabel').grid(row=7, column=0, pady=(20, 10))
        
        liability_types = ["Mortgage", "Car Loan", "Credit Cards", "Student Loans", "Other"]
        for i, liability_type in enumerate(liability_types):
            frame = ttk.Frame(main_frame, style='Card.TFrame')
            frame.grid(row=i+8, column=0, sticky='ew', pady=5)
            ttk.Label(frame, text=liability_type, style='Body.TLabel').grid(row=0, column=0)
            entry = ttk.Entry(frame)
            entry.grid(row=0, column=1, sticky='ew', padx=5)
            frame.grid_columnconfigure(1, weight=1)
            entries[liability_type] = entry
        
        # Save button
        ttk.Button(
            main_frame,
            text="Save",
            command=lambda: self.save_net_worth(entries, dialog),
            style='Primary.TButton'
        ).grid(row=13, column=0, pady=20)
    
    def save_net_worth(self, entries, dialog):
        try:
            conn = sqlite3.connect('financial_data.db')
            cursor = conn.cursor()
            
            # Get current date
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            # Save assets
            for asset_type, entry in entries.items():
                if entry.get().strip():
                    amount = float(entry.get())
                    cursor.execute('''
                        INSERT INTO networth (date, asset_name, amount, type)
                        VALUES (?, ?, ?, 'asset')
                    ''', (current_date, asset_type, amount))
            
            # Save liabilities
            for liability_type, entry in entries.items():
                if entry.get().strip():
                    amount = float(entry.get())
                    cursor.execute('''
                        INSERT INTO networth (date, asset_name, amount, type)
                        VALUES (?, ?, ?, 'liability')
                    ''', (current_date, liability_type, amount))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Net worth updated successfully!")
            dialog.destroy()
            self.update_charts()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for all fields")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving net worth: {str(e)}")
    
    def update_charts(self):
        try:
            conn = sqlite3.connect('financial_data.db')
            cursor = conn.cursor()
            
            # Get latest date
            cursor.execute('SELECT MAX(date) FROM networth')
            latest_date = cursor.fetchone()[0]
            
            if not latest_date:
                messagebox.showinfo("Info", "No net worth data available. Please add some data first.")
                return
            
            # Get assets and liabilities
            cursor.execute('''
                SELECT asset_name, SUM(amount) as total
                FROM networth
                WHERE date = ? AND type = 'asset'
                GROUP BY asset_name
            ''', (latest_date,))
            assets = cursor.fetchall()
            
            cursor.execute('''
                SELECT asset_name, SUM(amount) as total
                FROM networth
                WHERE date = ? AND type = 'liability'
                GROUP BY asset_name
            ''', (latest_date,))
            liabilities = cursor.fetchall()
            
            # Get net worth over time
            cursor.execute('''
                SELECT date,
                       SUM(CASE WHEN type = 'asset' THEN amount ELSE 0 END) as assets,
                       SUM(CASE WHEN type = 'liability' THEN amount ELSE 0 END) as liabilities
                FROM networth
                GROUP BY date
                ORDER BY date
            ''')
            net_worth_data = cursor.fetchall()
            
            conn.close()
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=("Assets and Liabilities", "Net Worth Over Time")
            )
            
            # Add assets pie chart
            if assets:
                fig.add_trace(
                    go.Pie(
                        labels=[a[0] for a in assets],
                        values=[a[1] for a in assets],
                        name="Assets",
                        hole=.3
                    ),
                    row=1, col=1
                )
            
            # Add liabilities pie chart
            if liabilities:
                fig.add_trace(
                    go.Pie(
                        labels=[l[0] for l in liabilities],
                        values=[l[1] for l in liabilities],
                        name="Liabilities",
                        hole=.3
                    ),
                    row=1, col=1
                )
            
            # Add net worth line
            if net_worth_data:
                dates = [d[0] for d in net_worth_data]
                net_worth = [d[1] - d[2] for d in net_worth_data]
                
                fig.add_trace(
                    go.Scatter(
                        x=dates,
                        y=net_worth,
                        name="Net Worth",
                        mode='lines+markers'
                    ),
                    row=2, col=1
                )
            
            # Update layout
            fig.update_layout(
                title=f"Net Worth Overview - Last Updated: {latest_date}",
                showlegend=True,
                height=800
            )
            
            # Save and show the chart
            html_file = 'net_worth.html'
            fig.write_html(html_file)
            webbrowser.open('file://' + os.path.realpath(html_file))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error updating charts: {str(e)}") 