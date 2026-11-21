
import os
import shutil
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog, filedialog

# Importo los módulos encargados de la conexión, los modelos y las operaciones de la base de datos.
import db
import models
import crud

# Verifico que la estructura de la base de datos cuente con la columna password.
db.asegurar_columna_password()

# Creo las tablas necesarias al iniciar la aplicación.
models.Base.metadata.create_all(bind=db.engine)

# Establezco la sesión que utilizaré para realizar las operaciones con la base de datos.
sesion = db.get_db()

# Verifico que exista un usuario administrador para garantizar el acceso inicial al sistema.
crud.asegurar_admin_por_defecto(sesion)

# Variables globales utilizadas para controlar el registro seleccionado y la sesión actual.
id_seleccionado = None
tipo_seleccionado = None
usuario_actual = None

# FUNCIONES DE USUARIO 
# En esta sección gestiono el registro, consulta, edición y eliminación de usuarios.

def registrar_usuario():
    # Obtengo los datos ingresados y elimino los espacios innecesarios.
    nombre = entry_nombre.get().strip()
    email = entry_email.get().strip()
    password = entry_password.get().strip()

    # Verifico que todos los campos obligatorios contengan información.
    if not nombre or not email or not password:
        messagebox.showwarning("Aviso", "Llena todos los campos de Usuario (Nombre, Email y Contraseña)")
        return

    try:
        # Registro el nuevo usuario mediante las funciones del módulo CRUD.
        crud.crear_usuario(sesion, nombre, email, password)
        messagebox.showinfo("Éxito", "Usuario registrado correctamente")
        limpiar_campos_usuario()
        mostrar_usuarios()
    except Exception as e:
        # Restauro la sesión ante cualquier error durante el registro.
        sesion.rollback()
        messagebox.showerror("Error", "El correo ya existe o hubo un fallo. Intenta con otro.")


def mostrar_usuarios():
    global id_seleccionado, tipo_seleccionado
    id_seleccionado = None
    tipo_seleccionado = None

    # Limpio los resultados anteriores antes de cargar los registros.
    lista_resultados.delete(0, tk.END)

    # Consulto los usuarios registrados y muestro su información.
    usuarios = crud.obtener_usuarios(sesion)
    for u in usuarios:
        lista_resultados.insert(tk.END, f"ID:{u.id} | Nombre:{u.nombre} | Email:{u.email}")


def seleccionar_usuario(event):
    # Actualizo las variables de control para identificar el usuario seleccionado.
    global id_seleccionado, tipo_seleccionado

    try:
        # Obtengo el registro seleccionado y recupero su identificador.
        seleccion = lista_resultados.curselection()[0]
        texto = lista_resultados.get(seleccion)

        id_seleccionado = int(texto.split("|")[0].split(":")[1].strip())
        tipo_seleccionado = "usuario"

        # Consulto la información del usuario seleccionado.
        usuario = sesion.query(models.Usuario).filter(models.Usuario.id == id_seleccionado).first()

        # Cargo los datos del usuario en los campos correspondientes.
        if usuario:
            entry_nombre.delete(0, tk.END)
            entry_nombre.insert(0, usuario.nombre)
            entry_email.delete(0, tk.END)
            entry_email.insert(0, usuario.email)
            entry_password.delete(0, tk.END)
            entry_password.insert(0, usuario.password if usuario.password else "")
    except (IndexError, ValueError):
        # Evito ejecutar operaciones cuando no existe una selección válida.
        pass


def editar_usuario():
    global id_seleccionado, tipo_seleccionado

    # Verifico que exista un usuario seleccionado antes de continuar.
    if id_seleccionado is None or tipo_seleccionado != "usuario":
        messagebox.showwarning("Aviso", "Selecciona un usuario de la lista de abajo")
        return

    nuevo_nombre = entry_nombre.get().strip()
    nuevo_email = entry_email.get().strip()
    nuevo_password = entry_password.get().strip()

    # Valido que los campos obligatorios no queden vacíos.
    if not nuevo_nombre or not nuevo_email or not nuevo_password:
        messagebox.showwarning("Aviso", "Nombre, Email y Contraseña no pueden quedar vacíos")
        return

    try:
        # Localizo el usuario y actualizo sus datos.
        usuario = sesion.query(models.Usuario).filter(models.Usuario.id == id_seleccionado).first()
        if usuario:
            usuario.nombre = nuevo_nombre
            usuario.email = nuevo_email
            usuario.password = nuevo_password
            sesion.commit()  # Confirmo los cambios en la base de datos.
            messagebox.showinfo("Éxito", "Usuario actualizado")
            limpiar_campos_usuario()
            mostrar_usuarios()
            id_seleccionado = None
            tipo_seleccionado = None
    except Exception as e:
        # Deshago los cambios si ocurre algún problema durante la actualización.
        sesion.rollback()
        messagebox.showerror("Error", "No se pudo actualizar. ¿El correo ya existe?")


