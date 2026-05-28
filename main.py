"""
Generador de Imágenes por Capas
Estructuras de Datos - Aplicación de consola
"""

import os
import sys

# Arreglar direccion para mis imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from estructuras.arbol_capas import ArbolCapas, Capa
from estructuras.lista_imagenes import ListaCircularImagenes, Imagen
from estructuras.arbol_usuarios import ArbolUsuarios, Usuario
from carga_masiva import cargar_capas, cargar_imagenes, cargar_usuarios
import reportes


# Global state


arbol_capas = ArbolCapas()
lista_imagenes = ListaCircularImagenes()
arbol_usuarios = ArbolUsuarios()


# UI Helpers


LINEA = "*" * 60
LINEA_SIMPLE = "*" * 60

def limpiar():
    os.system('cls' if sys.platform.startswith('win') else 'clear')

def pausar():
    input("\n  Presione Enter para continuar...")

def encabezado(titulo):
    print()
    print(LINEA)
    print(f"  {titulo}")
    print(LINEA)

def pedir_opcion(maximo):
    try:
        op = input("\n  Seleccione una opción: ").strip()
        val = int(op)
        if 1 <= val <= maximo:
            return val
        print("  Opción fuera de rango.")
        return None
    except ValueError:
        print("  Ingrese un número válido.")
        return None


# Carga Masiva


def menu_carga_masiva():
    while True:
        encabezado("Carga Masiva")
        print("  1. Cargar Capas         (.cap)")
        print("  2. Cargar Imágenes      (.im)")
        print("  3. Cargar Usuarios      (.usr)")
        print("  4. Carga Completa       (cap → im → usr)")
        print("  5. Volver al menú principal")

        op = pedir_opcion(5)
        if op == 1:
            ruta = input("  Ruta del archivo .cap: ").strip()
            n = cargar_capas(ruta, arbol_capas)
            print(f"  {n} capa(s) cargada(s).")
            pausar()
        elif op == 2:
            ruta = input("  Ruta del archivo .im: ").strip()
            n = cargar_imagenes(ruta, lista_imagenes, arbol_capas)
            print(f"  {n} imagen(es) cargada(s).")
            pausar()
        elif op == 3:
            ruta = input("  Ruta del archivo .usr: ").strip()
            n = cargar_usuarios(ruta, arbol_usuarios, lista_imagenes)
            print(f"  {n} usuario(s) cargado(s).")
            pausar()
        elif op == 4:
            ruta_cap = input("  Ruta del archivo .cap: ").strip()
            ruta_im = input("  Ruta del archivo .im:  ").strip()
            ruta_usr = input("  Ruta del archivo .usr: ").strip()
            n1 = cargar_capas(ruta_cap, arbol_capas)
            n2 = cargar_imagenes(ruta_im, lista_imagenes, arbol_capas)
            n3 = cargar_usuarios(ruta_usr, arbol_usuarios, lista_imagenes)
            print(f"\n  Cargados: {n1} capa(s), {n2} imagen(es), {n3} usuario(s).")
            pausar()
        elif op == 5:
            break


# Generación de Imágenes


def menu_generacion():
    while True:
        encabezado("Generación de imagenes")
        print("  1. Por recorrido del árbol (limitado)")
        print("  2. Por lista de imágenes")
        print("  3. Por capa individual")
        print("  4. Por usuario")
        print("  5. Volver al menú principal")

        op = pedir_opcion(5)
        if op == 1:
            _generar_por_recorrido()
        elif op == 2:
            _generar_por_imagen()
        elif op == 3:
            _generar_por_capa()
        elif op == 4:
            _generar_por_usuario()
        elif op == 5:
            break

def _generar_por_recorrido():
    encabezado("Generación por recorrido")
    if arbol_capas.esta_vacio():
        print("  El árbol de capas está vacío.")
        pausar()
        return

    print("  Tipo de recorrido:")
    print("    1. Inorden")
    print("    2. Preorden")
    print("    3. Postorden")
    tipo = pedir_opcion(3)
    if not tipo:
        return

    try:
        n = int(input("  Número de capas a usar: ").strip())
    except ValueError:
        print("  Número inválido.")
        pausar()
        return

    if tipo == 1:
        todas = arbol_capas.inorden()
        nombre_recorrido = "inorden"
    elif tipo == 2:
        todas = arbol_capas.preorden()
        nombre_recorrido = "preorden"
    else:
        todas = arbol_capas.postorden()
        nombre_recorrido = "postorden"

    capas_sel = todas[:n]
    if not capas_sel:
        print("  No hay capas disponibles.")
        pausar()
        return

    print(f"\n  Capas en orden {nombre_recorrido}: {[c.id_capa for c in capas_sel]}")
    nombre = f"recorrido_{nombre_recorrido}_{n}capas"
    ruta = reportes.generar_imagen_png(capas_sel, nombre)
    reportes.abrir_imagen(ruta)
    pausar()

