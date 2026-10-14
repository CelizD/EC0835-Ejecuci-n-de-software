# main.py

# Hola, yo soy un principiante y este es mi archivo main.py.
# Aquí importo tkinter para hacer la ventana. No entiendo todo pero voy aprendiendo.
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog

# Estos son mis otros archivos: db, models y crud.
# No sé bien cómo funcionan por dentro, pero los uso para la base de datos.
import db
import models
import crud

# Yo creo las tablas al iniciar. Me dijeron que esto es importante.
models.Base.metadata.create_all(bind=db.engine)

# Aquí abro una sesión para hablar con la base de datos.
sesion = db.get_db()

# Esta variable global la uso para guardar el ID de lo que selecciono en la lista.
# Todavía me confundo con global, pero así me funciona.
id_seleccionado = None

# --- FUNCIONES DE USUARIO ---
# Aquí empiezo con las funciones de usuario. Yo primero pido nombre y email.

def registrar_usuario():
    # Yo agarro lo que la persona escribió en las cajas.
    nombre = entry_nombre.get()
    email = entry_email.get()

    # Si está vacío, yo aviso con una ventanita.
    if not nombre or not email:
        messagebox.showwarning("Aviso", "Llena todos los campos de Usuario")
        return

    try:
        # Llamo a crud para que guarde el usuario. No sé bien cómo lo hace, pero funciona.
        crud.crear_usuario(sesion, nombre, email)
        messagebox.showinfo("Éxito", "Usuario registrado")
        limpiar_campos_usuario()
        mostrar_usuarios()
    except Exception as e:
        # Si hay error, hago rollback porque me dijeron que eso deshace cambios.
        sesion.rollback()
        messagebox.showerror("Error", "El correo ya existe o hubo un fallo. Intenta con otro.")


def mostrar_usuarios():
    # Primero borro la lista para que no se dupliquen cosas.
    lista_resultados.delete(0, tk.END)

    # Pido todos los usuarios y los muestro uno por uno.
    usuarios = crud.obtener_usuarios(sesion)
    for u in usuarios:
        lista_resultados.insert(tk.END, f"ID:{u.id} | Nombre:{u.nombre} | Email:{u.email}")


def seleccionar_usuario(event):
    # Uso global porque quiero guardar el ID seleccionado.
    global id_seleccionado

    try:
        # Aquí veo qué elemento de la lista se seleccionó.
        seleccion = lista_resultados.curselection()[0]
        texto = lista_resultados.get(seleccion)

        # Esto me lo copié de un ejemplo: separo el texto para sacar el ID.
        id_seleccionado = int(texto.split("|")[0].split(":")[1].strip())

        # Busco el usuario en la base de datos con ese ID.
        usuario = sesion.query(models.Usuario).filter(models.Usuario.id == id_seleccionado).first()

        # Si existe, pongo sus datos en las cajas.
        if usuario:
            entry_nombre.delete(0, tk.END)
            entry_nombre.insert(0, usuario.nombre)
            entry_email.delete(0, tk.END)
            entry_email.insert(0, usuario.email)
    except (IndexError, ValueError):
        # Si algo falla, no hago nada. A veces pasa si no hay selección.
        pass


def editar_usuario():
    global id_seleccionado

    # Si no hay ID seleccionado, aviso.
    if id_seleccionado is None:
        messagebox.showwarning("Aviso", "Selecciona un usuario de la lista de abajo")
        return

    try:
        # Busco el usuario y le cambio los datos.
        usuario = sesion.query(models.Usuario).filter(models.Usuario.id == id_seleccionado).first()
        if usuario:
            usuario.nombre = entry_nombre.get()
            usuario.email = entry_email.get()
            sesion.commit()  # Guardo los cambios.
            messagebox.showinfo("Éxito", "Usuario actualizado")
            limpiar_campos_usuario()
            mostrar_usuarios()
            id_seleccionado = None
    except Exception as e:
        sesion.rollback()
        messagebox.showerror("Error", "No se pudo actualizar. ¿El correo ya existe?")