def eliminar_usuario():
    # Solicito el identificador del usuario que se desea eliminar.
    usuario_id = simpledialog.askinteger(
        "Eliminar Usuario",
        "ID del usuario a eliminar:",
        parent=root,
        minvalue=1
    )

    # Finalizo la operación si se cancela la solicitud.
    if usuario_id is None:
        return

    # Consulto el usuario correspondiente al identificador ingresado.
    usuario = sesion.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()

    # Verifico que el usuario exista y permanezca activo.
    if not usuario or not usuario.activo:
        messagebox.showerror("Error", f"No existe ningún usuario activo con ID {usuario_id}")
        return

    # Compruebo que permanezca al menos un usuario activo en el sistema.
    total_activos = sesion.query(models.Usuario).filter(models.Usuario.activo == True).count()
    if total_activos <= 1:
        messagebox.showwarning("Aviso", "No puedes eliminar al único usuario activo del sistema (te quedarías sin acceso al Login).")
        return

    # Solicito confirmación antes de realizar la eliminación lógica.
    confirmar = messagebox.askyesno(
        "Confirmar eliminación",
        f"¿Seguro que quieres eliminar a '{usuario.nombre}'?\n\n También se desactivarán TODAS sus tareas."
    )

    if not confirmar:
        return

    try:
        # Ejecuto la eliminación lógica del usuario mediante el módulo CRUD.
        crud.eliminar_usuario(sesion, usuario_id)
        messagebox.showinfo("Éxito", f"Usuario '{usuario.nombre}' eliminado (soft delete)")
        limpiar_campos_usuario()
        mostrar_usuarios()
    except Exception as e:
        # Restauro la sesión y notifico si la operación no pudo completarse.
        sesion.rollback()
        messagebox.showerror("Error", f"No se pudo eliminar el usuario:\n{e}")


def limpiar_campos_usuario():
    # Restablezco los campos del formulario de usuarios.
    entry_nombre.delete(0, tk.END)
    entry_email.delete(0, tk.END)
    entry_password.delete(0, tk.END)


# FUNCIONES DE TAREA 
# En esta sección gestiono las tareas y su relación con los usuarios registrados.

def registrar_tarea():
    # Obtengo la información ingresada en el formulario de tareas.
    titulo = entry_titulo.get().strip()
    desc = entry_desc.get().strip()
    prioridad = entry_prioridad.get().strip()
    user_id = entry_id_usuario.get().strip()

    # Compruebo que los campos necesarios contengan información.
    if not titulo or not prioridad or not user_id:
        messagebox.showwarning("Aviso", "Llena Título, Prioridad e ID Usuario")
        return

    try:
        # Convierto la prioridad y el identificador del usuario a valores enteros.
        prioridad_num = int(prioridad)
        user_id_num = int(user_id)
    except ValueError:
        messagebox.showerror("Error", "La Prioridad y el ID Usuario deben ser números enteros.")
        return

    # Verifico que el usuario asignado exista y se encuentre activo.
    usuario_activo = crud.obtener_usuario_activo_por_id(sesion, user_id_num)
    if not usuario_activo:
        messagebox.showerror("Error", f"No existe ningún usuario activo con ID {user_id_num}. Revisa la lista de usuarios.")
        return

    try:
        # Registro la tarea y la relaciono con el usuario correspondiente.
        crud.crear_tarea(sesion, titulo, desc, prioridad_num, user_id_num)
        messagebox.showinfo("Éxito", "Tarea registrada")
        limpiar_campos_tarea()
        mostrar_tareas()
    except Exception as e:
        # Deshago los cambios cuando ocurre un error durante el registro.
        sesion.rollback()
        messagebox.showerror("Error", f"Revisa que el ID Usuario exista y los datos sean válidos:\n{e}")