def _generar_por_imagen():
    encabezado("Generación por imagen")
    if lista_imagenes.esta_vacia():
        print("  No hay imágenes registradas.")
        pausar()
        return

    # Mostrar imagenes disponibles
    imagenes = lista_imagenes.obtener_todas()
    print("  Imágenes disponibles:")
    for img in imagenes:
        capas = [c.id_capa for c in img.lista_capas.obtener_capas_en_orden()]
        print(f"    ID: {img.id_imagen}  Capas: {capas}")

    id_raw = input("\n  ID de la imagen: ").strip()
    try:
        id_img = int(id_raw)
    except ValueError:
        id_img = id_raw

    imagen = lista_imagenes.buscar(id_img)
    if not imagen:
        print(f"  Imagen '{id_img}' no encontrada.")
        pausar()
        return

    capas = imagen.lista_capas.obtener_capas_en_orden()
    if not capas:
        print("  Esta imagen no tiene capas; se generará pixel negro.")
        from estructuras.arbol_capas import Capa
        capa_vacia = Capa("vacia")
        capa_vacia.agregar_pixel(0, 0, "#000000")
        capas = [capa_vacia]

    nombre = f"imagen_{id_img}"
    ruta = reportes.generar_imagen_png(capas, nombre)
    reportes.abrir_imagen(ruta)
    pausar()

def _generar_por_capa():
    encabezado("Generación por capa")
    if arbol_capas.esta_vacio():
        print("  El árbol de capas está vacío.")
        pausar()
        return

    capas_disponibles = [c.id_capa for c in arbol_capas.inorden()]
    print(f"  Capas disponibles: {capas_disponibles}")
    id_capa = input("  ID de la capa: ").strip()

    capa = arbol_capas.buscar(id_capa)
    if not capa:
        print(f"  Capa '{id_capa}' no encontrada.")
        pausar()
        return

    ruta = reportes.generar_imagen_png([capa], f"capa_{id_capa}")
    reportes.abrir_imagen(ruta)
    pausar()

def _generar_por_usuario():
    encabezado("Generación por usuario")
    if arbol_usuarios.esta_vacio():
        print("  No hay usuarios registrados.")
        pausar()
        return

    usuarios = arbol_usuarios.todos()
    print("  Usuarios disponibles:")
    for u in usuarios:
        print(f"    {u.nombre}  Imágenes: {u.lista_imagenes.obtener_todas()}")

    nombre = input("  Nombre del usuario: ").strip()
    usuario = arbol_usuarios.buscar(nombre)
    if not usuario:
        print(f"  Usuario '{nombre}' no encontrado.")
        pausar()
        return

    ids = usuario.lista_imagenes.obtener_todas()
    if not ids:
        print("  Este usuario no tiene imágenes.")
        pausar()
        return

    print(f"  Imágenes de {nombre}: {ids}")
    id_raw = input("  ID de imagen a generar: ").strip()
    try:
        id_img = int(id_raw)
    except ValueError:
        id_img = id_raw

    if not usuario.lista_imagenes.contiene(id_img):
        print(f"  El usuario no tiene la imagen '{id_img}'.")
        pausar()
        return

    imagen = lista_imagenes.buscar(id_img)
    if not imagen:
        print(f"  Imagen '{id_img}' no encontrada en el sistema.")
        pausar()
        return

    capas = imagen.lista_capas.obtener_capas_en_orden()
    if not capas:
        capas_temp = Capa("vacia")
        capas_temp.agregar_pixel(0, 0, "#000000")
        capas = [capas_temp]

    ruta = reportes.generar_imagen_png(capas, f"usuario_{nombre}_img_{id_img}")
    reportes.abrir_imagen(ruta)
    pausar()

