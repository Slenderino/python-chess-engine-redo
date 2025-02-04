import pygame
import os
from svgpathtools import svg2paths, Line, CubicBezier, Arc
import xml.etree.ElementTree as ET


# TODO: fix svg conversion
def svg_to_pygame_surface(svg_file, scale=1):
    # Parsear el archivo SVG
    tree = ET.parse(svg_file)
    root = tree.getroot()

    # Crear una superficie de Pygame
    surface = pygame.Surface((800, 600), pygame.SRCALPHA)  # Ajusta el tamaño según necesites

    # Recorrer todos los elementos del SVG
    for element in root.iter():
        if element.tag.endswith('path'):
            # Obtener el estilo del elemento (si tiene)
            style = element.attrib.get('style', '')
            fill_color = (255, 255, 255)  # Color por defecto (blanco)
            if 'fill' in style:
                fill_color = parse_fill_color(style.split('fill:')[1].split(';')[0])

            # Convertir el path a una lista de segmentos
            paths, _ = svg2paths(svg_file)
            for path in paths:
                for segment in path:
                    if isinstance(segment, Line):  # Si es una línea
                        pygame.draw.line(surface, fill_color,
                                         (segment.start.real * scale, segment.start.imag * scale),
                                         (segment.end.real * scale, segment.end.imag * scale), 2)
                    elif isinstance(segment, CubicBezier):  # Si es una curva Bézier
                        pygame.draw.aalines(surface, fill_color,
                                            False,
                                            [(segment.start.real * scale, segment.start.imag * scale),
                                             (segment.control1.real * scale, segment.control1.imag * scale),
                                             (segment.control2.real * scale, segment.control2.imag * scale),
                                             (segment.end.real * scale, segment.end.imag * scale)])
                    elif isinstance(segment, Arc):  # Si es un arco (opcional)
                        pass  # Los arcos pueden ser más complicados de manejar

        # Manejo de relleno para elementos como rectángulos, círculos, etc.
        elif element.tag.endswith('rect') or element.tag.endswith('circle'):
            style = element.attrib.get('style', '')
            fill_color = (255, 255, 255)  # Color por defecto (blanco)
            if 'fill' in style:
                fill_color = parse_fill_color(style.split('fill:')[1].split(';')[0])

            if element.tag.endswith('rect'):
                x = float(element.attrib.get('x', 0)) * scale
                y = float(element.attrib.get('y', 0)) * scale
                width = float(element.attrib.get('width', 0)) * scale
                height = float(element.attrib.get('height', 0)) * scale
                pygame.draw.rect(surface, fill_color, pygame.Rect(x, y, width, height))

            elif element.tag.endswith('circle'):
                cx = float(element.attrib.get('cx', 0)) * scale
                cy = float(element.attrib.get('cy', 0)) * scale
                r = float(element.attrib.get('r', 0)) * scale
                pygame.draw.circle(surface, fill_color, (cx, cy), r)

    return surface

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

def load_set(name, scale=1) -> dict[str: pygame.Surface]:
    sets = list_sets()
    if not name in sets:
        raise Exception("Set not found")
    set_dir = sets[name]
    images = os.listdir(set_dir)
    surfaces = {}
    for file in images:
        path = os.path.join(set_dir, file)
        if path.endswith(".svg"):
            surfaces[os.path.splitext(file)[0]] = svg_to_pygame_surface(path, scale)
        elif path.endswith(".png"):
            surfaces[os.path.splitext(file)[0]] = pygame.image.load(path)
    return surfaces


