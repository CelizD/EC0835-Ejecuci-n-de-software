# crud.py

# Hola, yo soy principiante y este archivo lo hice para poner todas las funciones
# que hablan con la base de datos. No entiendo todo, pero aquí voy practicando.
from sqlalchemy.orm import Session
import models

# ---------- OPERACIONES DE USUARIO ----------

def crear_usuario(db: Session, nombre: str, email: str):
    # Aquí yo creo un usuario nuevo con los datos que me pasan.
    nuevo = models.Usuario(nombre=nombre, email=email)
    db.add(nuevo)       # Lo agrego a la base de datos.
    db.commit()         # Guardo los cambios. Me dijeron que esto es importante.
    db.refresh(nuevo)   # Actualizo el objeto para que tenga el ID que le tocó.
    return nuevo

def obtener_usuarios(db: Session):
    # CAMBIO: Solo traigo los usuarios activos (los que no han sido "eliminados")
    # Yo no borro de verdad, solo marco activo=False, así que aquí filtro.
    return db.query(models.Usuario).filter(models.Usuario.activo == True).all()

def eliminar_usuario(db: Session, usuario_id: int):
    # SOFT DELETE: En vez de borrar el registro, solo lo marco como inactivo.
    # Esto me lo enseñaron y me pareció más seguro que borrar todo.
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if usuario:
        usuario.activo = False  # Aquí está el soft delete.
        # También desactivo todas sus tareas para que no queden colgando.
        db.query(models.Tarea).filter(models.Tarea.usuario_id == usuario_id).update({"activo": False})
        db.commit()  # Guardo los cambios.
    return usuario

# ---------- OPERACIONES DE TAREA ----------

def crear_tarea(db: Session, titulo: str, descripcion: str, prioridad: int, usuario_id: int):
    # Aquí creo una tarea nueva. Le paso el título, la descripción, la prioridad y el ID del usuario.
    nueva = models.Tarea(titulo=titulo, descripcion=descripcion, prioridad=prioridad, usuario_id=usuario_id)
    db.add(nueva)       # La agrego a la base de datos.
    db.commit()         # Guardo los cambios.
    db.refresh(nueva)   # Actualizo para obtener el ID generado.
    return nueva

def obtener_tareas(db: Session):
    # CAMBIO: Solo traigo las tareas activas.
    # Igual que con usuarios, las tareas eliminadas tienen activo=False.
    return db.query(models.Tarea).filter(models.Tarea.activo == True).all()

def eliminar_tarea(db: Session, tarea_id: int):
    # SOFT DELETE: Marco la tarea como inactiva en lugar de borrarla.
    tarea = db.query(models.Tarea).filter(models.Tarea.id == tarea_id).first()
    if tarea:
        tarea.activo = False
        db.commit()
    return tarea

def obtener_tareas_por_usuario(db: Session, usuario_id: int):
    # CAMBIO: Filtro por usuario y que la tarea esté activa.
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