def mostrar_tareas():
    global id_seleccionado, tipo_seleccionado
    id_seleccionado = None
    tipo_seleccionado = None

    # Limpio la lista y consulto las tareas disponibles.
    lista_resultados.delete(0, tk.END)
    tareas = crud.obtener_tareas(sesion)

    for t in tareas:
        # Recupero el nombre del usuario relacionado con cada tarea.
        u = sesion.query(models.Usuario).filter(models.Usuario.id == t.usuario_id).first()
        nombre_u = u.nombre if u else "Desconocido"
        lista_resultados.insert(tk.END, f"ID:{t.id} | {t.titulo} | Prioridad:{t.prioridad} | Usuario:{nombre_u}")


def seleccionar_tarea(event):
    global id_seleccionado, tipo_seleccionado

    try:
        # Identifico la tarea seleccionada y recupero su identificador.
        seleccion = lista_resultados.curselection()[0]
        texto = lista_resultados.get(seleccion)
        id_seleccionado = int(texto.split("|")[0].split(":")[1].strip())
        tipo_seleccionado = "tarea"

        # Consulto los datos de la tarea seleccionada.
        tarea = sesion.query(models.Tarea).filter(models.Tarea.id == id_seleccionado).first()

        # Cargo la información de la tarea en el formulario correspondiente.
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
        # Evito procesar selecciones que no contengan un identificador válido.
        pass


def editar_tarea():
    global id_seleccionado, tipo_seleccionado

    # Verifico que se haya seleccionado una tarea antes de modificarla.
    if id_seleccionado is None or tipo_seleccionado != "tarea":
        messagebox.showwarning("Aviso", "Selecciona una tarea de la lista")
        return

    nuevo_titulo = entry_titulo.get().strip()
    nueva_desc = entry_desc.get().strip()
    nueva_prioridad = entry_prioridad.get().strip()
    nuevo_user_id = entry_id_usuario.get().strip()

    # Valido los campos obligatorios del formulario.
    if not nuevo_titulo or not nueva_prioridad or not nuevo_user_id:
        messagebox.showwarning("Aviso", "Título, Prioridad e ID Usuario no pueden quedar vacíos")
        return

    try:
        # Convierto los valores numéricos antes de realizar la actualización.
        prioridad_num = int(nueva_prioridad)
        user_id_num = int(nuevo_user_id)
    except ValueError:
        messagebox.showerror("Error", "La Prioridad y el ID Usuario deben ser números enteros.")
        return

    # Compruebo que el nuevo usuario asignado exista y esté activo.
    usuario_activo = crud.obtener_usuario_activo_por_id(sesion, user_id_num)
    if not usuario_activo:
        messagebox.showerror("Error", f"No existe ningún usuario activo con ID {user_id_num}.")
        return

    try:
        # Localizo la tarea y actualizo sus datos y su usuario relacionado.
        tarea = sesion.query(models.Tarea).filter(models.Tarea.id == id_seleccionado).first()
        if tarea:
            tarea.titulo = nuevo_titulo
            tarea.descripcion = nueva_desc
            tarea.prioridad = prioridad_num
            tarea.usuario_id = user_id_num
            sesion.commit()
            messagebox.showinfo("Éxito", "Tarea actualizada")
            limpiar_campos_tarea()
            mostrar_tareas()
            id_seleccionado = None
            tipo_seleccionado = None
    except Exception as e:
        # Restauro la sesión si ocurre algún error durante la actualización.
        sesion.rollback()
        messagebox.showerror("Error", "No se pudo actualizar. Revisa los datos")


