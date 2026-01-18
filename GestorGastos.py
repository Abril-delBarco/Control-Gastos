import tkinter as tk
from tkinter import messagebox
from tkinter import ttk 
import json
import os
from datetime import datetime 

class Gasto:
    def __init__(self, monto, descripcion, categoria, fecha, estado=False):
        self.monto = float(monto)
        self.descripcion = descripcion
        self.categoria = categoria
        self.fecha = fecha
        self.estado = estado
    
    def pagarCuenta(self):
        self.estado = True
        
    def to_dict(self):
        return {
            "monto": self.monto, 
            "descripcion": self.descripcion,
            "categoria": self.categoria,
            "fecha": self.fecha,
            "estado": self.estado
        }

    @staticmethod 
    def from_dict(data):
        return Gasto(data["monto"], data["descripcion"], data["categoria"], data["fecha"], data["estado"])
    
class Gestor:
    def __init__(self):
        self.archivo = "Gastos.json"
        self.gastos = []
        self.cargarGastos()

    def agregarGasto(self, monto, descripcion, categoria, fecha, estado):
        nuevoGasto = Gasto(monto, descripcion, categoria, fecha, estado)
        self.gastos.append(nuevoGasto)
        self.guardarGastos() 

    def eliminarGasto(self, indice):
         if 0 <= indice < len(self.gastos):
            self.gastos.pop(indice)
            self.guardarGastos() 
    
    def pagarGastos(self, indice):
        if 0 <= indice < len(self.gastos):
            self.gastos[indice].pagarCuenta()
            self.guardarGastos() 
    
    def guardarGastos(self):
        datos = [t.to_dict() for t in self.gastos] 
        with open(self.archivo, 'w') as f:  
            json.dump(datos, f, indent=4)

    def cargarGastos(self):
        try:
            with open(self.archivo, 'r') as f:
                datos = json.load(f)
                self.gastos = [Gasto.from_dict(d) for d in datos]
        except FileNotFoundError:
            self.gastos = [] 

    def obtener_balance(self):
        total = 0
        pagado = 0
        pendiente = 0
        
        for gasto in self.gastos:
            total += gasto.monto # Suma al total general
            
            if gasto.estado: #Si es True (Pagado)
                pagado += gasto.monto
            else: #Si es False (Deuda)
                pendiente += gasto.monto
                
        return total, pagado, pendiente
    

