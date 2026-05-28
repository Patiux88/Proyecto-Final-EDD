# Generador de Imágenes por Capas
## Estructuras de Datos

### Requisitos
- Python 3.8+
- Graphviz instalado en el sistema (comando `dot`)
  - Windows: https://graphviz.org/download/
  - Instalar y agregar al PATH del sistema

### Estructura del Proyecto

```
proyecto/
├── main.py                  # Punto de entrada principal
├── carga_masiva.py          # Parser para .cap, .im, .usr
├── reportes.py              # Generación de gráficas con Graphviz
├── estructuras/
│   ├── __init__.py
│   ├── matriz_dispersa.py   # Matriz dispersa (lista doble enlazada)
│   ├── arbol_capas.py       # ABB de capas
│   ├── lista_imagenes.py    # Lista circular doble + lista capas
│   └── arbol_usuarios.py    # ABB de usuarios
└── datos_ejemplo/
    ├── capas.cap            # Ejemplo de archivo de capas
    ├── imagenes.im          # Ejemplo de archivo de imágenes
    └── usuarios.usr         # Ejemplo de archivo de usuarios
```

### Ejecución

```cmd
cd proyecto
python main.py
```

### Formato de archivos

#### .cap (Capas)
```
id_capa {
    fila, columna, #hexcolor;
    fila, columna, #hexcolor;
}
```

#### .im (Imágenes)
```
id_imagen {
    id_capa;
    id_capa;
}
```

#### .usr (Usuarios)
```
nombre_usuario:id_img1,id_img2;
```

### Orden de carga masiva
1. Primero cargar `.cap` (capas)
2. Luego cargar `.im` (imágenes)
3. Finalmente cargar `.usr` (usuarios)

### Reportes generados
Los reportes se guardan en la carpeta `reportes/` como archivos PNG.
Se abren automáticamente con el visor predeterminado del sistema.

### Estructuras implementadas
| Estructura | Uso |
|-----------|-----|
| Matriz Dispersa (lista doble) | Almacena píxeles de cada capa |
| ABB (Árbol Binario Búsqueda) | Almacena todas las capas |
| Lista Circular Doble | Almacena todas las imágenes |
| Lista Simple Enlazada | Capas de cada imagen (punteros al ABB) |
| ABB | Almacena usuarios |
| Lista Simple Enlazada | Imágenes por usuario |