def eliminar_tarea():
    # Solicito el identificador de la tarea que se desea eliminar.
    tarea_id = simpledialog.askinteger(
        "Eliminar Tarea",
        "ID de la tarea a eliminar:",
        parent=root,
        minvalue=1
    )

    if tarea_id is None:
        return

    # Consulto la tarea correspondiente al identificador ingresado.
    tarea = sesion.query(models.Tarea).filter(models.Tarea.id == tarea_id).first()

    # Verifico que la tarea exista y permanezca activa.
    if not tarea or not tarea.activo:
        messagebox.showerror("Error", f"No existe ninguna tarea activa con ID {tarea_id}")
        return

    # Solicito confirmación antes de eliminar el registro.
    confirmar = messagebox.askyesno(
        "Confirmar eliminación",
        f"¿Seguro que quieres eliminar la tarea?\n\nID: {tarea.id}\nTítulo: {tarea.titulo}\nPrioridad: {tarea.prioridad}"
    )

    if not confirmar:
        return

    try:
        # Ejecuto la eliminación lógica de la tarea.
        crud.eliminar_tarea(sesion, tarea_id)
        messagebox.showinfo("Éxito", f"Tarea '{tarea.titulo}' eliminada (soft delete)")
        limpiar_campos_tarea()
        mostrar_tareas()
    except Exception as e:
        # Restauro la sesión y notifico cualquier problema durante la eliminación.
        sesion.rollback()
        messagebox.showerror("Error", f"No se pudo eliminar la tarea:\n{e}")


def filtrar_por_usuario():
    # Obtengo el identificador del usuario utilizado para realizar el filtro.
    user_id_texto = entry_id_usuario.get().strip()

    if not user_id_texto:
        messagebox.showwarning("Aviso", "Escribe un ID de Usuario en la caja de Tareas")
        return

    try:
        # Convierto el identificador ingresado a un valor entero.
        user_id = int(user_id_texto)
    except ValueError:
        messagebox.showerror("Error", f"'{user_id_texto}' no es un número válido. Escribe solo el ID.")
        return

    # Consulto si el usuario existe y se encuentra activo.
    usuario = sesion.query(models.Usuario).filter(models.Usuario.id == user_id, models.Usuario.activo == True).first()

    lista_resultados.delete(0, tk.END)

    if not usuario:
        # Muestro los usuarios disponibles cuando el identificador no corresponde a un registro activo.
        lista_resultados.insert(tk.END, f" No existe ningún usuario activo con ID {user_id}")
        lista_resultados.insert(tk.END, "--- Usuarios disponibles: ---")
        todos = crud.obtener_usuarios(sesion)
        if todos:
            for u in todos:
                lista_resultados.insert(tk.END, f"   ➜ ID:{u.id} | Nombre:{u.nombre}")
        else:
            lista_resultados.insert(tk.END, "   (No hay usuarios registrados todavía)")
        return

    # Recupero las tareas relacionadas con el usuario seleccionado.
    tareas = crud.obtener_tareas_por_usuario(sesion, user_id)

    if not tareas:
        lista_resultados.insert(tk.END, f"El usuario '{usuario.nombre}' (ID:{user_id}) no tiene tareas registradas.")
        return

    # Muestro las tareas encontradas junto con la información del usuario.
    for t in tareas:
        lista_resultados.insert(tk.END, f"ID:{t.id} | {t.titulo} | Prioridad:{t.prioridad} | Usuario:{usuario.nombre}")


def resumen_por_usuario():
    # Consulto y muestro el resumen de tareas agrupadas por usuario.
    lista_resultados.delete(0, tk.END)
    resumen = crud.obtener_resumen(sesion)
    for linea in resumen:
        lista_resultados.insert(tk.END, linea)


def limpiar_campos_tarea():
    # Restablezco los campos del formulario de tareas.
    entry_titulo.delete(0, tk.END)
    entry_desc.delete(0, tk.END)
    entry_prioridad.delete(0, tk.END)
    entry_id_usuario.delete(0, tk.END)


# FUNCIONES DE BACKUP (RESPALDOS)
# En esta sección gestiono la creación, restauración y exportación de respaldos.

def realizar_backup_manual():
    try:
        # Confirmo los cambios pendientes antes de generar el respaldo.
        sesion.commit()
        ruta_creada = crud.crear_backup_db(prefijo="backup_manual")
        nombre_archivo = os.path.basename(ruta_creada)
        messagebox.showinfo(
            "Backup Exitoso",
            f"Se creó el respaldo de la base de datos correctamente:\n\nArchivo: {nombre_archivo}\nCarpeta: {db.ruta_backups}"
        )
    except Exception as e:
        messagebox.showerror("Error en Backup", f"No se pudo crear el respaldo:\n{e}")


