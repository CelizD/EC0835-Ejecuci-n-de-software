# crud.py
# En este archivo pongo todas las funciones que hablan con la base de datos.
from sqlalchemy.orm import Session
import models

# ---------- OPERACIONES DE USUARIO ----------

def crear_usuario(db: Session, nombre: str, email: str):
    nuevo = models.Usuario(nombre=nombre, email=email)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

def obtener_usuarios(db: Session):
    # CAMBIO: Solo traigo los usuarios activos (los que no han sido "eliminados")
    return db.query(models.Usuario).filter(models.Usuario.activo == True).all()

def eliminar_usuario(db: Session, usuario_id: int):
    # SOFT DELETE: En vez de borrar el registro, solo lo marco como inactivo
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if usuario:
        usuario.activo = False  # Aquí está el soft delete
        # También desactivo todas sus tareas para que no queden colgando
        db.query(models.Tarea).filter(models.Tarea.usuario_id == usuario_id).update({"activo": False})
        db.commit()
    return usuario

# ---------- OPERACIONES DE TAREA ----------

def crear_tarea(db: Session, titulo: str, descripcion: str, prioridad: int, usuario_id: int):
    nueva = models.Tarea(titulo=titulo, descripcion=descripcion, prioridad=prioridad, usuario_id=usuario_id)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

def obtener_tareas(db: Session):
    # CAMBIO: Solo traigo las tareas activas
    return db.query(models.Tarea).filter(models.Tarea.activo == True).all()

def eliminar_tarea(db: Session, tarea_id: int):
    # SOFT DELETE: Marco la tarea como inactiva en lugar de borrarla
    tarea = db.query(models.Tarea).filter(models.Tarea.id == tarea_id).first()
    if tarea:
        tarea.activo = False
        db.commit()
    return tarea

def obtener_tareas_por_usuario(db: Session, usuario_id: int):
    # CAMBIO: Filtro por usuario y que la tarea esté activa
    return db.query(models.Tarea).filter(
        models.Tarea.usuario_id == usuario_id,
        models.Tarea.activo == True
    ).all()

def obtener_resumen(db: Session):
    # Solo cuento tareas de usuarios activos y tareas activas
    usuarios = db.query(models.Usuario).filter(models.Usuario.activo == True).all()
    resumen = []
    for u in usuarios:
        cantidad = db.query(models.Tarea).filter(
            models.Tarea.usuario_id == u.id,
            models.Tarea.activo == True
        ).count()
        resumen.append(f"Usuario: {u.nombre} | Total de tareas: {cantidad}")
    return resumen