class InterfazGrafica:
    def __init__(self, root):
        self.gestor = Gestor() 
        self.root = root
        self.root.title("Billetera - Dashboard")
        self.root.geometry("500x750") 
        self.root.configure(bg='#D0ABDE') 
        
        frame_form = tk.Frame(root, bg='#D0ABDE', pady=10)
        frame_form.pack()
        
        # Monto
        tk.Label(frame_form, text="Monto ($):", bg='#D0ABDE', font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=5)
        self.entry_monto = tk.Entry(frame_form, font=('Arial', 10))
        self.entry_monto.grid(row=0, column=1, padx=5, pady=5)

        # Descripción
        tk.Label(frame_form, text="Descripción:", bg='#D0ABDE', font=('Arial', 10, 'bold')).grid(row=1, column=0, padx=5, pady=5)
        self.entry_desc = tk.Entry(frame_form, font=('Arial', 10))
        self.entry_desc.grid(row=1, column=1, padx=5, pady=5)

        # Categoría 
        tk.Label(frame_form, text="Categoría:", bg='#D0ABDE', font=('Arial', 10, 'bold')).grid(row=2, column=0, padx=5, pady=5)
        self.combo_cat = ttk.Combobox(frame_form, 
                                      values=["Comida", "Servicios", "Diversión", "Transporte", "Ropa", "Otros"],
                                      state="readonly")
        self.combo_cat.grid(row=2, column=1, padx=5, pady=5)
        self.combo_cat.current(0)
        
        # Fecha
        tk.Label(frame_form, text="Fecha (dd/mm/aaaa):", bg='#D0ABDE', font=('Arial', 10, 'bold')).grid(row=3, column=0, padx=5, pady=5)
        self.entry_fecha = tk.Entry(frame_form, font=('Arial', 10))
        self.entry_fecha.grid(row=3, column=1, padx=5, pady=5)

        # Botón Agregar 
        btn_agregar = tk.Button(root, text="Agregar Gasto", command=self.agregar, bg='#27AE60', fg='white', font=('Arial', 11, 'bold'), width=20)
        btn_agregar.pack(pady=10)
        
        # Lista
        self.lista_box = tk.Listbox(root, font=('Consolas', 10), width=60, height=15)
        self.lista_box.pack(padx=10, pady=5)

        # Botones de Acción
        frame_acciones = tk.Frame(root, bg='#D0ABDE', pady=10)
        frame_acciones.pack()

        btn_pagar = tk.Button(frame_acciones, text="Pagar", command=self.pagar, bg='#3498DB', fg='white', font=('Arial', 10))
        btn_pagar.pack(side='left', padx=10)

        btn_eliminar = tk.Button(frame_acciones, text="Eliminar", command=self.eliminar, bg='#E74C3C', fg='white', font=('Arial', 10))
        btn_eliminar.pack(side='left', padx=10)

       
        self.label_total = tk.Label(root, text="Cargando...", bg='#9847B8', fg='white', font=('Arial', 12, 'bold'), width=50, height=4, justify="left")
        self.label_total.pack(pady=10, padx=10)

        self.actualizar_vista()
    
    def agregar(self):
        try:
            monto_texto = self.entry_monto.get()
            desc = self.entry_desc.get()
            cat = self.combo_cat.get() 
            fecha_texto = self.entry_fecha.get()
            
            estado_inicial = False 

            if not desc or not cat or not fecha_texto:
                messagebox.showwarning("Faltan datos", "Por favor completa todos los campos.")
                return 
          
            monto = float(monto_texto)
            datetime.strptime(fecha_texto, "%d/%m/%Y") #Validación fecha
    
            self.gestor.agregarGasto(monto, desc, cat, fecha_texto, estado_inicial)
            
            self.entry_monto.delete(0, tk.END)
            self.entry_desc.delete(0, tk.END)
            self.entry_fecha.delete(0, tk.END)
            
            self.actualizar_vista()

        except ValueError as e:
            if "could not convert string to float" in str(e):
                messagebox.showerror("Error", "El MONTO debe ser un número (ej: 1500)")
            else:
                messagebox.showerror("Error", "La FECHA debe ser formato dd/mm/aaaa (ej: 18/01/2026)")

    def eliminar(self):
        seleccion = self.lista_box.curselection()
        if seleccion:
            index = seleccion[0]
            self.gestor.eliminarGasto(index)
            self.actualizar_vista()
        else:
            messagebox.showwarning("Atención", "Selecciona un gasto primero")

    def pagar(self):
        seleccion = self.lista_box.curselection()
        if seleccion:
            index = seleccion[0]
            self.gestor.pagarGastos(index) 
            self.actualizar_vista()
        else:
            messagebox.showwarning("Atención", "Selecciona un gasto primero")

    def actualizar_vista(self):
        self.lista_box.delete(0, tk.END)
        for g in self.gestor.gastos:
            estado = "[PAGADO]" if g.estado else "[DEUDA]"
            texto = f"{g.fecha} | ${g.monto} | {g.descripcion} ({g.categoria}) {estado}"
            self.lista_box.insert(tk.END, texto)
            
            if g.estado:
                self.lista_box.itemconfig(tk.END, {'fg': 'green'}) 
            else:
                self.lista_box.itemconfig(tk.END, {'fg': 'red'})   

        total, pagado, pendiente = self.gestor.obtener_balance()
        
        texto_balance = f"TOTAL REGISTRADO: ${total}\n"
        texto_balance += f"YA PAGADO: ${pagado}\n"
        texto_balance += f"FALTA PAGAR: ${pendiente}"
        
        self.label_total.config(text=texto_balance)

    
if __name__ == "__main__":
    ventana = tk.Tk()
    app = InterfazGrafica(ventana)
    ventana.mainloop()