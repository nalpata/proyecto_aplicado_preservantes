"""
section_detector.py
Módulo para detectar y filtrar secciones de bajo valor en papers científicos.
Identifica: referencias, agradecimientos, apéndices, tablas, headers/footers.
"""

import re
from typing import List, Dict, Any, Tuple
from enum import Enum


class SectionType(Enum):
    """Tipos de sección en papers científicos."""
    VALUABLE = "valuable"  # Abstract, Introduction, Methods, Results, Discussion
    REFERENCES = "references"
    ACKNOWLEDGMENTS = "acknowledgments"
    APPENDIX = "appendix"
    TABLE = "table"
    HEADER_FOOTER = "header_footer"
    UNKNOWN = "unknown"


class SectionDetector:
    """Clase para detectar y filtrar secciones en papers científicos."""

    def __init__(self):
        """Inicializa el detector con patrones de secciones."""
        # Patrones para detectar inicios de secciones de bajo valor
        self.section_patterns = {
            SectionType.REFERENCES: [
                r'(?i)^\s*(references|bibliography|bibliograf[ií]a|literatura\s+citada|cited\s+literature)\s*$',
                r'(?i)^\s*\d+\.?\s*(references|bibliography|bibliograf[ií]a)\s*$',
            ],
            SectionType.ACKNOWLEDGMENTS: [
                r'(?i)^\s*(acknowledgments?|agradecimientos?|thanks)\s*$',
                r'(?i)^\s*\d+\.?\s*(acknowledgments?|agradecimientos?)\s*$',
            ],
            SectionType.APPENDIX: [
                r'(?i)^\s*(appendix|appendices|apéndice[s]?|anexo[s]?)\s*[a-z]?\s*$',
                r'(?i)^\s*\d+\.?\s*(appendix|apéndice)\s*',
            ],
        }

        # Patrones para detectar tablas
        self.table_patterns = [
            r'(?i)table\s+\d+[\.:]\s*',
            r'(?i)tabla\s+\d+[\.:]\s*',
            r'(?i)^[\|┌┐└┘├┤┬┴┼─═│║]\s*',  # Bordes de tablas
        ]

        # Patrones para headers/footers comunes
        self.header_footer_patterns = [
            r'^\s*\d+\s*$',  # Solo número de página
            r'^\s*page\s+\d+\s*$',  # "Page X"
            r'^\s*página\s+\d+\s*$',  # "Página X"
            r'^\s*\d+\s+of\s+\d+\s*$',  # "X of Y"
            r'^\s*\|\s*page\s+\d+\s*$',  # "| Page X"
            r'(?i)^\s*(copyright|©|®|™)\s+',  # Copyright notices
        ]

    def extract_sections(self, text: str) -> List[Dict[str, Any]]:
        """
        Extrae secciones del texto y las clasifica.

        Args:
            text: Texto completo del documento

        Returns:
            Lista de diccionarios con info de cada sección:
            - type: SectionType
            - start_pos: posición inicial en texto
            - end_pos: posición final en texto
            - content: contenido de la sección
            - header: encabezado de la sección
        """
        sections = []
        lines = text.split('\n')
        current_section = None
        current_start = 0
        current_lines = []

        for i, line in enumerate(lines):
            # Verificar si es inicio de sección de bajo valor
            section_type = self._detect_section_start(line)

            if section_type and section_type != SectionType.UNKNOWN:
                # Guardar sección anterior si existe
                if current_section:
                    sections.append({
                        'type': current_section,
                        'start_line': current_start,
                        'end_line': i - 1,
                        'content': '\n'.join(current_lines),
                        'header': current_lines[0] if current_lines else '',
                    })

                # Iniciar nueva sección
                current_section = section_type
                current_start = i
                current_lines = [line]
            else:
                # Continuar con la sección actual
                if current_section:
                    current_lines.append(line)
                else:
                    # Si no hay sección actual, es contenido valioso
                    if not sections or sections[-1]['type'] != SectionType.VALUABLE:
                        if sections:
                            # Guardar sección de bajo valor anterior
                            sections.append({
                                'type': current_section if current_section else SectionType.VALUABLE,
                                'start_line': current_start,
                                'end_line': i - 1,
                                'content': '\n'.join(current_lines) if current_lines else '',
                                'header': current_lines[0] if current_lines else '',
                            })
                        current_section = SectionType.VALUABLE
                        current_start = i
                        current_lines = [line]
                    else:
                        current_lines.append(line)

        # Agregar última sección
        if current_lines:
            sections.append({
                'type': current_section if current_section else SectionType.VALUABLE,
                'start_line': current_start,
                'end_line': len(lines) - 1,
                'content': '\n'.join(current_lines),
                'header': current_lines[0] if current_lines else '',
            })

        return sections

    def _detect_section_start(self, line: str) -> SectionType:
        """
        Detecta si una línea es el inicio de una sección específica.

        Args:
            line: Línea de texto a analizar

        Returns:
            SectionType detectado o UNKNOWN
        """
        line_stripped = line.strip()

        # Verificar patrones de cada tipo de sección
        for section_type, patterns in self.section_patterns.items():
            for pattern in patterns:
                if re.match(pattern, line_stripped):
                    return section_type

        return SectionType.UNKNOWN

    def filter_low_value_sections(
        self,
        text: str,
        remove_references: bool = True,
        remove_acknowledgments: bool = True,
        remove_appendix: bool = True,
        remove_tables: bool = True,
        remove_headers_footers: bool = True
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Filtra secciones de bajo valor del texto.

        Args:
            text: Texto completo del documento
            remove_references: Si True, remueve secciones de referencias
            remove_acknowledgments: Si True, remueve agradecimientos
            remove_appendix: Si True, remueve apéndices
            remove_tables: Si True, remueve tablas
            remove_headers_footers: Si True, remueve headers/footers

        Returns:
            Tupla (texto_filtrado, estadísticas)
        """
        original_length = len(text)
        stats = {
            'original_chars': original_length,
            'sections_removed': 0,
            'references_removed': 0,
            'acknowledgments_removed': 0,
            'appendix_removed': 0,
            'tables_removed': 0,
            'headers_footers_removed': 0,
        }

        # Primero, remover headers/footers línea por línea
        if remove_headers_footers:
            text, hf_count = self._remove_headers_footers(text)
            stats['headers_footers_removed'] = hf_count

        # Remover tablas si se solicita
        if remove_tables:
            text, table_count = self._remove_tables(text)
            stats['tables_removed'] = table_count

        # Extraer secciones
        sections = self.extract_sections(text)

        # Filtrar secciones según configuración
        filtered_sections = []
        for section in sections:
            section_type = section['type']

            should_remove = (
                (section_type == SectionType.REFERENCES and remove_references) or
                (section_type == SectionType.ACKNOWLEDGMENTS and remove_acknowledgments) or
                (section_type == SectionType.APPENDIX and remove_appendix)
            )

            if should_remove:
                stats['sections_removed'] += 1
                if section_type == SectionType.REFERENCES:
                    stats['references_removed'] += 1
                elif section_type == SectionType.ACKNOWLEDGMENTS:
                    stats['acknowledgments_removed'] += 1
                elif section_type == SectionType.APPENDIX:
                    stats['appendix_removed'] += 1
            else:
                filtered_sections.append(section)

        # Reconstruir texto filtrado
        filtered_text = '\n\n'.join(
            section['content'].strip()
            for section in filtered_sections
            if section['content'].strip()
        )

        stats['filtered_chars'] = len(filtered_text)
        stats['reduction_percentage'] = (
            (original_length - len(filtered_text)) / original_length * 100
            if original_length > 0 else 0
        )

        return filtered_text, stats

    def _remove_headers_footers(self, text: str) -> Tuple[str, int]:
        """
        Remueve líneas que parecen headers o footers.

        Args:
            text: Texto a procesar

        Returns:
            Tupla (texto_limpio, cantidad_removida)
        """
        lines = text.split('\n')
        filtered_lines = []
        removed_count = 0

        for line in lines:
            is_header_footer = False

            for pattern in self.header_footer_patterns:
                if re.match(pattern, line.strip(), re.IGNORECASE):
                    is_header_footer = True
                    removed_count += 1
                    break

            if not is_header_footer:
                filtered_lines.append(line)

        return '\n'.join(filtered_lines), removed_count

    def _remove_tables(self, text: str) -> Tuple[str, int]:
        """
        Detecta y remueve bloques de tablas del texto.

        Args:
            text: Texto a procesar

        Returns:
            Tupla (texto_sin_tablas, cantidad_removida)
        """
        lines = text.split('\n')
        filtered_lines = []
        in_table = False
        table_count = 0
        consecutive_table_lines = 0

        for line in lines:
            is_table_line = False

            # Detectar si la línea pertenece a una tabla
            for pattern in self.table_patterns:
                if re.search(pattern, line):
                    is_table_line = True
                    break

            # También detectar líneas con muchos separadores (tabs, pipes)
            if not is_table_line:
                separators = line.count('|') + line.count('\t')
                if separators >= 2 and len(line.strip()) > 0:
                    is_table_line = True

            if is_table_line:
                consecutive_table_lines += 1
                if not in_table:
                    in_table = True
                    table_count += 1
            else:
                # Si salimos de la tabla y era muy corta (1-2 líneas), no era tabla
                if in_table and consecutive_table_lines <= 2:
                    # Recuperar esas líneas
                    filtered_lines.extend([''] * consecutive_table_lines)
                    table_count -= 1

                in_table = False
                consecutive_table_lines = 0
                filtered_lines.append(line)

        return '\n'.join(filtered_lines), table_count

    def get_section_stats(self, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcula estadísticas de las secciones detectadas.

        Args:
            sections: Lista de secciones extraídas

        Returns:
            Diccionario con estadísticas
        """
        stats = {
            'total_sections': len(sections),
            'valuable_sections': 0,
            'references_sections': 0,
            'acknowledgments_sections': 0,
            'appendix_sections': 0,
            'valuable_chars': 0,
            'low_value_chars': 0,
        }

        for section in sections:
            section_type = section['type']
            chars = len(section['content'])

            if section_type == SectionType.VALUABLE:
                stats['valuable_sections'] += 1
                stats['valuable_chars'] += chars
            else:
                stats['low_value_chars'] += chars

                if section_type == SectionType.REFERENCES:
                    stats['references_sections'] += 1
                elif section_type == SectionType.ACKNOWLEDGMENTS:
                    stats['acknowledgments_sections'] += 1
                elif section_type == SectionType.APPENDIX:
                    stats['appendix_sections'] += 1

        total_chars = stats['valuable_chars'] + stats['low_value_chars']
        if total_chars > 0:
            stats['valuable_percentage'] = (stats['valuable_chars'] / total_chars) * 100
        else:
            stats['valuable_percentage'] = 0

        return stats
