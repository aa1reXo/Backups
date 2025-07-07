#!/usr/bin/env python3
"""
Test script for Multimodal PDF Processor
Demonstrates OCR and page-level processing capabilities
"""

import os
import sys
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.multimodal_pdf_processor import MultimodalPDFProcessor
from loguru import logger

def test_multimodal_processor():
    """Test the multimodal PDF processor with sample PDFs"""
    
    # Initialize processor
    processor = MultimodalPDFProcessor(
        chunk_size=1000,
        chunk_overlap=200,
        ocr_lang='eng',
        dpi=300,
        enable_ocr=True,
        enable_image_extraction=True
    )
    
    # Test with a sample PDF (you can replace with your own)
    pdf_path = "sample.pdf"  # Replace with your PDF path
    
    if not os.path.exists(pdf_path):
        logger.warning(f"PDF file {pdf_path} not found. Creating a test scenario...")
        
        # Create a test scenario
        logger.info("Testing processor initialization...")
        logger.info(f"OCR enabled: {processor.enable_ocr}")
        logger.info(f"Image extraction enabled: {processor.enable_image_extraction}")
        logger.info(f"OCR language: {processor.ocr_lang}")
        logger.info(f"DPI: {processor.dpi}")
        
        return
    
    logger.info(f"Processing PDF: {pdf_path}")
    
    # Process the PDF
    pages = processor.process_pdf_file(pdf_path)
    
    if not pages:
        logger.error("No pages processed")
        return
    
    # Get statistics
    stats = processor.get_processing_stats(pages)
    
    logger.info("=== Processing Statistics ===")
    for key, value in stats.items():
        logger.info(f"{key}: {value}")
    
    # Show details for first few pages
    logger.info("\n=== Page Details ===")
    for i, page in enumerate(pages[:3]):  # Show first 3 pages
        logger.info(f"\nPage {i + 1}:")
        logger.info(f"  Document: {page['doc_name']}")
        logger.info(f"  Page number: {page['page_num']}")
        logger.info(f"  Has text: {page['has_text']}")
        logger.info(f"  Has images: {page['has_images']}")
        logger.info(f"  Text chunks: {len(page['text_chunks'])}")
        logger.info(f"  Embedded images: {len(page['images'])}")
        
        if page['text_chunks']:
            first_chunk = page['text_chunks'][0]
            logger.info(f"  First chunk preview: {first_chunk['text'][:100]}...")
        
        if page['images']:
            logger.info(f"  First image: {page['images'][0]['width']}x{page['images'][0]['height']}")
    
    # Save results to JSON for inspection
    output_file = "multimodal_processing_results.json"
    with open(output_file, 'w') as f:
        # Convert numpy arrays to lists for JSON serialization
        json_data = []
        for page in pages:
            page_copy = page.copy()
            if page_copy.get('page_image'):
                page_copy['page_image'] = f"<base64_image_data_{len(page_copy['page_image'])}_chars>"
            json_data.append(page_copy)
        
        json.dump({
            "statistics": stats,
            "pages": json_data
        }, f, indent=2)
    
    logger.info(f"\nResults saved to: {output_file}")

def test_ocr_capabilities():
    """Test OCR capabilities with different configurations"""
    
    logger.info("\n=== Testing OCR Capabilities ===")
    
    # Test different OCR configurations
    configs = [
        {"ocr_lang": "eng", "dpi": 300},
        {"ocr_lang": "eng", "dpi": 600},
        {"ocr_lang": "eng+fra", "dpi": 300},  # English + French
    ]
    
    for i, config in enumerate(configs):
        logger.info(f"\nConfiguration {i + 1}: {config}")
        
        processor = MultimodalPDFProcessor(
            chunk_size=1000,
            chunk_overlap=200,
            ocr_lang=config["ocr_lang"],
            dpi=config["dpi"],
            enable_ocr=True,
            enable_image_extraction=True
        )
        
        logger.info(f"  OCR Language: {processor.ocr_lang}")
        logger.info(f"  DPI: {processor.dpi}")
        logger.info(f"  OCR Config: {processor.ocr_config}")

if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    
    logger.info("Starting Multimodal PDF Processor Test")
    
    # Test basic functionality
    test_multimodal_processor()
    
    # Test OCR capabilities
    test_ocr_capabilities()
    
    logger.info("\n=== Test Complete ===")
    logger.info("To use this processor:")
    logger.info("1. Install Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
    logger.info("2. Install additional language packs if needed")
    logger.info("3. Update the pdf_path in the script to point to your PDF file")
    logger.info("4. Run: python test_multimodal_processor.py") 