# CRUD Usuarios


def menu_crud_usuarios():
    while True:
        encabezado("CRUD - Usuarios")
        print("  1. Agregar usuario")
        print("  2. Eliminar usuario")
        print("  3. Modificar usuario (renombrar)")
        print("  4. Listar usuarios")
        print("  5. Volver")

        op = pedir_opcion(5)
        if op == 1:
            nombre = input("  Nombre del nuevo usuario: ").strip()
            if not nombre:
                print("  Nombre vacío.")
            elif arbol_usuarios.buscar(nombre):
                print(f"  El usuario '{nombre}' ya existe.")
            else:
                arbol_usuarios.insertar(Usuario(nombre))
                print(f"  Usuario '{nombre}' agregado.")
            pausar()
        elif op == 2:
            nombre = input("  Nombre del usuario a eliminar: ").strip()
            if arbol_usuarios.buscar(nombre):
                arbol_usuarios.eliminar(nombre)
                print(f"  Usuario '{nombre}' eliminado.")
            else:
                print(f"  Usuario '{nombre}' no encontrado.")
            pausar()
        elif op == 3:
            nombre_viejo = input("  Nombre actual del usuario: ").strip()
            nombre_nuevo = input("  Nuevo nombre: ").strip()
            if not nombre_nuevo:
                print("  Nombre nuevo vacío.")
            elif not arbol_usuarios.buscar(nombre_viejo):
                print(f"  Usuario '{nombre_viejo}' no encontrado.")
            elif arbol_usuarios.buscar(nombre_nuevo):
                print(f"  El nombre '{nombre_nuevo}' ya existe.")
            else:
                arbol_usuarios.modificar(nombre_viejo, nombre_nuevo)
                print(f"  Usuario renombrado a '{nombre_nuevo}'.")
            pausar()
        elif op == 4:
            usuarios = arbol_usuarios.todos()
            if not usuarios:
                print("  No hay usuarios registrados.")
            else:
                print(f"  {'Nombre':<20} {'Imágenes'}")
                print(LINEA_SIMPLE)
                for u in usuarios:
                    imgs = u.lista_imagenes.obtener_todas()
                    print(f"  {u.nombre:<20} {imgs}")
            pausar()
        elif op == 5:
            break


# CRUD Imágenes


def menu_crud_imagenes():
    while True:
        encabezado("CRUD - Imágenes")
        print("  1. Agregar imagen a usuario")
        print("  2. Eliminar imagen")
        print("  3. Listar imágenes")
        print("  4. Agregar capa a imagen")
        print("  5. Volver")

        op = pedir_opcion(5)
        if op == 1:
            _agregar_imagen_usuario()
        elif op == 2:
            _eliminar_imagen()
        elif op == 3:
            _listar_imagenes()
        elif op == 4:
            _agregar_capa_a_imagen()
        elif op == 5:
            break

def _agregar_imagen_usuario():
    encabezado("Agregar imagen a usuario")
    nombre = input("  Nombre del usuario: ").strip()
    usuario = arbol_usuarios.buscar(nombre)
    if not usuario:
        print(f"  Usuario '{nombre}' no encontrado.")
        pausar()
        return

    id_raw = input("  ID de la nueva imagen: ").strip()
    try:
        id_img = int(id_raw)
    except ValueError:
        id_img = id_raw

    if lista_imagenes.buscar(id_img):
        print(f"  Ya existe una imagen con ID '{id_img}'.")
        pausar()
        return

    nueva = Imagen(id_img)
    lista_imagenes.insertar_ordenado(nueva)
    usuario.agregar_imagen(id_img)
    print(f"  Imagen '{id_img}' creada y asignada a '{nombre}'.")

    # Añadir capas opcionales pa la imagen
    while True:
        agregar = input("  ¿Agregar capa a esta imagen? (s/n): ").strip().lower()
        if agregar != 's':
            break
        capas_disponibles = [c.id_capa for c in arbol_capas.inorden()]
        print(f"  Capas disponibles: {capas_disponibles}")
        id_capa = input("  ID de la capa: ").strip()
        capa_ref = arbol_capas.buscar(id_capa)
        if capa_ref:
            nueva.agregar_capa(capa_ref)
            print(f"  Capa '{id_capa}' agregada.")
        else:
            print(f"  Capa '{id_capa}' no encontrada.")
    pausar()

