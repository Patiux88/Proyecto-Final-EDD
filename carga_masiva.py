"""
Carga masiva de archivos .cap, .im, .usr
"""
import os
import re


def cargar_capas(ruta_archivo, arbol_capas):
    """
    Parse .cap file and load layers into the BST.
    
    Format:
    id {
        fila, columna, color;
        ...
        fila columna, color;
    }
    """
    from estructuras.arbol_capas import Capa

    if not os.path.exists(ruta_archivo):
        print(f"   Archivo no encontrado: {ruta_archivo}")
        return 0

    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()

    # Remove comments (// ...)
    contenido = re.sub(r'//.*', '', contenido)

    count = 0
    errores = 0

    # Match each layer block: id { ... }
    bloques = re.findall(r'(\w+)\s*\{([^}]*)\}', contenido, re.DOTALL)

    for id_capa_raw, cuerpo in bloques:
        id_capa = id_capa_raw.strip()

        # Check if already exists
        if arbol_capas.buscar(id_capa):
            print(f"  Capa '{id_capa}' ya existe, se actualizará.")

        capa = Capa(id_capa)

        # Parse pixels: fila, columna, color  OR  fila columna, color
        # Normalize: remove semicolons and split by lines
        lineas = cuerpo.strip().split('\n')
        for linea in lineas:
            linea = linea.strip().rstrip(';').strip()
            if not linea:
                continue

            # Try: fila, columna, color  OR  fila columna, color
            # Accept comma or space as separator between fila and columna
            parts = re.split(r'[\s,]+', linea)
            parts = [p.strip() for p in parts if p.strip()]

            if len(parts) < 3:
                errores += 1
                continue

            try:
                fila = int(parts[0])
                columna = int(parts[1])
                color = parts[2].strip()
                if not color.startswith('#'):
                    color = '#' + color
                capa.agregar_pixel(fila, columna, color)
            except ValueError:
                errores += 1

        arbol_capas.insertar(capa)
        count += 1

    if errores:
        print(f"   {errores} línea(s) con error en {ruta_archivo}")
    return count


def cargar_imagenes(ruta_archivo, lista_imagenes, arbol_capas):
    """
    Parse .im file and load images into circular list.
    
    Format:
    id {
        id_capa;
        id_capa;
    }
    """
    from estructuras.lista_imagenes import Imagen

    if not os.path.exists(ruta_archivo):
        print(f"   Archivo no encontrado: {ruta_archivo}")
        return 0

    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()

    contenido = re.sub(r'//.*', '', contenido)
    count = 0

    bloques = re.findall(r'(\w+)\s*\{([^}]*)\}', contenido, re.DOTALL)

    for id_img_raw, cuerpo in bloques:
        id_img = id_img_raw.strip()

        # Tratar de convertirlo a int, de otra manera mantenerlo como sttinrg
        try:
            id_img_key = int(id_img)
        except ValueError:
            id_img_key = id_img

        imagen = Imagen(id_img_key)

        lineas = cuerpo.strip().split('\n')
        for linea in lineas:
            id_capa = linea.strip().rstrip(';').strip()
            if not id_capa:
                continue
            capa_ref = arbol_capas.buscar(id_capa)
            if capa_ref:
                imagen.agregar_capa(capa_ref)
            else:
                print(f"   Imagen '{id_img_key}': capa '{id_capa}' no encontrada en árbol.")

        lista_imagenes.insertar_ordenado(imagen)
        count += 1

    return count


def cargar_usuarios(ruta_archivo, arbol_usuarios, lista_imagenes):
    """
    Parse .usr file.
    
    Format:
    nombre:id_img1,id_img2,...;
    """
    from estructuras.arbol_usuarios import Usuario

    if not os.path.exists(ruta_archivo):
        print(f"   Archivo no encontrado: {ruta_archivo}")
        return 0

    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()

    contenido = re.sub(r'//.*', '', contenido)
    count = 0

    # Separar por ; y procesar cada entrada
    entradas = contenido.split(';')
    for entrada in entradas:
        entrada = entrada.strip()
        if not entrada:
            continue

        if ':' not in entrada:
            continue

        partes = entrada.split(':', 1)
        nombre = partes[0].strip()
        if not nombre:
            continue

        usuario = Usuario(nombre)
        ids_str = partes[1].strip() if len(partes) > 1 else ''

        if ids_str:
            ids = [x.strip() for x in ids_str.split(',') if x.strip()]
            for id_img_raw in ids:
                try:
                    id_img = int(id_img_raw)
                except ValueError:
                    id_img = id_img_raw

                # Verify image exists
                if lista_imagenes.buscar(id_img):
                    usuario.agregar_imagen(id_img)
                else:
                    print(f" Usuario '{nombre}': imagen '{id_img}' no encontrada.")

        arbol_usuarios.insertar(usuario)
        count += 1

    return count
