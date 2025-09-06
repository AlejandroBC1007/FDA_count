import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import json
from datetime import datetime

# Archivo donde se guardará la sesión
SESSION_FILE = "productos_sesion.json"

# Función para guardar la sesión actual
def save_session(show_alert=True):
    try:
        with open(SESSION_FILE, "w") as file:
            json.dump(products, file)
        if show_alert:
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
                update_total_weight()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la sesión: {str(e)}")

# Función para calcular y actualizar el peso total
def update_total_weight():
    total_weight = sum(products.values())  # Suma todos los pesos
    total_weight_label.config(text=f"Peso Total: {total_weight:.2f} lb")

# Pila para deshacer cambios
undo_stack = []

def save_undo_state():
    undo_stack.append(products.copy())

def undo_action(event=None):
    if not undo_stack:
        messagebox.showinfo("Deshacer", "No hay acciones para deshacer.")
        return
    last_state = undo_stack.pop()
    global products, product_names
    products = last_state
    product_names = set(products.keys())
    update_product_list()
    update_total_weight()
    messagebox.showinfo("Deshacer", "Última acción revertida.")

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

        save_undo_state()  # Guardamos estado antes de modificar

        if product_name in products:
            products[product_name] += weight
            add_to_history("Modificado", f"{product_name} - +{weight:.2f} lb")
        else:
            products[product_name] = weight
            product_names.add(product_name)
            add_to_history("Añadido", f"{product_name} - {weight:.2f} lb")

        update_product_list()
        update_total_weight()
        product_name_entry.delete(0, tk.END)
        product_weight_entry.delete(0, tk.END)
        product_name_entry.focus()
    except ValueError:
        messagebox.showerror("Error", "El peso debe ser un número válido.")

# Función para actualizar la lista de productos mostrada
def update_product_list():
    product_list.delete(*product_list.get_children())
    # 🔹 Orden alfabético añadido
    for product, weight in sorted(products.items(), key=lambda x: x[0].lower()):
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
        # 🔹 Exportar también en orden alfabético
        for product, weight in sorted(products.items(), key=lambda x: x[0].lower()):
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
        save_undo_state()  # Guardamos estado antes de limpiar
        for product in products.keys():
            add_to_history("Eliminado", f"{product} - {products[product]:.2f} lb")
        products.clear()
        product_names.clear()
        update_product_list()
        update_total_weight()
        messagebox.showinfo("Éxito", "La lista ha sido despejada.")

# Función para eliminar productos seleccionados
def delete_selected():
    selected_items = product_list.selection()
    if not selected_items:
        messagebox.showerror("Error", "Selecciona al menos un producto para eliminar.")
        return
    if messagebox.askyesno("Confirmar", "¿Está seguro que quiere eliminar el producto seleccionado?"):
        save_undo_state()  # Guardamos estado antes de eliminar
        for item in selected_items:
            product_name = product_list.item(item)["values"][0]
            if product_name in products:
                add_to_history("Eliminado", f"{product_name} - {products[product_name]:.2f} lb")
                del products[product_name]
                product_names.discard(product_name)
        update_product_list()
        update_total_weight()

# Función para editar un producto (nombre, restar peso y peso nuevo)
def edit_product():
    selected_item = product_list.selection()
    if len(selected_item) != 1:
        messagebox.showerror("Error", "Selecciona un único producto para editar.")
        return
    product_name = product_list.item(selected_item[0])["values"][0]
    current_weight = products[product_name]

    edit_window = tk.Toplevel(root)
    edit_window.title("Editar Producto")
    edit_window.geometry("550x450")  # Ventana más grande
    edit_window.transient(root)

    tk.Label(edit_window, text=f"Producto actual: {product_name}", font=("Arial", 12, "bold")).pack(pady=5)
    tk.Label(edit_window, text=f"Peso actual: {current_weight:.2f} lb", font=("Arial", 12)).pack(pady=5)

    # Campo para cambiar nombre
    tk.Label(edit_window, text="Nuevo Nombre:").pack(pady=5)
    new_name_entry = ttk.Entry(edit_window, font=("Arial", 11))
    new_name_entry.pack(pady=5, ipadx=5, ipady=5)
    new_name_entry.insert(0, product_name)

    # Campo para restar peso
    tk.Label(edit_window, text="Restar peso (lb):").pack(pady=5)
    subtract_weight_entry = ttk.Entry(edit_window, font=("Arial", 11))
    subtract_weight_entry.pack(pady=5, ipadx=5, ipady=5)

    # Campo para ingresar peso nuevo directamente
    tk.Label(edit_window, text="Peso Nuevo (lb):").pack(pady=5)
    new_weight_entry = ttk.Entry(edit_window, font=("Arial", 11))
    new_weight_entry.pack(pady=5, ipadx=5, ipady=5)

    def save_edit():
        new_name = new_name_entry.get().strip() or product_name
        try:
            final_weight = current_weight

            # Restar peso si se ingresó
            if subtract_weight_entry.get().strip():
                subtract_value = float(subtract_weight_entry.get())
                if subtract_value < 0:
                    messagebox.showerror("Error", "No se puede restar un valor negativo.")
                    return
                final_weight -= subtract_value
                add_to_history("Peso Restado", f"{product_name} - {subtract_value:.2f} lb (Nuevo peso: {final_weight:.2f} lb)")

            # Reemplazar con peso nuevo si se ingresó
            if new_weight_entry.get().strip():
                new_weight = float(new_weight_entry.get())
                if new_weight <= 0:
                    messagebox.showerror("Error", "El peso nuevo debe ser mayor a 0.")
                    return
                final_weight = new_weight
                add_to_history("Peso Reemplazado", f"{product_name} → {new_name} - {final_weight:.2f} lb")

            if final_weight <= 0:
                messagebox.showerror("Error", "El peso final debe ser mayor a 0.")
                return

            save_undo_state()  # Guardamos estado antes de editar

            # Eliminar producto original
            del products[product_name]
            product_names.discard(product_name)

            # Si el nuevo nombre ya existe, sumamos el peso
            if new_name in products:
                products[new_name] += final_weight
                add_to_history("Peso Sumado", f"{product_name} → {new_name} - +{final_weight:.2f} lb (Total: {products[new_name]:.2f} lb)")
            else:
                products[new_name] = final_weight
                product_names.add(new_name)
                add_to_history("Editado", f"{product_name} → {new_name} - {final_weight:.2f} lb")

            update_product_list()
            update_total_weight()
            edit_window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos.")

    # Botón más grande y visible
    ttk.Button(edit_window, text="Guardar Cambios", command=save_edit).pack(pady=30, ipadx=15, ipady=8)

