"""
chunking.py
Módulo para dividir documentos en chunks manejables.
Implementa chunking semántico respetando párrafos y oraciones.
Mantiene contexto y solapamiento inteligente entre chunks.
"""

import re
from typing import List, Dict, Any


class DocumentChunker:
    """Clase para dividir documentos en chunks de forma semántica."""

    def __init__(self, chunk_size: int = 500, overlap: int = 50, min_chunk_size: int = 100):
        """
        Inicializa el chunker.

        Args:
            chunk_size: Número de caracteres por chunk (aproximado)
            overlap: Número de caracteres solapados entre chunks (aproximado)
            min_chunk_size: Tamaño mínimo para considerar un chunk válido
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.min_chunk_size = min_chunk_size

        # Abreviaciones científicas comunes que NO deben usarse para cortar
        self.abbreviations = {
            'e.g.', 'i.e.', 'et al.', 'Fig.', 'fig.', 'Dr.', 'Mr.', 'Mrs.',
            'vs.', 'etc.', 'cf.', 'vol.', 'ed.', 'pp.', 'no.', 'pH', 'aW',
            'v.', 'approx.', 'ca.', 'sp.', 'spp.', 'var.', 'subsp.',
        }
    
    def chunk_text(self, text: str, chunk_id_prefix: str = "") -> List[Dict[str, Any]]:
        """
        Divide un texto en chunks semánticos con solapamiento inteligente.

        Estrategia:
        1. Divide por párrafos primero (doble salto de línea)
        2. Agrupa párrafos hasta alcanzar chunk_size
        3. Si un párrafo es muy largo, divide por oraciones
        4. Garantiza overlap en límites de oración completa

        Args:
            text: Texto a dividir
            chunk_id_prefix: Prefijo para IDs de chunks

        Returns:
            Lista de chunks con metadata
        """
        chunks = []
        chunk_count = 0

        # Primero dividir en párrafos
        paragraphs = self._split_into_paragraphs(text)

        if not paragraphs:
            return chunks

        current_chunk = []
        current_length = 0

        for i, paragraph in enumerate(paragraphs):
            para_length = len(paragraph)

            # Si el párrafo individual es muy largo, dividirlo por oraciones
            if para_length > self.chunk_size * 1.5:
                # Primero guardar el chunk actual si existe
                if current_chunk:
                    chunk_text = '\n\n'.join(current_chunk).strip()
                    if len(chunk_text) >= self.min_chunk_size:
                        chunks.append(self._create_chunk(chunk_text, chunk_id_prefix, chunk_count))
                        chunk_count += 1
                    current_chunk = []
                    current_length = 0

                # Dividir párrafo largo en chunks por oraciones
                para_chunks = self._chunk_long_paragraph(paragraph, chunk_id_prefix, chunk_count)
                chunks.extend(para_chunks)
                chunk_count += len(para_chunks)

            # Si agregar este párrafo excede el tamaño, crear nuevo chunk
            elif current_length + para_length > self.chunk_size and current_chunk:
                chunk_text = '\n\n'.join(current_chunk).strip()
                if len(chunk_text) >= self.min_chunk_size:
                    chunks.append(self._create_chunk(chunk_text, chunk_id_prefix, chunk_count))
                    chunk_count += 1

                # Iniciar nuevo chunk con overlap inteligente
                current_chunk = self._get_overlap_paragraphs(current_chunk)
                current_length = sum(len(p) for p in current_chunk)
                current_chunk.append(paragraph)
                current_length += para_length

            # Agregar párrafo al chunk actual
            else:
                current_chunk.append(paragraph)
                current_length += para_length

        # Agregar último chunk si existe
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk).strip()
            if len(chunk_text) >= self.min_chunk_size:
                chunks.append(self._create_chunk(chunk_text, chunk_id_prefix, chunk_count))

        return chunks

    def _split_into_paragraphs(self, text: str) -> List[str]:
        """
        Divide texto en párrafos.

        Args:
            text: Texto a dividir

        Returns:
            Lista de párrafos
        """
        # Dividir por doble salto de línea o más
        paragraphs = re.split(r'\n\s*\n', text)

        # Filtrar párrafos vacíos y limpiar
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        return paragraphs

    def _chunk_long_paragraph(self, paragraph: str, chunk_id_prefix: str, start_count: int) -> List[Dict[str, Any]]:
        """
        Divide un párrafo muy largo en chunks por oraciones.

        Args:
            paragraph: Párrafo largo a dividir
            chunk_id_prefix: Prefijo para IDs
            start_count: Contador de chunks inicial

        Returns:
            Lista de chunks
        """
        chunks = []
        sentences = self._split_into_sentences(paragraph)

        current_chunk = []
        current_length = 0
        chunk_count = start_count

        for sentence in sentences:
            sent_length = len(sentence)

            # Si agregar esta oración excede el tamaño, crear nuevo chunk
            if current_length + sent_length > self.chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk).strip()
                if len(chunk_text) >= self.min_chunk_size:
                    chunks.append(self._create_chunk(chunk_text, chunk_id_prefix, chunk_count))
                    chunk_count += 1

                # Overlap: mantener última(s) oración(es)
                current_chunk = self._get_overlap_sentences(current_chunk)
                current_length = sum(len(s) for s in current_chunk)

            current_chunk.append(sentence)
            current_length += sent_length

        # Agregar último chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk).strip()
            if len(chunk_text) >= self.min_chunk_size:
                chunks.append(self._create_chunk(chunk_text, chunk_id_prefix, chunk_count))

        return chunks

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Divide texto en oraciones, respetando abreviaciones.

        Args:
            text: Texto a dividir

        Returns:
            Lista de oraciones
        """
        # Reemplazar abreviaciones temporalmente para evitar splits falsos
        temp_text = text
        replacements = {}

        for i, abbr in enumerate(self.abbreviations):
            placeholder = f"__ABBR{i}__"
            replacements[placeholder] = abbr
            temp_text = temp_text.replace(abbr, placeholder)

        # Dividir por punto seguido de espacio y mayúscula
        sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])'
        sentences = re.split(sentence_pattern, temp_text)

        # Restaurar abreviaciones
        restored_sentences = []
        for sentence in sentences:
            for placeholder, abbr in replacements.items():
                sentence = sentence.replace(placeholder, abbr)
            restored_sentences.append(sentence.strip())

        return [s for s in restored_sentences if s]

    def _get_overlap_paragraphs(self, paragraphs: List[str]) -> List[str]:
        """
        Obtiene párrafos para overlap inteligente.

        Args:
            paragraphs: Lista de párrafos del chunk actual

        Returns:
            Lista de párrafos para overlap
        """
        if not paragraphs:
            return []

        # Intentar incluir últimos párrafos hasta alcanzar overlap deseado
        overlap_paras = []
        overlap_length = 0

        for para in reversed(paragraphs):
            if overlap_length + len(para) <= self.overlap:
                overlap_paras.insert(0, para)
                overlap_length += len(para)
            else:
                break

        # Si no se logró overlap suficiente, tomar al menos el último párrafo
        if not overlap_paras and paragraphs:
            overlap_paras = [paragraphs[-1]]

        return overlap_paras

    def _get_overlap_sentences(self, sentences: List[str]) -> List[str]:
        """
        Obtiene oraciones para overlap inteligente.

        Args:
            sentences: Lista de oraciones del chunk actual

        Returns:
            Lista de oraciones para overlap
        """
        if not sentences:
            return []

        # Intentar incluir últimas oraciones hasta alcanzar overlap deseado
        overlap_sents = []
        overlap_length = 0

        for sent in reversed(sentences):
            if overlap_length + len(sent) <= self.overlap:
                overlap_sents.insert(0, sent)
                overlap_length += len(sent)
            else:
                break

        # Si no se logró overlap suficiente, tomar al menos la última oración
        if not overlap_sents and sentences:
            overlap_sents = [sentences[-1]]

        return overlap_sents

    def _create_chunk(self, text: str, chunk_id_prefix: str, chunk_count: int) -> Dict[str, Any]:
        """
        Crea un diccionario de chunk con metadata.

        Args:
            text: Contenido del chunk
            chunk_id_prefix: Prefijo para el ID
            chunk_count: Número del chunk

        Returns:
            Diccionario con metadata del chunk
        """
        return {
            "id": f"{chunk_id_prefix}_chunk_{chunk_count}",
            "content": text,
            "length": len(text),
            "num_paragraphs": len(text.split('\n\n')),
        }
    
    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Divide una lista de documentos en chunks.
        
        Args:
            documents: Documentos a procesar
            
        Returns:
            Lista de chunks con metadata del documento origen
        """
        all_chunks = []
        
        for doc in documents:
            doc_chunks = self.chunk_text(
                doc["content"],
                chunk_id_prefix=doc["filename"].replace(".pdf", "")
            )
            
            # Añadir metadata del documento a cada chunk
            for chunk in doc_chunks:
                chunk.update({
                    "source_file": doc["filename"],
                    "source_path": doc["path"],
                    "doc_title": doc["metadata"].get("title", "Unknown"),
                    "doc_author": doc["metadata"].get("author", "Unknown"),
                })
                all_chunks.append(chunk)
        
        return all_chunks
    
    def get_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Retorna estadísticas de chunking."""
        if not chunks:
            return {
                "total_chunks": 0,
                "avg_chunk_size": 0,
                "min_chunk_size": 0,
                "max_chunk_size": 0,
                "chunks_per_document": 0,
            }

        total_chunks = len(chunks)
        avg_size = sum(chunk["length"] for chunk in chunks) / total_chunks
        min_size = min(chunk["length"] for chunk in chunks)
        max_size = max(chunk["length"] for chunk in chunks)

        # Contar documentos únicos
        unique_docs = len(set(chunk["source_file"] for chunk in chunks))

        # Estadísticas de párrafos por chunk
        avg_paragraphs = sum(chunk.get("num_paragraphs", 1) for chunk in chunks) / total_chunks

        return {
            "total_chunks": total_chunks,
            "unique_documents": unique_docs,
            "avg_chunk_size": round(avg_size, 2),
            "min_chunk_size": min_size,
            "max_chunk_size": max_size,
            "chunks_per_document": round(total_chunks / unique_docs, 2) if unique_docs > 0 else 0,
            "avg_paragraphs_per_chunk": round(avg_paragraphs, 2),
        }
