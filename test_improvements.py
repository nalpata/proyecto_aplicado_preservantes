"""
test_improvements.py
Script para probar las mejoras de chunking y filtrado sin necesitar PDFs.
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from section_detector import SectionDetector
from chunking import DocumentChunker


def test_section_detection():
    """Prueba la detección de secciones."""
    print("=" * 60)
    print("TEST 1: DETECCIÓN DE SECCIONES")
    print("=" * 60)

    detector = SectionDetector()

    # Texto de ejemplo con secciones
    sample_text = """
Abstract

This paper discusses natural preservatives in food science.
The use of natural compounds is increasing.

Introduction

Food preservation is critical for safety and quality.
Natural preservatives offer many advantages.

Methods

We tested various natural compounds at different pH levels.
The pH ranged from 3.5 to 5.0.
Water activity (aW) was controlled at 0.95.

Results

Nisin showed excellent antimicrobial activity against E. coli.
The inhibition was pH-dependent, with optimal activity at pH 4.2.

Discussion

These results suggest that natural preservatives can effectively replace synthetic compounds.

Acknowledgments

We thank the funding agency for their support.

References

Smith, J. et al. (2020). Natural food preservatives. Journal of Food Science, 45(2), 123-145.
Jones, K. (2019). Antimicrobial peptides in food. Food Research International, 67(1), 89-101.
Brown, L. et al. (2018). pH effects on preservation. Food Chemistry, 234, 56-78.

Appendix A

Additional tables and figures are provided here.
"""

    # Filtrar secciones
    filtered_text, stats = detector.filter_low_value_sections(
        sample_text,
        remove_references=True,
        remove_acknowledgments=True,
        remove_appendix=True,
        remove_tables=False,
        remove_headers_footers=False
    )

    print(f"\n📊 Estadísticas de Filtrado:")
    print(f"  - Caracteres originales: {stats['original_chars']}")
    print(f"  - Caracteres filtrados: {stats['filtered_chars']}")
    print(f"  - Reducción: {stats['reduction_percentage']:.2f}%")
    print(f"  - Secciones removidas: {stats['sections_removed']}")
    print(f"    - Referencias: {stats['references_removed']}")
    print(f"    - Agradecimientos: {stats['acknowledgments_removed']}")
    print(f"    - Apéndices: {stats['appendix_removed']}")

    print(f"\n📝 Texto Filtrado (primeros 500 chars):")
    print(f"{filtered_text[:500]}...")

    return filtered_text


def test_semantic_chunking(text):
    """Prueba el chunking semántico."""
    print("\n" + "=" * 60)
    print("TEST 2: CHUNKING SEMÁNTICO")
    print("=" * 60)

    chunker = DocumentChunker(chunk_size=300, overlap=50, min_chunk_size=100)

    chunks = chunker.chunk_text(text, chunk_id_prefix="test")

    print(f"\n📊 Estadísticas de Chunking:")
    print(f"  - Total de chunks: {len(chunks)}")
    print(f"  - Tamaño promedio: {sum(c['length'] for c in chunks) / len(chunks):.2f} caracteres")
    print(f"  - Tamaño mín: {min(c['length'] for c in chunks)}")
    print(f"  - Tamaño máx: {max(c['length'] for c in chunks)}")

    print(f"\n📝 Chunks Generados:")
    for i, chunk in enumerate(chunks, 1):
        print(f"\n--- Chunk {i} ({chunk['length']} chars, {chunk['num_paragraphs']} párrafos) ---")
        print(chunk['content'][:200] + "..." if len(chunk['content']) > 200 else chunk['content'])


def test_abbreviations():
    """Prueba que no se corte en abreviaciones."""
    print("\n" + "=" * 60)
    print("TEST 3: RESPETO DE ABREVIACIONES")
    print("=" * 60)

    text_with_abbr = """
The study used various compounds. For example, e.g., nisin and lysozyme were tested.
The pH was measured at 4.5. Water activity (aW) was 0.95.
Smith et al. (2020) found similar results. The concentration was 100 ppm, i.e., parts per million.
Figures (Fig. 1, Fig. 2) show the results. Dr. Johnson conducted the experiments.
"""

    chunker = DocumentChunker(chunk_size=100, overlap=20, min_chunk_size=50)
    chunks = chunker.chunk_text(text_with_abbr, chunk_id_prefix="abbr_test")

    print(f"\n📊 Se crearon {len(chunks)} chunks")
    print(f"\n📝 Verificando que no se corten abreviaciones:")

    for i, chunk in enumerate(chunks, 1):
        print(f"\n--- Chunk {i} ---")
        print(chunk['content'])

        # Verificar que no termine con abreviación cortada
        content = chunk['content']
        bad_endings = ['e.g', 'i.e', 'et al', 'Fig', 'Dr', 'pH', 'aW']
        for bad in bad_endings:
            if content.rstrip().endswith(bad):
                print(f"⚠️  ADVERTENCIA: Termina con '{bad}' (posible corte)")
            else:
                pass  # OK


def main():
    """Ejecuta todas las pruebas."""
    print("\n🧪 PRUEBAS DE MEJORAS DEL SISTEMA\n")

    # Test 1: Detección de secciones
    filtered_text = test_section_detection()

    # Test 2: Chunking semántico
    test_semantic_chunking(filtered_text)

    # Test 3: Respeto de abreviaciones
    test_abbreviations()

    print("\n" + "=" * 60)
    print("✅ TODAS LAS PRUEBAS COMPLETADAS")
    print("=" * 60)


if __name__ == "__main__":
    main()
