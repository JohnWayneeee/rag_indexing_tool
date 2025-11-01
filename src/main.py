import os
import sys
import logging
from pathlib import Path

# Add project root to PYTHONPATH
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.core.document_processor import DocumentProcessor
from src.config.settings import RAW_DATA_DIR, PROCESSED_DATA_DIR
from src.utils.saver import ResultSaver

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def check_dependencies():
    """Check for all dependencies"""
    try:
        import docling
        print("✅ Docling installed")
    except ImportError:
        print("❌ Docling not installed")
        return False

    try:
        import pandas
        print("✅ Pandas installed")
    except ImportError:
        print("❌ Pandas not installed")
        return False

    return True


def main():
    print("Checking dependencies...")
    if not check_dependencies():
        print("Install dependencies: pip install docling pandas python-dotenv")
        return

    processor = DocumentProcessor()
    saver = ResultSaver(PROCESSED_DATA_DIR)

    raw_data_path = RAW_DATA_DIR

    if not os.path.exists(raw_data_path):
        print(f"Directory {raw_data_path} does not exist!")
        return

    print(f"\nStarting document processing in {raw_data_path}...")

    files = []
    supported_extensions = {'.pdf', '.docx', '.pptx', '.xlsx', '.jpg', '.png', '.jpeg'}

    for root, dirs, filenames in os.walk(raw_data_path):
        for filename in filenames:
            if any(filename.lower().endswith(ext) for ext in supported_extensions):
                files.append(os.path.join(root, filename))

    print(f"Found supported files: {len(files)}")
    for file in files:
        print(f"  - {file}")

    if not files:
        print("No files to process!")
        return

    processed_docs = processor.process_directory(raw_data_path)

    print(f"\nProcessing results:")
    print(f"Successfully processed: {len(processed_docs)}")
    print(f"Failed to process: {len(files) - len(processed_docs)}")

    # Save results
    print(f"\nSaving results to {PROCESSED_DATA_DIR}...")
    all_saved_files = []

    for doc in processed_docs:
        print(f"\n{'=' * 50}")
        print(f"File: {doc['file_name']}")
        print(f"Type: {doc['file_type']}")
        print(f"Size: {doc['metadata']['file_size']} bytes")
        print(f"Tables: {len(doc['tables'])}")
        print(f"Images: {len(doc['images'])}")

        # Save to files
        saved_files = saver.save_single_document(doc, format="both")
        all_saved_files.extend(saved_files)

        print("Saved files:")
        for saved_file in saved_files:
            print(f"  📁 {saved_file}")

        # Show content preview
        print(f"\nContent preview:")
        print("-" * 40)
        lines = doc['full_text'].split('\n')[:10]  # First 10 lines
        for line in lines[:10]:  # Show first 5 lines
            print(line[:100] + "..." if len(line) > 100 else line)
        if len(lines) > 5:
            print("...")
        print("-" * 40)

    print(f"\n🎉 Total files saved: {len(all_saved_files)}")
    print(f"📂 Results in: {PROCESSED_DATA_DIR}")


if __name__ == "__main__":
    main()