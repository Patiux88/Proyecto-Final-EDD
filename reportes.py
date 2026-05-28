"""
Generación de reportes con Graphviz
Genera archivos .dot y los convierte a PNG
"""
import os
import subprocess
import sys

SALIDA_DIR = "reportes"


def _asegurar_dir():
    if not os.path.exists(SALIDA_DIR):
        os.makedirs(SALIDA_DIR)


def _ejecutar_dot(dot_contenido, nombre_archivo):
    """Write .dot file and render to PNG, return PNG path"""
    _asegurar_dir()
    ruta_dot = os.path.join(SALIDA_DIR, nombre_archivo + ".dot")
    ruta_png = os.path.join(SALIDA_DIR, nombre_archivo + ".png")

    with open(ruta_dot, 'w', encoding='utf-8') as f:
        f.write(dot_contenido)

    try:
        resultado = subprocess.run(
            ["dot", "-Tpng", ruta_dot, "-o", ruta_png],
            capture_output=True, text=True
        )
        if resultado.returncode != 0:
            print(f"  [ERROR Graphviz] {resultado.stderr}")
            return None
        return ruta_png
    except FileNotFoundError:
        print("  [ERROR] Graphviz (dot) no encontrado. Instale Graphviz.")
        return None


# ── 1. Matrix report (capa detail) ───────────────────────────────────────────

def graficar_capa(capa):
    """
    Sparse matrix exactly like the reference image:
    - 'matriz' node top-left, arrow right to first column header
    - Column headers in a horizontal row (bidirectional arrows between them)
    - 'matriz' also points down to first row header
    - Row headers in a vertical column (bidirectional arrows between them)
    - Pixel nodes shown as plain box with the hex color value
    - Row pixels: bidirectional arrows left<->right
    - Column pixels: bidirectional arrows up<->down
    - Each row header points right to its first pixel
    - Each col header points down to its first pixel
    """
    matriz = capa.matriz

    # Collect column and row indices present
    col_indices = []
    enc_col = matriz.cabeza_columnas
    while enc_col:
        col_indices.append(enc_col.indice)
        enc_col = enc_col.siguiente

    fila_indices = []
    enc_fila = matriz.cabeza_filas
    while enc_fila:
        fila_indices.append(enc_fila.indice)
        enc_fila = enc_fila.siguiente

    # Build pixel dict for easy lookup
    pixeles = {}  # (fila, col) -> color
    enc_fila = matriz.cabeza_filas
    while enc_fila:
        actual = enc_fila.acceso
        while actual:
            pixeles[(actual.fila, actual.columna)] = actual.color
            actual = actual.derecha
        enc_fila = enc_fila.siguiente

    lines = []
    lines.append('digraph MatrizDispersa {')
    lines.append('  graph [splines=false nodesep=0.4 ranksep=0.5];')
    lines.append(f'  label="Matriz Dispersa - Capa: {capa.id_capa}";')
    lines.append('  labelloc=t; fontsize=13;')
    lines.append('  node [shape=box fontname="Arial" fontsize=10 width=0.6 height=0.35 fixedsize=true];')
    lines.append('  edge [arrowsize=0.6];')

    # 'matriz' header node
    lines.append('  matriz [label="matriz" width=0.8];')

    # Column header nodes
    for c in col_indices:
        lines.append(f'  col_{c} [label="{c}"];')

    # Row header nodes
    for f in fila_indices:
        lines.append(f'  fila_{f} [label="{f}"];')

    # Pixel nodes (plain box, label = hex color)
    for (f, c), color in pixeles.items():
        lines.append(f'  px_{f}_{c} [label="{color}"];')

    # ── Ranks to force layout ──────────────────────────────────────────────
    # Top row: matriz + all column headers on same rank
    top_nodes = ['matriz'] + [f'col_{c}' for c in col_indices]
    lines.append('  { rank=same; ' + '; '.join(top_nodes) + '; }')

    # Each data row: row_header + its pixels on the same rank
    for f in fila_indices:
        row_px = [f'px_{f}_{c}' for c in col_indices if (f, c) in pixeles]
        if row_px:
            lines.append(f'  {{ rank=same; fila_{f}; ' + '; '.join(row_px) + '; }')

    # ── Edges ──────────────────────────────────────────────────────────────

    # matriz -> first col header (right)
    if col_indices:
        lines.append(f'  matriz -> col_{col_indices[0]};')

    # col headers: bidirectional chain
    for i in range(len(col_indices) - 1):
        a, b = f'col_{col_indices[i]}', f'col_{col_indices[i+1]}'
        lines.append(f'  {a} -> {b};')
        lines.append(f'  {b} -> {a};')

    # matriz -> first row header (down)
    if fila_indices:
        lines.append(f'  matriz -> fila_{fila_indices[0]};')

    # row headers: bidirectional chain
    for i in range(len(fila_indices) - 1):
        a, b = f'fila_{fila_indices[i]}', f'fila_{fila_indices[i+1]}'
        lines.append(f'  {a} -> {b};')
        lines.append(f'  {b} -> {a};')

    # Each row header -> its first pixel (right)
    for f in fila_indices:
        row_cols = [c for c in col_indices if (f, c) in pixeles]
        if row_cols:
            lines.append(f'  fila_{f} -> px_{f}_{row_cols[0]};')
            lines.append(f'  px_{f}_{row_cols[0]} -> fila_{f};')

    # Pixels within each row: bidirectional left<->right
    for f in fila_indices:
        row_cols = [c for c in col_indices if (f, c) in pixeles]
        for i in range(len(row_cols) - 1):
            a = f'px_{f}_{row_cols[i]}'
            b = f'px_{f}_{row_cols[i+1]}'
            lines.append(f'  {a} -> {b};')
            lines.append(f'  {b} -> {a};')

    # Each col header -> its first pixel (down)
    for c in col_indices:
        col_filas = [f for f in fila_indices if (f, c) in pixeles]
        if col_filas:
            lines.append(f'  col_{c} -> px_{col_filas[0]}_{c};')
            lines.append(f'  px_{col_filas[0]}_{c} -> col_{c};')

    # Pixels within each column: bidirectional up<->down
    for c in col_indices:
        col_filas = [f for f in fila_indices if (f, c) in pixeles]
        for i in range(len(col_filas) - 1):
            a = f'px_{col_filas[i]}_{c}'
            b = f'px_{col_filas[i+1]}_{c}'
            lines.append(f'  {a} -> {b};')
            lines.append(f'  {b} -> {a};')

    lines.append('}')

    nombre = f"capa_{capa.id_capa}_matriz"
    ruta = _ejecutar_dot('\n'.join(lines), nombre)
    return ruta


