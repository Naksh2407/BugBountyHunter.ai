import os
import ast

class ContextAgent:

    @staticmethod
    def extract_context(
        file_path: str,
        line_number: int,
        radius: int = 30
    ) -> tuple[str, int, int]:
        """
        Dynamically extracts context around the issue line.
        For Python files, it uses the AST to locate the exact enclosing function/class.
        Falls back to lexical line scanning for non-Python or unparseable files.
        Returns a tuple of (context_string, start_line_idx, end_line_idx).
        """
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        total_lines = len(lines)
        target_idx = line_number - 1  # 0-indexed line index
        target_idx = max(0, min(total_lines - 1, target_idx))

        ext = os.path.splitext(file_path)[-1].lower()

        # AST Parsing context for Python files (Kaggle Day 3 Context Engineering)
        if ext == ".py":
            try:
                code_content = "".join(lines)
                tree = ast.parse(code_content)
                
                enclosing_node = None
                
                # Walk the AST to find the deepest class/function containing the line_number
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        # ast node lines are 1-indexed
                        start_line = getattr(node, "lineno", None)
                        end_line = getattr(node, "end_lineno", None)
                        if start_line and end_line:
                            if start_line <= line_number <= end_line:
                                if not enclosing_node:
                                    enclosing_node = node
                                else:
                                    # Select the narrower/deeper node
                                    enc_start = getattr(enclosing_node, "lineno")
                                    enc_end = getattr(enclosing_node, "end_lineno")
                                    if (start_line >= enc_start and end_line <= enc_end):
                                        enclosing_node = node
                
                if enclosing_node:
                    start = enclosing_node.lineno - 1
                    end = enclosing_node.end_lineno
                    print(f"AST context extraction succeeded for {os.path.basename(file_path)}: found node {type(enclosing_node).__name__} on lines {start+1}-{end}")
                    return "".join(lines[start:end]), start, end
            except Exception as e:
                print(f"AST parsing failed for {file_path}: {e}. Falling back to lexical scan.")

        # Lexical extraction fallback (for JS/TS or failed python parses)
        start = max(0, target_idx - radius)
        end = min(total_lines, target_idx + radius)

        if ext in (".py", ".js", ".ts", ".tsx", ".jsx"):
            block_start = -1
            block_indent = -1
            
            # Scan upwards to find enclosing class or function
            for i in range(target_idx, max(-1, target_idx - 100), -1):
                line = lines[i]
                stripped = line.lstrip()
                
                is_py_block = ext == ".py" and (stripped.startswith("def ") or stripped.startswith("class ") or stripped.startswith("async def "))
                is_js_block = ext != ".py" and ("function" in stripped or "class " in stripped or "=>" in stripped)
                
                if is_py_block or is_js_block:
                    block_start = i
                    block_indent = len(line) - len(stripped)
                    break
            
            if block_start != -1:
                start = block_start
                block_end = end
                for j in range(target_idx + 1, min(total_lines, target_idx + 150)):
                    line = lines[j]
                    stripped = line.strip()
                    if not stripped:
                        continue
                    
                    current_indent = len(line) - len(line.lstrip())
                    
                    if ext == ".py":
                        if current_indent <= block_indent:
                            block_end = j
                            break
                    else:
                        if current_indent <= block_indent:
                            block_end = j + 1
                            break
                
                end = max(block_end, target_idx + 1)
                
        return "".join(lines[start:end]), start, end