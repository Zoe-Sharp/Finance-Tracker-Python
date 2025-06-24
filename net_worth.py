import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
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
        self.update_charts()

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
            
            # Get current date
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            # Save all
            for asset_type, entry in entries.items():
                type = asset_type[0]
                name = asset_type[1]
                if entry.get().strip():
                    amount = float(entry.get())
                    cursor.execute('''
                        INSERT INTO networth (date, asset_name, amount, type)
                        VALUES (?, ?, ?, ?)
                    ''', (current_date, name, amount, type))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Net worth updated successfully!")
            dialog.destroy()
            self.update_charts()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for all fields")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving net worth: {str(e)}")
    
    def get_networth_data(self):
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
            sum_by_entry = cursor.fetchall()
            
            conn.close()

            networth_raw_data = {
                'assets': assets,
                'liabilities': liabilities,
                'total_by_entry': sum_by_entry
            }
            
            return networth_raw_data
        
        except Exception as e:
            messagebox.showerror("Error", f"Error updating charts: {str(e)}") 

    def update_charts(self):
        networth_raw_data = self.get_networth_data()
        if not networth_raw_data:
            return

        assets = networth_raw_data['assets']
        liabilities = networth_raw_data['liabilities']
        total_by_entry = networth_raw_data['total_by_entry']

        # Clear previous widgets
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Split layout
        table_frame = ttk.Frame(self.chart_frame)
        table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        graph_frame = ttk.Frame(self.chart_frame)
        graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Totals
        total_assets = sum([a[1] for a in assets])
        total_liabilities = sum([l[1] for l in liabilities])
        net_worth_total = total_assets - total_liabilities

        # === TABLES FIGURE ===
        table_fig = Figure(figsize=(5, 6), dpi=100)
        table_fig.patch.set_facecolor('#f0f4f8')

        def create_styled_table(ax, data, title):
            ax.axis('off')
            ax.set_title(title, fontweight='bold', color='navy')

            row_colors = ['#f6f8fa' if i % 2 == 0 else '#e0e8f0' for i in range(len(data))]
            table = ax.table(
                cellText=data,
                loc='center',
                cellLoc='left',
                colLabels=None,
                rowLabels=None,
                colWidths=[0.4, 0.3],
                cellColours=[[row_colors[i]] * len(data[0]) for i in range(len(data))]
            )

            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1.0, 1.5)

            for (row, col), cell in table.get_celld().items():
                if row == 0:
                    cell.set_text_props(weight='bold', color='white')
                    cell.set_facecolor('navy')
                elif row == len(data) - 1:
                    cell.set_text_props(weight='bold')
                    cell.set_facecolor('#cfe0f3')
                cell.set_edgecolor('#ccc')

        # === Assets Table ===
        ax1 = table_fig.add_subplot(211)
        asset_table_data = [["Asset", "Amount ($)"]] + [[a[0], f"{a[1]:,.2f}"] for a in assets]
        asset_table_data.append(["Total", f"{total_assets:,.2f}"])
        create_styled_table(ax1, asset_table_data, "Assets")

        # === Liabilities Table ===
        ax2 = table_fig.add_subplot(212)
        liability_table_data = [["Liability", "Amount ($)"]] + [[l[0], f"{l[1]:,.2f}"] for l in liabilities]
        liability_table_data.append(["Total", f"{total_liabilities:,.2f}"])
        create_styled_table(ax2, liability_table_data, "Liabilities")

        # === Render Table Figure ===
        table_canvas = FigureCanvasTkAgg(table_fig, master=table_frame)
        table_canvas.draw()
        table_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # === Total Net Worth Label ===
        ttk.Label(
            table_frame,
            text=f"Net Worth: ${net_worth_total:,.2f}",
            style='Heading.TLabel',
            foreground='navy',
            font=("Helvetica", 12, "bold")
        ).pack(pady=(10, 0))

        # === GRAPH FIGURE ===
        graph_fig = Figure(figsize=(6, 4), dpi=100)
        graph_fig.patch.set_facecolor('#f0f4f8')
        ax3 = graph_fig.add_subplot(111)
        ax3.set_facecolor('#e8ecf0')

        if total_by_entry:
            dates = [row[0] for row in total_by_entry]
            asset_totals = [row[1] for row in total_by_entry]
            liability_totals = [row[2] for row in total_by_entry]
            net_worth = [a - l for a, l in zip(asset_totals, liability_totals)]

            ax3.plot(dates, net_worth, marker='o', color='navy', label='Net Worth')
            ax3.set_title("Net Worth Over Time", fontweight='bold')
            ax3.set_xlabel("Date")
            ax3.set_ylabel("Amount")
            ax3.tick_params(axis='x', rotation=45)
            ax3.grid(True, linestyle='--', alpha=0.5)
            ax3.legend()

        # Render Graph Figure
        graph_canvas = FigureCanvasTkAgg(graph_fig, master=graph_frame)
        graph_canvas.draw()
        graph_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