# ── 2. BST Capas ─────────────────────────────────────────────────────────────

def graficar_arbol_capas(arbol_capas):
    """
    ABB exactly like reference image 2:
    - Each node is a record with two cells: [ id_capa | (empty) ]
    - Clean top-down tree, no extra info inside nodes
    - Plain arrows from parent to children
    """
    lines = []
    lines.append('digraph ABBCapas {')
    lines.append('  graph [nodesep=0.6 ranksep=0.7];')
    lines.append('  node [shape=record fontname="Arial" fontsize=11 width=1.2 height=0.4];')
    lines.append('  edge [arrowsize=0.7];')
    lines.append('  label="Árbol Binario de Búsqueda - Capas";')
    lines.append('  labelloc=t; fontsize=13;')

    def recorrer(nodo):
        if not nodo:
            return
        # Sanitize id for DOT node name
        nid = 'c_' + ''.join(ch if ch.isalnum() else '_' for ch in str(nodo.capa.id_capa))
        # Two-cell record: [ id_capa | <empty> ]  — matches image 2 exactly
        lines.append(f'  {nid} [label="{{ {nodo.capa.id_capa} | }}"];')

        if nodo.izquierdo:
            nid_izq = 'c_' + ''.join(ch if ch.isalnum() else '_' for ch in str(nodo.izquierdo.capa.id_capa))
            lines.append(f'  {nid} -> {nid_izq};')
            recorrer(nodo.izquierdo)
        if nodo.derecho:
            nid_der = 'c_' + ''.join(ch if ch.isalnum() else '_' for ch in str(nodo.derecho.capa.id_capa))
            lines.append(f'  {nid} -> {nid_der};')
            recorrer(nodo.derecho)

    recorrer(arbol_capas.raiz)
    lines.append('}')
    ruta = _ejecutar_dot('\n'.join(lines), "arbol_capas")
    return ruta


# ── 3. Circular list of images ────────────────────────────────────────────────

