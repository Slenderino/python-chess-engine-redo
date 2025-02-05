import pygame
import os
from svgpathtools import svg2paths, Line, CubicBezier, Arc
import xml.etree.ElementTree as ET

def svg_to_pygame_surface(svg_path, size=None, dpi=90):
    """
    Convierte un archivo SVG a una superficie de Pygame usando rsvg-convert con archivo temporal.
    Requiere que rsvg-convert esté instalado en el sistema.

    Args:
        svg_path (str): Ruta al archivo SVG
        size (int, int): Tamaño del SVG
        dpi (int): Calidad de la imagen

    Returns:
        pygame.Surface: Superficie de Pygame con la imagen
    """
    import pygame
    import subprocess
    import tempfile
    import os

    # Crear archivo temporal para el PNG
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        tmp_path = tmp_file.name

    try:
        # Crear comando para rsvg-convert
        cmd = ['rsvg-convert', svg_path, '-o', tmp_path]
        if size:
            width, height = size
            cmd.append(f'--width={str(width)}')
            cmd.append(f'--height={str(height)}')
        cmd.extend([f'--dpi-x={str(dpi)}', f'--dpi-y={str(dpi)}'])

        # Ejecutar rsvg-convert
        subprocess.run(cmd, check=True)
        print(cmd)

        # Cargar el PNG con Pygame
        surface = pygame.image.load(tmp_path)

        return surface

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error al convertir SVG: {e}")
    except FileNotFoundError:
        raise RuntimeError("rsvg-convert no está instalado. En Ubuntu/Debian: sudo apt-get install librsvg2-bin")
    finally:
        # Limpiar archivo temporal
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def parse_fill_color(color_str):
    """Parses a fill color from an SVG style string (e.g., #ff0000 or rgb(255, 0, 0))"""
    if color_str.startswith('#'):
        return tuple(int(color_str[i:i+2], 16) for i in (1, 3, 5))  # #RRGGBB
    elif color_str.startswith('rgb'):
        color_values = color_str[color_str.index('(') + 1:color_str.index(')')].split(',')
        return tuple(int(c.strip()) for c in color_values)
    else:
        return (255, 255, 255)  # Color por defecto si no se puede parsear


def list_sets():
    sets_location = os.path.join("..", "data", "sets")
    return {name: os.path.join(sets_location, name) for name in os.listdir(sets_location)}

def load_set(name, size=None, dpi=90) -> dict[str: pygame.Surface]:
    sets = list_sets()
    if not name in sets:
        raise Exception("Set not found")
    set_dir = sets[name]
    images = os.listdir(set_dir)
    surfaces = {}
    for file in images:
        path = os.path.join(set_dir, file)
        if path.endswith(".svg"):
            surfaces[os.path.splitext(file)[0]] = svg_to_pygame_surface(path, size, dpi)
        elif path.endswith(".png"):
            surfaces[os.path.splitext(file)[0]] = pygame.image.load(path)
    return surfaces