def _eliminar_imagen():
    encabezado("Eliminar imagen")
    nombre = input("  Nombre del usuario propietario: ").strip()
    usuario = arbol_usuarios.buscar(nombre)
    if not usuario:
        print(f"  Usuario '{nombre}' no encontrado.")
        pausar()
        return

    ids = usuario.lista_imagenes.obtener_todas()
    print(f"  Imágenes de {nombre}: {ids}")
    id_raw = input("  ID de imagen a eliminar: ").strip()
    try:
        id_img = int(id_raw)
    except ValueError:
        id_img = id_raw

    if not usuario.lista_imagenes.contiene(id_img):
        print(f"  El usuario no posee la imagen '{id_img}'.")
        pausar()
        return

    usuario.eliminar_imagen(id_img)
    lista_imagenes.eliminar(id_img)
    print(f"  Imagen '{id_img}' eliminada de la lista y del usuario '{nombre}'.")
    pausar()

def _listar_imagenes():
    encabezado("Lista de imágenes")
    imagenes = lista_imagenes.obtener_todas()
    if not imagenes:
        print("  No hay imágenes registradas.")
    else:
        for img in imagenes:
            capas = [c.id_capa for c in img.lista_capas.obtener_capas_en_orden()]
            print(f"  ID: {img.id_imagen:<8} Capas: {capas}")
    pausar()

def _agregar_capa_a_imagen():
    encabezado("Agregar capa a imagen")
    imagenes = lista_imagenes.obtener_todas()
    if not imagenes:
        print("  No hay imágenes.")
        pausar()
        return

    ids_imagenes = [str(img.id_imagen) for img in imagenes]
    print(f"  Imágenes disponibles: {ids_imagenes}")
    id_raw = input("  ID de la imagen: ").strip()
    try:
        id_img = int(id_raw)
    except ValueError:
        id_img = id_raw

    imagen = lista_imagenes.buscar(id_img)
    if not imagen:
        print(f"  Imagen '{id_img}' no encontrada.")
        pausar()
        return

    capas_disponibles = [c.id_capa for c in arbol_capas.inorden()]
    print(f"  Capas disponibles: {capas_disponibles}")
    id_capa = input("  ID de la capa: ").strip()
    capa_ref = arbol_capas.buscar(id_capa)
    if not capa_ref:
        print(f"  Capa '{id_capa}' no encontrada.")
    elif imagen.lista_capas.contiene(id_capa):
        print(f"  La imagen ya contiene la capa '{id_capa}'.")
    else:
        imagen.agregar_capa(capa_ref)
        print(f"  Capa '{id_capa}' agregada a imagen '{id_img}'.")
    pausar()


# Reportes / Graficar memoria

def menu_reportes():
    while True:
        encabezado("Reportes - Estado de memoria")
        print("  1. Ver lista de imágenes (lista circular + capas)")
        print("  2. Ver árbol de capas (ABB)")
        print("  3. Ver detalle de capa (matriz dispersa)")
        print("  4. Ver imagen y árbol de capas (punteros)")
        print("  5. Ver árbol de usuarios")
        print("  6. Volver")

        op = pedir_opcion(6)
        if op == 1:
            encabezado("Lista circular de imágenes")
            ruta = reportes.graficar_lista_imagenes(lista_imagenes)
            reportes.abrir_imagen(ruta)
            pausar()
        elif op == 2:
            encabezado("Árbol de capas")
            if arbol_capas.esta_vacio():
                print("  El árbol está vacío.")
            else:
                ruta = reportes.graficar_arbol_capas(arbol_capas)
                reportes.abrir_imagen(ruta)
            pausar()
        elif op == 3:
            encabezado("Detalle de capa")
            if arbol_capas.esta_vacio():
                print("  El árbol está vacío.")
                pausar()
                continue
            capas_disponibles = [c.id_capa for c in arbol_capas.inorden()]
            print(f"  Capas disponibles: {capas_disponibles}")
            id_capa = input("  ID de la capa: ").strip()
            capa = arbol_capas.buscar(id_capa)
            if capa:
                ruta = reportes.graficar_capa(capa)
                reportes.abrir_imagen(ruta)
            else:
                print(f"  Capa '{id_capa}' no encontrada.")
            pausar()
        elif op == 4:
            encabezado("Imagen + Árbol de capas")
            imagenes = lista_imagenes.obtener_todas()
            if not imagenes:
                print("  No hay imágenes.")
                pausar()
                continue
            ids = [str(img.id_imagen) for img in imagenes]
            print(f"  Imágenes disponibles: {ids}")
            id_raw = input("  ID de imagen: ").strip()
            try:
                id_img = int(id_raw)
            except ValueError:
                id_img = id_raw
            imagen = lista_imagenes.buscar(id_img)
            if imagen:
                ruta = reportes.graficar_imagen_y_arbol(imagen, arbol_capas)
                reportes.abrir_imagen(ruta)
            else:
                print(f"  Imagen '{id_img}' no encontrada.")
            pausar()
        elif op == 5:
            encabezado("Árbol de usuarios")
            if arbol_usuarios.esta_vacio():
                print("  No hay usuarios.")
            else:
                ruta = reportes.graficar_arbol_usuarios(arbol_usuarios, lista_imagenes)
                reportes.abrir_imagen(ruta)
            pausar()
        elif op == 6:
            break


