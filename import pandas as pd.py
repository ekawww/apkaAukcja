import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os

class ProductApp:
    def __init__(self, root):
        self.root = root 
        self.root.title("Product Auction Analyzer")
        self.products = self.load_from_csv()
        self.image_folder = "product_images"
        os.makedirs(self.image_folder, exist_ok=True)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Frame for product input
        self.input_frame = ttk.Frame(root, padding="10 10 10 10")
        self.input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Product name input
        ttk.Label(self.input_frame, text="Nazwa Produktu:").grid(row=0, column=0, sticky=tk.W)
        self.name_entry = ttk.Entry(self.input_frame, width=30)
        self.name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        # Sale price input
        ttk.Label(self.input_frame, text="Cena Sprzedaży:").grid(row=1, column=0, sticky=tk.W)
        self.price_entry = ttk.Entry(self.input_frame, width=30)
        self.price_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))

        # Quantity input
        ttk.Label(self.input_frame, text="Ilość Sztuk:").grid(row=2, column=0, sticky=tk.W)
        self.quantity_entry = ttk.Entry(self.input_frame, width=30)
        self.quantity_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))

        # Add product button
        self.add_button = ttk.Button(self.input_frame, text="Dodaj Produkt", command=self.add_product)
        self.add_button.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # Table for displaying products
        self.tree = ttk.Treeview(root, columns=("Nazwa Produktu", "Cena Sprzedaży", "Koszt Zakupu", "Zysk 20%", "Zysk 40%", "Zysk 60%", "Zdjęcie"), show='headings')
        self.tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.bind('<Double-1>', self.add_or_view_image)

        self.refresh_table()

        # Save and Load buttons
        self.save_button = ttk.Button(root, text="Zapisz Produkty", command=self.save_to_csv)
        self.save_button.grid(row=2, column=0, sticky=tk.W)

        # Sort button
        self.sort_button = ttk.Button(root, text="Sortuj Produkty", command=self.sort_products)
        self.sort_button.grid(row=3, column=0, sticky=tk.E)

        # Delete product button
        self.delete_button = ttk.Button(root, text="Usuń Produkt", command=self.delete_product)
        self.delete_button.grid(row=2, column=0, sticky=tk.E)

    def format_float(self, value):
        return f"{value:.2f}"

    def calculate_prices(self, sale_price, quantity):
        total_sale_price = sale_price * quantity
        purchase_price = sale_price * 0.55
        total_purchase_price = purchase_price * quantity
        profit_20 = purchase_price * 0.8
        total_profit_20 = profit_20 * quantity
        profit_40 = purchase_price * 0.6
        total_profit_40 = profit_40 * quantity
        profit_60 = purchase_price * 0.4
        total_profit_60 = profit_60 * quantity
        return (
            self.format_float(total_sale_price),
            self.format_float(total_purchase_price),
            self.format_float(total_profit_20),
            self.format_float(total_profit_40),
            self.format_float(total_profit_60),
        )

    def add_product(self):
        name = self.name_entry.get()
        try:
            price = float(self.price_entry.get())
            quantity = int(self.quantity_entry.get())
        except ValueError:
            messagebox.showerror("Błąd", "Proszę wprowadzić poprawne wartości dla ceny i ilości.")
            return

        total_sale_price, total_purchase_price, total_profit_20, total_profit_40, total_profit_60 = self.calculate_prices(price, quantity)
        self.products.append([name, total_sale_price, total_purchase_price, total_profit_20, total_profit_40, total_profit_60, ""])
        self.refresh_table()

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for product in self.products:
            product_data = product[:6] + [self.create_thumbnail(product[6])]
            self.tree.insert("", tk.END, values=product_data)

    def create_thumbnail(self, image_path):
        if not image_path:
            return ""
        try:
            img = Image.open(image_path)
            img.thumbnail((50, 50))
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error creating thumbnail for {image_path}: {e}")
            return ""

    def save_to_csv(self):
        df = pd.DataFrame(self.products, columns=['Nazwa Produktu', 'Cena Sprzedaży', 'Koszt Zakupu', 'Zysk 20%', 'Zysk 40%', 'Zysk 60%', 'Zdjęcie'])
        df.to_csv('products_history.csv', index=False)

    def load_from_csv(self):
        if os.path.exists('products_history.csv'):
            df = pd.read_csv('products_history.csv')
            return df.values.tolist()
        return []

    def sort_products(self):
        sort_window = tk.Toplevel(self.root)
        sort_window.title("Sortuj Produkty")

        tk.Label(sort_window, text="Wybierz kolumnę do sortowania:").pack()
        columns = ['Nazwa Produktu', 'Cena Sprzedaży', 'Koszt Zakupu', 'Zysk 20%', 'Zysk 40%', 'Zysk 60%']
        column_combo = ttk.Combobox(sort_window, values=columns)
        column_combo.pack()

        def sort_and_close():
            column = column_combo.get()
            if column:
                column_index = columns.index(column)
                self.products.sort(key=lambda x: float(x[column_index]), reverse=True)
                self.refresh_table()
            sort_window.destroy()

        ttk.Button(sort_window, text="Sortuj", command=sort_and_close).pack()

    def delete_product(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Brak zaznaczenia", "Proszę zaznaczyć produkt do usunięcia.")
            return

        for item in selected_item:
            item_values = self.tree.item(item, 'values')
            self.products = [product for product in self.products if product[0] != item_values[0]]
            self.tree.delete(item)

        self.refresh_table()

    def add_or_view_image(self, event):
        selected_item = self.tree.selection()[0]
        product_name = self.tree.item(selected_item, "values")[0]

        image_path = next((product[6] for product in self.products if product[0] == product_name), "")
        if image_path:
            self.view_image(image_path)
        else:
            self.add_image(product_name)

    def add_image(self, product_name):
        image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg")])
        if image_path:
            image_name = os.path.basename(image_path)
            target_path = os.path.join(self.image_folder, image_name)
            os.rename(image_path, target_path)

            for product in self.products:
                if product[0] == product_name:
                    product[6] = target_path
                    break
            self.refresh_table()

    def view_image(self, image_path):
        view_window = tk.Toplevel(self.root)
        view_window.title("Podgląd Zdjęcia")

        img = Image.open(image_path)
        img = ImageTk.PhotoImage(img)
        panel = tk.Label(view_window, image=img)
        panel.image = img
        panel.pack()

    def on_closing(self):
        self.save_to_csv()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductApp(root)
    root.mainloop()
