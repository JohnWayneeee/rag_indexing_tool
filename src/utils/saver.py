import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class ResultSaver:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_single_document(self, doc: Dict, format: str = "both") -> List[str]:
        """Save single document in different formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{Path(doc['file_name']).stem}_{timestamp}"

        saved_files = []

        if format in ["json", "both"]:
            json_path = self.output_dir / f"{base_name}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(doc, f, ensure_ascii=False, indent=2, default=str)
            saved_files.append(str(json_path))

        if format in ["txt", "both"]:
            txt_path = self.output_dir / f"{base_name}.txt"
            self._save_as_text(doc, txt_path)
            saved_files.append(str(txt_path))

        if format in ["md", "both"]:
            md_path = self.output_dir / f"{base_name}.md"
            self._save_as_markdown(doc, md_path)
            saved_files.append(str(md_path))

        return saved_files

    def _save_as_text(self, doc: Dict, file_path: Path):
        """Save document as readable text"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"File: {doc['file_name']}\n")
            f.write(f"Type: {doc['file_type']}\n")
            f.write(f"Size: {doc['metadata']['file_size']} bytes\n")
            f.write(f"Path: {doc['file_path']}\n")
            f.write("=" * 80 + "\n\n")
            f.write("CONTENT:\n")
            f.write("=" * 80 + "\n")
            f.write(doc['full_text'])
            f.write("\n\n" + "=" * 80 + "\n")
            f.write(f"Tables: {len(doc['tables'])}\n")
            f.write(f"Images: {len(doc['images'])}\n")

    def _save_as_markdown(self, doc: Dict, file_path: Path):
        """Save document in markdown format"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# {doc['file_name']}\n\n")
            f.write(f"- **File Type**: {doc['file_type']}\n")
            f.write(f"- **Size**: {doc['metadata']['file_size']} bytes\n")
            f.write(f"- **Path**: `{doc['file_path']}`\n")
            f.write(f"- **Tables**: {len(doc['tables'])}\n")
            f.write(f"- **Images**: {len(doc['images'])}\n\n")

            f.write("## Content\n\n")
            f.write(doc['full_text'])

            if doc['tables']:
                f.write("\n\n## Tables\n\n")
                for i, table in enumerate(doc['tables']):
                    f.write(f"### Table {i + 1}: {table.get('caption', '')}\n\n")
                    if 'markdown' in table:
                        f.write(table['markdown'] + "\n\n")
                    else:
                        f.write("```\n" + table.get('content', '') + "\n```\n\n")