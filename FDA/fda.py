import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import json

# Archivo donde se guardará la sesión
SESSION_FILE = "productos_sesion.json"

# Función para guardar la sesión actual
def save_session():
    try:
        with open(SESSION_FILE, "w") as file:
            json.dump(products, file)
        messagebox.showinfo("Éxito", "La sesión se ha guardado correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar la sesión: {str(e)}")

# Función para cargar la sesión al iniciar
def load_session():
    global products
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as file:
                products = json.load(file)
                update_product_list()
                product_names.update(products.keys())
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la sesión: {str(e)}")

# Función para añadir productos a la lista
def add_product(event=None):
    product_name = product_name_entry.get().strip()
    try:
        weight = float(product_weight_entry.get())
        if product_name == "":
            messagebox.showerror("Error", "El nombre del producto no puede estar vacío.")
            return
        if weight <= 0:
            messagebox.showerror("Error", "El peso debe ser mayor a 0.")
            return

        if product_name in products:
            products[product_name] += weight
        else:
            products[product_name] = weight
            product_names.add(product_name)

        update_product_list()
        product_name_entry.delete(0, tk.END)
        product_weight_entry.delete(0, tk.END)
        product_name_entry.focus()
    except ValueError:
        messagebox.showerror("Error", "El peso debe ser un número válido.")

# Función para actualizar la lista de productos mostrada
def update_product_list():
    product_list.delete(*product_list.get_children())
    for product, weight in products.items():
        product_list.insert("", "end", values=(product, f"{weight:.2f} lb"))

# Función para exportar la lista a un PDF
def export_to_pdf():
    if not products:
        messagebox.showerror("Error", "No hay productos para exportar.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        title="Guardar como PDF"
    )
    if not file_path:
        return

    try:
        pdf = canvas.Canvas(file_path, pagesize=letter)
        pdf.setFont("Helvetica", 12)
        pdf.drawString(30, 750, "Lista de Productos")
        pdf.drawString(30, 730, "-" * 50)

        y_position = 710
        for product, weight in products.items():
            pdf.drawString(30, y_position, f"{product}: {weight:.2f} lb")
            y_position -= 20
            if y_position < 50:
                pdf.showPage()
                pdf.setFont("Helvetica", 12)
                y_position = 750

        pdf.save()
        messagebox.showinfo("Éxito", f"Lista exportada a {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo exportar el PDF: {str(e)}")

# Función para limpiar la lista de productos
def clear_list():
    if messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas limpiar la lista?"):
        products.clear()
        product_names.clear()
        update_product_list()
        messagebox.showinfo("Éxito", "La lista ha sido despejada.")

# Función para eliminar productos seleccionados
def delete_selected():
    selected_items = product_list.selection()
    if not selected_items:
        messagebox.showerror("Error", "Selecciona al menos un producto para eliminar.")
        return
    for item in selected_items:
        product_name = product_list.item(item)["values"][0]
        if product_name in products:
            del products[product_name]
            product_names.discard(product_name)
    update_product_list()

# Función para editar un producto
def edit_product():
    selected_item = product_list.selection()
    if len(selected_item) != 1:
        messagebox.showerror("Error", "Selecciona un único producto para editar.")
        return
    product_name = product_list.item(selected_item[0])["values"][0]
    weight = products[product_name]

    product_name_entry.delete(0, tk.END)
    product_name_entry.insert(0, product_name)
    product_weight_entry.delete(0, tk.END)
    product_weight_entry.insert(0, str(weight))

    del products[product_name]
    product_names.discard(product_name)
    update_product_list()

# Configuración de la ventana principal
root = tk.Tk()
root.title("Gestión de Productos")
root.geometry("800x600")  # Ventana más grande para mejor visualización
root.minsize(600, 400)    # Tamaño mínimo para evitar recortes

# Estilo profesional
style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", background="#F5F5F5", foreground="#333333", font=("Arial", 10))
style.configure("TButton", background="#6286f0", foreground="white", font=("Arial", 10), padding=6)
style.map("TButton", background=[("active", "#5679d6")])
style.configure("Treeview", background="#FFFFFF", foreground="#333333", font=("Arial", 13), rowheight=25)
style.configure("Treeview.Heading", font=("Arial", 13, "bold"), background="#DDDDDD")
style.configure("TEntry", padding=5, font=("Arial", 13))
style.configure("TFrame", background="#F5F5F5")

root.configure(bg="#F5F5F5")

products = {}
product_names = set()

frame_top = ttk.Frame(root)
frame_top.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")

ttk.Label(frame_top, text="Nombre del Producto:").grid(row=0, column=0, padx=5, pady=5)
product_name_entry = ttk.Combobox(frame_top, width=25)
product_name_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_top, text="Peso (lb):").grid(row=1, column=0, padx=5, pady=5)
product_weight_entry = ttk.Entry(frame_top, width=25)
product_weight_entry.grid(row=1, column=1, padx=5, pady=5)

add_button = ttk.Button(frame_top, text="Añadir Producto", command=add_product)
add_button.grid(row=2, column=0, columnspan=2, pady=10)

product_list = ttk.Treeview(root, columns=("Producto", "Peso Total"), show="headings", height=15)
product_list.heading("Producto", text="Producto")
product_list.heading("Peso Total", text="Peso Total")
product_list.column("Producto", width=200)
product_list.column("Peso Total", width=100)
product_list.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

frame_bottom = ttk.Frame(root)
frame_bottom.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

buttons = [
    ("Exportar a PDF", export_to_pdf),
    ("Limpiar Lista", clear_list),
    ("Eliminar Producto", delete_selected),
    ("Editar Producto", edit_product),
    ("Guardar Sesión", save_session),
    ("Salir", root.quit),
]

for text, command in buttons:
    btn = ttk.Button(frame_bottom, text=text, command=command)
    btn.pack(side=tk.LEFT, padx=10)

product_name_entry.bind("<Return>", lambda e: product_weight_entry.focus())
product_weight_entry.bind("<Return>", add_product)

root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(1, weight=1)

load_session()
root.mainloop()
