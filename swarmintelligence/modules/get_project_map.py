import os
from pathlib import Path

class GetProjectMap:
    def __init__(self):
        pass

    def run(self, project_dir):
        root = Path(project_dir).resolve()
        py_files = self.find_python_files(root)
        flat_map, tree_map = self.build_maps(py_files, root)
        return flat_map, tree_map

    def find_python_files(self, root_path: Path, exclude_dirs=None):
        """Recorre el árbol desde root_path y devuelve archivos .py (excluyendo __init__.py).
        exclude_dirs: conjunto de nombres de directorios a excluir (solo nombre, no ruta completa)
        """
        root_path = root_path.resolve()
        if exclude_dirs is None:
            exclude_dirs = {
                '__pycache__', '.git', '.hg', '.svn',
                '.venv', 'venv', 'env', '.tox', '.eggs',
                'build', 'dist', '.mypy_cache', '.pytest_cache',
                '.idea', '.vscode', 'node_modules'
            }

        py_files = []
        for dirpath, dirnames, filenames in os.walk(root_path):
            # Filtrar directorios a excluir (no descender en ellos)
            dirnames[:] = [d for d in dirnames if d not in exclude_dirs and not d.startswith('.') and not d.endswith('.egg-info') and not d.endswith('.dist-info')]

            for fname in filenames:
                # Solo archivos fuente .py
                if not fname.endswith('.py'):
                    continue
                # Excluir archivos accesorios
                if fname == '__init__.py':
                    continue
                if fname.startswith('.'):
                    continue
                full = Path(dirpath) / fname
                # Asegurarnos de que esté dentro de root_path (evita symlinks que salgan del root)
                try:
                    _ = full.relative_to(root_path)
                except Exception:
                    continue
                py_files.append(full)
        return py_files

    def build_maps(self, py_files, root_path: Path):
        """Construye dos mapas:
        - flat_map: dotted.name -> absolute path
        - tree_map: nested dict con la estructura de carpetas y archivos
        """
        flat_map = {}
        tree = {}
        for f in sorted(py_files):
            rel = f.relative_to(root_path).with_suffix('')
            parts = rel.parts
            dotted = '.'.join(parts)
            flat_map[dotted] = str(f)

            node = tree
            for i, p in enumerate(parts):
                if i == len(parts) - 1:
                    # hoja -> file path
                    node[p] = str(f)
                else:
                    if p not in node or not isinstance(node[p], dict):
                        node[p] = node.get(p, {}) if isinstance(node.get(p, {}), dict) else {}
                    node = node[p]
        return flat_map, tree

    def ascii_pretty(self, node, prefix=''):
        """Genera una lista de líneas con una representación tipo árbol usando solo caracteres ASCII"""
        lines = []
        keys = sorted(node.keys(), key=lambda s: (s.lower()))
        for idx, key in enumerate(keys):
            is_last = (idx == len(keys) - 1)
            connector = '`-- ' if is_last else '|-- '
            val = node[key]
            if isinstance(val, dict):
                lines.append(prefix + connector + key + '/')
                new_prefix = prefix + ('    ' if is_last else '|   ')
                lines.extend(self.ascii_pretty(val, new_prefix))
            else:
                lines.append(prefix + connector + key + ' -> ' + val)
        return lines