def eliminar_usuario():
    # Aquí pregunto el ID con una ventanita.
    usuario_id = simpledialog.askinteger(
        "Eliminar Usuario",
        "ID del usuario a eliminar:",
        parent=root,
        minvalue=1
    )

    # Si cancelan, me salgo.
    if usuario_id is None:
        return

    # Busco el usuario.
    usuario = sesion.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()

    # Si no existe o está inactivo, aviso.
    if not usuario or not usuario.activo:
        messagebox.showerror("Error", f"No existe ningún usuario activo con ID {usuario_id}")
        return

    # Pregunto si de verdad quiere eliminarlo.
    confirmar = messagebox.askyesno(
        "Confirmar eliminación",
        f"¿Seguro que quieres eliminar a '{usuario.nombre}'?\n\n También se desactivarán TODAS sus tareas."
    )

    if not confirmar:
        return

    try:
        crud.eliminar_usuario(sesion, usuario_id)
        messagebox.showinfo("Éxito", f"Usuario '{usuario.nombre}' eliminado (soft delete)")
        limpiar_campos_usuario()
        mostrar_usuarios()
    except Exception as e:
        sesion.rollback()
        messagebox.showerror("Error", f"No se pudo eliminar el usuario:\n{e}")


def limpiar_campos_usuario():
    # Borro lo que haya en las cajas de usuario.
    entry_nombre.delete(0, tk.END)
    entry_email.delete(0, tk.END)


# --- FUNCIONES DE TAREA ---
# Ahora las funciones para las tareas. Son parecidas a las de usuario.

def registrar_tarea():
    # Agarro los datos de las cajas.
    titulo = entry_titulo.get()
    desc = entry_desc.get()
    prioridad = entry_prioridad.get()
    user_id = entry_id_usuario.get()

    # Si falta algo importante, aviso.
    if not titulo or not prioridad or not user_id:
        messagebox.showwarning("Aviso", "Llena Título, Prioridad e ID Usuario")
        return

    try:
        # Convierto a número la prioridad y el ID de usuario.
        crud.crear_tarea(sesion, titulo, desc, int(prioridad), int(user_id))
        messagebox.showinfo("Éxito", "Tarea registrada")
        limpiar_campos_tarea()
        mostrar_tareas()
    except Exception as e:
        sesion.rollback()
        messagebox.showerror("Error", "Revisa que el ID Usuario exista y los datos sean válidos")


def mostrar_tareas():
    # Borro la lista y muestro todas las tareas.
    lista_resultados.delete(0, tk.END)
    tareas = crud.obtener_tareas(sesion)

    for t in tareas:
        # Busco el nombre del usuario dueño de la tarea.
        u = sesion.query(models.Usuario).filter(models.Usuario.id == t.usuario_id).first()
        nombre_u = u.nombre if u else "Desconocido"
        lista_resultados.insert(tk.END, f"ID:{t.id} | {t.titulo} | Prioridad:{t.prioridad} | Usuario:{nombre_u}")


def seleccionar_tarea(event):
    global id_seleccionado

    try:
        # Saco el ID de la tarea seleccionada.
        seleccion = lista_resultados.curselection()[0]
        texto = lista_resultados.get(seleccion)
        id_seleccionado = int(texto.split("|")[0].split(":")[1].strip())

        # Busco la tarea en la base de datos.
        tarea = sesion.query(models.Tarea).filter(models.Tarea.id == id_seleccionado).first()

        # Si existe, pongo sus datos en las cajas.
        if tarea:
            entry_titulo.delete(0, tk.END)
            entry_titulo.insert(0, tarea.titulo)
            entry_desc.delete(0, tk.END)
            entry_desc.insert(0, tarea.descripcion)
            entry_prioridad.delete(0, tk.END)
            entry_prioridad.insert(0, str(tarea.prioridad))
            entry_id_usuario.delete(0, tk.END)
            entry_id_usuario.insert(0, str(tarea.usuario_id))
    except (IndexError, ValueError):
        pass


def editar_tarea():
    global id_seleccionado

    if id_seleccionado is None:
        messagebox.showwarning("Aviso", "Selecciona una tarea de la lista")
        return

    try:
        # Busco la tarea y la actualizo.
        tarea = sesion.query(models.Tarea).filter(models.Tarea.id == id_seleccionado).first()
        if tarea:
            tarea.titulo = entry_titulo.get()
            tarea.descripcion = entry_desc.get()
            tarea.prioridad = int(entry_prioridad.get())
            tarea.usuario_id = int(entry_id_usuario.get())
            sesion.commit()
            messagebox.showinfo("Éxito", "Tarea actualizada")
            limpiar_campos_tarea()
            mostrar_tareas()
            id_seleccionado = None
    except Exception as e:
        sesion.rollback()
        messagebox.showerror("Error", "No se pudo actualizar. Revisa los datos")


