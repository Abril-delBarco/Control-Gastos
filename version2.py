import tkinter as tk
from tkinter import messagebox
from tkinter import ttk 
import json
import os
from datetime import datetime 
from collections import defaultdict

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
    
    def get_mes_anio(self):
        """Retorna el mes en formato 'Mes'"""
        try:
            fecha_obj = datetime.strptime(self.fecha, "%d/%m/%Y")
            meses_nombres = {
                1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
            }
            mes_nombre = meses_nombres[fecha_obj.month]
            return mes_nombre
        except:
            return "Fecha inválida"

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

    def obtener_balance(self, mes_filtro=None):
        #Calcula balance total o filtrado por mes
        total = 0
        pagado = 0
        pendiente = 0
        
        gastos_filtrados = self.gastos
        if mes_filtro and mes_filtro != "Todos":
            gastos_filtrados = [g for g in self.gastos if g.get_mes_anio() == mes_filtro]
        
        for gasto in gastos_filtrados:
            total += gasto.monto
            if gasto.estado:
                pagado += gasto.monto
            else:
                pendiente += gasto.monto
                
        return total, pagado, pendiente
    
    def obtener_meses_disponibles(self):
        meses_nombres = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        
        return meses_nombres
    
    def obtener_gastos_por_categoria(self, mes_filtro=None):
        """Agrupa gastos por categoría"""
        categorias = defaultdict(float)
        
        gastos_filtrados = self.gastos
        if mes_filtro and mes_filtro != "Todos":
            gastos_filtrados = [g for g in self.gastos if g.get_mes_anio() == mes_filtro]
        
        for gasto in gastos_filtrados:
            categorias[gasto.categoria] += gasto.monto
            
        return dict(categorias)


#Interfaz

