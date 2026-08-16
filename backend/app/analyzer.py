from __future__ import annotations

import ast
import re
from pathlib import Path
from collections import defaultdict

ALLOWED_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java",
    ".c", ".h", ".cpp", ".hpp", ".cob", ".cbl",
    ".f", ".f90", ".for"
}

SECRET_PATTERNS = [
    ("Hard-coded credential", re.compile(
        r"(?i)\b(password|passwd|api[_-]?key|secret|token)\b\s*[:=]\s*['\"][^'\"]+['\"]"
    )),
]

DANGEROUS_PATTERNS = [
    ("Dynamic code execution", re.compile(r"\beval\s*\(")),
    ("Shell command execution", re.compile(r"\bos\.system\s*\(|\bsubprocess\.(run|Popen|call)\s*\(")),
    ("SQL string concatenation", re.compile(r"(?i)(select|insert|update|delete).{0,100}[+]\s*[A-Za-z_]")),
]

def safe_extract_name(name: str) -> str:
    # Keep uploads inside the server workspace.
    return Path(name).name

def read_source(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def analyze_python_imports(source: str):
    deps = []
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                deps.extend(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                deps.append(node.module.split(".")[0])
    except SyntaxError:
        pass
    return sorted(set(deps))

def analyze_file(path: Path):
    source = read_source(path)
    lines = source.count("\n") + (1 if source else 0)
    result = {
        "path": str(path),
        "name": path.name,
        "extension": path.suffix.lower(),
        "lines": lines,
        "language": path.suffix.lower().lstrip(".") or "unknown",
        "dependencies": [],
    }

    if path.suffix.lower() == ".py":
        result["dependencies"] = analyze_python_imports(source)
    else:
        # Lightweight include/import detection for other legacy languages.
        matches = re.findall(
            r"(?im)^\s*(?:import|include|#include|uses|use)\s+[<\"']?([A-Za-z0-9_./-]+)",
            source
        )
        result["dependencies"] = sorted(set(matches))

    return result, source

def security_scan(path: str, source: str):
    findings = []
    for label, pattern in SECRET_PATTERNS + DANGEROUS_PATTERNS:
        for match in pattern.finditer(source):
            line = source[:match.start()].count("\n") + 1
            severity = "HIGH" if label in {
                "Hard-coded credential", "Dynamic code execution", "Shell command execution"
            } else "MEDIUM"
            findings.append({
                "file": path,
                "line": line,
                "severity": severity,
                "type": label,
                "message": f"Potential {label.lower()} pattern detected."
            })
    return findings

def modernization_preview(path: str, source: str):
    ext = Path(path).suffix.lower()
    suggestions = []

    if ext in {".cob", ".cbl"}:
        suggestions.append({
            "file": path,
            "target": "Python/FastAPI",
            "reason": "COBOL source detected; identify business rules and expose them through a typed service layer."
        })
    elif ext in {".f", ".f90", ".for"}:
        suggestions.append({
            "file": path,
            "target": "Python",
            "reason": "Fortran source detected; isolate numerical/business logic before translating modules."
        })
    elif ext == ".py":
        if "print " in source:
            suggestions.append({
                "file": path,
                "target": "Modern Python",
                "reason": "Legacy print syntax detected; migrate to Python 3 print()."
            })
        if "os.system(" in source:
            suggestions.append({
                "file": path,
                "target": "Modern Python",
                "reason": "Replace shell execution with a safer subprocess/API abstraction."
            })

    if not suggestions:
        suggestions.append({
            "file": path,
            "target": "Modern service",
            "reason": "Analyze business rules, dependencies, interfaces, and tests before automated rewrite."
        })
    return suggestions

def build_documentation(file_results, dependencies, findings):
    lines = [
        "# LegacyMind AI — Generated Codebase Documentation",
        "",
        f"Files analyzed: **{len(file_results)}**",
        f"Total lines: **{sum(x['lines'] for x in file_results)}**",
        f"Security findings: **{len(findings)}**",
        "",
        "## Files",
    ]
    for item in file_results:
        deps = ", ".join(item["dependencies"]) if item["dependencies"] else "None detected"
        lines.append(f"- `{item['path']}` — {item['language']}, {item['lines']} lines — dependencies: {deps}")

    lines += ["", "## Dependency overview"]
    if dependencies:
        for dep in dependencies:
            lines.append(f"- `{dep['dependency']}` referenced by `{dep['file']}`")
    else:
        lines.append("- No dependencies detected by the MVP analyzer.")

    lines += [
        "",
        "## Security",
        "This section contains heuristic findings from the MVP scanner. Run dedicated SAST/dependency tools before production use."
    ]
    return "\n".join(lines)

def analyze_workspace(root: Path):
    source_files = [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in ALLOWED_EXTENSIONS]

    file_results = []
    dependency_rows = []
    findings = []
    modernization = []

    for path in source_files:
        result, source = analyze_file(path)
        relative = str(path.relative_to(root))
        result["path"] = relative
        file_results.append(result)

        for dep in result["dependencies"]:
            dependency_rows.append({"file": relative, "dependency": dep})

        findings.extend(security_scan(relative, source))
        modernization.extend(modernization_preview(relative, source))

    documentation = build_documentation(file_results, dependency_rows, findings)

    critical = sum(1 for f in findings if f["severity"] == "HIGH")
    verification = {
        "status": "PASS" if critical == 0 else "REVIEW_REQUIRED",
        "files_checked": len(file_results),
        "security_findings": len(findings),
        "critical_findings": critical,
        "message": (
            "No high-severity heuristic findings detected."
            if critical == 0
            else "High-severity findings require human review before modernization/deployment."
        ),
    }

    summary = {
        "files": len(file_results),
        "lines": sum(x["lines"] for x in file_results),
        "dependencies": len(dependency_rows),
        "security_findings": len(findings),
        "critical_findings": critical,
    }

    return {
        "summary": summary,
        "files": file_results,
        "dependencies": dependency_rows,
        "security_findings": findings,
        "documentation": documentation,
        "modernization": modernization,
        "verification": verification,
    }
