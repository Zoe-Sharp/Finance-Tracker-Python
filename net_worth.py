import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import webbrowser
import os
from datetime import datetime
import pandas as pd

class NetWorth(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.frame = ttk.Frame(self, style='Card.TFrame')
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)  # This ensures it displays properly

        # Create heading frame
        self.heading_frame = ttk.Frame(self.frame, style='Card.TFrame')
        self.heading_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        self.create_heading_bar()

        # Create chart frame
        self.chart_frame = ttk.Frame(self.frame, style='Card.TFrame')
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=(0, 10), side='left')

        # Load initial data
        # self.update_charts()

    def create_heading_bar(self):

        ttk.Label(self.heading_frame, text="Net Worth", style='Subheading.TLabel').pack(side=tk.LEFT, padx=5)

        # Create update button
        ttk.Button(
            self.heading_frame,
            text="Update Net Worth",
            command=self.show_update_dialog,
            style='Primary.TButton'
        ).pack(side=tk.LEFT, padx=20)

        # Back home button
        ttk.Button(
            self.heading_frame,
            text="Back",
            command=self.return_home,
            style='Primary.TButton'
        ).pack(side=tk.RIGHT, padx=20)

    def return_home(self):
        self.app.show_page(self.app.home_page)  
    
    def show_update_dialog(self):
        dialog = tk.Toplevel(self.frame)
        dialog.title("Update Net Worth")
        dialog.geometry("400x500")
    
        # Create main container
        main_frame = ttk.Frame(dialog, style='Card.TFrame')
        main_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
        
        # Configure dialog grid weights
        dialog.grid_rowconfigure(0, weight=1)
        dialog.grid_columnconfigure(0, weight=1)
        
        # Create entry fields
        self.entries = {}

        # Connect to database
        conn = sqlite3.connect('financial_data.db')
        cursor = conn.cursor()
                
        # Get all assets and libilities
        cursor.execute("SELECT asset_name FROM networth WHERE type = 'asset'")
        asset_types = [row[0] for row in cursor.fetchall()]  

        cursor.execute("SELECT asset_name FROM networth WHERE type = 'liability'")
        liability_types = [row[0] for row in cursor.fetchall()]  

        conn.close()
        
        # ----------------- Assets ---------------------------
        ttk.Label(main_frame, text="Assets", style='Subheading.TLabel').grid(row=0, column=0, pady=(0, 10))
        
        asset_container = ttk.Frame(main_frame)
        asset_container.grid(row=1, column=0, sticky='ew')
        asset_container.grid_columnconfigure(0, weight=1)

        for asset in asset_types:
            self._add_entry_row(asset_container, asset, "asset")

        def prompt_new_asset():
            self._prompt_and_add_new_row(asset_container, "asset")

        ttk.Button(main_frame, text="+ Add Asset", command=prompt_new_asset).grid(row=2, column=0, pady=(10, 20), sticky='w')


            # ----------------- Liabilities ------------------------
        ttk.Label(main_frame, text="Liabilities", style='Subheading.TLabel').grid(row=3, column=0, sticky='w', pady=(10, 10))

        liability_container = ttk.Frame(main_frame)
        liability_container.grid(row=4, column=0, sticky='ew')
        liability_container.grid_columnconfigure(0, weight=1)

        for liability in liability_types:
            self._add_entry_row(liability_container, liability, "liability")

        def prompt_new_liability():
            self._prompt_and_add_new_row(liability_container, "liability")

        ttk.Button(main_frame, text="+ Add Liability", command=prompt_new_liability).grid(row=5, column=0, pady=(10, 20), sticky='w')


        # === SAVE ===
        ttk.Button(
            main_frame,
            text="Save",
            command=lambda: self.save_net_worth(self.entries, dialog),
            style='Primary.TButton'
        ).grid(row=6, column=0, pady=20, sticky='ew')

    def _add_entry_row(self, container, name, entry_type):
        frame = ttk.Frame(container)
        frame.pack(fill='x', pady=5)
        ttk.Label(frame, text=name, style='Body.TLabel').pack(side='left', padx=5)
        entry = ttk.Entry(frame)
        entry.pack(side='right', fill='x', expand=True, padx=5)
        self.entries[(entry_type, name)] = entry

    def _prompt_and_add_new_row(self, container, entry_type):
        def on_confirm():
            name = name_entry.get().strip()
            if name:
                self._add_entry_row(container, name, entry_type)
                popup.destroy()
            else:
                messagebox.showerror("Error", "Name cannot be empty.")

        popup = tk.Toplevel(self)
        popup.title(f"Add New {entry_type.title()}")
        popup.geometry("300x120")

        ttk.Label(popup, text=f"{entry_type.title()} Name:").pack(pady=10)
        name_entry = ttk.Entry(popup)
        name_entry.pack(pady=5, padx=10, fill='x')
        ttk.Button(popup, text="Add", command=on_confirm).pack(pady=10)

    
    def save_net_worth(self, entries, dialog):
        try:
            conn = sqlite3.connect('financial_data.db')
            cursor = conn.cursor()
            
            print(entries)
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