def eliminar_tarea():
    # Pregunto el ID de la tarea a eliminar.
    tarea_id = simpledialog.askinteger(
        "Eliminar Tarea",
        "ID de la tarea a eliminar:",
        parent=root,
        minvalue=1
    )

    if tarea_id is None:
        return

    # Busco la tarea.
    tarea = sesion.query(models.Tarea).filter(models.Tarea.id == tarea_id).first()

    if not tarea or not tarea.activo:
        messagebox.showerror("Error", f"No existe ninguna tarea activa con ID {tarea_id}")
        return

    # Confirmo antes de eliminar.
    confirmar = messagebox.askyesno(
        "Confirmar eliminación",
        f"¿Seguro que quieres eliminar la tarea?\n\nID: {tarea.id}\nTítulo: {tarea.titulo}\nPrioridad: {tarea.prioridad}"
    )

    if not confirmar:
        return

    try:
        crud.eliminar_tarea(sesion, tarea_id)
        messagebox.showinfo("Éxito", f"Tarea '{tarea.titulo}' eliminada (soft delete)")
        mostrar_tareas()
    except Exception as e:
        sesion.rollback()
        messagebox.showerror("Error", f"No se pudo eliminar la tarea:\n{e}")


def filtrar_por_usuario():
    # Agarro el ID de usuario que escribieron en la caja.
    user_id_texto = entry_id_usuario.get().strip()

    if not user_id_texto:
        messagebox.showwarning("Aviso", "Escribe un ID de Usuario en la caja de Tareas")
        return

    try:
        # Lo convierto a número.
        user_id = int(user_id_texto)
    except ValueError:
        messagebox.showerror("Error", f"'{user_id_texto}' no es un número válido. Escribe solo el ID.")
        return

    # Busco el usuario activo.
    usuario = sesion.query(models.Usuario).filter(models.Usuario.id == user_id, models.Usuario.activo == True).first()

    lista_resultados.delete(0, tk.END)

    if not usuario:
        # Si no existe, muestro usuarios disponibles para ayudar.
        lista_resultados.insert(tk.END, f" No existe ningún usuario activo con ID {user_id}")
        lista_resultados.insert(tk.END, "--- Usuarios disponibles: ---")
        todos = crud.obtener_usuarios(sesion)
        if todos:
            for u in todos:
                lista_resultados.insert(tk.END, f"   ➜ ID:{u.id} | Nombre:{u.nombre}")
        else:
            lista_resultados.insert(tk.END, "   (No hay usuarios registrados todavía)")
        return

    # Busco las tareas de ese usuario.
    tareas = crud.obtener_tareas_por_usuario(sesion, user_id)

    if not tareas:
        lista_resultados.insert(tk.END, f"El usuario '{usuario.nombre}' (ID:{user_id}) no tiene tareas registradas.")
        return

    for t in tareas:
        lista_resultados.insert(tk.END, f"ID:{t.id} | {t.titulo} | Prioridad:{t.prioridad} | Usuario:{usuario.nombre}")


def resumen_por_usuario():
    # Borro la lista y muestro el resumen que me da crud.
    lista_resultados.delete(0, tk.END)
    resumen = crud.obtener_resumen(sesion)
    for linea in resumen:
        lista_resultados.insert(tk.END, linea)


def limpiar_campos_tarea():
    # Borro todas las cajas de tarea.
    entry_titulo.delete(0, tk.END)
    entry_desc.delete(0, tk.END)
    entry_prioridad.delete(0, tk.END)
    entry_id_usuario.delete(0, tk.END)


# --- DISEÑO DE LA VENTANA ---
# Aquí empiezo a crear la ventana. Yo uso tk.Tk() porque me enseñaron así.
root = tk.Tk()
root.title("Gestión de Usuarios y Tareas")
root.geometry("850x600")

# Recuadro de Usuarios (Izquierda)
# Aquí pongo las cosas de usuarios a la izquierda.
frame_usuarios = tk.LabelFrame(root, text="Usuarios", padx=10, pady=10)
frame_usuarios.grid(row=0, column=0, padx=10, pady=10, sticky="n")

tk.Label(frame_usuarios, text="Nombre:").grid(row=0, column=0, pady=5, sticky="e")
entry_nombre = tk.Entry(frame_usuarios, width=25)
entry_nombre.grid(row=0, column=1, pady=5)

