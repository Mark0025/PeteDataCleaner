#!/usr/bin/env python3
"""
🔍 Frontend Architecture Analyzer

Specialized analyzer for the frontend components, focusing on:
- Component modularity and reusability
- Data flow and state management
- Mapping and concatenation capabilities
- UI component relationships
- Backend integration points

This complements the main whatsworking.py utility by providing 
frontend-specific analysis.
"""

import os
import ast
import json
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class ComponentAnalysis:
    """Analysis of a frontend component"""
    file: str
    component_type: str  # Dialog, Widget, Component, Utility
    imports_backend: bool
    uses_pyqt: bool
    has_mapping_logic: bool
    has_concatenation: bool
    connects_to: List[str]  # Other components it uses
    ui_elements: List[str]  # Buttons, labels, etc.
    event_handlers: List[str]  # Functions that handle events
    data_methods: List[str]  # Methods that handle data
    complexity: int

class FrontendAnalyzer:
    """Analyzes frontend architecture and capabilities"""
    
    def __init__(self, frontend_dir: str = 'frontend'):
        self.frontend_dir = Path(frontend_dir)
        self.components: List[ComponentAnalysis] = []
        
        # Patterns for UI analysis
        self.ui_patterns = {
            'widgets': ['QWidget', 'QDialog', 'QMainWindow', 'QLabel', 'QButton', 
                       'QLineEdit', 'QTableWidget', 'QComboBox', 'QCheckBox'],
            'layouts': ['QVBoxLayout', 'QHBoxLayout', 'QGridLayout', 'QFormLayout'],
            'events': ['clicked', 'pressed', 'changed', 'selected', 'activated'],
            'mapping': ['map', 'transform', 'standardize', 'concatenate', 'combine'],
            'data': ['load', 'save', 'export', 'import', 'process', 'validate']
        }

    def analyze_component(self, filepath: Path) -> Optional[ComponentAnalysis]:
        """Analyze a single frontend component file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content, filename=str(filepath))
        except (SyntaxError, UnicodeDecodeError) as e:
            print(f"Could not parse {filepath}: {e}")
            return None

        # Extract information
        imports = set()
        classes = []
        functions = []
        ui_elements = []
        event_handlers = []
        data_methods = []
        connects_to = []
        
        imports_backend = False
        uses_pyqt = False
        has_mapping_logic = False
        has_concatenation = False
        complexity = 0

        # Walk AST
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name
                    imports.add(module)
                    if 'backend' in module:
                        imports_backend = True
                    if 'PyQt' in module or 'Qt' in module:
                        uses_pyqt = True
                        
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
                    if 'backend' in node.module:
                        imports_backend = True
                    if 'PyQt' in node.module or 'Qt' in node.module:
                        uses_pyqt = True
                        
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
                complexity += len(node.body)
                
                # Check for UI widgets
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        if base.id in self.ui_patterns['widgets']:
                            ui_elements.append(base.id)
                            
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)
                func_name_lower = node.name.lower()
                
                # Classify function types
                if any(pattern in func_name_lower for pattern in self.ui_patterns['events']):
                    event_handlers.append(node.name)
                elif any(pattern in func_name_lower for pattern in self.ui_patterns['data']):
                    data_methods.append(node.name)
                elif any(pattern in func_name_lower for pattern in self.ui_patterns['mapping']):
                    has_mapping_logic = True
                    data_methods.append(node.name)
                    
                if 'concat' in func_name_lower or 'combine' in func_name_lower:
                    has_concatenation = True
                    
        # Determine component type
        component_type = self._classify_component_type(filepath, classes, functions)
        
        # Check content for UI elements and connections
        for widget in self.ui_patterns['widgets']:
            if widget in content:
                if widget not in ui_elements:
                    ui_elements.append(widget)
                    
        # Look for connections to other components
        for comp_import in imports:
            if 'frontend' in comp_import or any(comp in comp_import for comp in ['dialog', 'component', 'widget']):
                connects_to.append(comp_import)

        return ComponentAnalysis(
            file=str(filepath),
            component_type=component_type,
            imports_backend=imports_backend,
            uses_pyqt=uses_pyqt,
            has_mapping_logic=has_mapping_logic,
            has_concatenation=has_concatenation,
            connects_to=connects_to,
            ui_elements=list(set(ui_elements)),
            event_handlers=event_handlers,
            data_methods=data_methods,
            complexity=complexity
        )

    def _classify_component_type(self, filepath: Path, classes: List[str], functions: List[str]) -> str:
        """Classify the type of frontend component"""
        filename = filepath.name.lower()
        
        if 'dialog' in filename or any('dialog' in cls.lower() for cls in classes):
            return 'Dialog'
        elif 'component' in filename or 'base' in filename:
            return 'Component'  
        elif 'main' in filename or 'window' in filename:
            return 'MainWindow'
        elif 'util' in filename or 'helper' in filename:
            return 'Utility'
        elif 'constant' in filename or 'config' in filename:
            return 'Configuration'
        else:
            return 'Widget'

    def analyze_frontend(self) -> None:
        """Analyze all frontend components"""
        print(f"🎨 Analyzing frontend at {self.frontend_dir}")
        
        if not self.frontend_dir.exists():
            print(f"Frontend directory {self.frontend_dir} not found")
            return
            
        py_files = list(self.frontend_dir.rglob('*.py'))
        print(f"Found {len(py_files)} frontend Python files")
        
        for filepath in py_files:
            analysis = self.analyze_component(filepath)
            if analysis:
                self.components.append(analysis)
                
        print(f"✅ Analyzed {len(self.components)} frontend components")

    def generate_frontend_report(self) -> str:
        """Generate detailed frontend analysis report"""
        lines = [
            "# 🎨 Frontend Architecture Analysis",
            "",
            f"**Components Analyzed:** {len(self.components)}",
            "",
            "---",
            ""
        ]
        
        # Summary by component type
        by_type = defaultdict(list)
        for comp in self.components:
            by_type[comp.component_type].append(comp)
            
        lines.extend([
            "## 📊 Component Distribution",
            ""
        ])
        
        for comp_type, comps in sorted(by_type.items()):
            lines.append(f"- **{comp_type}:** {len(comps)} files")
            
        lines.extend(["", "---", ""])
        
        # Backend Integration Analysis
        backend_integrated = [c for c in self.components if c.imports_backend]
        lines.extend([
            "## 🔌 Backend Integration",
            "",
            f"**Files importing backend:** {len(backend_integrated)} of {len(self.components)}",
            ""
        ])
        
        if backend_integrated:
            for comp in backend_integrated:
                rel_path = Path(comp.file).name  # Just use filename for simplicity
                lines.append(f"- `{rel_path}` ({comp.component_type})")
        else:
            lines.append("- No backend integration detected")
            
        lines.extend(["", "---", ""])
        
        # Mapping & Concatenation Capabilities
        mapping_comps = [c for c in self.components if c.has_mapping_logic]
        concat_comps = [c for c in self.components if c.has_concatenation]
        
        lines.extend([
            "## 🗺️ Data Mapping & Concatenation Capabilities",
            "",
            f"**Files with mapping logic:** {len(mapping_comps)}",
            f"**Files with concatenation:** {len(concat_comps)}",
            ""
        ])
        
        if mapping_comps:
            lines.append("### Mapping Components:")
            for comp in mapping_comps:
                rel_path = Path(comp.file).name
                data_methods_str = ', '.join(comp.data_methods[:3])
                if len(comp.data_methods) > 3:
                    data_methods_str += f" (+{len(comp.data_methods)-3} more)"
                lines.append(f"- `{rel_path}` - Methods: {data_methods_str}")
            lines.append("")
            
        if concat_comps:
            lines.append("### Concatenation Components:")
            for comp in concat_comps:
                rel_path = Path(comp.file).name
                lines.append(f"- `{rel_path}` ({comp.component_type})")
            lines.append("")
            
        lines.extend(["---", ""])
        
        # Detailed Component Analysis
        lines.extend([
            "## 📋 Detailed Component Analysis",
            ""
        ])
        
        for comp_type in sorted(by_type.keys()):
            comps = sorted(by_type[comp_type], key=lambda x: Path(x.file).name)
            lines.extend([
                f"### {comp_type} Components ({len(comps)})",
                ""
            ])
            
            for comp in comps:
                rel_path = Path(comp.file).name
                lines.append(f"#### 📄 `{rel_path}`")
                
                # Basic info
                features = []
                if comp.uses_pyqt:
                    features.append("🖼️ PyQt5")
                if comp.imports_backend:
                    features.append("🔌 Backend")
                if comp.has_mapping_logic:
                    features.append("🗺️ Mapping")
                if comp.has_concatenation:
                    features.append("🔗 Concatenation")
                    
                if features:
                    lines.append(f"**Features:** {' | '.join(features)}")
                    
                lines.append(f"**Complexity:** {comp.complexity}")
                
                # UI Elements
                if comp.ui_elements:
                    lines.append(f"- **UI Elements:** {', '.join(comp.ui_elements)}")
                    
                # Event Handlers
                if comp.event_handlers:
                    handlers_str = ', '.join(comp.event_handlers[:3])
                    if len(comp.event_handlers) > 3:
                        handlers_str += f" (+{len(comp.event_handlers)-3} more)"
                    lines.append(f"- **Event Handlers:** {handlers_str}")
                    
                # Data Methods
                if comp.data_methods:
                    methods_str = ', '.join(comp.data_methods[:3])
                    if len(comp.data_methods) > 3:
                        methods_str += f" (+{len(comp.data_methods)-3} more)"
                    lines.append(f"- **Data Methods:** {methods_str}")
                    
                # Connections
                if comp.connects_to:
                    lines.append(f"- **Connects To:** {', '.join(comp.connects_to)}")
                    
                lines.append("")
                
        # Architecture Recommendations
        lines.extend([
            "---",
            "",
            "## 💡 Architecture Analysis & Recommendations",
            ""
        ])
        
        # Modularity check
        total_complexity = sum(c.complexity for c in self.components)
        avg_complexity = total_complexity / len(self.components) if self.components else 0
        
        lines.append(f"**Average Component Complexity:** {avg_complexity:.1f}")
        
        # Find highly complex components
        complex_comps = [c for c in self.components if c.complexity > avg_complexity * 2]
        if complex_comps:
            lines.extend([
                "",
                "### 🚨 High Complexity Components (Consider Refactoring):",
                ""
            ])
            for comp in sorted(complex_comps, key=lambda x: x.complexity, reverse=True):
                rel_path = Path(comp.file).name
                lines.append(f"- `{rel_path}` (Complexity: {comp.complexity})")
                
        # Backend integration suggestions
        lines.extend([
            "",
            "### 🔌 Backend Integration Suggestions:",
            ""
        ])
        
        non_integrated = [c for c in self.components if not c.imports_backend and c.has_mapping_logic]
        if non_integrated:
            lines.append("**Components with mapping logic that could benefit from backend integration:**")
            for comp in non_integrated:
                rel_path = Path(comp.file).name
                lines.append(f"- `{rel_path}`")
        else:
            lines.append("- Good backend integration for mapping components ✅")
            
        # Concatenation workflow analysis
        lines.extend([
            "",
            "### 🔗 Concatenation Workflow:",
            ""
        ])
        
        if concat_comps:
            lines.append("**Files handling concatenation (e.g., FirstName + LastName → Seller):**")
            for comp in concat_comps:
                rel_path = Path(comp.file).name
                lines.append(f"- `{rel_path}` ({comp.component_type})")
        else:
            lines.append("- ⚠️ No concatenation logic detected. Consider adding for field combination.")
            
        return '\n'.join(lines)

    def analyze_data_flow(self) -> Dict[str, Any]:
        """Analyze data flow patterns in the frontend"""
        flow_analysis = {
            'upload_handlers': [],
            'mapping_components': [],
            'preview_components': [],
            'export_components': [],
            'concatenation_points': []
        }
        
        for comp in self.components:
            rel_path = Path(comp.file).name
            
            # Check for upload handling
            if any('upload' in method.lower() or 'load' in method.lower() 
                  for method in comp.data_methods):
                flow_analysis['upload_handlers'].append(rel_path)
                
            # Check for mapping
            if comp.has_mapping_logic:
                flow_analysis['mapping_components'].append(rel_path)
                
            # Check for preview
            if any('preview' in method.lower() or 'show' in method.lower() 
                  for method in comp.data_methods + comp.event_handlers):
                flow_analysis['preview_components'].append(rel_path)
                
            # Check for export
            if any('export' in method.lower() or 'download' in method.lower() or 'save' in method.lower()
                  for method in comp.data_methods):
                flow_analysis['export_components'].append(rel_path)
                
            # Check for concatenation
            if comp.has_concatenation:
                flow_analysis['concatenation_points'].append(rel_path)
                
        return flow_analysis

def main():
    """Run frontend analysis"""
    analyzer = FrontendAnalyzer()
    analyzer.analyze_frontend()
    
    if not analyzer.components:
        print("No frontend components found to analyze")
        return
        
    # Generate report
    report = analyzer.generate_frontend_report()
    
    # Save report
    os.makedirs('DEV_MAN', exist_ok=True)
    timestamp = str(int(datetime.datetime.now().timestamp()))
    filename = f"DEV_MAN/FRONTEND_ANALYSIS_{timestamp}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
        
    print(f"✅ Frontend analysis saved to: {filename}")
    
    # Data flow analysis
    flow = analyzer.analyze_data_flow()
    print(f"\n📊 Data Flow Summary:")
    print(f"  - Upload handlers: {len(flow['upload_handlers'])}")
    print(f"  - Mapping components: {len(flow['mapping_components'])}")
    print(f"  - Preview components: {len(flow['preview_components'])}")
    print(f"  - Export components: {len(flow['export_components'])}")
    print(f"  - Concatenation points: {len(flow['concatenation_points'])}")

if __name__ == '__main__':
    import datetime
    main()