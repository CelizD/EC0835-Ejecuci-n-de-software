# main.py
# Aquí importo las cosas que voy a necesitar para que funcione todo
import tkinter as tk                          # Esta es la librería para hacer ventanas
from tkinter import messagebox, ttk, simpledialog  # Unos extras para mensajes y ventanitas
import db        # Mi archivo donde configuro la base de datos
import models    # Mi archivo donde están las clases (Usuario y Tarea)
import crud      # Mi archivo donde están las funciones que guardan y consultan datos

# Aquí le digo a SQLAlchemy que cree las tablas si no existen todavía
models.Base.metadata.create_all(bind=db.engine)
# Abro la sesión de la base de datos para usarla en todo el programa
sesion = db.get_db()

# Esta variable la uso para guardar el ID de lo que seleccione en la lista
id_seleccionado = None

# ---------- FUNCIONES DE USUARIO ----------

# Esta función la hago para registrar un usuario nuevo
def registrar_usuario():
    # Aquí tomo lo que el usuario escribió en las cajitas
    nombre = entry_nombre.get()
    email = entry_email.get()
    # Reviso que no estén vacías, si lo están aviso
    if not nombre or not email:
        messagebox.showwarning("Aviso", "Llena todos los campos de Usuario")
        return
    # Uso try porque si el correo ya existe, va a marcar error
    try:
        crud.crear_usuario(sesion, nombre, email)
        messagebox.showinfo("Éxito", "Usuario registrado")
        limpiar_campos_usuario()
        mostrar_usuarios()
    except Exception as e:
        # Esto lo aprendí porque el programa se trababa cuando repetía un correo
        sesion.rollback()  # Limpio la sesión para que no se quede "sucia"
        messagebox.showerror("Error", "El correo ya existe o hubo un fallo. Intenta con otro.")

# Esta función la hago para que se vean todos los usuarios en la listita de abajo
def mostrar_usuarios():
    lista_resultados.delete(0, tk.END)  # Primero limpio la lista
    usuarios = crud.obtener_usuarios(sesion)  # Traigo todos los usuarios
    for u in usuarios:
        lista_resultados.insert(tk.END, f"ID:{u.id} | Nombre:{u.nombre} | Email:{u.email}")

# Esta la hago para cuando le pico a un usuario de la lista, se llenen las cajitas
def seleccionar_usuario(event):
    global id_seleccionado
    try:
        # Aquí saco qué elemento de la lista se seleccionó
        seleccion = lista_resultados.curselection()[0]
        texto = lista_resultados.get(seleccion)
        # Saco el ID del texto que dice "ID:1 | Nombre:..."
        id_seleccionado = int(texto.split("|")[0].split(":")[1].strip())
        
        usuario = sesion.query(models.Usuario).filter(models.Usuario.id == id_seleccionado).first()
        if usuario:
            # Limpio y lleno las cajitas con los datos del usuario
            entry_nombre.delete(0, tk.END)
            entry_nombre.insert(0, usuario.nombre)
            entry_email.delete(0, tk.END)
            entry_email.insert(0, usuario.email)
    except (IndexError, ValueError):
        pass  # Si no hay nada seleccionado, no hago nada

# Esta la hago para editar al usuario que tengo seleccionado
def editar_usuario():
    global id_seleccionado
    # Si no he seleccionado nada, aviso
    if id_seleccionado is None:
        messagebox.showwarning("Aviso", "Selecciona un usuario de la lista de abajo")
        return
    try:
        usuario = sesion.query(models.Usuario).filter(models.Usuario.id == id_seleccionado).first()
        if usuario:
            # Actualizo los datos con lo que está en las cajitas
            usuario.nombre = entry_nombre.get()
            usuario.email = entry_email.get()
            sesion.commit()  # Guardo los cambios
            messagebox.showinfo("Éxito", "Usuario actualizado")
            limpiar_campos_usuario()
            mostrar_usuarios()
            id_seleccionado = None
    except Exception as e:
        sesion.rollback()
        messagebox.showerror("Error", "No se pudo actualizar. ¿El correo ya existe?")

