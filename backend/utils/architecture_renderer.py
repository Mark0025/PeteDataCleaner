"""
Architecture Renderer Utility

Utility for rendering architecture diagrams from JSON configuration data.
Can be used to programmatically generate and update Mermaid diagrams.
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

class ArchitectureRenderer:
    """
    Renders architecture diagrams from JSON configuration and analysis data.
    
    Can generate:
    - Mermaid diagrams from JSON
    - HTML visualizations
    - Architecture summaries
    """
    
    def __init__(self, architecture_json_path: str):
        """
        Initialize renderer with architecture JSON data.
        
        Args:
            architecture_json_path: Path to architecture JSON file
        """
        self.architecture_data = self._load_architecture_data(architecture_json_path)
        
    def _load_architecture_data(self, json_path: str) -> Dict[str, Any]:
        """Load architecture data from JSON file."""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Architecture JSON not found: {json_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in architecture file: {e}")
    
    def render_mermaid_from_json(self) -> str:
        """Render Mermaid diagram from JSON architecture data."""
        return self.architecture_data.get('mermaid_diagram', '')
    
    def render_summary(self) -> str:
        """Render a text summary of the architecture."""
        config = self.architecture_data.get('config', {})
        categorized_files = self.architecture_data.get('categorized_files', {})
        
        lines = [
            f"# {config.get('title', 'Architecture Summary')}",
            f"**Generated:** {self.architecture_data.get('timestamp', 'Unknown')}",
            f"**Version:** {self.architecture_data.get('version', 'Unknown')}",
            "",
            "## 📊 File Distribution by Category",
            ""
        ]
        
        total_files = 0
        total_loc = 0
        
        for category, files in categorized_files.items():
            file_count = len(files)
            category_loc = sum(file.get('lines_of_code', 0) for file in files)
            
            lines.append(f"### {category}")
            lines.append(f"- **Files:** {file_count}")
            lines.append(f"- **Lines of Code:** {category_loc:,}")
            lines.append(f"- **Average LOC/File:** {category_loc/file_count:.1f}" if file_count > 0 else "- **Average LOC/File:** 0")
            lines.append("")
            
            total_files += file_count
            total_loc += category_loc
        
        lines.extend([
            "## 📈 Overall Statistics",
            "",
            f"- **Total Files:** {total_files}",
            f"- **Total Lines of Code:** {total_loc:,}",
            f"- **Average LOC/File:** {total_loc/total_files:.1f}" if total_files > 0 else "- **Average LOC/File:** 0",
            ""
        ])
        
        return '\n'.join(lines)
    
    def render_html_visualization(self, output_path: str):
        """
        Render an HTML visualization of the architecture.
        
        Args:
            output_path: Path where to save the HTML file
        """
        mermaid_diagram = self.render_mermaid_from_json()
        summary = self.render_summary()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pete Architecture Visualization</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .header {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .diagram-container {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .summary {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        pre {{
            background: #f6f8fa;
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
        }}
        h1, h2, h3 {{
            color: #333;
        }}
        .mermaid {{
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Pete Codebase Architecture</h1>
        <p><strong>Generated:</strong> {self.architecture_data.get('timestamp', 'Unknown')}</p>
        <p><strong>Version:</strong> {self.architecture_data.get('version', 'Unknown')}</p>
        <p>Interactive visualization of the Pete codebase architecture showing component relationships and file organization.</p>
    </div>
    
    <div class="diagram-container">
        <h2>🏗️ Architecture Diagram</h2>
        <div class="mermaid">
{mermaid_diagram}
        </div>
    </div>
    
    <div class="summary">
        <h2>📊 Architecture Summary</h2>
        <pre>{summary}</pre>
    </div>
    
    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
    </script>
</body>
</html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML visualization saved to: {output_path}")
    
    def get_file_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all files in a specific category."""
        return self.architecture_data.get('categorized_files', {}).get(category, [])
    
    def find_files_by_pattern(self, pattern: str) -> List[Dict[str, Any]]:
        """Find files matching a specific pattern across all categories."""
        matching_files = []
        categorized_files = self.architecture_data.get('categorized_files', {})
        
        for category, files in categorized_files.items():
            for file_data in files:
                file_path = file_data.get('file', '')
                if pattern.lower() in file_path.lower():
                    file_data['category'] = category
                    matching_files.append(file_data)
        
        return matching_files
    
    def export_to_json(self, output_path: str, include_mermaid: bool = True):
        """
        Export architecture data to a new JSON file.
        
        Args:
            output_path: Where to save the JSON
            include_mermaid: Whether to include the Mermaid diagram string
        """
        data_to_export = self.architecture_data.copy()
        
        if not include_mermaid:
            data_to_export.pop('mermaid_diagram', None)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_export, f, indent=2)
        
        print(f"✅ Architecture data exported to: {output_path}")

def main():
    """Demo usage of ArchitectureRenderer"""
    # Find the latest architecture JSON
    reports_dir = Path('DEV_MAN/whatsworking')
    if not reports_dir.exists():
        print("❌ No whatsworking reports directory found")
        return
    
    # Find latest architecture JSON
    arch_files = list(reports_dir.glob('architecture_*.json'))
    if not arch_files:
        print("❌ No architecture JSON files found")
        return
    
    latest_arch = max(arch_files, key=os.path.getctime)
    print(f"📊 Using architecture file: {latest_arch}")
    
    # Render various outputs
    renderer = ArchitectureRenderer(str(latest_arch))
    
    # Generate HTML visualization
    html_output = reports_dir / 'architecture_visualization.html'
    renderer.render_html_visualization(str(html_output))
    
    # Show summary
    print("\\n" + renderer.render_summary())
    
    # Example: Find all frontend files
    frontend_files = renderer.get_file_by_category('Frontend_Components')
    if frontend_files:
        print(f"\\n🧩 Found {len(frontend_files)} frontend component files:")
        for file_data in frontend_files[:5]:  # Show first 5
            print(f"  - {file_data.get('file', 'Unknown')} ({file_data.get('lines_of_code', 0)} LOC)")

if __name__ == '__main__':
    main()