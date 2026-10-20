import streamlit as st
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import json
import calc_engine

# --- Page Configuration ---
st.set_page_config(
    page_title="OmniCalc & Grapher Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Enhanced Glassmorphic Dark CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Outfit:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    /* Background and containers */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1350px;
    }

    /* Screen display header card */
    .calc-screen {
        background: linear-gradient(145deg, #0f172a, #1e293b);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 18px;
        padding: 24px 28px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.7), 0 0 25px rgba(56, 189, 248, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .calc-screen::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
    }

    .calc-expr-row {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.25rem;
        color: #94a3b8;
        min-height: 32px;
        text-align: right;
        word-break: break-all;
        letter-spacing: 0.5px;
    }

    .calc-result-row {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.75rem;
        font-weight: 700;
        color: #f8fafc;
        text-align: right;
        word-break: break-all;
        letter-spacing: -0.5px;
        line-height: 1.2;
        margin-top: 6px;
        text-shadow: 0 0 12px rgba(56, 189, 248, 0.25);
    }

    .badge-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }

    .mode-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 20px;
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        letter-spacing: 1px;
    }

    .status-badge {
        font-size: 0.75rem;
        color: #64748b;
    }

    /* Calculator Buttons */
    div[data-testid="stButton"] > button {
        width: 100%;
        border-radius: 12px;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.05rem;
        padding: 10px 0;
        transition: all 0.15s ease-in-out;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }

    div[data-testid="stButton"] > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(0, 0, 0, 0.35);
    }

    div[data-testid="stButton"] > button:active {
        transform: translateY(1px);
    }

    /* Card styling */
    .metric-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 14px;
        backdrop-filter: blur(8px);
    }

    .history-item {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 8px;
        transition: all 0.2s ease;
    }
    .history-item:hover {
        border-color: rgba(56, 189, 248, 0.4);
        background: rgba(30, 41, 59, 0.85);
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if "expression" not in st.session_state:
    st.session_state.expression = ""
if "last_result" not in st.session_state:
    st.session_state.last_result = "0"
if "history" not in st.session_state:
    st.session_state.history = []
if "angle_mode" not in st.session_state:
    st.session_state.angle_mode = "RAD"
if "error_msg" not in st.session_state:
    st.session_state.error_msg = None
if "current_latex" not in st.session_state:
    st.session_state.current_latex = ""

# --- Keypad Action Handlers ---
def handle_append(token: str):
    st.session_state.expression += token
    st.session_state.error_msg = None

def handle_clear():
    st.session_state.expression = ""
    st.session_state.error_msg = None

def handle_all_clear():
    st.session_state.expression = ""
    st.session_state.last_result = "0"
    st.session_state.current_latex = ""
    st.session_state.error_msg = None

def handle_backspace():
    if st.session_state.expression:
        st.session_state.expression = st.session_state.expression[:-1]
    st.session_state.error_msg = None

def handle_evaluate():
    expr = st.session_state.expression.strip()
    if not expr:
        return
    res = calc_engine.evaluate_expression(expr, angle_mode=st.session_state.angle_mode)
    if res["success"]:
        st.session_state.last_result = str(res["result"])
        st.session_state.current_latex = res["latex"]
        st.session_state.error_msg = None
        # Add to history
        st.session_state.history.append({
            "expression": expr,
            "result": str(res["result"]),
            "latex": res["latex"],
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
    else:
        st.session_state.error_msg = res["error"]

def toggle_angle_mode():
    st.session_state.angle_mode = "DEG" if st.session_state.angle_mode == "RAD" else "RAD"

def load_history_expression(expr: str):
    st.session_state.expression = expr
    st.session_state.error_msg = None

# --- Main App Header ---
col_logo, col_stat = st.columns([3, 1])
with col_logo:
    st.markdown("## ⚡ OmniCalc & Grapher Studio")
    st.caption("Scientific Computing • High-Precision Arithmetic • Analytical & Interactive Graphing")

# --- Tabs ---
tab_calc, tab_graph, tab_history_full = st.tabs([
    "🧮 Calculator & Functions", 
    "📈 Graphing Studio", 
    "📜 History & Logs"
])

# ==============================================================================
# TAB 1: CALCULATOR
# ==============================================================================
with tab_calc:
    calc_col, side_col = st.columns([1.6, 1.0], gap="large")

    with calc_col:
        # Display Box
        expr_display = st.session_state.expression if st.session_state.expression else " "
        res_display = st.session_state.last_result if st.session_state.last_result else "0"
        err_display = f"<div style='color: #f87171; font-size: 0.85rem; margin-top: 4px;'>⚠️ {st.session_state.error_msg}</div>" if st.session_state.error_msg else ""

        st.markdown(f"""
        <div class="calc-screen">
            <div class="badge-bar">
                <span class="mode-badge">{st.session_state.angle_mode}</span>
                <span class="status-badge">READY</span>
            </div>
            <div class="calc-expr-row">{expr_display}</div>
            <div class="calc-result-row">{res_display}</div>
            {err_display}
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.current_latex:
            with st.expander("📐 Exact LaTeX Representation", expanded=False):
                st.latex(st.session_state.current_latex)

        # Quick keyboard direct input
        with st.form("quick_calc_form", clear_on_submit=False):
            typed_expr = st.text_input(
                "⌨️ Or type expression directly (Press Enter to evaluate):",
                value=st.session_state.expression,
                placeholder="e.g. sin(pi/4) + sqrt(16) * 2^3",
                key="direct_calc_input"
            )
            form_col1, form_col2 = st.columns([4, 1])
            with form_col1:
                submitted = st.form_submit_button("⚡ Evaluate Expression", use_container_width=True)
            with form_col2:
                ans_btn = st.form_submit_button("Ans", use_container_width=True)
                
            if submitted and typed_expr:
                st.session_state.expression = typed_expr
                handle_evaluate()
                st.rerun()
            elif ans_btn:
                st.session_state.expression += str(st.session_state.last_result)
                st.rerun()

        st.write("")

        # Visual Keypad Layout
        # Row 0: Mode Toggle, Parens, Clears
        k0_1, k0_2, k0_3, k0_4, k0_5 = st.columns(5)
        with k0_1:
            if st.button(f"⚙️ {st.session_state.angle_mode}", help="Toggle Radians / Degrees", use_container_width=True):
                toggle_angle_mode()
                st.rerun()
        with k0_2:
            if st.button("(", use_container_width=True):
                handle_append("(")
                st.rerun()
        with k0_3:
            if st.button(")", use_container_width=True):
                handle_append(")")
                st.rerun()
        with k0_4:
            if st.button("C", help="Clear current input", use_container_width=True):
                handle_clear()
                st.rerun()
        with k0_5:
            if st.button("⌫ Del", help="Backspace", use_container_width=True):
                handle_backspace()
                st.rerun()

        # Row 1: Trig + Powers
        k1_1, k1_2, k1_3, k1_4, k1_5 = st.columns(5)
        with k1_1:
            if st.button("sin", use_container_width=True):
                handle_append("sin(")
                st.rerun()
        with k1_2:
            if st.button("cos", use_container_width=True):
                handle_append("cos(")
                st.rerun()
        with k1_3:
            if st.button("tan", use_container_width=True):
                handle_append("tan(")
                st.rerun()
        with k1_4:
            if st.button("xʸ (^)", use_container_width=True):
                handle_append("^")
                st.rerun()
        with k1_5:
            if st.button("÷", use_container_width=True):
                handle_append(" / ")
                st.rerun()

        # Row 2: Inverse Trig + Roots
        k2_1, k2_2, k2_3, k2_4, k2_5 = st.columns(5)
        with k2_1:
            if st.button("asin", use_container_width=True):
                handle_append("asin(")
                st.rerun()
        with k2_2:
            if st.button("acos", use_container_width=True):
                handle_append("acos(")
                st.rerun()
        with k2_3:
            if st.button("atan", use_container_width=True):
                handle_append("atan(")
                st.rerun()
        with k2_4:
            if st.button("√ (sqrt)", use_container_width=True):
                handle_append("sqrt(")
                st.rerun()
        with k2_5:
            if st.button("×", use_container_width=True):
                handle_append(" * ")
                st.rerun()

        # Row 3: Logarithms & Constants
        k3_1, k3_2, k3_3, k3_4, k3_5 = st.columns(5)
        with k3_1:
            if st.button("ln", use_container_width=True):
                handle_append("ln(")
                st.rerun()
        with k3_2:
            if st.button("log₁₀", use_container_width=True):
                handle_append("log(")
                st.rerun()
        with k3_3:
            if st.button("π", use_container_width=True):
                handle_append("pi")
                st.rerun()
        with k3_4:
            if st.button("e", use_container_width=True):
                handle_append("e")
                st.rerun()
        with k3_5:
            if st.button("−", use_container_width=True):
                handle_append(" - ")
                st.rerun()

        # Row 4: Digits 7,8,9 + Abs + Plus
        k4_1, k4_2, k4_3, k4_4, k4_5 = st.columns(5)
        with k4_1:
            if st.button("7", use_container_width=True):
                handle_append("7")
                st.rerun()
        with k4_2:
            if st.button("8", use_container_width=True):
                handle_append("8")
                st.rerun()
        with k4_3:
            if st.button("9", use_container_width=True):
                handle_append("9")
                st.rerun()
        with k4_4:
            if st.button("|x| (abs)", use_container_width=True):
                handle_append("abs(")
                st.rerun()
        with k4_5:
            if st.button("+", use_container_width=True):
                handle_append(" + ")
                st.rerun()

        # Row 5: Digits 4,5,6 + Fact + Mod
        k5_1, k5_2, k5_3, k5_4, k5_5 = st.columns(5)
        with k5_1:
            if st.button("4", use_container_width=True):
                handle_append("4")
                st.rerun()
        with k5_2:
            if st.button("5", use_container_width=True):
                handle_append("5")
                st.rerun()
        with k5_3:
            if st.button("6", use_container_width=True):
                handle_append("6")
                st.rerun()
        with k5_4:
            if st.button("n! (fact)", use_container_width=True):
                handle_append("fact(")
                st.rerun()
        with k5_5:
            if st.button("% (mod)", use_container_width=True):
                handle_append(" % ")
                st.rerun()

        # Row 6: Digits 1,2,3 + 0 + .
        k6_1, k6_2, k6_3, k6_4, k6_5 = st.columns(5)
        with k6_1:
            if st.button("1", use_container_width=True):
                handle_append("1")
                st.rerun()
        with k6_2:
            if st.button("2", use_container_width=True):
                handle_append("2")
                st.rerun()
        with k6_3:
            if st.button("3", use_container_width=True):
                handle_append("3")
                st.rerun()
        with k6_4:
            if st.button("0", use_container_width=True):
                handle_append("0")
                st.rerun()
        with k6_5:
            if st.button(".", use_container_width=True):
                handle_append(".")
                st.rerun()

        # Row 7: AC + Big Equals
        eq_c1, eq_c2 = st.columns([1, 4])
        with eq_c1:
            if st.button("AC", help="All Clear (Input & Result)", use_container_width=True):
                handle_all_clear()
                st.rerun()
        with eq_c2:
            if st.button("🟰  E V A L U A T E", type="primary", use_container_width=True):
                handle_evaluate()
                st.rerun()

    # History Quick Panel
    with side_col:
        st.markdown("### 📋 Recent History")
        if st.session_state.history:
            h_count = len(st.session_state.history)
            st.caption(f"{h_count} operation(s) logged")
            
            # Action buttons for history
            h_btn1, h_btn2 = st.columns(2)
            with h_btn1:
                if st.button("🗑️ Clear History", use_container_width=True):
                    st.session_state.history = []
                    st.rerun()
            with h_btn2:
                # Format text for download
                hist_txt = "\n".join([f"[{item['timestamp']}] {item['expression']} = {item['result']}" for item in st.session_state.history])
                st.download_button("💾 Save Log", data=hist_txt, file_name="calculator_history.txt", mime="text/plain", use_container_width=True)

            st.write("")
            # Show the last 8 entries in reverse order
            for idx, item in enumerate(reversed(st.session_state.history[-8:])):
                with st.container():
                    st.markdown(f"""
                    <div class="history-item">
                        <div style="font-size:0.75rem; color:#64748b; display:flex; justify-content:space-between;">
                            <span>#{h_count - idx}</span>
                            <span>{item['timestamp']}</span>
                        </div>
                        <div style="font-family:'JetBrains Mono'; font-size:0.95rem; color:#cbd5e1; margin: 4px 0;">{item['expression']}</div>
                        <div style="font-family:'JetBrains Mono'; font-weight:700; font-size:1.15rem; color:#38bdf8;">= {item['result']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    c_load, c_use_res = st.columns(2)
                    with c_load:
                        if st.button("↩ Load", key=f"hist_load_{idx}", use_container_width=True):
                            load_history_expression(item['expression'])
                            st.rerun()
                    with c_use_res:
                        if st.button("➕ Use Ans", key=f"hist_use_{idx}", use_container_width=True):
                            st.session_state.expression += str(item['result'])
                            st.rerun()
        else:
            st.info("No calculations performed yet. Try calculating `sin(pi/6)` or `2^10`!")

# ==============================================================================
# TAB 2: INTERACTIVE GRAPHING STUDIO
# ==============================================================================
with tab_graph:
    st.markdown("### 📈 Interactive Function Graphing & Analysis")
    st.caption("Plot multiple 2D continuous functions, examine derivatives, find roots, and calculate areas.")

    # Graph configuration controls
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 1.2, 1.2])

    with ctrl_col1:
        # Preset selection
        preset_options = {
            "Custom Function": "",
            "Sine Wave: sin(x)": "sin(x)",
            "Damped Oscillation: exp(-0.2*x) * cos(3*x)": "exp(-0.2*x) * cos(3*x)",
            "Cubic Polynomial: x^3 - 3*x": "x^3 - 3*x",
            "Gaussian Distribution: exp(-x^2)": "exp(-x^2)",
            "Rational Function: 1 / (1 + x^2)": "1 / (1 + x^2)",
            "Sigmoid Curve: 1 / (1 + exp(-x))": "1 / (1 + exp(-x))",
            "Trig Product: sin(x) * cos(2*x)": "sin(x) * cos(2*x)",
            "Logarithmic: ln(abs(x) + 0.1)": "ln(abs(x) + 0.1)"
        }
        chosen_preset = st.selectbox("🎯 Load Preset Function:", list(preset_options.keys()))

    with ctrl_col2:
        graph_theme = st.selectbox("🎨 Chart Theme:", [
            "Midnight Cyber (Dark)", 
            "Neon Glow (Dark)", 
            "Solar Flare (Warm)", 
            "Clean High-Contrast (Light)"
        ])

    with ctrl_col3:
        num_points = st.slider("Resolution (Points):", min_value=200, max_value=2000, value=800, step=100)

    # Function Inputs
    default_f = preset_options[chosen_preset] if preset_options[chosen_preset] else "sin(x)"
    
    g_col1, g_col2 = st.columns(2)
    with g_col1:
        f_expr = st.text_input("Primary Function f(x):", value=default_f, help="Use standard math expressions in terms of x")
    with g_col2:
        g_expr = st.text_input("Secondary Function g(x) (Optional):", value="cos(x)", help="Plot a companion curve for comparison")

    # Range and Feature Toggles
    f_toggles_col, f_ranges_col = st.columns([1, 1])
    with f_toggles_col:
        t_col1, t_col2, t_col3 = st.columns(3)
        with t_col1:
            show_derivative = st.checkbox("Show f'(x) Derivative", value=False)
        with t_col2:
            show_roots = st.checkbox("Highlight Roots f(x)=0", value=True)
        with t_col3:
            show_grid = st.checkbox("Show Grid Lines", value=True)

    with f_ranges_col:
        r_col1, r_col2 = st.columns(2)
        with r_col1:
            x_min = st.number_input("X Min", value=-10.0, step=1.0)
        with r_col2:
            x_max = st.number_input("X Max", value=10.0, step=1.0)

    if x_min >= x_max:
        st.error("Error: X Min must be strictly less than X Max.")
    else:
        # Generate X samples
        x_vals = np.linspace(x_min, x_max, num_points)
        
        # Evaluate f(x)
        y_vals, err_f = calc_engine.evaluate_graph_function(f_expr, x_vals)
        
        # Prepare Plotly Figure
        fig = go.Figure()
        
        # Theme styling definitions
        if "Midnight" in graph_theme:
            bg_color = "#0b0f19"
            paper_color = "#0f172a"
            grid_color = "rgba(255, 255, 255, 0.08)"
            f_color = "#38bdf8"      # Sky cyan
            g_color = "#f472b6"      # Soft pink
            df_color = "#a78bfa"     # Purple
            font_color = "#e2e8f0"
        elif "Neon" in graph_theme:
            bg_color = "#030712"
            paper_color = "#0b0f19"
            grid_color = "rgba(74, 222, 128, 0.12)"
            f_color = "#4ade80"      # Neon green
            g_color = "#facc15"      # Neon yellow
            df_color = "#22d3ee"     # Cyan
            font_color = "#f0fdf4"
        elif "Solar" in graph_theme:
            bg_color = "#180d07"
            paper_color = "#24140b"
            grid_color = "rgba(251, 146, 60, 0.12)"
            f_color = "#fb923c"      # Orange
            g_color = "#f43f5e"      # Rose
            df_color = "#fde047"     # Yellow
            font_color = "#ffedd5"
        else: # Light
            bg_color = "#f8fafc"
            paper_color = "#ffffff"
            grid_color = "rgba(0, 0, 0, 0.08)"
            f_color = "#2563eb"      # Blue
            g_color = "#db2777"      # Pink
            df_color = "#7c3aed"     # Violet
            font_color = "#1e293b"

        # Reference Axes (x=0, y=0)
        fig.add_hline(y=0, line_width=1.5, line_color="rgba(148, 163, 184, 0.4)", line_dash="solid")
        fig.add_vline(x=0, line_width=1.5, line_color="rgba(148, 163, 184, 0.4)", line_dash="solid")

        # Plot f(x)
        if err_f:
            st.error(f"Error evaluating f(x): {err_f}")
        else:
            fig.add_trace(go.Scatter(
                x=x_vals,
                y=y_vals,
                mode='lines',
                name=f"f(x) = {f_expr}",
                line=dict(color=f_color, width=3.2),
                hovertemplate="<b>x:</b> %{x:.3f}<br><b>f(x):</b> %{y:.3f}<extra></extra>"
            ))

        # Plot g(x) if present
        if g_expr.strip():
            y_vals_g, err_g = calc_engine.evaluate_graph_function(g_expr, x_vals)
            if not err_g:
                fig.add_trace(go.Scatter(
                    x=x_vals,
                    y=y_vals_g,
                    mode='lines',
                    name=f"g(x) = {g_expr}",
                    line=dict(color=g_color, width=2.4, dash="dot"),
                    hovertemplate="<b>x:</b> %{x:.3f}<br><b>g(x):</b> %{y:.3f}<extra></extra>"
                ))

        # Plot Derivative f'(x) if toggled
        analysis_data = calc_engine.analyze_function(f_expr)
        if show_derivative and analysis_data["success"] and analysis_data["derivative_str"]:
            y_vals_df, err_df = calc_engine.evaluate_graph_function(analysis_data["derivative_str"], x_vals)
            if not err_df:
                fig.add_trace(go.Scatter(
                    x=x_vals,
                    y=y_vals_df,
                    mode='lines',
                    name=f"f'(x) = {analysis_data['derivative_str']}",
                    line=dict(color=df_color, width=2.0, dash="dash"),
                    hovertemplate="<b>x:</b> %{x:.3f}<br><b>f'(x):</b> %{y:.3f}<extra></extra>"
                ))

        # Highlight roots if found
        if show_roots and analysis_data["success"] and analysis_data["roots"]:
            valid_roots = [r for r in analysis_data["roots"] if x_min <= r <= x_max]
            if valid_roots:
                fig.add_trace(go.Scatter(
                    x=valid_roots,
                    y=[0]*len(valid_roots),
                    mode='markers+text',
                    name='Roots (f(x) = 0)',
                    marker=dict(size=11, color='#ef4444', symbol='circle', line=dict(width=2, color='#ffffff')),
                    text=[f"x={r}" for r in valid_roots],
                    textposition="top center",
                    textfont=dict(color='#ef4444', size=11, family='JetBrains Mono'),
                    hovertemplate="<b>Root:</b> (%{x}, 0)<extra></extra>"
                ))

        # Chart layout styling
        fig.update_layout(
            paper_bgcolor=paper_color,
            plot_bgcolor=bg_color,
            font=dict(color=font_color, family="JetBrains Mono"),
            height=580,
            margin=dict(l=40, r=40, t=30, b=40),
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(0,0,0,0.3)",
                bordercolor="rgba(255,255,255,0.1)",
                borderwidth=1
            ),
            xaxis=dict(
                showgrid=show_grid,
                gridcolor=grid_color,
                zeroline=False,
                range=[x_min, x_max]
            ),
            yaxis=dict(
                showgrid=show_grid,
                gridcolor=grid_color,
                zeroline=False
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        # Calculus Insight Box
        if analysis_data["success"]:
            st.markdown("#### 🔬 Analytical Insights")
            an_c1, an_c2, an_c3 = st.columns(3)
            with an_c1:
                st.markdown("**Derivative $f'(x)$:**")
                st.latex(analysis_data["derivative_latex"])
            with an_c2:
                st.markdown("**Indefinite Integral $\\int f(x) dx$:**")
                st.latex(analysis_data["integral_latex"])
            with an_c3:
                st.markdown("**Detected Zeros (Roots):**")
                if analysis_data["roots"]:
                    st.write(", ".join([f"x = {r}" for r in analysis_data["roots"]]))
                else:
                    st.caption("No real roots found within standard algebraic bounds")

# ==============================================================================
# TAB 3: FULL HISTORY LOGS & EXPORT
# ==============================================================================
with tab_history_full:
    st.markdown("### 📜 Comprehensive History & Session Export")
    if not st.session_state.history:
        st.info("No calculations have been logged yet.")
    else:
        st.caption(f"Total calculations in current session: {len(st.session_state.history)}")
        
        # Download options
        exp_col1, exp_col2, exp_col3 = st.columns([1, 1, 2])
        with exp_col1:
            json_data = json.dumps(st.session_state.history, indent=2)
            st.download_button(
                "📥 Export as JSON",
                data=json_data,
                file_name=f"calc_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        with exp_col2:
            csv_lines = ["Timestamp,Expression,Result"]
            for h in st.session_state.history:
                safe_expr = h['expression'].replace('"', '""')
                csv_lines.append(f'"{h["timestamp"]}","{safe_expr}","{h["result"]}"')
            st.download_button(
                "📊 Export as CSV",
                data="\n".join(csv_lines),
                file_name=f"calc_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with exp_col3:
            if st.button("🗑️ Clear All History", type="secondary"):
                st.session_state.history = []
                st.rerun()

        st.write("---")
        
        # History Table
        table_data = []
        for i, item in enumerate(reversed(st.session_state.history)):
            table_data.append({
                "#": len(st.session_state.history) - i,
                "Time": item["timestamp"],
                "Expression": item["expression"],
                "Result": item["result"]
            })
        st.dataframe(table_data, use_container_width=True)
