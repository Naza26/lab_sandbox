#!/usr/bin/env python3
import os
import sys
import inspect
import datetime
from typing import List, Dict, Any, Tuple

ROOT = os.path.dirname(os.path.dirname(__file__))
VERSION0 = os.path.join(ROOT, 'version0')
ISX_LOCAL = os.path.join(ROOT, 'Inscopix Data Processing 1.9.6', 'Inscopix Data Processing.linux', 'Contents', 'API', 'Python')

# Ensure imports resolve
if VERSION0 not in sys.path:
    sys.path.insert(0, VERSION0)
if ISX_LOCAL not in sys.path:
    sys.path.insert(0, ISX_LOCAL)

# Import targets
from isx_pipeline.isx_pipeline import ISXPipeline  # type: ignore
import importlib

# Try to import isx package (local vendored)
isx = importlib.import_module('isx')

DocEntry = Dict[str, Any]


def get_signature_safe(obj) -> Tuple[str, List[Tuple[str, str]]]:
    """Return (signature_str, list of (param, default)) for the callable, best-effort.
    If not introspectable, return placeholders."""
    try:
        sig = inspect.signature(obj)
        parts = []
        for name, p in sig.parameters.items():
            if p.default is inspect._empty:
                default = ''
            else:
                default = repr(p.default)
            parts.append((name, default))
        return (str(sig), parts)
    except Exception:
        # Fallback: try getfullargspec
        try:
            fas = inspect.getfullargspec(obj)
            defaults = fas.defaults or ()
            # align defaults to args
            start = len(fas.args) - len(defaults)
            parts = []
            for i, a in enumerate(fas.args):
                if i >= start:
                    d = repr(defaults[i - start])
                else:
                    d = ''
                parts.append((a, d))
            return (f"({', '.join(fas.args)})", parts)
        except Exception:
            return ("(unavailable)", [])


def collect_pipeline_methods() -> List[DocEntry]:
    methods = []
    for name, func in inspect.getmembers(ISXPipeline, predicate=inspect.isfunction):
        if name.startswith('_'):
            continue
        # Inspect source to check if it calls self.step(
        try:
            src = inspect.getsource(func)
        except OSError:
            continue
        if 'self.step(' not in src:
            continue
        # heuristic: find referenced isx functions inside the method body
        referenced_isx = []
        for isx_name, isx_obj in inspect.getmembers(isx):
            if not (inspect.isfunction(isx_obj) or inspect.ismethod(isx_obj)):
                continue
            # if function name appears in source, consider it referenced
            token = f".{isx_name}("
            if token in src:
                referenced_isx.append((isx_name, isx_obj))
        # Manual hints for functions that may be bound/aliased differently
        if 'preprocess_videos' in name and not any(n == 'preprocess' for n, _ in referenced_isx):
            if hasattr(isx, 'preprocess'):
                referenced_isx.append(('preprocess', getattr(isx, 'preprocess')))
        methods.append({
            'method_name': name,
            'source': src,
            'referenced_isx': referenced_isx,
        })
    # Keep original declaration order by using source line numbers
    def start_line(m):
        try:
            return inspect.getsourcelines(getattr(ISXPipeline, m['method_name']))[1]
        except Exception:
            return 0
    methods.sort(key=start_line)
    return methods


def render_en(methods: List[DocEntry]) -> str:
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    lines = []
    lines.append(f"# ISXPipeline Documentation (English)\n\nGenerated: {now}\n")
    lines.append("## Introduction\n")
    lines.append("ISXPipeline is a high-level pipeline built on top of the Inscopix Python API (package `isx`). It orchestrates common calcium imaging preprocessing and analysis steps (preprocessing, filtering, motion correction, dF/F normalization, PCA-ICA cell extraction, event detection, and exports).\n")
    lines.append("\n## Usage\n")
    lines.append("Example usage to run a simple pipeline:\n")
    lines.append("```python\nfrom version0.isx_pipeline.isx_pipeline import ISXPipeline\nfrom version0.logger.file_logger import FileLogger\n\nlogger = FileLogger('/path/to/output')\np = ISXPipeline.new('/path/to/input_folder_with_isxd', logger)\\\n    .preprocess_videos()\\\n    .bandpass_filter_videos()\\\n    .motion_correction_videos()\\\n    .normalize_dff_videos()\\\n    .extract_neurons_pca_ica()\\\n    .detect_events_in_cells()\\\n    .auto_accept_reject_cells()\\\n    .export_movie_to_tiff()\n# Final outputs available in logger directory\n```\n")
    lines.append("\n## Implemented functions\n")
    for m in methods:
        lines.append(f"### {m['method_name']}\n")
        lines.append("Calls to isx functions:\n")
        if not m['referenced_isx']:
            lines.append("- (No direct isx calls detected; this step likely manages files or uses higher-level utilities.)\n")
        for isx_name, isx_obj in m['referenced_isx']:
            sig_str, parts = get_signature_safe(isx_obj)
            lines.append(f"- `{isx_name}{sig_str}`\n")
            if parts:
                lines.append("  - Parameters and defaults:\n")
                for pname, default in parts:
                    if default:
                        lines.append(f"    - {pname} = {default}\n")
                    else:
                        lines.append(f"    - {pname}\n")
            doc = inspect.getdoc(isx_obj) or ''
            if doc:
                # keep short
                short = doc.split('\n')[0]
                lines.append(f"  - Summary: {short}\n")
        lines.append("\n")
    lines.append("## Extensibility\n")
    lines.append("You can add new steps to ISXPipeline by creating a new method that wraps `self.step(name, fn)` and uses the `isx` API to process inputs and produce outputs. Reuse the private helpers `_input_and_output_files`, `_process_input_output_pairs`, and `_step_folder_path` to follow existing conventions.\n")
    return ''.join(lines)