def exportar_datos_csv_json():
    try:
        # Exporto la información de usuarios y tareas a formatos legibles.
        ruta_json, ruta_csv_u, ruta_csv_t = crud.exportar_backup_legible(sesion)
        messagebox.showinfo(
            "Exportación Exitosa",
            "Se exportaron los datos en formatos legibles dentro de la carpeta 'backups/':\n\n"
            f"• JSON: {os.path.basename(ruta_json)}\n"
            f"• CSV Usuarios: {os.path.basename(ruta_csv_u)}\n"
            f"• CSV Tareas: {os.path.basename(ruta_csv_t)}"
        )
    except Exception as e:
        messagebox.showerror("Error al Exportar", f"No se pudieron exportar los archivos:\n{e}")


def restaurar_backup():
    global sesion, id_seleccionado, tipo_seleccionado

    # Permito seleccionar el archivo de base de datos que se utilizará para la restauración.
    archivo_backup = filedialog.askopenfilename(
        parent=root,
        title="Seleccionar archivo de Backup (.db) para restaurar",
        initialdir=db.ruta_backups,
        filetypes=[("Base de datos SQLite", "*.db"), ("Todos los archivos", "*.*")]
    )

    if not archivo_backup:
        return

    # Solicito confirmación e informo que se generará un respaldo del estado actual.
    confirmar = messagebox.askyesno(
        "Confirmar Restauración",
        f"¿Estás seguro de que quieres restaurar este respaldo?\n\n{os.path.basename(archivo_backup)}\n\n"
        "NOTA: Antes de restaurar, se guardará un backup automático del estado actual por seguridad."
    )
    if not confirmar:
        return

    try:
        # Genero un respaldo de seguridad antes de reemplazar la base de datos actual.
        if os.path.exists(db.ruta_db):
            crud.crear_backup_db(prefijo="pre_restauracion")

        # Cierro la sesión y libero las conexiones para permitir el reemplazo del archivo.
        sesion.close()
        db.engine.dispose()

        # Restauro el archivo seleccionado en la ubicación de la base de datos principal.
        shutil.copy2(archivo_backup, db.ruta_db)

        # Verifico la estructura de la base de datos y establezco una nueva sesión.
        db.asegurar_columna_password()
        sesion = db.get_db()
        crud.asegurar_admin_por_defecto(sesion)

        # Restablezco las variables y los formularios para cargar la información restaurada.
        id_seleccionado = None
        tipo_seleccionado = None
        limpiar_campos_usuario()
        limpiar_campos_tarea()
        mostrar_usuarios()

        messagebox.showinfo("Restauración Completa", "El backup se restauró correctamente y los datos fueron actualizados.")
    except Exception as e:
        # Intento establecer una nueva sesión para mantener disponible la aplicación.
        sesion = db.get_db()
        messagebox.showerror("Error al Restaurar", f"Ocurrió un problema al restaurar el backup:\n{e}")


def al_cerrar_programa():
    # Genero automáticamente un respaldo al cerrar la aplicación.
    try:
        sesion.commit()
        crud.crear_backup_db(prefijo="auto_cierre")
    except Exception:
        pass
    finally:
        # Cierro la sesión y libero la ventana principal.
        try:
            sesion.close()
        except Exception:
            pass
        root.destroy()


# FUNCIÓN DE LOGIN 
# En esta sección controlo el acceso al sistema mediante la autenticación de usuarios.