def graficar_lista_imagenes(lista_imagenes):
    imagenes = lista_imagenes.obtener_todas()
    dot = ['digraph ListaCircularImagenes {']
    dot.append('  rankdir=LR;')
    dot.append('  node [shape=box fontname="Arial" fontsize=11];')
    dot.append('  label="Lista Circular Doblemente Enlazada - Imágenes";')
    dot.append('  labelloc=t;')

    if not imagenes:
        dot.append('  vacio [label="(vacía)" shape=plaintext];')
        dot.append('}')
        return _ejecutar_dot('\n'.join(dot), "lista_imagenes")

    # Image nodes
    for img in imagenes:
        nid = f"img_{img.id_imagen}"
        capas = img.lista_capas.obtener_capas_en_orden()
        capas_str = ", ".join([c.id_capa for c in capas]) if capas else "(sin capas)"
        dot.append(f'  {nid} [label="imagen{img.id_imagen}\\n[{capas_str}]" style=filled fillcolor=lightyellow];')

    # Arrows between images (doubly linked + circular)
    for i in range(len(imagenes)):
        nid_actual = f"img_{imagenes[i].id_imagen}"
        nid_sig = f"img_{imagenes[(i+1) % len(imagenes)].id_imagen}"
        dot.append(f'  {nid_actual} -> {nid_sig};')
        dot.append(f'  {nid_sig} -> {nid_actual} [style=dashed];')

    # Layer sub-lists
    for img in imagenes:
        nid_img = f"img_{img.id_imagen}"
        capas = img.lista_capas.obtener_capas_en_orden()
        prev = nid_img
        for i, capa in enumerate(capas):
            nid_c = f"lc_{img.id_imagen}_{capa.id_capa}".replace('-', '_')
            dot.append(f'  {nid_c} [label="{capa.id_capa}" shape=ellipse style=filled fillcolor=lightblue];')
            dot.append(f'  {prev} -> {nid_c};')
            prev = nid_c

    dot.append('}')
    ruta = _ejecutar_dot('\n'.join(dot), "lista_imagenes")
    return ruta


# ── 4. Image + BST pointer view ──────────────────────────────────────────────

def graficar_imagen_y_arbol(imagen, arbol_capas):
    dot = ['digraph ImagenYArbol {']
    dot.append('  node [fontname="Arial" fontsize=10];')
    dot.append(f'  label="Imagen {imagen.id_imagen} y Árbol de Capas";')
    dot.append('  labelloc=t;')

    # Image node
    dot.append(f'  img [label="imagen{imagen.id_imagen}" shape=box style=filled fillcolor=red fontcolor=white];')

    # Layer list
    capas = imagen.lista_capas.obtener_capas_en_orden()
    prev = "img"
    for capa in capas:
        nid = f"lc_{capa.id_capa}".replace('-', '_')
        dot.append(f'  {nid} [label="{capa.id_capa}" shape=ellipse style=filled fillcolor=lightsalmon];')
        dot.append(f'  {prev} -> {nid} [color=red];')
        prev = nid

    # BST (same double-cell style as graficar_arbol_capas)
    def recorrer_abb(nodo):
        if not nodo:
            return
        nid = 'abb_' + ''.join(ch if ch.isalnum() else '_' for ch in str(nodo.capa.id_capa))
        dot.append(f'  {nid} [label="{{ {nodo.capa.id_capa} | }}" shape=record fontname="Arial" fontsize=10];')
        if nodo.izquierdo:
            nid_izq = 'abb_' + ''.join(ch if ch.isalnum() else '_' for ch in str(nodo.izquierdo.capa.id_capa))
            dot.append(f'  {nid} -> {nid_izq};')
            recorrer_abb(nodo.izquierdo)
        if nodo.derecho:
            nid_der = 'abb_' + ''.join(ch if ch.isalnum() else '_' for ch in str(nodo.derecho.capa.id_capa))
            dot.append(f'  {nid} -> {nid_der};')
            recorrer_abb(nodo.derecho)

    recorrer_abb(arbol_capas.raiz)

    # Pointers from list to BST
    for capa in capas:
        nid_lista = f"lc_{capa.id_capa}".replace('-', '_')
        nid_abb = 'abb_' + ''.join(ch if ch.isalnum() else '_' for ch in str(capa.id_capa))
        dot.append(f'  {nid_lista} -> {nid_abb} [style=dashed color=blue label="ptr"];')

    dot.append('}')
    nombre = f"imagen_{imagen.id_imagen}_arbol"
    ruta = _ejecutar_dot('\n'.join(dot), nombre)
    return ruta


# ── 5. Users BST ─────────────────────────────────────────────────────────────