# Esta la hago para eliminar un usuario. Uso la ventanita emergente para pedir el ID
def eliminar_usuario():
    # Esta línea crea la ventanita que pide el ID
    usuario_id = simpledialog.askinteger(
        "Eliminar Usuario",              # Título de la ventanita
        "ID del usuario a eliminar:",    # El mensaje que sale
        parent=root,                     # La ventana de donde sale
        minvalue=1                       # Solo acepto números mayores a 0
    )
    # Si el usuario cancela, ya no hago nada
    if usuario_id is None:
        return
    
    # Reviso que sí exista ese usuario
    usuario = sesion.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        messagebox.showerror("Error", f"No existe ningún usuario con ID {usuario_id}")
        return
    
    # Le pregunto si de verdad quiere borrarlo porque también se borran sus tareas
    confirmar = messagebox.askyesno(
        "Confirmar eliminación",
        f"¿Seguro que quieres eliminar a '{usuario.nombre}'?\n\n También se borrarán TODAS sus tareas."
    )
    if not confirmar:
        return
    
    try:
        crud.eliminar_usuario(sesion, usuario_id)
        messagebox.showinfo("Éxito", f"Usuario '{usuario.nombre}' eliminado con sus tareas")
        limpiar_campos_usuario()
        mostrar_usuarios()
    except Exception as e:
        sesion.rollback()
        messagebox.showerror("Error", f"No se pudo eliminar el usuario:\n{e}")

# Esta la hago para limpiar las cajitas de usuario
def limpiar_campos_usuario():
    entry_nombre.delete(0, tk.END)
    entry_email.delete(0, tk.END)

# ---------- FUNCIONES DE TAREA ----------

# Esta la hago para registrar una tarea nueva
def registrar_tarea():
    # Tomo lo que el usuario escribió
    titulo = entry_titulo.get()
    desc = entry_desc.get()
    prioridad = entry_prioridad.get()
    user_id = entry_id_usuario.get()
    
    # Reviso que los campos importantes no estén vacíos
    if not titulo or not prioridad or not user_id:
        messagebox.showwarning("Aviso", "Llena Título, Prioridad e ID Usuario")
        return
    try:
        # Convierto la prioridad y el ID a número porque son texto en las cajitas
        crud.crear_tarea(sesion, titulo, desc, int(prioridad), int(user_id))
        messagebox.showinfo("Éxito", "Tarea registrada")
        limpiar_campos_tarea()
        mostrar_tareas()
    except Exception as e:
        sesion.rollback()
        messagebox.showerror("Error", "Revisa que el ID Usuario exista y los datos sean válidos")

# Esta la hago para mostrar todas las tareas
def mostrar_tareas():
    lista_resultados.delete(0, tk.END)
    tareas = crud.obtener_tareas(sesion)
    for t in tareas:
        # Busco el nombre del usuario dueño de la tarea para que se vea bonito
        u = sesion.query(models.Usuario).filter(models.Usuario.id == t.usuario_id).first()
        nombre_u = u.nombre if u else "Desconocido"
        lista_resultados.insert(tk.END, f"ID:{t.id} | {t.titulo} | Prioridad:{t.prioridad} | Usuario:{nombre_u}")

# Esta la hago para que al seleccionar una tarea se llenen las cajitas
def seleccionar_tarea(event):
    global id_seleccionado
    try:
        seleccion = lista_resultados.curselection()[0]
        texto = lista_resultados.get(seleccion)
        id_seleccionado = int(texto.split("|")[0].split(":")[1].strip())
        
        tarea = sesion.query(models.Tarea).filter(models.Tarea.id == id_seleccionado).first()
        if tarea:
            # Limpio y lleno cada cajita con los datos de la tarea
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

# Esta la hago para editar la tarea seleccionada
def editar_tarea():
    global id_seleccionado
    if id_seleccionado is None:
        messagebox.showwarning("Aviso", "Selecciona una tarea de la lista")
        return
    try:
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

