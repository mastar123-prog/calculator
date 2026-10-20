"""
test_calc.py - Test suite verifying calculator arithmetic, scientific functions, and graphing engine.
"""
import calc_engine
import numpy as np

def run_tests():
    print("--- Running Calculator Engine Unit Tests ---")
    
    # Basic Arithmetic
    tests = [
        ("2 + 3 * 4", "14"),
        ("10 / 4", "2.5"),
        ("2^10", "1024"),
        ("15 % 4", "3"),
        ("sqrt(144)", "12"),
        ("abs(-42)", "42"),
        ("fact(5)", "120"),
    ]
    
    for expr, expected in tests:
        res = calc_engine.evaluate_expression(expr)
        assert res["success"], f"Failed for {expr}: {res['error']}"
        assert res["result"] == expected, f"Failed for {expr}: got {res['result']}, expected {expected}"
        print(f"[PASS] {expr} = {res['result']}")

    # Trig in Rad vs Deg
    rad_res = calc_engine.evaluate_expression("sin(pi / 2)", angle_mode="RAD")
    assert rad_res["success"] and rad_res["result"] == "1", f"Rad test failed: {rad_res}"
    print(f"[PASS] sin(pi / 2) [RAD] = {rad_res['result']}")

    deg_res = calc_engine.evaluate_expression("sin(90)", angle_mode="DEG")
    assert deg_res["success"] and deg_res["result"] == "1", f"Deg test failed: {deg_res}"
    print(f"[PASS] sin(90) [DEG] = {deg_res['result']}")

    # Graph function evaluation
    x = np.linspace(-5, 5, 100)
    y, err = calc_engine.evaluate_graph_function("x^2 - 4", x)
    assert err is None, f"Graph eval failed: {err}"
    assert len(y) == 100
    print("[PASS] Graph function evaluation f(x) = x^2 - 4")

    # Analytical Derivative & Roots
    analysis = calc_engine.analyze_function("x^2 - 4")
    assert analysis["success"], f"Analysis failed: {analysis['error']}"
    print(f"[DEBUG] analysis roots: {analysis['roots']}")
    assert 2.0 in analysis["roots"] or 2 in analysis["roots"]
    assert -2.0 in analysis["roots"] or -2 in analysis["roots"]
    print(f"[PASS] Roots for x^2 - 4: {analysis['roots']}")
    print(f"[PASS] Derivative f'(x) for x^2 - 4: {analysis['derivative_str']}")
    print("\n>>> ALL TESTS PASSED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    run_tests()