def graficar_arbol_usuarios(arbol_usuarios, lista_imagenes=None):
    dot = ['digraph ABBUsuarios {']
    dot.append('  node [shape=record fontname="Arial" fontsize=11 style=filled fillcolor=lightblue];')
    dot.append('  label="Árbol Binario de Búsqueda - Usuarios";')
    dot.append('  labelloc=t;')

    def recorrer(nodo):
        if not nodo:
            return
        nid = f"u_{nodo.usuario.nombre}".replace(' ', '_')
        dot.append(f'  {nid} [label="{nodo.usuario.nombre}"];')
        if nodo.izquierdo:
            nid_izq = f"u_{nodo.izquierdo.usuario.nombre}".replace(' ', '_')
            dot.append(f'  {nid} -> {nid_izq};')
            recorrer(nodo.izquierdo)
        if nodo.derecho:
            nid_der = f"u_{nodo.derecho.usuario.nombre}".replace(' ', '_')
            dot.append(f'  {nid} -> {nid_der};')
            recorrer(nodo.derecho)

        # Image list
        imgs = nodo.usuario.lista_imagenes.obtener_todas()
        prev = nid
        for i, id_img in enumerate(imgs):
            nid_img = f"ui_{nodo.usuario.nombre}_{id_img}".replace(' ', '_')
            dot.append(f'  {nid_img} [label="img{id_img}" style=filled fillcolor=lightyellow shape=box];')
            dot.append(f'  {prev} -> {nid_img};')
            prev = nid_img

    recorrer(arbol_usuarios.raiz)
    dot.append('}')
    ruta = _ejecutar_dot('\n'.join(dot), "arbol_usuarios")
    return ruta


# ── 6. Generate image (pixel grid) ───────────────────────────────────────────

def generar_imagen_png(capas_lista, nombre_salida="imagen_generada"):
    """
    Overlay layers in order and generate a PNG pixel art image.
    capas_lista: list of Capa objects in overlay order (first = bottom)
    """
    _asegurar_dir()

    # Merge all layers
    pixeles_merged = {}
    for capa in capas_lista:
        for f, c, color in capa.matriz.obtener_todos_pixeles():
            pixeles_merged[(f, c)] = color

    if not pixeles_merged:
        # Single black pixel
        pixeles_merged[(0, 0)] = '#000000'

    max_f = max(k[0] for k in pixeles_merged) + 1
    max_c = max(k[1] for k in pixeles_merged) + 1

    PIXEL_SIZE = 20
    ancho = max_c * PIXEL_SIZE
    alto = max_f * PIXEL_SIZE

    # Build SVG (reliable, no external deps)
    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}">',
        f'<rect width="{ancho}" height="{alto}" fill="white"/>'
    ]
    for (f, c), color in pixeles_merged.items():
        x = c * PIXEL_SIZE
        y = f * PIXEL_SIZE
        svg_lines.append(f'<rect x="{x}" y="{y}" width="{PIXEL_SIZE}" height="{PIXEL_SIZE}" fill="{color}"/>')
    svg_lines.append('</svg>')

    ruta_svg = os.path.join(SALIDA_DIR, nombre_salida + ".svg")
    ruta_png = os.path.join(SALIDA_DIR, nombre_salida + ".png")

    with open(ruta_svg, 'w') as f:
        f.write('\n'.join(svg_lines))

    # Convert SVG to PNG with Graphviz (neato can render SVG), or use rsvg/inkscape
    # Try converting with dot via a wrapper graph
    dot_contenido = f'''digraph G {{
  graph [bgcolor=transparent];
  node [shape=none margin=0];
  img [label=<
    <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0">
'''
    for f_idx in range(max_f):
        dot_contenido += '      <TR>'
        for c_idx in range(max_c):
            color = pixeles_merged.get((f_idx, c_idx), '#ffffff')
            dot_contenido += f'<TD WIDTH="{PIXEL_SIZE}" HEIGHT="{PIXEL_SIZE}" BGCOLOR="{color}"> </TD>'
        dot_contenido += '</TR>\n'
    dot_contenido += '    </TABLE>>];\n}'

    ruta_dot = os.path.join(SALIDA_DIR, nombre_salida + ".dot")
    with open(ruta_dot, 'w') as f:
        f.write(dot_contenido)

    try:
        resultado = subprocess.run(
            ["dot", "-Tpng", ruta_dot, "-o", ruta_png],
            capture_output=True, text=True
        )
        if resultado.returncode != 0:
            print(f"  [ERROR Graphviz] {resultado.stderr}")
            print(f"  SVG guardado en: {ruta_svg}")
            return ruta_svg
        return ruta_png
    except FileNotFoundError:
        print("  [ERROR] dot no encontrado, imagen guardada como SVG.")
        return ruta_svg


def abrir_imagen(ruta):
    """Open image with default system viewer"""
    if not ruta or not os.path.exists(ruta):
        print("  [ERROR] No se pudo generar o encontrar la imagen.")
        return
    print(f"  Imagen guardada en: {ruta}")
    try:
        if sys.platform.startswith('win'):
            os.startfile(ruta)
        elif sys.platform == 'darwin':
            subprocess.run(['open', ruta])
        else:
            subprocess.run(['xdg-open', ruta])
    except Exception as e:
        print(f"  No se pudo abrir automáticamente: {e}")