# Función para registrar acciones en el historial
history_log = []

def add_to_history(action, details):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history_log.append({"fecha": timestamp.split()[0], "hora": timestamp.split()[1], "accion": action, "detalles": details})

# Función para mostrar el historial
def show_history():
    if not history_log:
        messagebox.showinfo("Historial", "No hay acciones registradas.")
        return

    history_window = tk.Toplevel(root)
    history_window.title("Historial de Acciones")
    history_window.geometry("500x400")
    history_window.transient(root)

    frame = tk.Frame(history_window)
    frame.pack(expand=True, fill="both")

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side="right", fill="y")

    text_widget = tk.Text(frame, wrap="word", font=("Arial", 11), yscrollcommand=scrollbar.set)
    text_widget.pack(expand=True, fill="both", padx=10, pady=10)

    scrollbar.config(command=text_widget.yview)

    text_widget.insert("end", "=== HISTORIAL DE ACCIONES ===\n\n")

    last_date = ""
    for entry in history_log:
        if entry["fecha"] != last_date:
            last_date = entry["fecha"]
            text_widget.insert("end", f"\n📅 {last_date}:\n")

        text_widget.insert("end", f"  🕑 {entry['hora']} - {entry['accion']}: {entry['detalles']}\n")

    text_widget.config(state="disabled")

# Configuración de la ventana principal
root = tk.Tk()
root.title("FDA")
root.geometry("800x600")
root.minsize(600, 400)

products = {}
product_names = set()

# Estilo profesional
style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", background="#E0E0E0", foreground="#333333", font=("Arial", 11))
style.configure("TButton", background="#6286f0", foreground="white", font=("Arial", 10), padding=6)
style.map("TButton", background=[("active", "#5679d6")])
style.configure("Treeview", background="#FFFFFF", foreground="#333333", font=("Arial", 13), rowheight=25)
style.configure("Treeview.Heading", font=("Arial", 13, "bold"), background="#DDDDDD")

root.configure(bg="#E0E0E0")

menu_frame = tk.Frame(root, bg="#333333", width=200)
menu_frame.grid(row=0, column=0, rowspan=3, sticky="nsw")

buttons = [
    ("Exportar a PDF", export_to_pdf),
    ("Limpiar Lista", clear_list),
    ("Eliminar Producto", delete_selected),
    ("Editar Producto", edit_product),
    ("Guardar Sesión", save_session),
    ("Ver Historial", show_history),
    ("Salir", root.quit),
]

for i, (text, command) in enumerate(buttons):
    btn = tk.Button(menu_frame, text=text, command=command, bg="#333333", fg="white", font=("Arial", 10), relief="flat")
    btn.pack(fill="x", pady=5)
    tk.Frame(menu_frame, height=2, bg="white").pack(fill="x")  # Línea blanca debajo
    btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#5679d6"))
    btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#333333"))

frame_top = tk.Frame(root, bg="#E0E0E0")
frame_top.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

tk.Label(frame_top, text="Nombre del Producto:", bg="#E0E0E0").grid(row=0, column=0, sticky="w")
product_name_entry = ttk.Combobox(frame_top, width=25)
product_name_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_top, text="Peso (lb):", bg="#E0E0E0").grid(row=1, column=0, sticky="w")
product_weight_entry = ttk.Entry(frame_top, width=25)
product_weight_entry.grid(row=1, column=1, padx=5, pady=5)

add_button = ttk.Button(frame_top, text="Añadir Producto", command=add_product)
add_button.grid(row=2, column=0, columnspan=2, pady=10)

product_list = ttk.Treeview(root, columns=("Producto", "Peso Total"), show="headings", height=15)
product_list.heading("Producto", text="Producto")
product_list.heading("Peso Total", text="Peso Total")
product_list.column("Producto", width=200)
product_list.column("Peso Total", width=100)
product_list.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

total_weight_label = tk.Label(root, text="Peso Total: 0.00 lb", font=("Arial", 12, "bold"), bg="#E0E0E0")
total_weight_label.grid(row=2, column=1, pady=10)

root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(1, weight=1)

product_name_entry.bind("<Return>", lambda e: product_weight_entry.focus())
product_weight_entry.bind("<Return>", add_product)

# Ctrl+Z para deshacer
root.bind("<Control-z>", undo_action)

def auto_save():
    if root.winfo_exists():
        save_session(False)  
        root.after(10000, auto_save)

load_session()
root.after(10000, auto_save)
root.mainloop()