# Esta la hago para eliminar la tarea. Igual uso la ventanita emergente
def eliminar_tarea():
    tarea_id = simpledialog.askinteger(
        "Eliminar Tarea",
        "ID de la tarea a eliminar:",
        parent=root,
        minvalue=1
    )
    if tarea_id is None:
        return
    
    # Reviso que sí exista esa tarea
    tarea = sesion.query(models.Tarea).filter(models.Tarea.id == tarea_id).first()
    if not tarea:
        messagebox.showerror("Error", f"No existe ninguna tarea con ID {tarea_id}")
        return
    
    # Le muestro los datos y le pregunto si de verdad quiere borrarla
    confirmar = messagebox.askyesno(
        "Confirmar eliminación",
        f"¿Seguro que quieres eliminar la tarea?\n\nID: {tarea.id}\nTítulo: {tarea.titulo}\nPrioridad: {tarea.prioridad}"
    )
    if not confirmar:
        return
    
    try:
        crud.eliminar_tarea(sesion, tarea_id)
        messagebox.showinfo("Éxito", f"Tarea '{tarea.titulo}' eliminada correctamente")
        mostrar_tareas()
    except Exception as e:
        sesion.rollback()
        messagebox.showerror("Error", f"No se pudo eliminar la tarea:\n{e}")

# Esta la hago para filtrar tareas por el ID del usuario
def filtrar_por_usuario():
    # Tomo lo que escribieron y le quito espacios por si las dudas
    user_id_texto = entry_id_usuario.get().strip()
    
    if not user_id_texto:
        messagebox.showwarning("Aviso", "Escribe un ID de Usuario en la caja de Tareas")
        return
    
    # Reviso que sea un número, si no, aviso
    try:
        user_id = int(user_id_texto)
    except ValueError:
        messagebox.showerror("Error", f"'{user_id_texto}' no es un número válido. Escribe solo el ID.")
        return
    
    # Busco si el usuario existe
    usuario = sesion.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    
    lista_resultados.delete(0, tk.END)
    
    if not usuario:
        # Si no existe, aviso y le muestro los IDs que sí hay
        lista_resultados.insert(tk.END, f" No existe ningún usuario con ID {user_id}")
        lista_resultados.insert(tk.END, "--- Usuarios disponibles en la base de datos: ---")
        todos = crud.obtener_usuarios(sesion)
        if todos:
            for u in todos:
                lista_resultados.insert(tk.END, f"   ➜ ID:{u.id} | Nombre:{u.nombre}")
        else:
            lista_resultados.insert(tk.END, "   (No hay usuarios registrados todavía)")
        return
    
    # Si existe, busco sus tareas
    tareas = crud.obtener_tareas_por_usuario(sesion, user_id)
    
    if not tareas:
        lista_resultados.insert(tk.END, f"El usuario '{usuario.nombre}' (ID:{user_id}) no tiene tareas registradas.")
        return
    
    # Muestro las tareas que encontré
    for t in tareas:
        lista_resultados.insert(tk.END, f"ID:{t.id} | {t.titulo} | Prioridad:{t.prioridad} | Usuario:{usuario.nombre}")

# Esta la hago para mostrar cuántas tareas tiene cada usuario
def resumen_por_usuario():
    lista_resultados.delete(0, tk.END)
    resumen = crud.obtener_resumen(sesion)
    for linea in resumen:
        lista_resultados.insert(tk.END, linea)

# Esta la hago para limpiar las cajitas de tarea
def limpiar_campos_tarea():
    entry_titulo.delete(0, tk.END)
    entry_desc.delete(0, tk.END)
    entry_prioridad.delete(0, tk.END)
    entry_id_usuario.delete(0, tk.END)


# ---------- AQUÍ EMPIEZO A ARMAR LA VENTANA ----------

# Creo la ventana principal
root = tk.Tk()
root.title("Gestión de Usuarios y Tareas")  # El título de arriba
root.geometry("850x600")                    # El tamaño de la ventana

# ----- Recuadro de Usuarios (del lado izquierdo) -----
# Uso LabelFrame para hacer el recuadro con título como en la foto del profe
frame_usuarios = tk.LabelFrame(root, text="Usuarios", padx=10, pady=10)
frame_usuarios.grid(row=0, column=0, padx=10, pady=10, sticky="n")

# Aquí pongo la etiqueta y la cajita del Nombre
tk.Label(frame_usuarios, text="Nombre:").grid(row=0, column=0, pady=5, sticky="e")
entry_nombre = tk.Entry(frame_usuarios, width=25)
entry_nombre.grid(row=0, column=1, pady=5)

# Aquí la del Email
tk.Label(frame_usuarios, text="Email:").grid(row=1, column=0, pady=5, sticky="e")
entry_email = tk.Entry(frame_usuarios, width=25)
entry_email.grid(row=1, column=1, pady=5)

