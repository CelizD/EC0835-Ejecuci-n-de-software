# crud.py

import os
import shutil
import json
import csv
from datetime import datetime
from sqlalchemy.orm import Session
import models
import db as db_config

#  OPERACIONES DE LOGIN Y ADMIN 

def asegurar_admin_por_defecto(db: Session):
    # Si no hay ningún usuario activo en la base de datos (por ejemplo la primera vez que abro el programa),
    # creo un usuario "admin" por defecto para poder entrar al Login sin quedarme afuera.
    hay_activos = db.query(models.Usuario).filter(models.Usuario.activo == True).first()
    if not hay_activos:
        admin_existente = db.query(models.Usuario).filter(models.Usuario.email == "admin@sistema.com").first()
        if admin_existente:
            admin_existente.activo = True
            if not admin_existente.password:
                admin_existente.password = "admin123"
            db.commit()
        else:
            admin = models.Usuario(
                nombre="admin",
                email="admin@sistema.com",
                password="admin123",
                activo=True
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)

def autenticar_usuario(db: Session, identificador: str, password: str):
    # Esta función revisa si el usuario escribió bien su correo (o su nombre) y su contraseña.
    # También revisa que el usuario esté activo (que no haya sido eliminado).
    identificador = identificador.strip()
    usuario = db.query(models.Usuario).filter(
        models.Usuario.activo == True,
        (models.Usuario.email == identificador) | (models.Usuario.nombre == identificador)
    ).first()

    if usuario and usuario.password == password:
        return usuario
    return None

# OPERACIONES DE USUARIO 

def crear_usuario(db: Session, nombre: str, email: str, password: str = "1234"):
    # Aquí yo creo un usuario nuevo con los datos que me pasan (ahora también incluye su password).
    nuevo = models.Usuario(nombre=nombre.strip(), email=email.strip(), password=password)
    db.add(nuevo)       # Lo agrego a la base de datos.
    db.commit()         # Guardo los cambios. Me dijeron que esto es importante.
    db.refresh(nuevo)   # Actualizo el objeto para que tenga el ID que le tocó.
    return nuevo

def obtener_usuarios(db: Session):
    # Solo traigo los usuarios activos (los que no han sido "eliminados")
    # Yo no borro de verdad, solo marco activo=False, así que aquí filtro.
    return db.query(models.Usuario).filter(models.Usuario.activo == True).all()

def obtener_usuario_activo_por_id(db: Session, usuario_id: int):
    # Función para verificar que un usuario exista y NO esté eliminado antes de asignarle tareas.
    return db.query(models.Usuario).filter(
        models.Usuario.id == usuario_id,
        models.Usuario.activo == True
    ).first()

def eliminar_usuario(db: Session, usuario_id: int):
    # En vez de borrar el registro, solo lo marco como inactivo.
    # Esto me lo enseñaron y me pareció más seguro que borrar todo.
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if usuario:
        usuario.activo = False  # Aquí está el soft delete.
        # También desactivo todas sus tareas para que no queden colgando.
        db.query(models.Tarea).filter(models.Tarea.usuario_id == usuario_id).update({"activo": False})
        db.commit()  # Guardo los cambios.
    return usuario

#  OPERACIONES DE TAREA 
def crear_tarea(db: Session, titulo: str, descripcion: str, prioridad: int, usuario_id: int):
    # Primero verifico que el usuario dueño de la tarea exista y esté activo.
    # Antes SQLite dejaba guardar tareas con cualquier ID de usuario aunque no existiera o estuviera borrado.
    usuario = obtener_usuario_activo_por_id(db, usuario_id)
    if not usuario:
        raise ValueError(f"El usuario con ID {usuario_id} no existe o está inactivo.")

    # Aquí creo una tarea nueva. Le paso el título, la descripción, la prioridad y el ID del usuario.
    nueva = models.Tarea(titulo=titulo.strip(), descripcion=descripcion.strip(), prioridad=prioridad, usuario_id=usuario_id)
    db.add(nueva)       # La agrego a la base de datos.
    db.commit()         # Guardo los cambios.
    db.refresh(nueva)   # Actualizo para obtener el ID generado.
    return nueva

def obtener_tareas(db: Session):
    # Solo traigo las tareas activas.
    # Igual que con usuarios, las tareas eliminadas tienen activo=False.
    return db.query(models.Tarea).filter(models.Tarea.activo == True).all()

