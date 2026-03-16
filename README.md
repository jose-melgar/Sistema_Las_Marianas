# Sistema de Gestión de SO - Las Marianas (v2.0)

Este proyecto es una herramienta de línea de comandos (CLI) para el análisis, auditoría y generación de reportes de datos de Salud Ocupacional, diseñado para ser escalable y mantenible.

## Nueva Arquitectura

El proyecto ha sido reestructurado siguiendo un enfoque de "carpetas por función" para mejorar la separación de responsabilidades:

- **`config/`**: Archivos de configuración centralizados (YAML) para el cargador de datos y el registro de reportes. Esto permite modificar el comportamiento del sistema sin tocar el código.
- **`data/`**: Almacén para el archivo Excel principal (`.xlsm`).
- **`outputs/`**: Directorio donde se guardan todos los artefactos generados por el sistema, como informes `.docx` y gráficos `.png`.
- **`src/las_marianas_so/`**: Contiene todo el código fuente de Python, estructurado como un paquete instalable.
  - **`cli/`**: Lógica de la interfaz de línea de comandos (menús, prompts, tablas).
  - **`loader/`**: El cargador de datos centralizado y su configuración.
  - **`audit/`**: Funciones para la auditoría de calidad de datos (duplicados, faltantes).
  - **`domain/`**: Lógica de negocio pura (ej: cómo se define un "trabajador activo").
  - **`reports/`**: El sistema de generación de reportes, incluyendo un orquestador y generadores "pluggables".
  - **`common/`**: Utilidades compartidas, como funciones de formateo.

## Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd <NOMBRE_DEL_REPOSITORIO>
    ```

2.  **Crear y activar un entorno virtual:**
    ```bash
    python -m venv venv
    # En Windows
    venv\Scripts\activate
    # En macOS/Linux
    source venv/bin/activate
    ```

3.  **Instalar las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## Uso

La aplicación se ejecuta a través del punto de entrada `main.py` y requiere el argumento `--cli` para iniciar en modo interactivo.

```bash
python main.py --cli
```

Esto lanzará el menú principal, desde donde podrás acceder a los diferentes módulos:

### 1. Auditoría de Datos

Selecciona la opción "Auditoría de Datos" para ejecutar una revisión completa de los datos en el archivo Excel. El sistema buscará:
- **Registros Duplicados**: Basado en las claves únicas definidas en `config/loader.config.yml`.
- **Valores Faltantes**: En todas las columnas configuradas para cada hoja.

Los resultados se mostrarán en la consola, indicando las filas exactas (según su número en Excel) donde se encontraron los problemas. **El sistema no modifica el archivo Excel.**

### 2. Generación de Reportes

Selecciona la opción "Generar Reportes" para acceder al submenú del orquestador de reportes.
1.  El sistema mostrará una lista de los reportes disponibles, leídos desde `config/reports.config.yml`.
2.  Elige el `ID` del reporte que deseas generar.
3.  El sistema te pedirá interactivamente los parámetros necesarios para ese reporte (ej: Obra, año, mes).
4.  Una vez generados, los archivos (`.docx`, `.png`) se guardarán en la carpeta `outputs/`.

## Cómo Extender el Sistema

### Añadir un Nuevo Reporte

1.  **Crear el Generador**: Crea un nuevo archivo Python en `src/las_marianas_so/reports/generators/`, por ejemplo, `mi_nuevo_reporte.py`. Dentro, define una clase que herede de `BaseReportGenerator` e implemente el método `generate()`.
2.  **Registrar el Reporte**: Abre `config/reports.config.yml` y añade una nueva entrada bajo `report_registry`, apuntando a tu nueva clase y definiendo los parámetros que necesita.

¡Y eso es todo! El CLI detectará automáticamente el nuevo reporte y lo mostrará en el menú.