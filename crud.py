# crud.py
# En este archivo pongo todas las funciones que hablan con la base de datos.
# La idea es no revolver esto con la interfaz, así el código se ve más ordenado.
from sqlalchemy.orm import Session
import models   # Importo mis clases (Usuario y Tarea) para poder usarlas aquí

# ---------- OPERACIONES DE USUARIO ----------

# Esta función la hago para guardar un usuario nuevo en la base de datos
def crear_usuario(db: Session, nombre: str, email: str):
    # Creo un objeto de tipo Usuario con los datos que me pasan
    nuevo = models.Usuario(nombre=nombre, email=email)
    db.add(nuevo)        # Lo agrego a la sesión
    db.commit()          # Guardo los cambios en la base de datos
    db.refresh(nuevo)    # Lo refresco para que traiga el ID que le asignó SQLite
    return nuevo         # Regreso el usuario ya creado

# Esta la hago para traer TODOS los usuarios de la base de datos
def obtener_usuarios(db: Session):
    # Uso .all() para que me devuelva una lista con todos los registros
    return db.query(models.Usuario).all()

# Esta la hago para borrar un usuario por su ID
def eliminar_usuario(db: Session, usuario_id: int):
    # Primero busco al usuario con ese ID
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if usuario:
        # Primero borro sus tareas para no dejar registros "huérfanos" (sin dueño)
        db.query(models.Tarea).filter(models.Tarea.usuario_id == usuario_id).delete()
        # Ahora sí borro al usuario
        db.delete(usuario)
        db.commit()  # Guardo los cambios
    return usuario   # Regreso el usuario que borré (o None si no existía)

# ---------- OPERACIONES DE TAREA ----------

# Esta función la hago para guardar una tarea nueva
def crear_tarea(db: Session, titulo: str, descripcion: str, prioridad: int, usuario_id: int):
    # Creo el objeto Tarea con todos los datos que me pasan
    nueva = models.Tarea(titulo=titulo, descripcion=descripcion, prioridad=prioridad, usuario_id=usuario_id)
    db.add(nueva)        # La agrego a la sesión
    db.commit()          # Guardo en la base de datos
    db.refresh(nueva)    # La refresco para obtener su ID
    return nueva         # Regreso la tarea creada

# Esta la hago para traer TODAS las tareas
def obtener_tareas(db: Session):
    return db.query(models.Tarea).all()

# Esta la hago para borrar una tarea por su ID
def eliminar_tarea(db: Session, tarea_id: int):
    # Busco la tarea con ese ID
    tarea = db.query(models.Tarea).filter(models.Tarea.id == tarea_id).first()
    if tarea:
        db.delete(tarea)   # La borro
        db.commit()        # Guardo el cambio
    return tarea           # Regreso la tarea borrada (o None)

# Esta la hago para traer solo las tareas de un usuario específico
def obtener_tareas_por_usuario(db: Session, usuario_id: int):
    # Filtro las tareas donde el usuario_id coincida con el que me pasan
    return db.query(models.Tarea).filter(models.Tarea.usuario_id == usuario_id).all()

# Esta la hago para el botón de "Resumen por Usuario"
def obtener_resumen(db: Session):
    # Primero traigo a todos los usuarios
    usuarios = db.query(models.Usuario).all()
    resumen = []   # Creo una lista vacía donde voy a ir guardando los textos
    for u in usuarios:
        # Por cada usuario, cuento cuántas tareas tiene
        cantidad = db.query(models.Tarea).filter(models.Tarea.usuario_id == u.id).count()
        # Armo un texto bonito y lo agrego a la lista
        resumen.append(f"Usuario: {u.nombre} | Total de tareas: {cantidad}")
    return resumen   # Regreso la lista con todos los resúmenes