def render_es(methods: List[DocEntry]) -> str:
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    lines = []
    lines.append(f"# Documentación de ISXPipeline (Español)\n\nGenerado: {now}\n")
    lines.append("## Introducción\n")
    lines.append("ISXPipeline es una canalización (pipeline) de alto nivel construida sobre la API de Python de Inscopix (`isx`). Orquesta pasos comunes de preprocesamiento y análisis de imagen de calcio: preprocesamiento, filtrado, corrección de movimiento, normalización dF/F, extracción de células por PCA-ICA, detección de eventos y exportaciones.\n")
    lines.append("\n## Uso\n")
    lines.append("Ejemplo de uso para ejecutar una canalización simple:\n")
    lines.append("```python\nfrom version0.isx_pipeline.isx_pipeline import ISXPipeline\nfrom version0.logger.file_logger import FileLogger\n\nlogger = FileLogger('/ruta/a/salida')\np = ISXPipeline.new('/ruta/a/carpeta_entrada_con_isxd', logger)\\\n    .preprocess_videos()\\\n    .bandpass_filter_videos()\\\n    .motion_correction_videos()\\\n    .normalize_dff_videos()\\\n    .extract_neurons_pca_ica()\\\n    .detect_events_in_cells()\\\n    .auto_accept_reject_cells()\\\n    .export_movie_to_tiff()\n# Los resultados finales están disponibles en el directorio del logger\n```\n")
    lines.append("\n## Funciones implementadas\n")
    for m in methods:
        lines.append(f"### {m['method_name']}\n")
        lines.append("Llamadas a funciones de isx:\n")
        if not m['referenced_isx']:
            lines.append("- (No se detectaron llamadas directas a isx; este paso probablemente gestiona archivos o usa utilidades de mayor nivel.)\n")
        for isx_name, isx_obj in m['referenced_isx']:
            sig_str, parts = get_signature_safe(isx_obj)
            lines.append(f"- `{isx_name}{sig_str}`\n")
            if parts:
                lines.append("  - Parámetros y valores por defecto:\n")
                for pname, default in parts:
                    if default:
                        lines.append(f"    - {pname} = {default}\n")
                    else:
                        lines.append(f"    - {pname}\n")
            doc = inspect.getdoc(isx_obj) or ''
            if doc:
                short = doc.split('\n')[0]
                lines.append(f"  - Resumen: {short}\n")
        lines.append("\n")
    lines.append("## Extensibilidad\n")
    lines.append("Puede agregar nuevos pasos a ISXPipeline creando un nuevo método que envuelva `self.step(name, fn)` y utilice la API `isx` para procesar entradas y producir salidas. Reutilice las ayudas privadas `_input_and_output_files`, `_process_input_output_pairs` y `_step_folder_path` para seguir las convenciones existentes.\n")
    return ''.join(lines)


def main():
    methods = collect_pipeline_methods()
    docs_dir = os.path.join(ROOT, 'docs')
    os.makedirs(docs_dir, exist_ok=True)
    en = render_en(methods)
    es = render_es(methods)
    with open(os.path.join(docs_dir, 'ISXPipeline_en.md'), 'w', encoding='utf-8') as f:
        f.write(en)
    with open(os.path.join(docs_dir, 'ISXPipeline_es.md'), 'w', encoding='utf-8') as f:
        f.write(es)
    print('Docs generated in', docs_dir)


if __name__ == '__main__':
    main()