def eliminar_tarea(db: Session, tarea_id: int):
    # Marco la tarea como inactiva en lugar de borrarla.
    tarea = db.query(models.Tarea).filter(models.Tarea.id == tarea_id).first()
    if tarea:
        tarea.activo = False
        db.commit()
    return tarea

def obtener_tareas_por_usuario(db: Session, usuario_id: int):
    # Filtro por usuario y que la tarea esté activa.
    # Así solo me traigo las tareas que pertenecen a ese usuario y no están eliminadas.
    return db.query(models.Tarea).filter(
        models.Tarea.usuario_id == usuario_id,
        models.Tarea.activo == True
    ).all()

def obtener_resumen(db: Session):
    # Solo cuento tareas de usuarios activos y tareas activas.
    # Primero saco todos los usuarios activos.
    usuarios = db.query(models.Usuario).filter(models.Usuario.activo == True).all()
    resumen = []
    for u in usuarios:
        # Por cada usuario, cuento cuántas tareas activas tiene.
        cantidad = db.query(models.Tarea).filter(
            models.Tarea.usuario_id == u.id,
            models.Tarea.activo == True
        ).count()
        # Guardo una línea con el nombre y el total.
        resumen.append(f"Usuario: {u.nombre} | Total de tareas: {cantidad}")
    return resumen

#  OPERACIONES DE BACKUP (RESPALDOS) 

def crear_backup_db(prefijo: str = "backup"):
    # Esta función saca una copia exacta del archivo sistema.db y la guarda
    # en la carpeta "backups/" poniéndole la fecha y la hora en el nombre.
    if not os.path.exists(db_config.ruta_db):
        raise FileNotFoundError("Todavía no existe el archivo de base de datos sistema.db")

    if not os.path.exists(db_config.ruta_backups):
        os.makedirs(db_config.ruta_backups)

    fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"{prefijo}_{fecha_hora}.db"
    ruta_destino = os.path.join(db_config.ruta_backups, nombre_archivo)

    # Uso shutil.copy2 para copiar el archivo de base de datos completo.
    shutil.copy2(db_config.ruta_db, ruta_destino)
    return ruta_destino

def exportar_backup_legible(db: Session):
    # Además del archivo .db, esta función exporta los usuarios y tareas
    # a archivos JSON y CSV dentro de la carpeta "backups/" para poder abrirlos en Excel o bloc de notas.
    if not os.path.exists(db_config.ruta_backups):
        os.makedirs(db_config.ruta_backups)

    fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
    usuarios = db.query(models.Usuario).all()
    tareas = db.query(models.Tarea).all()

    # 1. Armo un diccionario con toda la información para guardarlo en JSON
    datos_json = {
        "fecha_respaldo": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "usuarios": [
            {
                "id": u.id,
                "nombre": u.nombre,
                "email": u.email,
                "activo": u.activo
            }
            for u in usuarios
        ],
        "tareas": [
            {
                "id": t.id,
                "titulo": t.titulo,
                "descripcion": t.descripcion,
                "prioridad": t.prioridad,
                "usuario_id": t.usuario_id,
                "activo": t.activo
            }
            for t in tareas
        ]
    }

    ruta_json = os.path.join(db_config.ruta_backups, f"respaldo_{fecha_hora}.json")
    with open(ruta_json, "w", encoding="utf-8") as f_json:
        json.dump(datos_json, f_json, indent=4, ensure_ascii=False)

    # 2. También guardo archivos CSV (uno para usuarios y otro para tareas)
    ruta_csv_usuarios = os.path.join(db_config.ruta_backups, f"usuarios_{fecha_hora}.csv")
    with open(ruta_csv_usuarios, "w", newline="", encoding="utf-8") as f_csv_u:
        writer = csv.writer(f_csv_u)
        writer.writerow(["id", "nombre", "email", "activo"])
        for u in usuarios:
            writer.writerow([u.id, u.nombre, u.email, u.activo])

    ruta_csv_tareas = os.path.join(db_config.ruta_backups, f"tareas_{fecha_hora}.csv")
    with open(ruta_csv_tareas, "w", newline="", encoding="utf-8") as f_csv_t:
        writer = csv.writer(f_csv_t)
        writer.writerow(["id", "titulo", "descripcion", "prioridad", "usuario_id", "activo"])
        for t in tareas:
            writer.writerow([t.id, t.titulo, t.descripcion, t.prioridad, t.usuario_id, t.activo])

    return ruta_json, ruta_csv_usuarios, ruta_csv_tareas