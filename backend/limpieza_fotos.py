"""
========================================
LIMPIEZA AUTOMÁTICA DE FOTOGRAFÍAS
Sistema de Control de Visitantes
========================================

Este script elimina fotografías de visitantes antiguas
basándose en la fecha del nombre del archivo.

Formato de archivo esperado:
{TIPO_ID}-{NUM_ID}-{DDMMYYYY}_{HHMMSS}.jpg
Ejemplo: CC-14652319-09032026_120335.jpg

La fecha se extrae de la posición 11-18 (DDMMYYYY)
y se compara con la fecha actual menos DIAS_RETENCION_FOTOS

Uso:
    python limpieza_fotos.py              # Ejecuta limpieza
    python limpieza_fotos.py --dry-run    # Simula limpieza (no elimina)
    python limpieza_fotos.py --dias 30    # Retención personalizada
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import re
from config import Config


def extraer_fecha_de_nombre(nombre_archivo):
    """
    Extrae la fecha del nombre del archivo
    
    Formato: CC-14652319-09032026_120335.jpg
    La fecha está en la posición después del segundo guion: DDMMYYYY
    
    Args:
        nombre_archivo: Nombre del archivo (ej: CC-14652319-09032026_120335.jpg)
    
    Returns:
        datetime object o None si no se puede extraer
    """
    try:
        # Patrón: cualquier cosa, luego DDMMYYYY después del segundo guion
        # CC-14652319-09032026_120335.jpg
        #            ^^^^^^^^ 
        patron = r'^[^-]+-[^-]+-(\d{8})_'
        match = re.search(patron, nombre_archivo)
        
        if match:
            fecha_str = match.group(1)  # DDMMYYYY
            # Convertir DDMMYYYY a datetime
            dia = int(fecha_str[0:2])
            mes = int(fecha_str[2:4])
            anio = int(fecha_str[4:8])
            return datetime(anio, mes, dia)
        
        return None
    except Exception as e:
        print(f"⚠️  Error al extraer fecha de '{nombre_archivo}': {e}")
        return None


def limpiar_fotos_antiguas(dias_retencion=None, dry_run=False):
    """
    Elimina fotografías antiguas basándose en la fecha del nombre
    
    Args:
        dias_retencion: Días de retención (usa config si es None)
        dry_run: Si es True, solo simula sin eliminar
    
    Returns:
        dict con estadísticas de la limpieza
    """
    config = Config()
    
    # Usar configuración o parámetro
    dias = dias_retencion if dias_retencion is not None else config.DIAS_RETENCION_FOTOS
    upload_folder = config.UPLOAD_FOLDER
    
    # Resolver ruta relativa
    if not os.path.isabs(upload_folder):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        upload_folder = os.path.normpath(os.path.join(base_dir, upload_folder))
    
    # Verificar que existe la carpeta
    if not os.path.exists(upload_folder):
        print(f"❌ La carpeta no existe: {upload_folder}")
        return {
            'total_archivos': 0,
            'eliminados': 0,
            'conservados': 0,
            'errores': 0
        }
    
    # Fecha límite
    fecha_limite = datetime.now() - timedelta(days=dias)
    
    print("=" * 70)
    print("🧹 LIMPIEZA DE FOTOGRAFÍAS DE VISITANTES")
    print("=" * 70)
    print(f"📁 Carpeta: {upload_folder}")
    print(f"📅 Fecha límite: {fecha_limite.strftime('%d/%m/%Y')}")
    print(f"⏳ Retención: {dias} días")
    print(f"🔍 Modo: {'SIMULACIÓN' if dry_run else 'ELIMINACIÓN REAL'}")
    print("=" * 70)
    print()
    
    # Buscar archivos JPG
    archivos_jpg = list(Path(upload_folder).glob('*.jpg'))
    
    stats = {
        'total_archivos': len(archivos_jpg),
        'eliminados': 0,
        'conservados': 0,
        'errores': 0,
        'archivos_eliminados': [],
        'archivos_conservados': []
    }
    
    for archivo in archivos_jpg:
        nombre = archivo.name
        fecha_foto = extraer_fecha_de_nombre(nombre)
        
        if fecha_foto is None:
            print(f"⚠️  No se pudo extraer fecha: {nombre}")
            stats['errores'] += 1
            continue
        
        # Calcular antigüedad
        antiguedad = (datetime.now() - fecha_foto).days
        
        if fecha_foto < fecha_limite:
            # Foto antigua - eliminar
            print(f"🗑️  ELIMINAR: {nombre}")
            print(f"   └─ Fecha: {fecha_foto.strftime('%d/%m/%Y')} ({antiguedad} días)")
            
            if not dry_run:
                try:
                    archivo.unlink()
                    print(f"   └─ ✅ Eliminado")
                except Exception as e:
                    print(f"   └─ ❌ Error: {e}")
                    stats['errores'] += 1
                    continue
            else:
                print(f"   └─ 🔍 Simulación - no eliminado")
            
            stats['eliminados'] += 1
            stats['archivos_eliminados'].append({
                'nombre': nombre,
                'fecha': fecha_foto,
                'antiguedad_dias': antiguedad
            })
        else:
            # Foto reciente - conservar
            print(f"✅ CONSERVAR: {nombre}")
            print(f"   └─ Fecha: {fecha_foto.strftime('%d/%m/%Y')} ({antiguedad} días)")
            
            stats['conservados'] += 1
            stats['archivos_conservados'].append({
                'nombre': nombre,
                'fecha': fecha_foto,
                'antiguedad_dias': antiguedad
            })
    
    # Resumen
    print()
    print("=" * 70)
    print("📊 RESUMEN DE LIMPIEZA")
    print("=" * 70)
    print(f"📁 Total archivos analizados: {stats['total_archivos']}")
    print(f"🗑️  Archivos eliminados: {stats['eliminados']}")
    print(f"✅ Archivos conservados: {stats['conservados']}")
    print(f"⚠️  Errores: {stats['errores']}")
    print("=" * 70)
    
    return stats


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Limpieza automática de fotografías de visitantes'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simula la limpieza sin eliminar archivos'
    )
    parser.add_argument(
        '--dias',
        type=int,
        help='Días de retención (sobrescribe configuración)'
    )
    
    args = parser.parse_args()
    
    # Ejecutar limpieza
    stats = limpiar_fotos_antiguas(
        dias_retencion=args.dias,
        dry_run=args.dry_run
    )
    
    # Retornar código de salida
    if stats['errores'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
