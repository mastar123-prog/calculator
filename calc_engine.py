"""
calc_engine.py - Core evaluation, parsing, and analysis engine for the calculator and grapher.
"""

import math
import numpy as np
import sympy as sp
from typing import Dict, Any, Tuple, Optional, List

# Define sympy symbols
x_sym = sp.Symbol('x')

SAFE_MATH_NAMES = {
    # Constants
    'pi': math.pi,
    'e': math.e,
    'phi': (1 + 5**0.5) / 2,
    'inf': math.inf,
    # Basic
    'abs': abs,
    'round': round,
    'sqrt': math.sqrt,
    'cbrt': lambda v: math.copysign(abs(v)**(1/3), v),
    # Trigonometry (default in rad, can be wrapped)
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'asin': math.asin,
    'acos': math.acos,
    'atan': math.atan,
    'sinh': math.sinh,
    'cosh': math.cosh,
    'tanh': math.tanh,
    # Exponential / Logarithmic
    'exp': math.exp,
    'log': math.log10,  # standard calculator log is base 10
    'ln': math.log,     # natural log
    'log2': math.log2,
    # Misc
    'fact': math.factorial,
    'factorial': math.factorial,
    'floor': math.floor,
    'ceil': math.ceil,
}

def preprocess_expression(expr: str, angle_mode: str = "RAD") -> str:
    """Preprocess user input into a valid python/sympy expression."""
    expr = expr.strip()
    if not expr:
        return ""
    
    # Replace display symbols
    expr = expr.replace('×', '*').replace('÷', '/').replace('^', '**')
    expr = expr.replace('π', 'pi').replace('√', 'sqrt')
    
    # If angle mode is DEG, wrap trig function inputs
    # E.g., sin(30) -> sin(radians(30)) or sin(30 * pi / 180)
    if angle_mode == "DEG":
        # We can handle degree conversion through custom functions in dict
        pass
        
    return expr

def evaluate_expression(expr: str, angle_mode: str = "RAD") -> Dict[str, Any]:
    """
    Safely evaluate a mathematical expression.
    Returns dict with {success, result, error, formatted_latex}
    """
    cleaned = preprocess_expression(expr, angle_mode)
    if not cleaned:
        return {"success": False, "result": None, "error": "Empty expression", "latex": ""}
    
    try:
        # Build evaluation environment
        context = dict(SAFE_MATH_NAMES)
        
        # Sympy representation for LaTeX
        try:
            sympy_expr = sp.sympify(
                cleaned.replace('ln', 'log').replace('log(', 'log10('),
                locals={'log10': lambda a: sp.log(a, 10), 'pi': sp.pi, 'e': sp.E}
            )
            latex_str = sp.latex(sympy_expr)
        except Exception:
            sympy_expr = None
            latex_str = cleaned
        
        if angle_mode == "DEG":
            context['sin'] = lambda a: math.sin(math.radians(a))
            context['cos'] = lambda a: math.cos(math.radians(a))
            context['tan'] = lambda a: math.tan(math.radians(a))
            context['asin'] = lambda a: math.degrees(math.asin(a))
            context['acos'] = lambda a: math.degrees(math.acos(a))
            context['atan'] = lambda a: math.degrees(math.atan(a))
            
            raw_res = eval(cleaned, {"__builtins__": None}, context)
            if isinstance(raw_res, (int, float)):
                num_val = float(raw_res)
                if abs(num_val - round(num_val)) < 1e-12:
                    formatted_res = str(int(round(num_val)))
                elif abs(num_val) < 1e-4 or abs(num_val) > 1e10:
                    formatted_res = f"{num_val:.6e}"
                else:
                    formatted_res = f"{num_val:.8g}"
            else:
                formatted_res = str(raw_res)
        else:
            # RAD mode
            try:
                num_val = float(sympy_expr.evalf())
                if abs(num_val - round(num_val)) < 1e-12:
                    formatted_res = str(int(round(num_val)))
                elif abs(num_val) < 1e-4 or abs(num_val) > 1e10:
                    formatted_res = f"{num_val:.6e}"
                else:
                    formatted_res = f"{num_val:.8g}"
            except Exception:
                raw_res = eval(cleaned, {"__builtins__": None}, context)
                if isinstance(raw_res, (int, float)):
                    num_val = float(raw_res)
                    if abs(num_val - round(num_val)) < 1e-12:
                        formatted_res = str(int(round(num_val)))
                    else:
                        formatted_res = f"{num_val:.8g}"
                else:
                    formatted_res = str(raw_res)
        
        return {
            "success": True,
            "result": formatted_res,
            "raw_value": num_val if 'num_val' in locals() else formatted_res,
            "latex": latex_str,
            "error": None
        }
    except ZeroDivisionError:
        return {"success": False, "result": None, "error": "Error: Division by zero", "latex": ""}
    except ValueError as e:
        return {"success": False, "result": None, "error": f"Math error: {str(e)}", "latex": ""}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Syntax error: {str(e)}", "latex": ""}