tk.Label(frame_usuarios, text="Email:").grid(row=1, column=0, pady=5, sticky="e")
entry_email = tk.Entry(frame_usuarios, width=25)
entry_email.grid(row=1, column=1, pady=5)

tk.Button(frame_usuarios, text="Registrar Usuario", width=20, command=registrar_usuario).grid(row=2, column=0, columnspan=2, pady=5)
tk.Button(frame_usuarios, text="Editar Usuario", width=20, command=editar_usuario).grid(row=3, column=0, columnspan=2, pady=5)
tk.Button(frame_usuarios, text="Eliminar Usuario", width=20, command=eliminar_usuario).grid(row=4, column=0, columnspan=2, pady=5)
tk.Button(frame_usuarios, text="Mostrar Usuarios", width=20, command=mostrar_usuarios).grid(row=5, column=0, columnspan=2, pady=5)


# Recuadro de Tareas (Derecha)
# Aquí pongo las cosas de tareas a la derecha.
frame_tareas = tk.LabelFrame(root, text="Tareas", padx=10, pady=10)
frame_tareas.grid(row=0, column=1, padx=10, pady=10, sticky="n")

tk.Label(frame_tareas, text="Título:").grid(row=0, column=0, pady=5, sticky="e")
entry_titulo = tk.Entry(frame_tareas, width=25)
entry_titulo.grid(row=0, column=1, pady=5)

tk.Label(frame_tareas, text="Descripción:").grid(row=1, column=0, pady=5, sticky="e")
entry_desc = tk.Entry(frame_tareas, width=25)
entry_desc.grid(row=1, column=1, pady=5)

tk.Label(frame_tareas, text="Prioridad:").grid(row=2, column=0, pady=5, sticky="e")
entry_prioridad = tk.Entry(frame_tareas, width=25)
entry_prioridad.grid(row=2, column=1, pady=5)

tk.Label(frame_tareas, text="ID Usuario:").grid(row=3, column=0, pady=5, sticky="e")
entry_id_usuario = tk.Entry(frame_tareas, width=25)
entry_id_usuario.grid(row=3, column=1, pady=5)

tk.Button(frame_tareas, text="Registrar Tarea", width=20, command=registrar_tarea).grid(row=4, column=0, columnspan=2, pady=5)
tk.Button(frame_tareas, text="Editar Tarea", width=20, command=editar_tarea).grid(row=5, column=0, columnspan=2, pady=5)
tk.Button(frame_tareas, text="Eliminar Tarea", width=20, command=eliminar_tarea).grid(row=6, column=0, columnspan=2, pady=5)
tk.Button(frame_tareas, text="Mostrar Tareas", width=20, command=mostrar_tareas).grid(row=7, column=0, columnspan=2, pady=5)
tk.Button(frame_tareas, text="Filtrar por Usuario", width=20, command=filtrar_por_usuario).grid(row=8, column=0, columnspan=2, pady=5)
tk.Button(frame_tareas, text="Resumen por Usuario", width=20, command=resumen_por_usuario).grid(row=9, column=0, columnspan=2, pady=5)


# Recuadro de Resultados (Abajo)
# Aquí pongo la lista donde se muestran los resultados.
frame_resultados = tk.LabelFrame(root, text="Resultados", padx=10, pady=10)
frame_resultados.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# Una barra para moverme hacia abajo si hay muchos resultados.
scrollbar = tk.Scrollbar(frame_resultados)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

lista_resultados = tk.Listbox(frame_resultados, width=100, height=12, yscrollcommand=scrollbar.set)
lista_resultados.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=lista_resultados.yview)


def al_seleccionar(event):
    # Esta función decide si lo que seleccioné es usuario o tarea.
    try:
        texto = lista_resultados.get(lista_resultados.curselection()[0])

        # Si el texto tiene "Nombre:", entonces es un usuario.
        if "Nombre:" in texto:
            seleccionar_usuario(event)
        else:
            seleccionar_tarea(event)
    except IndexError:
        # Si no hay nada seleccionado, no hago nada.
        pass


# Aquí digo que cuando haga clic en la lista, se ejecute al_seleccionar.
lista_resultados.bind("<<ListboxSelect>>", al_seleccionar)

# Y esto es para que la ventana se quede abierta. Me dijeron que es importante.
root.mainloop()