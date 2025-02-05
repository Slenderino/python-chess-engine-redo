import pygame
import os

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


def list_sets():
    sets_location = os.path.join("..", "data", "sets")
    return {name: os.path.join(sets_location, name) for name in os.listdir(sets_location)}

def load_set(name, size=None, dpi=90) -> dict[str: pygame.Surface]:
    sets = list_sets()
    if not name in sets:
        raise Exception("Set not found")
    set_dir = sets[name]  # set directory name
    images = os.listdir(set_dir)  # images files
    surfaces = {}
    for file in images:
        path = os.path.join(set_dir, file)  # get image path
        if path.endswith(".svg"):
            surfaces[os.path.splitext(file)[0]] = svg_to_pygame_surface(path, size, dpi)
        elif path.endswith(".png"):
            surfaces[os.path.splitext(file)[0]] = pygame.image.load(path)
    return surfaces


