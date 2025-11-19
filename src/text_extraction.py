"""
text_extraction.py
Módulo para limpiar y normalizar texto extraído de PDFs.
"""

import re
from typing import List, Dict, Any
from section_detector import SectionDetector


class TextExtractor:
    """Clase para limpiar y normalizar texto."""

    def __init__(
        self,
        filter_sections: bool = True,
        remove_references: bool = True,
        remove_acknowledgments: bool = True,
        remove_appendix: bool = True,
        remove_tables: bool = True,
        remove_headers_footers: bool = True
    ):
        """
        Inicializa el extractor.

        Args:
            filter_sections: Si True, filtra secciones de bajo valor
            remove_references: Si True, remueve referencias bibliográficas
            remove_acknowledgments: Si True, remueve agradecimientos
            remove_appendix: Si True, remueve apéndices
            remove_tables: Si True, remueve tablas
            remove_headers_footers: Si True, remueve headers/footers
        """
        self.filter_sections = filter_sections
        self.remove_references = remove_references
        self.remove_acknowledgments = remove_acknowledgments
        self.remove_appendix = remove_appendix
        self.remove_tables = remove_tables
        self.remove_headers_footers = remove_headers_footers

        if filter_sections:
            self.section_detector = SectionDetector()
        else:
            self.section_detector = None
    
    def clean_text(self, text: str) -> str:
        """
        Limpia el texto extraído de PDFs.
        
        Args:
            text: Texto crudo
            
        Returns:
            Texto limpio y normalizado
        """
        # Eliminar saltos de línea múltiples
        text = re.sub(r'\n\n+', '\n', text)
        
        # Eliminar espacios en blanco múltiples
        text = re.sub(r' +', ' ', text)
        
        # Eliminar caracteres especiales problemáticos
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
        
        # Normalizar espacios alrededor de puntuación
        text = re.sub(r' +([.,;:!?])', r'\1', text)
        
        # Eliminar URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Eliminar emails
        text = re.sub(r'\S+@\S+', '', text)
        
        # Eliminar números de página (patrón común)
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Strip
        text = text.strip()
        
        return text
    
    def extract_references(self, text: str) -> List[str]:
        """
        Extrae referencias bibliográficas del texto.
        
        Args:
            text: Texto que contiene referencias
            
        Returns:
            Lista de referencias encontradas
        """
        # Patrón simple para detectar referencias (mejorarlo según formato)
        pattern = r'\[.*?\]|\(.*?20\d{2}.*?\)|doi:.*'
        references = re.findall(pattern, text)
        return references
    
    def extract_numbers(self, text: str) -> List[float]:
        """
        Extrae números del texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Lista de números encontrados
        """
        pattern = r'\d+\.?\d*'
        numbers = [float(m) for m in re.findall(pattern, text)]
        return numbers
    
    def process_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Procesa una lista de documentos.

        Args:
            documents: Documentos cargados

        Returns:
            Documentos con texto limpio y filtrado
        """
        processed = []

        for doc in documents:
            # Primero limpiar el texto
            cleaned_content = self.clean_text(doc["content"])

            # Luego filtrar secciones de bajo valor si está habilitado
            filtering_stats = {}
            if self.filter_sections and self.section_detector:
                cleaned_content, filtering_stats = self.section_detector.filter_low_value_sections(
                    cleaned_content,
                    remove_references=self.remove_references,
                    remove_acknowledgments=self.remove_acknowledgments,
                    remove_appendix=self.remove_appendix,
                    remove_tables=self.remove_tables,
                    remove_headers_footers=self.remove_headers_footers
                )

            processed.append({
                **doc,
                "content": cleaned_content,
                "content_cleaned": True,
                "sections_filtered": self.filter_sections,
                "length_original": len(doc["content"]),
                "length_cleaned": len(cleaned_content),
                "filtering_stats": filtering_stats,
                "references": self.extract_references(doc["content"]) if not self.filter_sections else [],
            })

        return processed
    
    def get_stats(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Retorna estadísticas de limpieza y filtrado."""
        total_original = sum(doc.get("length_original", 0) for doc in documents)
        total_cleaned = sum(doc.get("length_cleaned", 0) for doc in documents)
        reduction = ((total_original - total_cleaned) / total_original * 100) if total_original > 0 else 0

        # Agregar estadísticas de filtrado de secciones
        total_sections_removed = 0
        total_references_removed = 0
        total_acknowledgments_removed = 0
        total_appendix_removed = 0
        total_tables_removed = 0
        total_headers_footers_removed = 0

        for doc in documents:
            filtering_stats = doc.get("filtering_stats", {})
            total_sections_removed += filtering_stats.get("sections_removed", 0)
            total_references_removed += filtering_stats.get("references_removed", 0)
            total_acknowledgments_removed += filtering_stats.get("acknowledgments_removed", 0)
            total_appendix_removed += filtering_stats.get("appendix_removed", 0)
            total_tables_removed += filtering_stats.get("tables_removed", 0)
            total_headers_footers_removed += filtering_stats.get("headers_footers_removed", 0)

        return {
            "total_original_chars": total_original,
            "total_cleaned_chars": total_cleaned,
            "reduction_percentage": round(reduction, 2),
            "documents_processed": len(documents),
            "sections_filtered": any(doc.get("sections_filtered", False) for doc in documents),
            "total_sections_removed": total_sections_removed,
            "total_references_removed": total_references_removed,
            "total_acknowledgments_removed": total_acknowledgments_removed,
            "total_appendix_removed": total_appendix_removed,
            "total_tables_removed": total_tables_removed,
            "total_headers_footers_removed": total_headers_footers_removed,
        }