def mostrar_ventana_login():
    global usuario_actual

    # Mantengo oculta la ventana principal hasta completar el inicio de sesión.
    root.withdraw()

    ventana_login = tk.Toplevel(root)
    ventana_login.title("Iniciar Sesión - Sistema de Usuarios y Tareas")
    ventana_login.geometry("400x280")
    ventana_login.resizable(False, False)

    # Cierro la aplicación si se intenta cerrar la ventana de acceso.
    ventana_login.protocol("WM_DELETE_WINDOW", root.destroy)

    frame_login = tk.LabelFrame(ventana_login, text="Acceso al Sistema", padx=20, pady=15)
    frame_login.pack(padx=20, pady=20, fill="both", expand=True)

    tk.Label(frame_login, text="Usuario o Email:").grid(row=0, column=0, pady=8, sticky="e")
    entry_login_user = tk.Entry(frame_login, width=25)
    entry_login_user.grid(row=0, column=1, pady=8, padx=5)
    entry_login_user.insert(0, "admin")

    tk.Label(frame_login, text="Contraseña:").grid(row=1, column=0, pady=8, sticky="e")
    entry_login_pass = tk.Entry(frame_login, width=25, show="*")
    entry_login_pass.grid(row=1, column=1, pady=8, padx=5)

    lbl_ayuda = tk.Label(
        frame_login,
        text="Por defecto: usuario 'admin' / contraseña 'admin123'",
        fg="gray",
        font=("Arial", 8)
    )
    lbl_ayuda.grid(row=2, column=0, columnspan=2, pady=5)

    def intentar_login(event=None):
        global usuario_actual
        identificador = entry_login_user.get().strip()
        password = entry_login_pass.get().strip()

        # Verifico que se hayan ingresado las credenciales necesarias.
        if not identificador or not password:
            messagebox.showwarning("Aviso", "Escribe tu usuario/email y tu contraseña", parent=ventana_login)
            return

        # Valido las credenciales mediante el proceso de autenticación del módulo CRUD.
        usuario = crud.autenticar_usuario(sesion, identificador, password)
        if usuario:
            usuario_actual = usuario
            lbl_sesion_activa.config(text=f"Sesión iniciada como: {usuario.nombre} ({usuario.email})")
            ventana_login.destroy()
            root.deiconify()  # Habilito la ventana principal después de autenticar al usuario.
            mostrar_usuarios()
        else:
            messagebox.showerror(
                "Acceso Denegado",
                "Usuario/Email o contraseña incorrectos (o el usuario está inactivo).",
                parent=ventana_login
            )

    btn_entrar = tk.Button(frame_login, text="Iniciar Sesión", width=20, command=intentar_login)
    btn_entrar.grid(row=3, column=0, columnspan=2, pady=10)

    # Vinculo la tecla Enter con el proceso de autenticación.
    ventana_login.bind("<Return>", intentar_login)
    entry_login_pass.focus_set()


def cerrar_sesion():
    global usuario_actual, id_seleccionado, tipo_seleccionado
    confirmar = messagebox.askyesno("Cerrar Sesión", "¿Deseas cerrar la sesión actual?")
    if confirmar:
        # Finalizo la sesión actual y restablezco los datos de selección.
        usuario_actual = None
        id_seleccionado = None
        tipo_seleccionado = None
        limpiar_campos_usuario()
        limpiar_campos_tarea()
        lista_resultados.delete(0, tk.END)
        mostrar_ventana_login()


# DISEÑO DE LA VENTANA PRINCIPAL 
# En esta sección construyo la interfaz gráfica y organizo sus componentes.

root = tk.Tk()
root.title("Gestión de Usuarios y Tareas")
root.geometry("900x730")

# Configuro el cierre de la ventana para ejecutar el proceso de respaldo automático.
root.protocol("WM_DELETE_WINDOW", al_cerrar_programa)

# Barra superior con información de la sesión y acceso al cierre de sesión.
frame_top = tk.Frame(root, padx=10, pady=5)
frame_top.grid(row=0, column=0, columnspan=2, sticky="ew")

lbl_sesion_activa = tk.Label(frame_top, text="Sesión no iniciada", font=("Arial", 10, "bold"))
lbl_sesion_activa.pack(side=tk.LEFT)

btn_logout = tk.Button(frame_top, text="Cerrar Sesión", command=cerrar_sesion)
btn_logout.pack(side=tk.RIGHT)

# FORMULARIO DE USUARIOS 
# Organizo los campos y las operaciones disponibles para administrar usuarios.

frame_usuarios = tk.LabelFrame(root, text="Usuarios", padx=10, pady=10)
frame_usuarios.grid(row=1, column=0, padx=10, pady=5, sticky="n")

tk.Label(frame_usuarios, text="Nombre:").grid(row=0, column=0, pady=5, sticky="e")
entry_nombre = tk.Entry(frame_usuarios, width=25)
entry_nombre.grid(row=0, column=1, pady=5)

tk.Label(frame_usuarios, text="Email:").grid(row=1, column=0, pady=5, sticky="e")
entry_email = tk.Entry(frame_usuarios, width=25)
entry_email.grid(row=1, column=1, pady=5)

tk.Label(frame_usuarios, text="Contraseña:").grid(row=2, column=0, pady=5, sticky="e")
entry_password = tk.Entry(frame_usuarios, width=25, show="*")
entry_password.grid(row=2, column=1, pady=5)

