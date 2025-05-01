import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import sqlite3
from datetime import datetime

class TransactionManager:
    def __init__(self, parent):
        self.parent = parent
        self.db_path = 'financial_data.db'
        self.current_index = 0
        self.df = None
        self.show_file_dialog()

    def show_file_dialog(self):
        """Open file dialog to select a CSV file."""
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            try:
                self.df = self.process_csv(file_path)
                self.show_transaction_popup()
            except Exception as e:
                messagebox.showerror("Error", f"Error loading CSV file: {str(e)}")

    def process_csv(self, file_path):
        """Read and process the CSV file."""
        df = pd.read_csv(file_path, skiprows=5)
        df = df.iloc[:, [0, 4, 6]]
        df.columns = ['date', 'payee', 'amount']
        return df

    def show_transaction_popup(self):
        """Show a pop-up window to categorize transactions one by one."""
        if self.current_index >= len(self.df):
            messagebox.showinfo("Finished", "All transactions have been processed.")
            return

        row = self.df.iloc[self.current_index]
        self.popup = tk.Toplevel(self.parent)
        self.popup.title("Review Transaction")
        self.popup.geometry("400x300")

        tk.Label(self.popup, text=f"Date: {row['date']}").pack(pady=5)
        tk.Label(self.popup, text=f"Payee: {row['payee']}").pack(pady=5)

        self.amount_var = tk.StringVar(value=f"{row['amount']:.2f}")
        tk.Label(self.popup, text="Amount:").pack()
        self.amount_entry = tk.Entry(self.popup, textvariable=self.amount_var)
        self.amount_entry.pack(pady=5)

        tk.Label(self.popup, text="Category:").pack()
        self.category_var = tk.StringVar()
        self.categories = self.load_categories()
        self.category_dropdown = ttk.Combobox(self.popup, textvariable=self.category_var, values=self.categories)
        self.category_dropdown.pack(pady=5)
        self.category_dropdown.set("Select Category")

        tk.Button(self.popup, text="Save", command=self.save_transaction, bg="green", fg="white").pack(pady=5)
        tk.Button(self.popup, text="Delete", command=self.delete_transaction, bg="red", fg="white").pack(pady=5)

    def load_categories(self):
        """Load categories from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM categories')
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return categories

    def save_transaction(self):
        """Save the current transaction to the database."""
        category = self.category_var.get()
        if category == "Select Category":
            messagebox.showwarning("Warning", "Please select a category.")
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            row = self.df.iloc[self.current_index]
            date = row['date']
            payee = row['payee']
            amount = float(self.amount_var.get())
            trans_date = datetime.strptime(date, '%Y/%m/%d')
            month, year = trans_date.month, trans_date.year

            cursor.execute('''
                INSERT INTO transactions (date, payee, amount, category, month, year)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (date, payee, amount, category, month, year))

            conn.commit()
            conn.close()

            self.popup.destroy()
            self.current_index += 1
            self.show_transaction_popup()
        except Exception as e:
            messagebox.showerror("Error", f"Error saving transaction: {str(e)}")

    def delete_transaction(self):
        """Delete the current transaction and move to the next one."""
        self.df.drop(self.df.index[self.current_index], inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        self.popup.destroy()
        self.show_transaction_popup()
