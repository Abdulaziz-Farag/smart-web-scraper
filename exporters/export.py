"""
Exporter Module — CSV, JSON, Excel
Export scraped data to any format
"""

import csv
import json
import os
from typing import List, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Exporter:
    """Export scraped data to multiple formats."""

    def __init__(self, data: List[Dict]):
        self.data = data

    def to_csv(self, path: str = None) -> str:
        """Export to CSV file."""
        path = path or f"export_{self._timestamp()}.csv"
        if not self.data:
            logger.warning("No data to export")
            return path

        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=self.data[0].keys())
            writer.writeheader()
            writer.writerows(self.data)

        logger.info(f"CSV saved: {path} ({len(self.data)} rows)")
        return path

    def to_json(self, path: str = None, indent: int = 2) -> str:
        """Export to JSON file."""
        path = path or f"export_{self._timestamp()}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=indent)

        logger.info(f"JSON saved: {path}")
        return path

    def to_excel(self, path: str = None) -> str:
        """Export to Excel file."""
        try:
            import pandas as pd
            path = path or f"export_{self._timestamp()}.xlsx"
            df = pd.DataFrame(self.data)
            df.to_excel(path, index=False, engine="openpyxl")
            logger.info(f"Excel saved: {path}")
            return path
        except ImportError:
            logger.error("pandas/openpyxl not installed. Run: pip install pandas openpyxl")
            return self.to_csv(path)

    def to_html(self, path: str = None) -> str:
        """Export to HTML table."""
        path = path or f"export_{self._timestamp()}.html"
        if not self.data:
            return path

        headers = self.data[0].keys()
        rows = ""
        for row in self.data:
            cells = "".join(f"<td>{v or ''}</td>" for v in row.values())
            rows += f"<tr>{cells}</tr>\n"

        headers_html = "".join(f"<th>{h}</th>" for h in headers)
        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Scraped Data</title>
<style>
  body {{ font-family: Arial; padding: 20px; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th {{ background: #4CAF50; color: white; padding: 8px; }}
  td {{ border: 1px solid #ddd; padding: 8px; }}
  tr:nth-child(even) {{ background: #f2f2f2; }}
</style>
</head>
<body>
<h2>Scraped Data — {len(self.data)} items</h2>
<table>
<thead><tr>{headers_html}</tr></thead>
<tbody>{rows}</tbody>
</table>
</body>
</html>"""

        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

        logger.info(f"HTML saved: {path}")
        return path

    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
