# ⚡ OmniCalc & Grapher Studio

A modern, glassmorphic scientific calculator and 2D function graphing studio built with **Python**, **Streamlit**, **Plotly**, and **SymPy**.

---

## 🚀 Features

### 1. 🧮 Scientific Calculator
- **Standard Arithmetic**: Addition (`+`), subtraction (`-`), multiplication (`*` / `×`), division (`/` / `÷`), powers (`^`), modulus (`%`), and nested parentheses `( )`.
- **Advanced Math Functions**: `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `sqrt`, `cbrt`, `abs`, `exp`, `log10`, `ln` (natural log), and factorial (`fact`).
- **Angle Mode Switcher**: Seamless toggle between **Radians (RAD)** and **Degrees (DEG)** for all trigonometric operations.
- **Precision & Display**:
  - OLED/Glassmorphic dark screen displaying the active formula and high-precision result.
  - Live LaTeX mathematical formatting display with expandable view.
- **Dual Input**: Use either the interactive on-screen touch/mouse keypad or direct keyboard input.

### 2. 🧹 Clear & Editing Operations
- **`C` (Clear)**: Clears the current input expression.
- **`AC` (All Clear)**: Resets input expression, last result, and LaTeX preview.
- **`⌫ Del` (Backspace)**: Removes the last entered character or operator.
- **`Ans`**: Recalls the previous calculation's result into the current formula.

### 3. 📜 Session History & Export
- **Dynamic History Log**: Tracks timestamps, evaluated expressions, and results.
- **Quick Recall**: Single-click `↩ Load` to edit a previous expression or `➕ Use Ans` to pipe a past result into your current formula.
- **Export Options**: One-click download of session logs in **JSON** or **CSV** formats, or save a formatted text log.
- **Clear History**: Instantly purge history whenever needed.

### 4. 📈 Interactive Graphing Studio
- **Multi-Function Plotting**: Plot primary function $f(x)$ and optional companion function $g(x)$ simultaneously.
- **Interactive Plotly Canvas**:
  - Smooth zoom, pan, box zoom, and crosshair hover tooltips with exact $(x, y)$ coordinates.
  - Coordinate axes ($x=0, y=0$) and configurable grid lines.
- **Analytical Calculus Tools**:
  - **Derivative Plotting**: Automatically differentiates and plots $f'(x)$ as a companion curve.
  - **Exact Formulas**: Analytical derivative $f'(x)$ and indefinite integral $\int f(x) dx$ rendered in LaTeX.
  - **Root Finder**: Detects real zeros $f(x)=0$ and highlights them with markers directly on the graph.
- **Presets Gallery**:
  - Sine Wave (`sin(x)`)
  - Damped Harmonic Oscillation (`exp(-0.2*x) * cos(3*x)`)
  - Cubic Polynomial (`x^3 - 3*x`)
  - Gaussian Bell Curve (`exp(-x^2)`)
  - Rational Function (`1 / (1 + x^2)`)
  - Sigmoid Curve (`1 / (1 + exp(-x))`)
  - Trigonometric Product (`sin(x) * cos(2*x)`)
- **Themes**: Switch between Midnight Cyber, Neon Glow, Solar Flare, and Clean High-Contrast.

---

## 📦 Installation & Setup

1. **Prerequisites**: Python 3.10+ installed.
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the App**:
   ```bash
   streamlit run app.py
   ```
   Or run the included batch file on Windows:
   ```cmd
   run.bat
   ```
4. **Open in Browser**: Navigate to `http://localhost:8501`.

---

## 🧪 Running Automated Tests

Run the test suite to verify math operations, angle modes, graphing, and calculus analysis:
```bash
python test_calc.py
```