# Aquí los botones de usuario, cada uno llama a su función
tk.Button(frame_usuarios, text="Registrar Usuario", width=20, command=registrar_usuario).grid(row=2, column=0, columnspan=2, pady=5)
tk.Button(frame_usuarios, text="Editar Usuario", width=20, command=editar_usuario).grid(row=3, column=0, columnspan=2, pady=5)
tk.Button(frame_usuarios, text="Eliminar Usuario", width=20, command=eliminar_usuario).grid(row=4, column=0, columnspan=2, pady=5)
tk.Button(frame_usuarios, text="Mostrar Usuarios", width=20, command=mostrar_usuarios).grid(row=5, column=0, columnspan=2, pady=5)


# ----- Recuadro de Tareas (del lado derecho) -----
frame_tareas = tk.LabelFrame(root, text="Tareas", padx=10, pady=10)
frame_tareas.grid(row=0, column=1, padx=10, pady=10, sticky="n")

# Aquí la etiqueta y cajita del Título
tk.Label(frame_tareas, text="Título:").grid(row=0, column=0, pady=5, sticky="e")
entry_titulo = tk.Entry(frame_tareas, width=25)
entry_titulo.grid(row=0, column=1, pady=5)

# La de Descripción
tk.Label(frame_tareas, text="Descripción:").grid(row=1, column=0, pady=5, sticky="e")
entry_desc = tk.Entry(frame_tareas, width=25)
entry_desc.grid(row=1, column=1, pady=5)

# La de Prioridad
tk.Label(frame_tareas, text="Prioridad:").grid(row=2, column=0, pady=5, sticky="e")
entry_prioridad = tk.Entry(frame_tareas, width=25)
entry_prioridad.grid(row=2, column=1, pady=5)

# La del ID Usuario (aquí pongo el ID para filtrar o para asignar a quién es la tarea)
tk.Label(frame_tareas, text="ID Usuario:").grid(row=3, column=0, pady=5, sticky="e")
entry_id_usuario = tk.Entry(frame_tareas, width=25)
entry_id_usuario.grid(row=3, column=1, pady=5)

# Los botones de tareas
tk.Button(frame_tareas, text="Registrar Tarea", width=20, command=registrar_tarea).grid(row=4, column=0, columnspan=2, pady=5)
tk.Button(frame_tareas, text="Editar Tarea", width=20, command=editar_tarea).grid(row=5, column=0, columnspan=2, pady=5)
tk.Button(frame_tareas, text="Eliminar Tarea", width=20, command=eliminar_tarea).grid(row=6, column=0, columnspan=2, pady=5)
tk.Button(frame_tareas, text="Mostrar Tareas", width=20, command=mostrar_tareas).grid(row=7, column=0, columnspan=2, pady=5)
tk.Button(frame_tareas, text="Filtrar por Usuario", width=20, command=filtrar_por_usuario).grid(row=8, column=0, columnspan=2, pady=5)
tk.Button(frame_tareas, text="Resumen por Usuario", width=20, command=resumen_por_usuario).grid(row=9, column=0, columnspan=2, pady=5)


# ----- Recuadro de Resultados (abajo, donde sale la listita) -----
frame_resultados = tk.LabelFrame(root, text="Resultados", padx=10, pady=10)
frame_resultados.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# Le pongo una barrita para poder bajar si hay muchos datos
scrollbar = tk.Scrollbar(frame_resultados)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Esta es la listita donde muestro los resultados
lista_resultados = tk.Listbox(frame_resultados, width=100, height=12, yscrollcommand=scrollbar.set)
lista_resultados.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=lista_resultados.yview)

# Esta función la hago para saber qué seleccionó el usuario en la lista
def al_seleccionar(event):
    try:
        texto = lista_resultados.get(lista_resultados.curselection()[0])
        # Si el texto dice "Nombre:" es un usuario, si no, es una tarea
        if "Nombre:" in texto:
            seleccionar_usuario(event)
        else:
            seleccionar_tarea(event)
    except IndexError:
        pass  # Si no hay nada seleccionado, no hago nada

# Aquí le digo a la lista que cuando seleccionen algo, ejecute esa función
lista_resultados.bind("<<ListboxSelect>>", al_seleccionar)

# Esta línea hace que la ventana se quede abierta esperando a que el usuario haga algo
root.mainloop()