import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class AccountingApp:
    def __init__(self, master):
        self.master = master
        self.master.title("برنامج المحاسبة الجزائري")
        self.master.geometry("800x600")

        # إنشاء قاعدة البيانات وجدول الحسابات
        self.conn = sqlite3.connect('accounting.db')
        self.create_table()

        # إنشاء الواجهة
        self.create_widgets()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions
        (id INTEGER PRIMARY KEY, 
        date TEXT, 
        description TEXT, 
        amount REAL, 
        type TEXT)
        ''')
        self.conn.commit()

    def create_widgets(self):
        # إنشاء علامات التبويب
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill="both")

        # تبويب إدخال المعاملات
        self.transactions_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.transactions_frame, text="إدخال المعاملات")

        # تبويب عرض التقارير
        self.reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_frame, text="التقارير")

        # إضافة عناصر لتبويب المعاملات
        ttk.Label(self.transactions_frame, text="التاريخ:").grid(row=0, column=0, padx=5, pady=5)
        self.date_entry = ttk.Entry(self.transactions_frame)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ttk.Label(self.transactions_frame, text="الوصف:").grid(row=1, column=0, padx=5, pady=5)
        self.description_entry = ttk.Entry(self.transactions_frame)
        self.description_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.transactions_frame, text="المبلغ:").grid(row=2, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(self.transactions_frame)
        self.amount_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.transactions_frame, text="النوع:").grid(row=3, column=0, padx=5, pady=5)
        self.type_combobox = ttk.Combobox(self.transactions_frame, values=["دخل", "مصروف"])
        self.type_combobox.grid(row=3, column=1, padx=5, pady=5)
        self.type_combobox.set("دخل")

        ttk.Button(self.transactions_frame, text="إضافة معاملة", command=self.add_transaction).grid(row=4, column=0, columnspan=2, pady=10)

        # إضافة عناصر لتبويب التقارير
        ttk.Button(self.reports_frame, text="عرض جميع المعاملات", command=self.show_all_transactions).pack(pady=10)
        ttk.Button(self.reports_frame, text="عرض ملخص الحساب", command=self.show_summary).pack(pady=10)

    def add_transaction(self):
        date = self.date_entry.get()
        description = self.description_entry.get()
        amount = self.amount_entry.get()
        type_ = self.type_combobox.get()

        if not all([date, description, amount, type_]):
            messagebox.showerror("خطأ", "يرجى ملء جميع الحقول")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("خطأ", "يرجى إدخال رقم صحيح للمبلغ")
            return

        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO transactions (date, description, amount, type) VALUES (?, ?, ?, ?)",
                       (date, description, amount, type_))
        self.conn.commit()
        messagebox.showinfo("نجاح", "تمت إضافة المعاملة بنجاح")
        self.clear_entries()

    def clear_entries(self):
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.description_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.type_combobox.set("دخل")

    def show_all_transactions(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM transactions")
        transactions = cursor.fetchall()

        # إنشاء نافذة جديدة لعرض المعاملات
        transactions_window = tk.Toplevel(self.master)
        transactions_window.title("جميع المعاملات")
        transactions_window.geometry("600x400")

        # إنشاء جدول لعرض المعاملات
        tree = ttk.Treeview(transactions_window, columns=("ID", "التاريخ", "الوصف", "المبلغ", "النوع"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("التاريخ", text="التاريخ")
        tree.heading("الوصف", text="الوصف")
        tree.heading("المبلغ", text="المبلغ")
        tree.heading("النوع", text="النوع")

        for transaction in transactions:
            tree.insert("", "end", values=transaction)

        tree.pack(expand=True, fill="both")

    def show_summary(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT SUM(CASE WHEN type='دخل' THEN amount ELSE 0 END) as income, SUM(CASE WHEN type='مصروف' THEN amount ELSE 0 END) as expenses FROM transactions")
        summary = cursor.fetchone()
        income, expenses = summary
        balance = income - expenses

        messagebox.showinfo("ملخص الحساب", f"إجمالي الدخل: {income:.2f}\nإجمالي المصروفات: {expenses:.2f}\nالرصيد: {balance:.2f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AccountingApp(root)
    root.mainloop()