class InterfazGrafica:
    def __init__(self, root):
        self.gestor = Gestor() 
        self.root = root
        self.root.title("Billetera - Dashboard")
        self.root.geometry("550x800") 
        self.root.configure(bg='#1F3A5F') 
        
        # === FILTRO DE MESES ===
        frame_filtro = tk.Frame(root, bg='#1F3A5F', pady=10)
        frame_filtro.pack()
        
        tk.Label(frame_filtro, text="Filtrar por mes:", bg='#2E86DE', font=('Arial', 11, 'bold')).pack(side='left', padx=5)
        self.combo_mes = ttk.Combobox(frame_filtro, state="readonly", width=15, font=('Arial', 10))
        self.combo_mes.pack(side='left', padx=5)
        self.combo_mes.bind("<<ComboboxSelected>>", lambda e: self.actualizar_vista())
        
    
        frame_form = tk.Frame(root, bg='#1F3A5F', pady=10)
        frame_form.pack()
        
        #Monto
        tk.Label(frame_form, text="Monto ($):", bg='#2E86DE', font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.entry_monto = tk.Entry(frame_form, font=('Arial', 10), width=20)
        self.entry_monto.grid(row=0, column=1, padx=5, pady=5)

        #Descripción
        tk.Label(frame_form, text="Descripción:", bg='#2E86DE', font=('Arial', 10, 'bold')).grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.entry_desc = tk.Entry(frame_form, font=('Arial', 10), width=20)
        self.entry_desc.grid(row=1, column=1, padx=5, pady=5)

        #Categoría 
        tk.Label(frame_form, text="Categoría:", bg='#2E86DE', font=('Arial', 10, 'bold')).grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.combo_cat = ttk.Combobox(frame_form, 
                                      values=["Comida", "Servicios", "Diversión", "Transporte", "Ropa", "Salud", "Educación", "Otros"],
                                      state="readonly", width=18)
        self.combo_cat.grid(row=2, column=1, padx=5, pady=5)
        self.combo_cat.current(0)
        
        #Fecha
        tk.Label(frame_form, text="Fecha (dd/mm/aaaa):", bg='#2E86DE', font=('Arial', 10, 'bold')).grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.entry_fecha = tk.Entry(frame_form, font=('Arial', 10), width=20)
        self.entry_fecha.grid(row=3, column=1, padx=5, pady=5)
        
        #Botón para fecha de hoy
        btn_hoy = tk.Button(frame_form, text="Hoy", command=self.poner_fecha_hoy, bg='#95A5A6', fg='white', font=('Arial', 8))
        btn_hoy.grid(row=3, column=2, padx=2)

        #Botón Agregar
        btn_agregar = tk.Button(root, text="Agregar Gasto", command=self.agregar, bg='#2E86DE', fg='white', font=('Arial', 11, 'bold'), width=20)
        btn_agregar.pack(pady=10)
        
        #LISTA DE GASTOS 
        frame_lista = tk.Frame(root, bg='#1F3A5F')
        frame_lista.pack(padx=10, pady=5, fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side='right', fill='y')
        
        self.lista_box = tk.Listbox(frame_lista, font=('Consolas', 9), width=65, height=12, yscrollcommand=scrollbar.set)
        self.lista_box.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.lista_box.yview)

    
        frame_acciones = tk.Frame(root, bg='#1F3A5F', pady=10)
        frame_acciones.pack()

        btn_pagar = tk.Button(frame_acciones, text="Pagar", command=self.pagar, bg='#27AE60', fg='white', font=('Arial', 10, 'bold'), width=12)
        btn_pagar.pack(side='left', padx=5)

        btn_eliminar = tk.Button(frame_acciones, text="Eliminar", command=self.eliminar, bg='#E74C3C', fg='white', font=('Arial', 10, 'bold'), width=12)
        btn_eliminar.pack(side='left', padx=5)
        
        btn_editar = tk.Button(frame_acciones, text="Editar", command=self.editar, bg='#FFA500', fg='white', font=('Arial', 10, 'bold'), width=12)
        btn_editar.pack(side='left', padx=5)

        #BALANCE 
        self.label_total = tk.Label(root, text="Cargando...", bg='#7F9C96', fg='black', font=('Arial', 12, 'bold'), width=50, height=4, justify="left")
        self.label_total.pack(pady=10, padx=10)

        self.actualizar_vista()
    
    def poner_fecha_hoy(self):
        """Coloca la fecha de hoy en el campo de fecha"""
        hoy = datetime.now().strftime("%d/%m/%Y")
        self.entry_fecha.delete(0, tk.END)
        self.entry_fecha.insert(0, hoy)
    
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
            datetime.strptime(fecha_texto, "%d/%m/%Y")
    
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
            index = self.obtener_indice_real(seleccion[0])
            respuesta = messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar este gasto?")
            if respuesta:
                self.gestor.eliminarGasto(index)
                self.actualizar_vista()
        else:
            messagebox.showwarning("Atención", "Selecciona un gasto primero")

    def pagar(self):
        seleccion = self.lista_box.curselection()
        if seleccion:
            index = self.obtener_indice_real(seleccion[0])
            self.gestor.pagarGastos(index) 
            self.actualizar_vista()
        else:
            messagebox.showwarning("Atención", "Selecciona un gasto primero")
    
    def editar(self):
        """Permite editar un gasto existente"""
        seleccion = self.lista_box.curselection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un gasto primero")
            return
            
        index = self.obtener_indice_real(seleccion[0])
        gasto = self.gestor.gastos[index]
        
        # Crear ventana de edición
        ventana_editar = tk.Toplevel(self.root)
        ventana_editar.title("Editar Gasto")
        ventana_editar.geometry("350x250")
        ventana_editar.configure(bg='#1F3A5F')
        
        # Campos de edición
        tk.Label(ventana_editar, text="Monto ($):", bg='#1F3A5F', font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=10, pady=10, sticky='e')
        entry_monto_edit = tk.Entry(ventana_editar, font=('Arial', 10))
        entry_monto_edit.insert(0, str(gasto.monto))
        entry_monto_edit.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(ventana_editar, text="Descripción:", bg='#1F3A5F', font=('Arial', 10, 'bold')).grid(row=1, column=0, padx=10, pady=10, sticky='e')
        entry_desc_edit = tk.Entry(ventana_editar, font=('Arial', 10))
        entry_desc_edit.insert(0, gasto.descripcion)
        entry_desc_edit.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(ventana_editar, text="Categoría:", bg='#1F3A5F', font=('Arial', 10, 'bold')).grid(row=2, column=0, padx=10, pady=10, sticky='e')
        combo_cat_edit = ttk.Combobox(ventana_editar, values=["Comida", "Servicios", "Diversión", "Transporte", "Ropa", "Salud", "Educación", "Otros"], state="readonly")
        combo_cat_edit.set(gasto.categoria)
        combo_cat_edit.grid(row=2, column=1, padx=10, pady=10)
        
        tk.Label(ventana_editar, text="Fecha:", bg='#1F3A5F', font=('Arial', 10, 'bold')).grid(row=3, column=0, padx=10, pady=10, sticky='e')
        entry_fecha_edit = tk.Entry(ventana_editar, font=('Arial', 10))
        entry_fecha_edit.insert(0, gasto.fecha)
        entry_fecha_edit.grid(row=3, column=1, padx=10, pady=10)
        
        def guardar_cambios():
            try:
                nuevo_monto = float(entry_monto_edit.get())
                nueva_desc = entry_desc_edit.get()
                nueva_cat = combo_cat_edit.get()
                nueva_fecha = entry_fecha_edit.get()
                
                datetime.strptime(nueva_fecha, "%d/%m/%Y")
                
                gasto.monto = nuevo_monto
                gasto.descripcion = nueva_desc
                gasto.categoria = nueva_cat
                gasto.fecha = nueva_fecha
                
                self.gestor.guardarGastos()
                self.actualizar_vista()
                ventana_editar.destroy()
                messagebox.showinfo("Éxito", "Gasto actualizado correctamente")
            except ValueError:
                messagebox.showerror("Error", "Verifica los datos ingresados")
        
        btn_guardar = tk.Button(ventana_editar, text="Guardar Cambios", command=guardar_cambios, bg='#27AE60', fg='white', font=('Arial', 10, 'bold'))
        btn_guardar.grid(row=4, column=0, columnspan=2, pady=20)

    def obtener_indice_real(self, indice_visual):
        """Convierte el índice visual (filtrado) al índice real en la lista completa"""
        mes_seleccionado = self.combo_mes.get()
        
        if mes_seleccionado == "Todos":
            return indice_visual
        contador = 0
        for i, gasto in enumerate(self.gestor.gastos):
            if gasto.get_mes_anio() == mes_seleccionado:
                if contador == indice_visual:
                    return i
                contador += 1
        return indice_visual

    def actualizar_vista(self):
        # Actualizar combo de meses
        meses = ["Todos"] + self.gestor.obtener_meses_disponibles()
        self.combo_mes['values'] = meses
        if not self.combo_mes.get() or self.combo_mes.get() not in meses:
            self.combo_mes.current(0)
        
        mes_seleccionado = self.combo_mes.get()
        
        # Actualizar lista de gastos
        self.lista_box.delete(0, tk.END)
        
        gastos_a_mostrar = self.gestor.gastos
        if mes_seleccionado != "Todos":
            gastos_a_mostrar = [g for g in self.gestor.gastos if g.get_mes_anio() == mes_seleccionado]
        
        for g in gastos_a_mostrar:
            estado = "[PAGADO]" if g.estado else "[DEUDA]"
            texto = f"{g.fecha} | ${g.monto:,.2f} | {g.descripcion[:25]} ({g.categoria}) {estado}"
            self.lista_box.insert(tk.END, texto)
            
            if g.estado:
                self.lista_box.itemconfig(tk.END, {'fg': 'green'}) 
            else:
                self.lista_box.itemconfig(tk.END, {'fg': 'red'})   

        # Actualizar balance con colores
        total, pagado, pendiente = self.gestor.obtener_balance(mes_seleccionado)
        
        titulo = f"BALANCE - {mes_seleccionado}\n" if mes_seleccionado != "Todos" else "BALANCE TOTAL\n"
        
        # Crear texto con colores usando tags
        self.label_total.config(text="")
        
        # Destruir label anterior y crear uno nuevo con Text widget
        self.label_total.pack_forget()
        
        # Crear un widget Text en lugar de Label para usar colores
        if not hasattr(self, 'text_balance'):
            self.text_balance = tk.Text(self.root, bg='white', fg='white', 
                                        font=('Arial', 12, 'bold'), width=50, height=4,
                                        relief='flat', borderwidth=0)
            self.text_balance.pack(pady=10, padx=10)
            
            # Configurar tags de colores
            self.text_balance.tag_config('verde', foreground='#008000')
            self.text_balance.tag_config('rojo', foreground='#E74C3C')
            self.text_balance.tag_config('blanco', foreground='black')
        
        # Limpiar y actualizar contenido
        self.text_balance.config(state='normal')
        self.text_balance.delete('1.0', tk.END)
        
        self.text_balance.insert('end', titulo, 'blanco')
        self.text_balance.insert('end', f"Total registrado: ${total:,.2f}\n", 'blanco')
        self.text_balance.insert('end', f"Ya pago: ${pagado:,.2f}\n", 'verde')
        self.text_balance.insert('end', f"Falta pagar: ${pendiente:,.2f}", 'rojo')
        
        self.text_balance.config(state='disabled')   

        # Actualizar balance
        total, pagado, pendiente = self.gestor.obtener_balance(mes_seleccionado)
        
        titulo = f"BALANCE - {mes_seleccionado}\n" if mes_seleccionado != "Todos" else "BALANCE TOTAL\n"
        texto_balance = titulo
        texto_balance += f"Total : ${total:,.2f}\n"
        texto_balance += f"Ya pago: ${pagado:,.2f}\n"
        texto_balance += f"Falta pagar: ${pendiente:,.2f}"
        
        self.label_total.config(text=texto_balance)


#Arranque


if __name__ == "__main__":
    ventana = tk.Tk()
    app = InterfazGrafica(ventana)
    ventana.mainloop()