tk.Button(frame_usuarios, text="Registrar Usuario", width=20, command=registrar_usuario).grid(row=3, column=0, columnspan=2, pady=4)
tk.Button(frame_usuarios, text="Editar Usuario", width=20, command=editar_usuario).grid(row=4, column=0, columnspan=2, pady=4)
tk.Button(frame_usuarios, text="Eliminar Usuario", width=20, command=eliminar_usuario).grid(row=5, column=0, columnspan=2, pady=4)
tk.Button(frame_usuarios, text="Mostrar Usuarios", width=20, command=mostrar_usuarios).grid(row=6, column=0, columnspan=2, pady=4)


# FORMULARIO DE TAREAS
# Organizo los campos y las operaciones para administrar las tareas y sus asignaciones.

frame_tareas = tk.LabelFrame(root, text="Tareas", padx=10, pady=10)
frame_tareas.grid(row=1, column=1, padx=10, pady=5, sticky="n")

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

tk.Button(frame_tareas, text="Registrar Tarea", width=20, command=registrar_tarea).grid(row=4, column=0, columnspan=2, pady=4)
tk.Button(frame_tareas, text="Editar Tarea", width=20, command=editar_tarea).grid(row=5, column=0, columnspan=2, pady=4)
tk.Button(frame_tareas, text="Eliminar Tarea", width=20, command=eliminar_tarea).grid(row=6, column=0, columnspan=2, pady=4)
tk.Button(frame_tareas, text="Mostrar Tareas", width=20, command=mostrar_tareas).grid(row=7, column=0, columnspan=2, pady=4)
tk.Button(frame_tareas, text="Filtrar por Usuario", width=20, command=filtrar_por_usuario).grid(row=8, column=0, columnspan=2, pady=4)
tk.Button(frame_tareas, text="Resumen por Usuario", width=20, command=resumen_por_usuario).grid(row=9, column=0, columnspan=2, pady=4)


# SECCIÓN DE RESPALDOS
# Incluyo las opciones para crear, restaurar y exportar copias de seguridad.

frame_backups = tk.LabelFrame(root, text="Respaldos de Base de Datos (Backups)", padx=10, pady=8)
frame_backups.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

tk.Button(frame_backups, text="Crear Backup (.db)", width=22, command=realizar_backup_manual).pack(side=tk.LEFT, padx=10, pady=4)
tk.Button(frame_backups, text="Restaurar Backup (.db)", width=22, command=restaurar_backup).pack(side=tk.LEFT, padx=10, pady=4)
tk.Button(frame_backups, text="Exportar a CSV / JSON", width=22, command=exportar_datos_csv_json).pack(side=tk.LEFT, padx=10, pady=4)
tk.Label(frame_backups, text="(Backup automático activado al salir)", fg="gray").pack(side=tk.RIGHT, padx=10)


# SECCIÓN DE RESULTADOS
# Utilizo una lista para mostrar los registros y resultados de las consultas.

frame_resultados = tk.LabelFrame(root, text="Resultados", padx=10, pady=10)
frame_resultados.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# Configuro la barra de desplazamiento para facilitar la consulta de los registros.
scrollbar = tk.Scrollbar(frame_resultados)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

lista_resultados = tk.Listbox(frame_resultados, width=105, height=11, yscrollcommand=scrollbar.set)
lista_resultados.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=lista_resultados.yview)


def al_seleccionar(event):
    # Identifico el tipo de registro seleccionado para ejecutar la función correspondiente.
    # Ignoro las líneas informativas que no contienen un identificador de usuario o tarea.
    try:
        texto = lista_resultados.get(lista_resultados.curselection()[0])

        if not texto.startswith("ID:"):
            return

        # Distingo los registros de usuario de los registros de tareas.
        if "| Nombre:" in texto:
            seleccionar_usuario(event)
        else:
            seleccionar_tarea(event)
    except IndexError:
        # Evito procesar el evento cuando no existe ningún elemento seleccionado.
        pass


# Asocio el evento de selección de la lista con la función de identificación del registro.
lista_resultados.bind("<<ListboxSelect>>", al_seleccionar)

# Muestro la ventana de inicio de sesión antes de permitir el acceso al sistema.
mostrar_ventana_login()

# Inicio el ciclo principal de Tkinter para mantener la aplicación en ejecución.
root.mainloop()
