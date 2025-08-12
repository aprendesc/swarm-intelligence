import io
import sys
import ast
import traceback
import json
import time
import signal
from contextlib import redirect_stdout, redirect_stderr
import requests

class PythonCodeInterpreterToolClass:
    def __init__(self, timeout_seconds=30):
        self.name = "python_code_interpreter"
        self.description = "Run a Python code in the current project environment and catch the prints in the code as output. So think carefully what you will print."
        self.args = [{'name': 'code_str', 'type': 'string', 'description': 'String of the Python code to run.', 'required': True}]
        self.timeout_seconds = timeout_seconds

    def initialize(self):
        pass

    def get_tool_dict(self):
        return self._gen_tool_dict(self.name, self.description, self.args)

    def _validate_syntax(self, code_str):
        """Validate Python syntax before execution"""
        try:
            ast.parse(code_str)
            return True, None
        except SyntaxError as e:
            return False, f"Syntax Error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, f"Parse Error: {str(e)}"

    def _safe_exec(self, code_str, global_vars):
        """Execute code with proper error handling and context"""
        buf_out = io.StringIO()
        buf_err = io.StringIO()

        # Store original values
        original_stdout = sys.stdout
        original_stderr = sys.stderr

        execution_info = {'start_time': time.time(), 'end_time': None, 'execution_duration': None, 'memory_before': None, 'memory_after': None, 'lines_executed': 0}

        try:
            # Set up timeout
            if hasattr(signal, 'SIGALRM'):  # Unix systems
                signal.signal(signal.SIGALRM, self.timeout_handler)
                signal.alarm(self.timeout_seconds)

            with redirect_stdout(buf_out), redirect_stderr(buf_err):
                # Count lines for execution info
                execution_info['lines_executed'] = len([line for line in code_str.split('\n') if line.strip()])
                # Execute the code
                exec(code_str, global_vars)

            execution_info['end_time'] = time.time()
            execution_info['execution_duration'] = execution_info['end_time'] - execution_info['start_time']

            return buf_out.getvalue(), buf_err.getvalue(), None, execution_info

        except TimeoutError:
            return buf_out.getvalue(), buf_err.getvalue(), f"TIMEOUT: Code execution exceeded {self.timeout_seconds} seconds", execution_info
        except Exception as e:
            execution_info['end_time'] = time.time()
            execution_info['execution_duration'] = execution_info['end_time'] - execution_info['start_time']

            # Get detailed traceback
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)

            # Extract relevant information
            error_details = {'type': exc_type.__name__, 'message': str(exc_value), 'traceback': ''.join(tb_lines), 'line_number': None, 'file_context': None}

            # Try to get line number from traceback
            if exc_traceback:
                tb = exc_traceback
                while tb.tb_next:
                    tb = tb.tb_next
                error_details['line_number'] = tb.tb_lineno

                # Get context around the error line
                code_lines = code_str.split('\n')
                if error_details['line_number'] and error_details['line_number'] <= len(code_lines):
                    line_idx = error_details['line_number'] - 1
                    start_idx = max(0, line_idx - 2)
                    end_idx = min(len(code_lines), line_idx + 3)

                    context_lines = []
                    for i in range(start_idx, end_idx):
                        marker = ">>> " if i == line_idx else "    "
                        context_lines.append(f"{marker}{i + 1}: {code_lines[i]}")

                    error_details['file_context'] = '\n'.join(context_lines)

            return buf_out.getvalue(), buf_err.getvalue(), error_details, execution_info

        finally:
            # Clean up timeout
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)

            # Restore original stdout/stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr

    def run(self, code_str):
        if not code_str or not code_str.strip():
            return json.dumps({"success": False, "code_output": "", "error": "Empty code provided", "error_type": "ValidationError", "execution_info": None, "debug_info": {"suggestion": "Please provide valid Python code to execute"}})

        # Validate syntax first
        is_valid, syntax_error = self._validate_syntax(code_str)
        if not is_valid:
            return json.dumps({"success": False, "code_output": "", "error": syntax_error, "error_type": "SyntaxError", "execution_info": None, "debug_info": {"suggestion": "Fix the syntax error before running the code", "code_preview": code_str[:200] + "..." if len(code_str) > 200 else code_str}})

        # Prepare execution environment
        global_vars = {'__builtins__': __builtins__, 'requests': requests, 'json': json,}

        # Execute code
        stdout_content, stderr_content, error_details, execution_info = self._safe_exec(code_str, global_vars)

        # Prepare result
        result = {"success": error_details is None, "code_output": stdout_content, "execution_info": {"duration_seconds": execution_info.get('execution_duration'), "lines_executed": execution_info.get('lines_executed'), "completed": execution_info.get('end_time') is not None}}

        # Handle errors
        if error_details:
            if isinstance(error_details, dict):
                result.update({"error": error_details['message'], "error_type": error_details['type'], "error_traceback": error_details['traceback'], "error_line": error_details['line_number'], "debug_info": {"error_context": error_details['file_context'], "suggestion": self._get_error_suggestion(error_details['type'], error_details['message']), "common_fixes": self._get_common_fixes(error_details['type'])}})
            else:
                result.update({"error": str(error_details), "error_type": "ExecutionError", "debug_info": {"suggestion": "Check the error message for details"}})
        else:
            result["error"] = None
            result["error_type"] = None

        # Add stderr if present (warnings, etc.)
        if stderr_content:
            result["warnings"] = stderr_content
            if not error_details:  # Only add debug info for warnings if no errors
                result["debug_info"] = {"note": "Code executed successfully but produced warnings/messages in stderr"}

        # Add code analysis
        result["code_analysis"] = self._analyze_code(code_str)

        return json.dumps(result, indent=2)

    def _get_error_suggestion(self, error_type, error_message):
        """Provide helpful suggestions based on error type"""
        suggestions = {
            'NameError': "Check if all variables and functions are defined before use",
            'ImportError': "Verify that the module is installed and the import path is correct",
            'ModuleNotFoundError': "Install the required module or check the module name",
            'TypeError': "Check data types and function arguments",
            'ValueError': "Verify that values are in the expected format or range",
            'KeyError': "Check if the key exists in the dictionary",
            'IndexError': "Verify list/array indices are within bounds",
            'AttributeError': "Check if the object has the specified attribute or method",
            'FileNotFoundError': "Verify the file path exists and is accessible",
            'ZeroDivisionError': "Check for division by zero in calculations",
            'IndentationError': "Fix code indentation",
            'SyntaxError': "Check Python syntax, parentheses, quotes, and colons"
        }
        return suggestions.get(error_type, "Review the error message and traceback for details")

    def _get_common_fixes(self, error_type):
        """Provide common fixes for error types"""
        fixes = {
            'NameError': ["Define the variable before using it", "Check for typos in variable names", "Import required modules"],
            'ImportError': ["pip install <module_name>", "Check module spelling", "Use correct import syntax"],
            'TypeError': ["Check function arguments", "Verify data types", "Use appropriate type conversion"],
            'ValueError': ["Validate input values", "Check value ranges", "Use try-except for conversion"],
            'KeyError': ["Use dict.get() method", "Check if key exists with 'in' operator", "Handle missing keys"],
            'IndexError': ["Check list length", "Use try-except for index access", "Validate index ranges"]
        }
        return fixes.get(error_type, ["Review error message", "Check Python documentation", "Debug step by step"])

    def _analyze_code(self, code_str):
        """Analyze code for potential issues and suggestions"""
        analysis = {
            "line_count": len(code_str.split('\n')),
            "has_imports": 'import' in code_str,
            "has_functions": 'def ' in code_str,
            "has_classes": 'class ' in code_str,
            "has_loops": any(keyword in code_str for keyword in ['for ', 'while ']),
            "has_conditionals": any(keyword in code_str for keyword in ['if ', 'elif ', 'else:']),
            "complexity": "simple" if len(code_str.split('\n')) < 10 else "moderate" if len(
                code_str.split('\n')) < 50 else "complex"
        }
        return analysis

    def _gen_tool_dict(self, tool_name, tool_description, tool_args=[{'name': '', 'type': '', 'description': '', 'required': False}]):
        args_dict = {}
        required_list = []
        for a in tool_args:
            arg_name = a['name']
            arg_type = a['type']
            arg_description = a['description']
            if a['required']:
                required_list.append(arg_name)
            args_dict[arg_name] = {"type": arg_type, "description": arg_description}
        return {"type": "function", "function": {"name": tool_name, "description": tool_description, "parameters": {"type": "object", "properties": args_dict, "required": required_list}}}

    class TimeoutError(Exception):
        pass

    def timeout_handler(self, signum, frame):
        raise TimeoutError("Code execution timed out")