def evaluate_graph_function(expr_str: str, x_vals: np.ndarray) -> Tuple[np.ndarray, Optional[str]]:
    """
    Evaluates f(x) over a numpy array of x values.
    Returns (y_vals, error_message).
    Handles discontinuities and invalid values smoothly.
    """
    cleaned = expr_str.strip().replace('^', '**').replace('×', '*').replace('÷', '/').replace('π', 'pi')
    
    # Custom numpy mapping
    np_dict = {
        'x': x_vals,
        'pi': np.pi,
        'e': np.e,
        'sin': np.sin,
        'cos': np.cos,
        'tan': np.tan,
        'arcsin': np.arcsin,
        'asin': np.arcsin,
        'arccos': np.arccos,
        'acos': np.arccos,
        'arctan': np.arctan,
        'atan': np.arctan,
        'sinh': np.sinh,
        'cosh': np.cosh,
        'tanh': np.tanh,
        'sqrt': np.sqrt,
        'cbrt': np.cbrt,
        'abs': np.abs,
        'exp': np.exp,
        'log': np.log10,
        'ln': np.log,
        'log2': np.log2,
        'floor': np.floor,
        'ceil': np.ceil,
        'sinc': np.sinc,
    }

    try:
        # Sympy parse to ensure valid structure
        sym_expr = sp.sympify(cleaned.replace('ln', 'log'))
        # Generate vectorized function with lambdify
        fn = sp.lambdify(x_sym, sym_expr, modules=['numpy', {'ln': np.log, 'log': np.log10}])
        y_vals = fn(x_vals)
        
        # If output is a constant scalar, broadcast to match x_vals shape
        if np.isscalar(y_vals):
            y_vals = np.full_like(x_vals, float(y_vals))
        else:
            y_vals = np.array(y_vals, dtype=float)
            
        # Replace inf and massive asymptotes with NaN for clean plotting
        y_vals[np.isinf(y_vals)] = np.nan
        y_vals[np.abs(y_vals) > 1e6] = np.nan
        
        return y_vals, None
    except Exception as e:
        return np.full_like(x_vals, np.nan), str(e)

def analyze_function(expr_str: str) -> Dict[str, Any]:
    """
    Uses SymPy to analytically compute:
    - Derivative f'(x)
    - Indefinite integral ∫ f(x) dx
    - Roots / zeros
    - Critical points (extrema / inflection)
    """
    cleaned = expr_str.strip().replace('^', '**').replace('×', '*').replace('÷', '/').replace('π', 'pi')
    try:
        sym_expr = sp.sympify(cleaned.replace('ln', 'log'), locals={'x': x_sym})
        
        # Derivative
        derivative = sp.diff(sym_expr, x_sym)
        derivative_latex = sp.latex(derivative)
        derivative_str = str(derivative)
        
        # Integral
        try:
            integral = sp.integrate(sym_expr, x_sym)
            integral_latex = sp.latex(integral) + r" + C"
        except Exception:
            integral_latex = r"\text{No closed form found}"
            
        # Roots / Zeros (analytical or real solutions within reasonable complexity)
        roots = []
        try:
            sol = sp.solve(sym_expr, x_sym)
            for s in sol:
                if s.is_real:
                    try:
                        val = float(s.evalf())
                        roots.append(round(val, 4))
                    except Exception:
                        pass
        except Exception:
            pass
            
        return {
            "success": True,
            "derivative_str": derivative_str,
            "derivative_latex": derivative_latex,
            "integral_latex": integral_latex,
            "roots": list(sorted(set(roots))) if roots else [],
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "derivative_str": "",
            "derivative_latex": "",
            "integral_latex": "",
            "roots": [],
            "error": str(e)
        }
