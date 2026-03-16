"""
Módulo de utilidades para formateo de datos en la salida (CLI, reportes).
"""
import pandas as pd

# Columnas que deben ser tratadas como DNI y formateadas con ceros a la izquierda.
# Se define aquí para ser consistente a través de toda la aplicación.
DNI_COLUMN_NAMES = {'dni', 'DNI'}

def format_cell(value, column_name: str) -> str:
    """
    Formatea un valor para su visualización basado en el nombre de la columna.
    - DNI: Se asegura de que sea un string de 8 dígitos con ceros a la izquierda.
    - Floats: Se muestran sin decimales si son enteros.
    - NaT/NaN: Se muestran como strings vacíos.
    """
    if pd.isna(value) or value is None:
        return ""
    
    if column_name in DNI_COLUMN_NAMES:
        # Asegura que el DNI se muestre con 8 dígitos, rellenando con ceros.
        try:
            # Primero convierte a int para eliminar decimales, luego a str para zfill
            return str(int(value)).zfill(8)
        except (ValueError, TypeError):
            # Si no se puede convertir (ej. ya es un string con caracteres), lo devuelve tal cual
            return str(value)

    if isinstance(value, float):
        # Si el float es un entero (ej: 5.0), lo muestra como '5'
        if value.is_integer():
            return str(int(value))
        # De lo contrario, lo formatea a 2 decimales
        return f"{value:.2f}"

    return str(value)
