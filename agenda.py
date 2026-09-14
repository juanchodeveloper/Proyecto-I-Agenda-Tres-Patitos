import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import customtkinter as ctk
import psycopg2

try:
    from tkcalendar import DateEntry
except ImportError:
    DateEntry = None


# Configuracion sencilla para la defensa. Ajustar solo este bloque si cambia el entorno.
DB_CONFIG = {
    "dbname": "agenda",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432",
}

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class AppAgenda(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Agenda 3 Patitos')
        self.geometry('1500x860')
        self.minsize(1180, 720)

        self.conn_params = DB_CONFIG.copy()

        self.usuarios_combo = {}
        self.usuarios_activos_combo = {}
        self.categorias_combo = {}
        self.categorias_padre_combo = {}
        self.ubicaciones_combo = {}
        self.eventos_combo = {}
        self.tipos_disponibilidad_combo = {}

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.crear_sidebar()
        self.crear_area_principal()
        self.configurar_estilos()
        self.actualizar_todas_las_tablas()

        if DateEntry is None:
            self.after(
                500,
                lambda: messagebox.showwarning(
                    'Calendario no instalado',
                    'Para usar selectores de fecha instala:\n\npip install tkcalendar',
                ),
            )

    # ------------------------------------------------------------
    # INFRAESTRUCTURA
    # ------------------------------------------------------------
    def obtener_conexion(self):
        conn = psycopg2.connect(**self.conn_params)
        with conn.cursor() as cur:
            cur.execute('SET search_path TO prototipo, public;')
        return conn

    def ejecutar_consulta(self, sql, params=None, fetch=False):
        conn = None
        try:
            conn = self.obtener_conexion()
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall() if fetch else None
            conn.commit()
            return rows
        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def configurar_estilos(self):
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass
        style.configure('Treeview', rowheight=29, font=('Arial', 10))
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))

    def crear_treeview(self, parent, columnas, widths, height=None):
        contenedor = ctk.CTkFrame(parent, fg_color='transparent')
        contenedor.pack(fill='both', expand=True, padx=10, pady=10)
        tree = ttk.Treeview(contenedor, columns=columnas, show='headings', height=height)
        for col, width in zip(columnas, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor='center')
        scroll_y = ttk.Scrollbar(contenedor, orient='vertical', command=tree.yview)
        scroll_x = ttk.Scrollbar(contenedor, orient='horizontal', command=tree.xview)
        tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        tree.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')
        scroll_x.grid(row=1, column=0, sticky='ew')
        contenedor.grid_rowconfigure(0, weight=1)
        contenedor.grid_columnconfigure(0, weight=1)
        return tree

    @staticmethod
    def id_seleccionado(tree):
        seleccion = tree.selection()
        return tree.item(seleccion[0])['values'][0] if seleccion else None

    def crear_selector_fecha(self, parent):
        if DateEntry is not None:
            return DateEntry(parent, date_pattern='yyyy-mm-dd', font=('Arial', 10))
        return ttk.Entry(parent)

    @staticmethod
    def obtener_fecha(widget):
        if DateEntry is not None and isinstance(widget, DateEntry):
            return widget.get_date().strftime('%Y-%m-%d')
        return widget.get().strip()

    @staticmethod
    def establecer_fecha(widget, valor):
        fecha = valor.date() if hasattr(valor, 'date') else datetime.strptime(str(valor)[:10], '%Y-%m-%d').date()
        if DateEntry is not None and isinstance(widget, DateEntry):
            widget.set_date(fecha)
        else:
            widget.delete(0, tk.END)
            widget.insert(0, fecha.strftime('%Y-%m-%d'))

    @staticmethod
    def leer_hora(valor):
        try:
            return datetime.strptime(valor.strip(), '%H:%M').time()
        except ValueError as exc:
            raise ValueError('La hora debe tener formato HH:MM, por ejemplo 09:30.') from exc

    @staticmethod
    def valor_textbox(widget):
        return widget.get('1.0', 'end').strip()

    def seleccionar_modulo(self, nombre):
        self.tabview.set(nombre)
        for modulo, boton in self.botones_nav.items():
            boton.configure(fg_color=('gray75', 'gray25') if modulo == nombre else 'transparent')

    # ------------------------------------------------------------
    # NAVEGACION
    # ------------------------------------------------------------
    def crear_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=245, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky='nsew')
        self.sidebar_frame.grid_propagate(False)
        self.sidebar_frame.grid_rowconfigure(20, weight=1)

        ctk.CTkLabel(
            self.sidebar_frame,
            text='📅 AGENDA 🦆🦆🦆',
            font=ctk.CTkFont(size=22, weight='bold'),
        ).grid(row=0, column=0, padx=20, pady=(28, 5), sticky='w')
        ctk.CTkLabel(
            self.sidebar_frame,
            text='Agenda Digital Tres Patitos',
            font=ctk.CTkFont(size=11),
        ).grid(row=1, column=0, padx=20, pady=(0, 18), sticky='w')

        modulos = [
            ('Usuarios', '👥'),
            ('Categorías', '📁'),
            ('Eventos', '📆'),
            ('Ubicaciones', '📍'),
            ('Disponibilidad', '🕒'),
            ('Tareas', '✅'),
        ]
        self.botones_nav = {}
        for i, (nombre, icono) in enumerate(modulos, start=2):
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=f'{icono} {nombre}',
                anchor='w',
                fg_color='transparent',
                command=lambda n=nombre: self.seleccionar_modulo(n),
            )
            btn.grid(row=i, column=0, padx=15, pady=4, sticky='ew')
            self.botones_nav[nombre] = btn

        ctk.CTkButton(
            self.sidebar_frame,
            text='🔄 Recargar datos',
            command=self.actualizar_todas_las_tablas,
        ).grid(row=9, column=0, padx=15, pady=(18, 5), sticky='ew')

        ctk.CTkLabel(
            self.sidebar_frame,
            text='APARIENCIA',
            font=ctk.CTkFont(size=11, weight='bold'),
        ).grid(row=21, column=0, padx=20, pady=(10, 5), sticky='w')
        self.option_mode = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=['System', 'Dark', 'Light'],
            command=ctk.set_appearance_mode,
        )
        self.option_mode.set('System')
        self.option_mode.grid(row=22, column=0, padx=15, pady=(0, 25), sticky='ew')

    def crear_area_principal(self):
        self.main_container = ctk.CTkFrame(self, fg_color='transparent')
        self.main_container.grid(row=0, column=1, sticky='nsew', padx=18, pady=18)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(self.main_container, command=self.al_cambiar_pestana)
        self.tabview.grid(row=0, column=0, sticky='nsew')

        self.tab_usuarios = self.tabview.add('Usuarios')
        self.tab_categorias = self.tabview.add('Categorías')
        self.tab_eventos = self.tabview.add('Eventos')
        self.tab_ubicaciones = self.tabview.add('Ubicaciones')
        self.tab_disponibilidad = self.tabview.add('Disponibilidad')
        self.tab_tareas = self.tabview.add('Tareas')

        self.configurar_pestana_usuarios()
        self.configurar_pestana_categorias()
        self.configurar_pestana_eventos()
        self.configurar_pestana_ubicaciones()
        self.configurar_pestana_disponibilidad()
        self.configurar_pestana_tareas()
        self.seleccionar_modulo('Usuarios')

    def al_cambiar_pestana(self):
        nombre = self.tabview.get()
        for modulo, boton in self.botones_nav.items():
            boton.configure(fg_color=('gray75', 'gray25') if modulo == nombre else 'transparent')

    @staticmethod
    def crear_encabezado(parent, titulo, descripcion):
        ctk.CTkLabel(parent, text=titulo, font=ctk.CTkFont(size=24, weight='bold')).pack(
            anchor='w', padx=15, pady=(15, 0)
        )
        ctk.CTkLabel(parent, text=descripcion, font=ctk.CTkFont(size=12)).pack(
            anchor='w', padx=15, pady=(0, 10)
        )

    # ------------------------------------------------------------
    # USUARIOS
    # ------------------------------------------------------------
    def configurar_pestana_usuarios(self):
        self.crear_encabezado(self.tab_usuarios, 'Usuarios', 'Registra, consulta y administra los usuarios de la agenda.')
        cuerpo = ctk.CTkFrame(self.tab_usuarios, fg_color='transparent')
        cuerpo.pack(fill='both', expand=True, padx=10, pady=5)
        cuerpo.grid_columnconfigure(0, weight=3)
        cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=1)

        tabla = ctk.CTkFrame(cuerpo)
        tabla.grid(row=0, column=0, sticky='nsew', padx=(0, 8))
        form = ctk.CTkScrollableFrame(cuerpo, width=310)
        form.grid(row=0, column=1, sticky='nsew')

        self.tree_usuarios = self.crear_treeview(
            tabla, ('ID', 'Nombre', 'Apellido', 'Registro', 'Activo'), (70, 170, 170, 140, 90)
        )
        self.tree_usuarios.bind('<<TreeviewSelect>>', self.cargar_usuario_seleccionado)

        ctk.CTkLabel(form, text='Formulario de usuario', font=ctk.CTkFont(size=16, weight='bold')).pack(pady=(10, 15))
        self.entry_nombre = ctk.CTkEntry(form, placeholder_text='Nombre')
        self.entry_nombre.pack(fill='x', padx=10, pady=6)
        self.entry_apellido = ctk.CTkEntry(form, placeholder_text='Apellido')
        self.entry_apellido.pack(fill='x', padx=10, pady=6)
        self.switch_usuario_activo = ctk.CTkSwitch(form, text='Usuario activo')
        self.switch_usuario_activo.select()
        self.switch_usuario_activo.pack(anchor='w', padx=12, pady=10)

        ctk.CTkButton(form, text='➕ Registrar usuario', command=self.agregar_usuario).pack(fill='x', padx=10, pady=(12, 5))
        ctk.CTkButton(form, text='💾 Actualizar seleccionado', command=self.actualizar_usuario).pack(fill='x', padx=10, pady=5)
        ctk.CTkButton(form, text='🧹 Nuevo / Limpiar', command=self.limpiar_form_usuario, fg_color='gray').pack(fill='x', padx=10, pady=5)
        ctk.CTkButton(form, text='🗑 Eliminar seleccionado', command=self.eliminar_usuario, fg_color='#b33939', hover_color='#8f2d2d').pack(fill='x', padx=10, pady=5)

    def cargar_usuario_seleccionado(self, _=None):
        sel = self.tree_usuarios.selection()
        if not sel:
            return
        vals = self.tree_usuarios.item(sel[0])['values']
        self.entry_nombre.delete(0, tk.END)
        self.entry_nombre.insert(0, vals[1])
        self.entry_apellido.delete(0, tk.END)
        self.entry_apellido.insert(0, vals[2])
        self.switch_usuario_activo.select() if vals[4] == 'Sí' else self.switch_usuario_activo.deselect()

    def limpiar_form_usuario(self):
        self.tree_usuarios.selection_remove(self.tree_usuarios.selection())
        self.entry_nombre.delete(0, tk.END)
        self.entry_apellido.delete(0, tk.END)
        self.switch_usuario_activo.select()

    def agregar_usuario(self):
        nombre, apellido = self.entry_nombre.get().strip(), self.entry_apellido.get().strip()
        if not nombre or not apellido:
            return messagebox.showwarning('Campos incompletos', 'Indica nombre y apellido.')
        try:
            self.ejecutar_consulta(
                'INSERT INTO usuarios (nombre, apellido, activo) VALUES (%s, %s, %s)',
                (nombre, apellido, self.switch_usuario_activo.get() == 1),
            )
            self.limpiar_form_usuario()
            self.actualizar_todas_las_tablas()
            messagebox.showinfo('Éxito', 'Usuario registrado correctamente.')
        except Exception as e:
            messagebox.showerror('Error de base de datos', str(e))

    def actualizar_usuario(self):
        uid = self.id_seleccionado(self.tree_usuarios)
        if uid is None:
            return messagebox.showwarning('Selección requerida', 'Selecciona un usuario para actualizar.')
        nombre, apellido = self.entry_nombre.get().strip(), self.entry_apellido.get().strip()
        if not nombre or not apellido:
            return messagebox.showwarning('Campos incompletos', 'Indica nombre y apellido.')
        try:
            self.ejecutar_consulta(
                'UPDATE usuarios SET nombre=%s, apellido=%s, activo=%s WHERE id_usuario=%s',
                (nombre, apellido, self.switch_usuario_activo.get() == 1, uid),
            )
            self.actualizar_todas_las_tablas()
            messagebox.showinfo('Éxito', 'Usuario actualizado.')
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def eliminar_usuario(self):
        uid = self.id_seleccionado(self.tree_usuarios)
        if uid is None:
            return messagebox.showwarning('Selección requerida', 'Selecciona un usuario.')
        if not messagebox.askyesno('Confirmar', '¿Eliminar el usuario seleccionado?'):
            return
        try:
            self.ejecutar_consulta('DELETE FROM usuarios WHERE id_usuario=%s', (uid,))
            self.limpiar_form_usuario()
            self.actualizar_todas_las_tablas()
            messagebox.showinfo('Eliminado', 'Usuario eliminado.')
        except Exception as e:
            messagebox.showerror('No se pudo eliminar', str(e))

    def cargar_datos_usuarios(self):
        rows = self.ejecutar_consulta(
            'SELECT id_usuario, nombre, apellido, fecha_registro, activo FROM usuarios ORDER BY nombre, apellido',
            fetch=True,
        )
        for item in self.tree_usuarios.get_children():
            self.tree_usuarios.delete(item)
        self.usuarios_combo = {}
        self.usuarios_activos_combo = {}
        for uid, nombre, apellido, registro, activo in rows:
            self.tree_usuarios.insert('', 'end', values=(uid, nombre, apellido, registro, 'Sí' if activo else 'No'))
            etiqueta = f'{nombre} {apellido} — #{uid}'
            self.usuarios_combo[etiqueta] = uid
            if activo:
                self.usuarios_activos_combo[etiqueta] = uid

    # ------------------------------------------------------------
    # CATEGORIAS
    # ------------------------------------------------------------
    def configurar_pestana_categorias(self):
        self.crear_encabezado(self.tab_categorias, 'Categorías', 'Organiza los eventos mediante categorías y subcategorías.')
        cuerpo = ctk.CTkFrame(self.tab_categorias, fg_color='transparent')
        cuerpo.pack(fill='both', expand=True, padx=10, pady=5)
        cuerpo.grid_columnconfigure(0, weight=3)
        cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=1)

        tabla = ctk.CTkFrame(cuerpo)
        tabla.grid(row=0, column=0, sticky='nsew', padx=(0, 8))
        form = ctk.CTkScrollableFrame(cuerpo, width=320)
        form.grid(row=0, column=1, sticky='nsew')

        self.tree_categorias = self.crear_treeview(tabla, ('ID', 'Categoría', 'Categoría padre'), (80, 230, 230))
        self.tree_categorias.bind('<<TreeviewSelect>>', self.cargar_categoria_seleccionada)

        ctk.CTkLabel(form, text='Formulario de categoría', font=ctk.CTkFont(size=16, weight='bold')).pack(pady=(10, 15))
        self.entry_cat_nombre = ctk.CTkEntry(form, placeholder_text='Nombre de la categoría')
        self.entry_cat_nombre.pack(fill='x', padx=10, pady=6)
        ctk.CTkLabel(form, text='Categoría padre').pack(anchor='w', padx=10, pady=(10, 2))
        self.combo_cat_padre = ctk.CTkComboBox(form, values=['Sin categoría padre'], state='readonly')
        self.combo_cat_padre.set('Sin categoría padre')
        self.combo_cat_padre.pack(fill='x', padx=10, pady=6)

        ctk.CTkButton(form, text='➕ Crear categoría', command=self.agregar_categoria).pack(fill='x', padx=10, pady=(15, 5))
        ctk.CTkButton(form, text='💾 Actualizar seleccionada', command=self.actualizar_categoria).pack(fill='x', padx=10, pady=5)
        ctk.CTkButton(form, text='🧹 Nueva / Limpiar', command=self.limpiar_form_categoria, fg_color='gray').pack(fill='x', padx=10, pady=5)
        ctk.CTkButton(form, text='🗑 Eliminar seleccionada', command=self.eliminar_categoria, fg_color='#b33939', hover_color='#8f2d2d').pack(fill='x', padx=10, pady=5)

    def cargar_categoria_seleccionada(self, _=None):
        sel = self.tree_categorias.selection()
        if not sel:
            return
        vals = self.tree_categorias.item(sel[0])['values']
        self.entry_cat_nombre.delete(0, tk.END)
        self.entry_cat_nombre.insert(0, vals[1])
        self.combo_cat_padre.set(vals[2] if vals[2] in self.categorias_padre_combo else 'Sin categoría padre')

    def limpiar_form_categoria(self):
        self.tree_categorias.selection_remove(self.tree_categorias.selection())
        self.entry_cat_nombre.delete(0, tk.END)
        self.combo_cat_padre.set('Sin categoría padre')

    def _padre_id_actual(self):
        valor = self.combo_cat_padre.get()
        return None if valor == 'Sin categoría padre' else self.categorias_padre_combo.get(valor)

    def agregar_categoria(self):
        nombre = self.entry_cat_nombre.get().strip()
        if not nombre:
            return messagebox.showwarning('Campo requerido', 'Indica el nombre de la categoría.')
        try:
            self.ejecutar_consulta(
                'INSERT INTO categorias (nombre, id_categoria_padre) VALUES (%s, %s)',
                (nombre, self._padre_id_actual()),
            )
            self.limpiar_form_categoria()
            self.actualizar_todas_las_tablas()
            messagebox.showinfo('Éxito', 'Categoría creada.')
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def actualizar_categoria(self):
        cid = self.id_seleccionado(self.tree_categorias)
        if cid is None:
            return messagebox.showwarning('Selección requerida', 'Selecciona una categoría.')
        nombre, padre = self.entry_cat_nombre.get().strip(), self._padre_id_actual()
        if not nombre:
            return messagebox.showwarning('Campo requerido', 'Indica el nombre.')
        if padre == cid:
            return messagebox.showwarning('Relación inválida', 'Una categoría no puede ser su propia categoría padre.')
        try:
            self.ejecutar_consulta(
                'UPDATE categorias SET nombre=%s, id_categoria_padre=%s WHERE id_categoria=%s',
                (nombre, padre, cid),
            )
            self.actualizar_todas_las_tablas()
            messagebox.showinfo('Éxito', 'Categoría actualizada.')
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def eliminar_categoria(self):
        cid = self.id_seleccionado(self.tree_categorias)
        if cid is None:
            return messagebox.showwarning('Selección requerida', 'Selecciona una categoría.')
        if not messagebox.askyesno('Confirmar', '¿Eliminar la categoría seleccionada?'):
            return
        try:
            self.ejecutar_consulta('DELETE FROM categorias WHERE id_categoria=%s', (cid,))
            self.limpiar_form_categoria()
            self.actualizar_todas_las_tablas()
            messagebox.showinfo('Eliminado', 'Categoría eliminada.')
        except Exception as e:
            messagebox.showerror('No se pudo eliminar', str(e))

    def cargar_datos_categorias(self):
        rows = self.ejecutar_consulta(
            '''SELECT c.id_categoria, c.nombre, p.id_categoria, p.nombre
               FROM categorias c
               LEFT JOIN categorias p ON p.id_categoria = c.id_categoria_padre
               ORDER BY c.nombre''',
            fetch=True,
        )
        for item in self.tree_categorias.get_children():
            self.tree_categorias.delete(item)
        self.categorias_combo = {}
        self.categorias_padre_combo = {}
        for cid, nombre, _, _ in rows:
            etiqueta = f'{nombre} — #{cid}'
            self.categorias_combo[etiqueta] = cid
            self.categorias_padre_combo[etiqueta] = cid
        for cid, nombre, pid, pnombre in rows:
            padre = 'Sin categoría padre' if pid is None else f'{pnombre} — #{pid}'
            self.tree_categorias.insert('', 'end', values=(cid, nombre, padre))
        valores = ['Sin categoría padre'] + list(self.categorias_padre_combo.keys())
        self.combo_cat_padre.configure(values=valores)

    # ------------------------------------------------------------
    # EVENTOS - RF04 corregido + integracion RF09
    # ------------------------------------------------------------
    def configurar_pestana_eventos(self):
        self.crear_encabezado(self.tab_eventos, 'Eventos', 'Programa eventos con propietario activo, categoría, ubicación, descripción y horario.')
        cuerpo = ctk.CTkFrame(self.tab_eventos, fg_color='transparent')
        cuerpo.pack(fill='both', expand=True, padx=10, pady=5)
        cuerpo.grid_columnconfigure(0, weight=3)
        cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=1)

        tabla = ctk.CTkFrame(cuerpo)
        tabla.grid(row=0, column=0, sticky='nsew', padx=(0, 8))
        form = ctk.CTkScrollableFrame(cuerpo, width=370)
        form.grid(row=0, column=1, sticky='nsew')

        self.tree_eventos = self.crear_treeview(
            tabla,
            ('ID', 'Propietario', 'Categoría', 'Ubicación', 'Título', 'Descripción', 'Inicio', 'Fin'),
            (65, 175, 150, 160, 190, 220, 145, 145),
        )
        self.tree_eventos.bind('<<TreeviewSelect>>', self.cargar_evento_seleccionado)

        ctk.CTkLabel(form, text='Formulario de evento', font=ctk.CTkFont(size=16, weight='bold')).pack(pady=(10, 12))
        self.entry_ev_titulo = ctk.CTkEntry(form, placeholder_text='Título del evento')
        self.entry_ev_titulo.pack(fill='x', padx=10, pady=5)
        ctk.CTkLabel(form, text='Descripción').pack(anchor='w', padx=10, pady=(6, 2))
        self.text_ev_descripcion = ctk.CTkTextbox(form, height=75)
        self.text_ev_descripcion.pack(fill='x', padx=10, pady=5)

        ctk.CTkLabel(form, text='Propietario activo').pack(anchor='w', padx=10, pady=(6, 2))
        self.combo_ev_usuario = ctk.CTkComboBox(form, values=['Seleccione un usuario'], state='readonly')
        self.combo_ev_usuario.pack(fill='x', padx=10, pady=4)
        ctk.CTkLabel(form, text='Categoría').pack(anchor='w', padx=10, pady=(6, 2))
        self.combo_ev_categoria = ctk.CTkComboBox(form, values=['Seleccione una categoría'], state='readonly')
        self.combo_ev_categoria.pack(fill='x', padx=10, pady=4)
        ctk.CTkLabel(form, text='Ubicación').pack(anchor='w', padx=10, pady=(6, 2))
        self.combo_ev_ubicacion = ctk.CTkComboBox(form, values=['Seleccione una ubicación'], state='readonly')
        self.combo_ev_ubicacion.pack(fill='x', padx=10, pady=4)

        ctk.CTkLabel(form, text='Inicio').pack(anchor='w', padx=10, pady=(8, 2))
        fila_inicio = ctk.CTkFrame(form, fg_color='transparent')
        fila_inicio.pack(fill='x', padx=10)
        self.fecha_inicio = self.crear_selector_fecha(fila_inicio)
        self.fecha_inicio.pack(side='left', fill='x', expand=True)
        self.hora_inicio = ctk.CTkEntry(fila_inicio, placeholder_text='HH:MM', width=80)
        self.hora_inicio.pack(side='left', padx=(6, 0))

        ctk.CTkLabel(form, text='Fin').pack(anchor='w', padx=10, pady=(8, 2))
        fila_fin = ctk.CTkFrame(form, fg_color='transparent')
        fila_fin.pack(fill='x', padx=10)
        self.fecha_fin = self.crear_selector_fecha(fila_fin)
        self.fecha_fin.pack(side='left', fill='x', expand=True)
        self.hora_fin = ctk.CTkEntry(fila_fin, placeholder_text='HH:MM', width=80)
        self.hora_fin.pack(side='left', padx=(6, 0))

        ctk.CTkButton(form, text='➕ Crear evento', command=self.agregar_evento).pack(fill='x', padx=10, pady=(14, 5))
        ctk.CTkButton(form, text='💾 Actualizar seleccionado', command=self.actualizar_evento).pack(fill='x', padx=10, pady=5)
        ctk.CTkButton(form, text='🧹 Nuevo / Limpiar', command=self.limpiar_form_evento, fg_color='gray').pack(fill='x', padx=10, pady=5)
        ctk.CTkButton(form, text='🗑 Eliminar seleccionado', command=self.eliminar_evento, fg_color='#b33939', hover_color='#8f2d2d').pack(fill='x', padx=10, pady=5)
        self.limpiar_form_evento()

    def cargar_evento_seleccionado(self, _=None):
        sel = self.tree_eventos.selection()
        if not sel:
            return
        vals = self.tree_eventos.item(sel[0])['values']
        self.entry_ev_titulo.delete(0, tk.END)
        self.entry_ev_titulo.insert(0, vals[4])
        self.text_ev_descripcion.delete('1.0', 'end')
        self.text_ev_descripcion.insert('1.0', vals[5] or '')
        self.combo_ev_usuario.set(vals[1])
        self.combo_ev_categoria.set(vals[2])
        self.combo_ev_ubicacion.set(vals[3])
        try:
            ini = datetime.strptime(str(vals[6]), '%Y-%m-%d %H:%M')
            fin = datetime.strptime(str(vals[7]), '%Y-%m-%d %H:%M')
            self.establecer_fecha(self.fecha_inicio, ini)
            self.establecer_fecha(self.fecha_fin, fin)
            self.hora_inicio.delete(0, tk.END)
            self.hora_inicio.insert(0, ini.strftime('%H:%M'))
            self.hora_fin.delete(0, tk.END)
            self.hora_fin.insert(0, fin.strftime('%H:%M'))
        except ValueError:
            pass

    def limpiar_form_evento(self):
        if hasattr(self, 'tree_eventos'):
            self.tree_eventos.selection_remove(self.tree_eventos.selection())
        self.entry_ev_titulo.delete(0, tk.END)
        self.text_ev_descripcion.delete('1.0', 'end')
        self.combo_ev_usuario.set('Seleccione un usuario')
        self.combo_ev_categoria.set('Seleccione una categoría')
        self.combo_ev_ubicacion.set('Seleccione una ubicación')
        hoy = datetime.now()
        self.establecer_fecha(self.fecha_inicio, hoy)
        self.establecer_fecha(self.fecha_fin, hoy)
        self.hora_inicio.delete(0, tk.END)
        self.hora_inicio.insert(0, '09:00')
        self.hora_fin.delete(0, tk.END)
        self.hora_fin.insert(0, '10:00')

    def datos_evento_formulario(self):
        titulo = self.entry_ev_titulo.get().strip()
        descripcion = self.valor_textbox(self.text_ev_descripcion) or None
        usuario = self.usuarios_activos_combo.get(self.combo_ev_usuario.get())
        categoria = self.categorias_combo.get(self.combo_ev_categoria.get())
        ubicacion = self.ubicaciones_combo.get(self.combo_ev_ubicacion.get())
        try:
            inicio = datetime.strptime(f'{self.obtener_fecha(self.fecha_inicio)} {self.hora_inicio.get().strip()}', '%Y-%m-%d %H:%M')
            fin = datetime.strptime(f'{self.obtener_fecha(self.fecha_fin)} {self.hora_fin.get().strip()}', '%Y-%m-%d %H:%M')
        except ValueError as exc:
            raise ValueError('Fecha u hora inválida. Use el formato HH:MM para las horas.') from exc
        if not titulo or usuario is None or categoria is None or ubicacion is None:
            raise ValueError('Completa título, propietario activo, categoría y ubicación.')
        if fin <= inicio:
            raise ValueError('La fecha y hora de finalización deben ser posteriores al inicio.')
        return usuario, categoria, ubicacion, titulo, descripcion, inicio, fin

    def agregar_evento(self):
        try:
            datos = self.datos_evento_formulario()
            self.ejecutar_consulta(
                '''INSERT INTO eventos
                   (id_usuario_propietario, id_categoria, id_ubicacion, titulo, descripcion, fecha_inicio, fecha_fin)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                datos,
            )
            self.limpiar_form_evento()
            self.actualizar_todas_las_tablas()
            messagebox.showinfo('Éxito', 'Evento creado correctamente.')
        except Exception as e:
            messagebox.showerror('No se pudo crear el evento', str(e))

    def actualizar_evento(self):
        eid = self.id_seleccionado(self.tree_eventos)
        if eid is None:
            return messagebox.showwarning('Selección requerida', 'Selecciona un evento.')
        try:
            datos = self.datos_evento_formulario()
            self.ejecutar_consulta(
                '''UPDATE eventos
                   SET id_usuario_propietario=%s, id_categoria=%s, id_ubicacion=%s,
                       titulo=%s, descripcion=%s, fecha_inicio=%s, fecha_fin=%s
                   WHERE id_evento=%s''',
                (*datos, eid),
            )
            self.actualizar_todas_las_tablas()
            messagebox.showinfo('Éxito', 'Evento actualizado.')
        except Exception as e:
            messagebox.showerror('No se pudo actualizar', str(e))

    def eliminar_evento(self):
        eid = self.id_seleccionado(self.tree_eventos)
        if eid is None:
            return messagebox.showwarning('Selección requerida', 'Selecciona un evento.')
        if not messagebox.askyesno('Confirmar', '¿Eliminar el evento seleccionado?'):
            return
        try:
            self.ejecutar_consulta('DELETE FROM eventos WHERE id_evento=%s', (eid,))
            self.limpiar_form_evento()
            self.actualizar_todas_las_tablas()
            messagebox.showinfo('Eliminado', 'Evento eliminado.')
        except Exception as e:
            messagebox.showerror('No se pudo eliminar', str(e))

    def cargar_datos_eventos(self):
        rows = self.ejecutar_consulta(
            '''SELECT e.id_evento,
                      u.id_usuario, u.nombre, u.apellido,
                      c.id_categoria, c.nombre,
                      ub.id_ubicacion, ub.nombre,
                      e.titulo, e.descripcion, e.fecha_inicio, e.fecha_fin
               FROM eventos e
               JOIN usuarios u ON u.id_usuario = e.id_usuario_propietario
               JOIN categorias c ON c.id_categoria = e.id_categoria
               JOIN ubicaciones ub ON ub.id_ubicacion = e.id_ubicacion
               ORDER BY e.fecha_inicio DESC''',
            fetch=True,
        )
        for item in self.tree_eventos.get_children():
            self.tree_eventos.delete(item)
        self.eventos_combo = {}
        for row in rows:
            usuario = f'{row[2]} {row[3]} — #{row[1]}'
            categoria = f'{row[5]} — #{row[4]}'
            ubicacion = f'{row[7]} — #{row[6]}'
            inicio = row[10].strftime('%Y-%m-%d %H:%M')
            fin = row[11].strftime('%Y-%m-%d %H:%M')
            self.tree_eventos.insert('', 'end', values=(row[0], usuario, categoria, ubicacion, row[8], row[9] or '', inicio, fin))
            self.eventos_combo[f'{row[8]} — #{row[0]}'] = row[0]
        self.combo_ev_usuario.configure(values=['Seleccione un usuario'] + list(self.usuarios_activos_combo.keys()))
        self.combo_ev_categoria.configure(values=['Seleccione una categoría'] + list(self.categorias_combo.keys()))
        self.combo_ev_ubicacion.configure(values=['Seleccione una ubicación'] + list(self.ubicaciones_combo.keys()))

    # ------------------------------------------------------------
    # UBICACIONES - RF08, RF09, RF10
    # ------------------------------------------------------------
    def configurar_pestana_ubicaciones(self):
        self.crear_encabezado(self.tab_ubicaciones, 'Ubicaciones', 'Administra recintos y consulta su demanda de uso.')
        cuerpo = ctk.CTkFrame(self.tab_ubicaciones, fg_color='transparent')
        cuerpo.pack(fill='both', expand=True, padx=10, pady=5)
        cuerpo.grid_columnconfigure(0, weight=3)
        cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=3)
        cuerpo.grid_rowconfigure(1, weight=2)

        tabla = ctk.CTkFrame(cuerpo)
        tabla.grid(row=0, column=0, sticky='nsew', padx=(0, 8), pady=(0, 8))
        form = ctk.CTkScrollableFrame(cuerpo, width=330)
        form.grid(row=0, column=1, rowspan=2, sticky='nsew')
        reporte = ctk.CTkFrame(cuerpo)
        reporte.grid(row=1, column=0, sticky='nsew', padx=(0, 8))

        self.tree_ubicaciones = self.crear_treeview(tabla, ('ID', 'Nombre', 'Dirección', 'Ciudad', 'Capacidad'), (70, 190, 260, 150, 100))
        self.tree_ubicaciones.bind('<<TreeviewSelect>>', self.cargar_ubicacion_seleccionada)

        ctk.CTkLabel(form, text='Formulario de ubicación', font=ctk.CTkFont(size=16, weight='bold')).pack(pady=(10, 12))
        self.entry_ubi_nombre = ctk.CTkEntry(form, placeholder_text='Nombre')
        self.entry_ubi_direccion = ctk.CTkEntry(form, placeholder_text='Dirección')
        self.entry_ubi_ciudad = ctk.CTkEntry(form, placeholder_text='Ciudad')
        self.entry_ubi_capacidad = ctk.CTkEntry(form, placeholder_text='Capacidad')
        for widget in (self.entry_ubi_nombre, self.entry_ubi_direccion, self.entry_ubi_ciudad, self.entry_ubi_capacidad):
            widget.pack(fill='x', padx=10, pady=5)
        ctk.CTkButton(form, text='➕ Registrar ubicación', command=self.agregar_ubicacion).pack(fill='x', padx=10, pady=(12, 5))
        ctk.CTkButton(form, text='💾 Actualizar seleccionada', command=self.actualizar_ubicacion).pack(fill='x', padx=10, pady=5)
        ctk.CTkButton(form, text='🧹 Nueva / Limpiar', command=self.limpiar_form_ubicacion, fg_color='gray').pack(fill='x', padx=10, pady=5)
        ctk.CTkButton(form, text='🗑 Eliminar seleccionada', command=self.eliminar_ubicacion, fg_color='#b33939', hover_color='#8f2d2d').pack(fill='x', padx=10, pady=5)

        self.tabs_analitica_ubicaciones = ctk.CTkTabview(reporte)
        self.tabs_analitica_ubicaciones.pack(fill='both', expand=True, padx=8, pady=6)
        tab_ranking = self.tabs_analitica_ubicaciones.add('Ranking RF10')
        tab_agenda = self.tabs_analitica_ubicaciones.add('Agenda RF09')

        self.tree_reporte_ubicaciones = self.crear_treeview(
            tab_ranking,
            ('Lugar', 'Ciudad', 'Capacidad', 'Total', 'Programados', 'Históricos'),
            (210, 150, 90, 80, 100, 100),
            height=6,
        )

        filtros_agenda = ctk.CTkFrame(tab_agenda, fg_color='transparent')
        filtros_agenda.pack(fill='x', padx=10, pady=(6, 0))
        self.combo_agenda_ubicacion = ctk.CTkComboBox(
            filtros_agenda, values=['Seleccione una ubicación'], state='readonly', width=300
        )
        self.combo_agenda_ubicacion.pack(side='left', padx=(0, 8))
        ctk.CTkButton(
            filtros_agenda, text='Consultar histórico / agenda', command=self.buscar_eventos_ubicacion
        ).pack(side='left')
        self.tree_agenda_ubicacion = self.crear_treeview(
            tab_agenda,
            ('ID', 'Evento', 'Inicio', 'Fin', 'Estado temporal'),
            (65, 260, 150, 150, 130),
            height=5,
        )

    def cargar_ubicacion_seleccionada(self, _=None):
        sel = self.tree_ubicaciones.selection()
        if not sel:
            return
        vals = self.tree_ubicaciones.item(sel[0])['values']
        for widget, valor in zip((self.entry_ubi_nombre, self.entry_ubi_direccion, self.entry_ubi_ciudad, self.entry_ubi_capacidad), vals[1:5]):
            widget.delete(0, tk.END)
            widget.insert(0, valor)

    def limpiar_form_ubicacion(self):
        self.tree_ubicaciones.selection_remove(self.tree_ubicaciones.selection())
        for widget in (self.entry_ubi_nombre, self.entry_ubi_direccion, self.entry_ubi_ciudad, self.entry_ubi_capacidad):
            widget.delete(0, tk.END)

    def datos_ubicacion_formulario(self):
        nombre = self.entry_ubi_nombre.get().strip()
        direccion = self.entry_ubi_direccion.get().strip()
        ciudad = self.entry_ubi_ciudad.get().strip()
        try:
            capacidad = int(self.entry_ubi_capacidad.get().strip())
        except ValueError as exc:
            raise ValueError('La capacidad debe ser un número entero positivo.') from exc
        if not nombre or not direccion or not ciudad:
            raise ValueError('Completa nombre, dirección y ciudad.')
        if capacidad <= 0:
            raise ValueError('La capacidad debe ser mayor que cero.')
        return nombre, direccion, ciudad, capacidad

    def agregar_ubicacion(self):
        try:
            datos = self.datos_ubicacion_formulario()
            self.ejecutar_consulta('INSERT INTO ubicaciones (nombre, direccion, ciudad, capacidad) VALUES (%s, %s, %s, %s)', datos)
            self.limpiar_form_ubicacion()
            self.actualizar_todas_las_tablas()
            messagebox.showinfo('Éxito', 'Ubicación registrada.')
        except Exception as e:
            messagebox.showerror('No se pudo registrar', str(e))

    def actualizar_ubicacion(self):
        uid = self.id_seleccionado(self.tree_ubicaciones)
        if uid is None:
            return messagebox.showwarning('Selección requerida', 'Selecciona una ubicación.')
        try:
            datos = self.datos_ubicacion_formulario()
            self.ejecutar_consulta('UPDATE ubicaciones SET nombre=%s, direccion=%s, ciudad=%s, capacidad=%s WHERE id_ubicacion=%s', (*datos, uid))
            self.actualizar_todas_las_tablas()
            messagebox.showinfo('Éxito', 'Ubicación actualizada.')
        except Exception as e:
            messagebox.showerror('No se pudo actualizar', str(e))

    def eliminar_ubicacion(self):
        uid = self.id_seleccionado(self.tree_ubicaciones)
        if uid is None:
            return messagebox.showwarning('Selección requerida', 'Selecciona una ubicación.')
        if not messagebox.askyesno('Confirmar', '¿Eliminar la ubicación seleccionada?'):
            return
        try:
            self.ejecutar_consulta('DELETE FROM ubicaciones WHERE id_ubicacion=%s', (uid,))
            self.limpiar_form_ubicacion()
            self.actualizar_todas_las_tablas()
            messagebox.showinfo('Eliminado', 'Ubicación eliminada.')
        except Exception as e:
            messagebox.showerror('No se pudo eliminar', str(e))

    def cargar_datos_ubicaciones(self):
        rows = self.ejecutar_consulta('SELECT id_ubicacion, nombre, direccion, ciudad, capacidad FROM ubicaciones ORDER BY nombre', fetch=True)
        for item in self.tree_ubicaciones.get_children():
            self.tree_ubicaciones.delete(item)
        self.ubicaciones_combo = {}
        for row in rows:
            self.tree_ubicaciones.insert('', 'end', values=row)
            self.ubicaciones_combo[f'{row[1]} — #{row[0]}'] = row[0]
        report = self.ejecutar_consulta(
            '''SELECT nombre, ciudad, capacidad, total_eventos, eventos_programados, eventos_historicos
               FROM vista_ocupacion_ubicaciones
               ORDER BY total_eventos DESC, nombre''',
            fetch=True,
        )
        for item in self.tree_reporte_ubicaciones.get_children():
            self.tree_reporte_ubicaciones.delete(item)
        for row in report:
            self.tree_reporte_ubicaciones.insert('', 'end', values=row)
        valores_agenda = ['Seleccione una ubicación'] + list(self.ubicaciones_combo.keys())
        self.combo_agenda_ubicacion.configure(values=valores_agenda)
        if self.combo_agenda_ubicacion.get() not in valores_agenda:
            self.combo_agenda_ubicacion.set('Seleccione una ubicación')

    def buscar_eventos_ubicacion(self):
        ubicacion = self.ubicaciones_combo.get(self.combo_agenda_ubicacion.get())
        if ubicacion is None:
            return messagebox.showwarning('Selección requerida', 'Selecciona una ubicación para consultar.')
        try:
            rows = self.ejecutar_consulta(
                '''SELECT id_evento, titulo, fecha_inicio, fecha_fin,
                          CASE
                            WHEN fecha_fin < LOCALTIMESTAMP THEN 'Histórico'
                            WHEN fecha_inicio <= LOCALTIMESTAMP AND fecha_fin > LOCALTIMESTAMP THEN 'En curso'
                            ELSE 'Programado'
                          END
                   FROM eventos
                   WHERE id_ubicacion = %s
                   ORDER BY fecha_inicio DESC''',
                (ubicacion,),
                fetch=True,
            )
            for item in self.tree_agenda_ubicacion.get_children():
                self.tree_agenda_ubicacion.delete(item)
            for row in rows:
                inicio = row[2].strftime('%Y-%m-%d %H:%M')
                fin = row[3].strftime('%Y-%m-%d %H:%M')
                self.tree_agenda_ubicacion.insert('', 'end', values=(row[0], row[1], inicio, fin, row[4]))
        except Exception as e:
            messagebox.showerror('No se pudo consultar la ubicación', str(e))

    # ------------------------------------------------------------
    # DISPONIBILIDAD - RF11, RF12
    # ------------------------------------------------------------
    def configurar_pestana_disponibilidad(self):
        self.crear_encabezado(self.tab_disponibilidad, 'Disponibilidad', 'Gestiona franjas horarias y busca usuarios libres para un rango específico.')
        cuerpo = ctk.CTkFrame(self.tab_disponibilidad, fg_color='transparent')
        cuerpo.pack(fill='both', expand=True, padx=10, pady=5)
        cuerpo.grid_columnconfigure(0, weight=3)
        cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=3)
        cuerpo.grid_rowconfigure(1, weight=2)

        tabla = ctk.CTkFrame(cuerpo)
        tabla.grid(row=0, column=0, sticky='nsew', padx=(0, 8), pady=(0, 8))
        form = ctk.CTkScrollableFrame(cuerpo, width=350)
        form.grid(row=0, column=1, rowspan=2, sticky='nsew')
        analitica = ctk.CTkFrame(cuerpo)
        analitica.grid(row=1, column=0, sticky='nsew', padx=(0, 8))

        self.tree_disponibilidades = self.crear_treeview(tabla, ('ID', 'Usuario', 'Fecha', 'Inicio', 'Fin', 'Tipo'), (65, 230, 110, 90, 90, 130))
        self.tree_disponibilidades.bind('<<TreeviewSelect>>', self.cargar_disponibilidad_seleccionada)

        ctk.CTkLabel(form, text='Formulario de disponibilidad', font=ctk.CTkFont(size=16, weight='bold')).pack(pady=(10, 12))
        ctk.CTkLabel(form, text='Usuario').pack(anchor='w', padx=10, pady=(4, 2))
        self.combo_disp_usuario = ctk.CTkComboBox(form, values=['Seleccione un usuario'], state='readonly')
        self.combo_disp_usuario.pack(fill='x', padx=10, pady=5)
        ctk.CTkLabel(form, text='Fecha').pack(anchor='w', padx=10, pady=(4, 2))
        self.fecha_disp = self.crear_selector_fecha(form)
        self.fecha_disp.pack(fill='x', padx=10, pady=5)
        self.entry_disp_inicio = ctk.CTkEntry(form, placeholder_text='Hora inicio HH:MM')
        self.entry_disp_fin = ctk.CTkEntry(form, placeholder_text='Hora fin HH:MM')
        self.entry_disp_inicio.pack(fill='x', padx=10, pady=5)
        self.entry_disp_fin.pack(fill='x', padx=10, pady=5)
        ctk.CTkLabel(form, text='Tipo').pack(anchor='w', padx=10, pady=(4, 2))
        self.combo_disp_tipo = ctk.CTkComboBox(form, values=['Seleccione un tipo'], state='readonly')
        self.combo_disp_tipo.pack(fill='x', padx=10, pady=5)

        ctk.CTkButton(form, text='➕ Registrar franja', command=self.agregar_disponibilidad).pack(fill='x', padx=10, pady=(12, 5))
        ctk.CTkButton(form, text='💾 Actualizar seleccionada', command=self.actualizar_disponibilidad).pack(fill='x', padx=10, pady=5)
        ctk.CTkButton(form, text='🧹 Nueva / Limpiar', command=self.limpiar_form_disponibilidad, fg_color='gray').pack(fill='x', padx=10, pady=5)
        ctk.CTkButton(form, text='🗑 Eliminar seleccionada', command=self.eliminar_disponibilidad, fg_color='#b33939', hover_color='#8f2d2d').pack(fill='x', padx=10, pady=5)

        ctk.CTkLabel(analitica, text='RF12 · Usuarios libres y disponibles', font=ctk.CTkFont(size=15, weight='bold')).pack(anchor='w', padx=12, pady=(10, 4))
        filtros = ctk.CTkFrame(analitica, fg_color='transparent')
        filtros.pack(fill='x', padx=10)
        self.fecha_busqueda_disp = self.crear_selector_fecha(filtros)
        self.fecha_busqueda_disp.pack(side='left', padx=(0, 6))
        self.entry_busqueda_inicio = ctk.CTkEntry(filtros, width=90, placeholder_text='14:00')
        self.entry_busqueda_inicio.pack(side='left', padx=4)
        self.entry_busqueda_fin = ctk.CTkEntry(filtros, width=90, placeholder_text='16:00')
        self.entry_busqueda_fin.pack(side='left', padx=4)
        self.entry_busqueda_inicio.insert(0, '14:00')
        self.entry_busqueda_fin.insert(0, '16:00')
        ctk.CTkButton(filtros, text='Buscar', width=100, command=self.buscar_usuarios_disponibles).pack(side='left', padx=8)
        self.tree_usuarios_disponibles = self.crear_treeview(analitica, ('ID', 'Nombre', 'Apellido'), (80, 220, 220), height=5)
        self.limpiar_form_disponibilidad()

    def cargar_disponibilidad_seleccionada(self, _=None):
        sel = self.tree_disponibilidades.selection()
        if not sel:
            return
        vals = self.tree_disponibilidades.item(sel[0])['values']
        self.combo_disp_usuario.set(vals[1])
        self.establecer_fecha(self.fecha_disp, vals[2])
        self.entry_disp_inicio.delete(0, tk.END)
        self.entry_disp_inicio.insert(0, vals[3])
        self.entry_disp_fin.delete(0, tk.END)
        self.entry_disp_fin.insert(0, vals[4])
        self.combo_disp_tipo.set(vals[5])

    def limpiar_form_disponibilidad(self):
        if hasattr(self, 'tree_disponibilidades'):
            self.tree_disponibilidades.selection_remove(self.tree_disponibilidades.selection())
        self.combo_disp_usuario.set('Seleccione un usuario')
        self.combo_disp_tipo.set('Seleccione un tipo')
        self.establecer_fecha(self.fecha_disp, datetime.now())
        self.entry_disp_inicio.delete(0, tk.END)
        self.entry_disp_inicio.insert(0, '09:00')
        self.entry_disp_fin.delete(0, tk.END)
        self.entry_disp_fin.insert(0, '17:00')

    def datos_disponibilidad_formulario(self):
        usuario = self.usuarios_combo.get(self.combo_disp_usuario.get())
        tipo = self.tipos_disponibilidad_combo.get(self.combo_disp_tipo.get())
        fecha = self.obtener_fecha(self.fecha_disp)
        inicio = self.leer_hora(self.entry_disp_inicio.get())
        fin = self.leer_hora(self.entry_disp_fin.get())
        if usuario is None or tipo is None:
            raise ValueError('Selecciona usuario y tipo de disponibilidad.')
        if fin <= inicio:
            raise ValueError('La hora final debe ser posterior a la hora inicial.')
        return usuario, fecha, inicio, fin, tipo

    def agregar_disponibilidad(self):
        try:
            datos = self.datos_disponibilidad_formulario()
            self.ejecutar_consulta(
                '''INSERT INTO disponibilidades
                   (id_usuario, fecha, hora_inicio, hora_fin, id_tipo_disponibilidad)
                   VALUES (%s, %s, %s, %s, %s)''',
                datos,
            )
            self.limpiar_form_disponibilidad()
            self.actualizar_todas_las_tablas()
            messagebox.showinfo('Éxito', 'Franja registrada.')
        except Exception as e:
            messagebox.showerror('No se pudo registrar', str(e))

    def actualizar_disponibilidad(self):
        did = self.id_seleccionado(self.tree_disponibilidades)
        if did is None:
            return messagebox.showwarning('Selección requerida', 'Selecciona una franja.')
        try:
            datos = self.datos_disponibilidad_formulario()
            self.ejecutar_consulta(
                '''UPDATE disponibilidades
                   SET id_usuario=%s, fecha=%s, hora_inicio=%s, hora_fin=%s, id_tipo_disponibilidad=%s
                   WHERE id_disponibilidad=%s''',
                (*datos, did),
            )
            self.actualizar_todas_las_tablas()
            messagebox.showinfo('Éxito', 'Franja actualizada.')
        except Exception as e:
            messagebox.showerror('No se pudo actualizar', str(e))

    def eliminar_disponibilidad(self):
        did = self.id_seleccionado(self.tree_disponibilidades)
        if did is None:
            return messagebox.showwarning('Selección requerida', 'Selecciona una franja.')
        if not messagebox.askyesno('Confirmar', '¿Eliminar la franja seleccionada?'):
            return
        try:
            self.ejecutar_consulta('DELETE FROM disponibilidades WHERE id_disponibilidad=%s', (did,))
            self.actualizar_todas_las_tablas()
            messagebox.showinfo('Eliminado', 'Franja eliminada.')
        except Exception as e:
            messagebox.showerror('No se pudo eliminar', str(e))

    def cargar_datos_disponibilidades(self):
        tipos = self.ejecutar_consulta('SELECT id_tipo_disponibilidad, nombre FROM tipos_disponibilidad ORDER BY id_tipo_disponibilidad', fetch=True)
        self.tipos_disponibilidad_combo = {nombre: tid for tid, nombre in tipos}
        self.combo_disp_tipo.configure(values=['Seleccione un tipo'] + list(self.tipos_disponibilidad_combo.keys()))
        self.combo_disp_usuario.configure(values=['Seleccione un usuario'] + list(self.usuarios_combo.keys()))

        rows = self.ejecutar_consulta(
            '''SELECT d.id_disponibilidad, u.id_usuario, u.nombre, u.apellido,
                      d.fecha, d.hora_inicio, d.hora_fin, td.nombre
               FROM disponibilidades d
               JOIN usuarios u ON u.id_usuario = d.id_usuario
               JOIN tipos_disponibilidad td ON td.id_tipo_disponibilidad = d.id_tipo_disponibilidad
               ORDER BY d.fecha DESC, d.hora_inicio, u.nombre''',
            fetch=True,
        )
        for item in self.tree_disponibilidades.get_children():
            self.tree_disponibilidades.delete(item)
        for row in rows:
            usuario = f'{row[2]} {row[3]} — #{row[1]}'
            self.tree_disponibilidades.insert('', 'end', values=(row[0], usuario, row[4], str(row[5])[:5], str(row[6])[:5], row[7]))

    def buscar_usuarios_disponibles(self):
        try:
            fecha = self.obtener_fecha(self.fecha_busqueda_disp)
            inicio = self.leer_hora(self.entry_busqueda_inicio.get())
            fin = self.leer_hora(self.entry_busqueda_fin.get())
            rows = self.ejecutar_consulta('SELECT * FROM usuarios_disponibles(%s, %s, %s)', (fecha, inicio, fin), fetch=True)
            for item in self.tree_usuarios_disponibles.get_children():
                self.tree_usuarios_disponibles.delete(item)
            for row in rows:
                self.tree_usuarios_disponibles.insert('', 'end', values=row)
        except Exception as e:
            messagebox.showerror('No se pudo ejecutar el análisis', str(e))

    # ------------------------------------------------------------
    # TAREAS - RF15, RF16, RF17
    # ------------------------------------------------------------
    def configurar_pestana_tareas(self):
        self.crear_encabezado(self.tab_tareas, 'Tareas', 'Administra tareas asociadas a eventos y revisa la carga de trabajo por usuario.')
        cuerpo = ctk.CTkFrame(self.tab_tareas, fg_color='transparent')
        cuerpo.pack(fill='both', expand=True, padx=10, pady=5)
        cuerpo.grid_columnconfigure(0, weight=3)
        cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=3)
        cuerpo.grid_rowconfigure(1, weight=2)

        tabla = ctk.CTkFrame(cuerpo)
        tabla.grid(row=0, column=0, sticky='nsew', padx=(0, 8), pady=(0, 8))
        form = ctk.CTkScrollableFrame(cuerpo, width=380)
        form.grid(row=0, column=1, rowspan=2, sticky='nsew')
        reporte = ctk.CTkFrame(cuerpo)
        reporte.grid(row=1, column=0, sticky='nsew', padx=(0, 8))

        self.tree_tareas = self.crear_treeview(
            tabla,
            ('ID', 'Evento', 'Responsable', 'Título', 'Prioridad', 'Límite', 'Estado', 'Descripción'),
            (65, 220, 210, 200, 100, 110, 120, 220),
        )
        self.tree_tareas.bind('<<TreeviewSelect>>', self.cargar_tarea_seleccionada)

        ctk.CTkLabel(form, text='Formulario de tarea', font=ctk.CTkFont(size=16, weight='bold')).pack(pady=(10, 12))
        ctk.CTkLabel(form, text='Evento').pack(anchor='w', padx=10, pady=(4, 2))
        self.combo_tarea_evento = ctk.CTkComboBox(form, values=['Seleccione un evento'], state='readonly')
        self.combo_tarea_evento.pack(fill='x', padx=10, pady=5)
        ctk.CTkLabel(form, text='Responsable').pack(anchor='w', padx=10, pady=(4, 2))
        self.combo_tarea_responsable = ctk.CTkComboBox(form, values=['Seleccione un usuario'], state='readonly')
        self.combo_tarea_responsable.pack(fill='x', padx=10, pady=5)
        self.entry_tarea_titulo = ctk.CTkEntry(form, placeholder_text='Título')
        self.entry_tarea_titulo.pack(fill='x', padx=10, pady=5)
        ctk.CTkLabel(form, text='Descripción').pack(anchor='w', padx=10, pady=(4, 2))
        self.text_tarea_descripcion = ctk.CTkTextbox(form, height=65)
        self.text_tarea_descripcion.pack(fill='x', padx=10, pady=5)
        self.entry_tarea_prioridad = ctk.CTkEntry(form, placeholder_text='Prioridad')
        self.entry_tarea_prioridad.pack(fill='x', padx=10, pady=5)
        ctk.CTkLabel(form, text='Fecha límite').pack(anchor='w', padx=10, pady=(5, 2))
        self.fecha_tarea_limite = self.crear_selector_fecha(form)
        self.fecha_tarea_limite.pack(fill='x', padx=10, pady=5)
        ctk.CTkLabel(form, text='Estado').pack(anchor='w', padx=10, pady=(4, 2))
        self.combo_tarea_estado = ctk.CTkComboBox(form, values=['Pendiente', 'En progreso', 'Completada', 'Cancelada'], state='readonly')
        self.combo_tarea_estado.pack(fill='x', padx=10, pady=5)

        ctk.CTkButton(form, text='➕ Crear tarea', command=self.agregar_tarea).pack(fill='x', padx=10, pady=(12, 5))
        ctk.CTkButton(form, text='💾 Actualizar seleccionada', command=self.actualizar_tarea).pack(fill='x', padx=10, pady=5)
        ctk.CTkButton(form, text='🧹 Nueva / Limpiar', command=self.limpiar_form_tarea, fg_color='gray').pack(fill='x', padx=10, pady=5)
        ctk.CTkButton(form, text='🗑 Eliminar seleccionada', command=self.eliminar_tarea, fg_color='#b33939', hover_color='#8f2d2d').pack(fill='x', padx=10, pady=5)

        self.tabs_reportes_tareas = ctk.CTkTabview(reporte)
        self.tabs_reportes_tareas.pack(fill='both', expand=True, padx=8, pady=6)
        tab_carga = self.tabs_reportes_tareas.add('Carga RF16-RF17')
        tab_vencidas = self.tabs_reportes_tareas.add('Vencimientos RF16')
        self.tree_carga_trabajo = self.crear_treeview(
            tab_carga,
            ('Usuario', 'Activas', 'Pendientes', 'En progreso', 'Vencidas'),
            (260, 90, 100, 110, 90),
            height=6,
        )
        self.tree_eventos_vencidos = self.crear_treeview(
            tab_vencidas,
            ('ID Evento', 'Evento', 'Tareas vencidas'),
            (100, 360, 130),
            height=6,
        )
        self.limpiar_form_tarea()

    def cargar_tarea_seleccionada(self, _=None):
        sel = self.tree_tareas.selection()
        if not sel:
            return
        vals = self.tree_tareas.item(sel[0])['values']
        self.combo_tarea_evento.set(vals[1])
        self.combo_tarea_responsable.set(vals[2])
        self.entry_tarea_titulo.delete(0, tk.END)
        self.entry_tarea_titulo.insert(0, vals[3])
        self.entry_tarea_prioridad.delete(0, tk.END)
        self.entry_tarea_prioridad.insert(0, vals[4])
        self.establecer_fecha(self.fecha_tarea_limite, vals[5])
        self.combo_tarea_estado.set(vals[6])
        self.text_tarea_descripcion.delete('1.0', 'end')
        self.text_tarea_descripcion.insert('1.0', vals[7] or '')

    def limpiar_form_tarea(self):
        if hasattr(self, 'tree_tareas'):
            self.tree_tareas.selection_remove(self.tree_tareas.selection())
        self.combo_tarea_evento.set('Seleccione un evento')
        self.combo_tarea_responsable.set('Seleccione un usuario')
        self.entry_tarea_titulo.delete(0, tk.END)
        self.text_tarea_descripcion.delete('1.0', 'end')
        self.entry_tarea_prioridad.delete(0, tk.END)
        self.combo_tarea_estado.set('Pendiente')
        self.establecer_fecha(self.fecha_tarea_limite, datetime.now())

    def datos_tarea_formulario(self):
        evento = self.eventos_combo.get(self.combo_tarea_evento.get())
        responsable = self.usuarios_combo.get(self.combo_tarea_responsable.get())
        titulo = self.entry_tarea_titulo.get().strip()
        descripcion = self.valor_textbox(self.text_tarea_descripcion) or None
        prioridad = self.entry_tarea_prioridad.get().strip()
        fecha_limite = self.obtener_fecha(self.fecha_tarea_limite)
        estado = self.combo_tarea_estado.get()
        if evento is None or responsable is None:
            raise ValueError('Selecciona evento y usuario responsable.')
        if not titulo or not prioridad:
            raise ValueError('Completa título y prioridad.')
        if estado not in ('Pendiente', 'En progreso', 'Completada', 'Cancelada'):
            raise ValueError('Selecciona un estado válido.')
        return evento, responsable, titulo, descripcion, prioridad, fecha_limite, estado

    def agregar_tarea(self):
        try:
            datos = self.datos_tarea_formulario()
            self.ejecutar_consulta(
                '''INSERT INTO tareas
                   (id_evento, id_usuario_responsable, titulo, descripcion, prioridad, fecha_limite, estado)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                datos,
            )
            self.limpiar_form_tarea()
            self.actualizar_todas_las_tablas()
            messagebox.showinfo('Éxito', 'Tarea creada.')
        except Exception as e:
            messagebox.showerror('No se pudo crear', str(e))

    def actualizar_tarea(self):
        tid = self.id_seleccionado(self.tree_tareas)
        if tid is None:
            return messagebox.showwarning('Selección requerida', 'Selecciona una tarea.')
        try:
            datos = self.datos_tarea_formulario()
            self.ejecutar_consulta(
                '''UPDATE tareas
                   SET id_evento=%s, id_usuario_responsable=%s, titulo=%s, descripcion=%s,
                       prioridad=%s, fecha_limite=%s, estado=%s
                   WHERE id_tarea=%s''',
                (*datos, tid),
            )
            self.actualizar_todas_las_tablas()
            messagebox.showinfo('Éxito', 'Tarea actualizada.')
        except Exception as e:
            messagebox.showerror('No se pudo actualizar', str(e))

    def eliminar_tarea(self):
        tid = self.id_seleccionado(self.tree_tareas)
        if tid is None:
            return messagebox.showwarning('Selección requerida', 'Selecciona una tarea.')
        if not messagebox.askyesno('Confirmar', '¿Eliminar la tarea seleccionada?'):
            return
        try:
            self.ejecutar_consulta('DELETE FROM tareas WHERE id_tarea=%s', (tid,))
            self.actualizar_todas_las_tablas()
            messagebox.showinfo('Eliminado', 'Tarea eliminada.')
        except Exception as e:
            messagebox.showerror('No se pudo eliminar', str(e))

    def cargar_datos_tareas(self):
        self.combo_tarea_evento.configure(values=['Seleccione un evento'] + list(self.eventos_combo.keys()))
        self.combo_tarea_responsable.configure(values=['Seleccione un usuario'] + list(self.usuarios_combo.keys()))

        rows = self.ejecutar_consulta(
            '''SELECT t.id_tarea,
                      e.id_evento, e.titulo,
                      u.id_usuario, u.nombre, u.apellido,
                      t.titulo, t.prioridad, t.fecha_limite, t.estado, t.descripcion
               FROM tareas t
               JOIN eventos e ON e.id_evento = t.id_evento
               JOIN usuarios u ON u.id_usuario = t.id_usuario_responsable
               ORDER BY t.fecha_limite, t.id_tarea''',
            fetch=True,
        )
        for item in self.tree_tareas.get_children():
            self.tree_tareas.delete(item)
        for row in rows:
            evento = f'{row[2]} — #{row[1]}'
            usuario = f'{row[4]} {row[5]} — #{row[3]}'
            self.tree_tareas.insert('', 'end', values=(row[0], evento, usuario, row[6], row[7], row[8], row[9], row[10] or ''))

        carga = self.ejecutar_consulta(
            '''SELECT nombre || ' ' || apellido, tareas_activas, pendientes, en_progreso, vencidas
               FROM vista_carga_trabajo
               ORDER BY tareas_activas DESC, vencidas DESC, nombre, apellido''',
            fetch=True,
        )
        for item in self.tree_carga_trabajo.get_children():
            self.tree_carga_trabajo.delete(item)
        for row in carga:
            self.tree_carga_trabajo.insert('', 'end', values=row)

        vencidas = self.ejecutar_consulta(
            '''SELECT id_evento, evento, tareas_vencidas
               FROM vista_eventos_tareas_vencidas
               ORDER BY tareas_vencidas DESC, evento''',
            fetch=True,
        )
        for item in self.tree_eventos_vencidos.get_children():
            self.tree_eventos_vencidos.delete(item)
        for row in vencidas:
            self.tree_eventos_vencidos.insert('', 'end', values=row)

    # ------------------------------------------------------------
    # REFRESCO GENERAL
    # ------------------------------------------------------------
    def actualizar_todas_las_tablas(self):
        try:
            # Orden importante por dependencias de los ComboBox.
            self.cargar_datos_usuarios()
            self.cargar_datos_categorias()
            self.cargar_datos_ubicaciones()
            self.cargar_datos_eventos()
            self.cargar_datos_disponibilidades()
            self.cargar_datos_tareas()
        except Exception as e:
            messagebox.showerror('Error de conexión o estructura', str(e))


if __name__ == '__main__':
    app = AppAgenda()
    app.mainloop()