# Capas manual

def menu_capas():
    while True:
        encabezado("Gestión de capas")
        print("  1. Agregar capa manualmente")
        print("  2. Agregar píxel a capa")
        print("  3. Listar capas")
        print("  4. Eliminar capa")
        print("  5. Volver")

        op = pedir_opcion(5)
        if op == 1:
            id_capa = input("  ID de la nueva capa: ").strip()
            if arbol_capas.buscar(id_capa):
                print(f"  La capa '{id_capa}' ya existe.")
            else:
                arbol_capas.insertar(Capa(id_capa))
                print(f"  Capa '{id_capa}' creada.")
            pausar()
        elif op == 2:
            capas_disponibles = [c.id_capa for c in arbol_capas.inorden()]
            if not capas_disponibles:
                print("  No hay capas.")
                pausar()
                continue
            print(f"  Capas: {capas_disponibles}")
            id_capa = input("  ID de la capa: ").strip()
            capa = arbol_capas.buscar(id_capa)
            if not capa:
                print(f"  Capa '{id_capa}' no encontrada.")
                pausar()
                continue
            try:
                fila = int(input("  Fila: ").strip())
                columna = int(input("  Columna: ").strip())
                color = input("  Color (hex, ej: #ff0000): ").strip()
                if not color.startswith('#'):
                    color = '#' + color
                capa.agregar_pixel(fila, columna, color)
                print("  Píxel agregado.")
            except ValueError:
                print("  Datos inválidos.")
            pausar()
        elif op == 3:
            capas = arbol_capas.inorden()
            if not capas:
                print("  No hay capas.")
            else:
                print(f"  {'ID':<15} {'Píxeles'}")
                print(LINEA_SIMPLE)
                for c in capas:
                    n = len(c.matriz.obtener_todos_pixeles())
                    print(f"  {c.id_capa:<15} {n}")
            pausar()
        elif op == 4:
            capas = [c.id_capa for c in arbol_capas.inorden()]
            print(f"  Capas: {capas}")
            id_capa = input("  ID a eliminar: ").strip()
            if arbol_capas.buscar(id_capa):
                arbol_capas.eliminar(id_capa)
                print(f"  Capa '{id_capa}' eliminada.")
            else:
                print(f"  Capa '{id_capa}' no encontrada.")
            pausar()
        elif op == 5:
            break

# Menu principal


def menu_principal():
    while True:
        limpiar()
        print()
        print("Generador de imágenes")
        print("Proyecto Final EDD")
        print()
        print("  1. Carga Masiva")
        print("  2. Generación de Imágenes")
        print("  3. CRUD Usuarios")
        print("  4. CRUD Imágenes")
        print("  5. Gestión de Capas")
        print("  6. Reportes / Estado de Memoria")
        print("  7. Salir")
        print()

        op = pedir_opcion(7)
        if op == 1:
            menu_carga_masiva()
        elif op == 2:
            menu_generacion()
        elif op == 3:
            menu_crud_usuarios()
        elif op == 4:
            menu_crud_imagenes()
        elif op == 5:
            menu_capas()
        elif op == 6:
            menu_reportes()
        elif op == 7:
            print("\n  Saliendo del sistema...\n")
            sys.exit(0)



if __name__ == "__main__":
    menu_principal()
