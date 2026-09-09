# import sympy as sp
# from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, \
#     convert_xor
#
# # ייבוא פונקציות העזר שכבר קיימות אצלך בתיקייה
# try:
#     from .linear_solver import solve_linear_steps
#     from .quadratic_solver import solve_quadratic_steps
# except ImportError:
#     # למקרה של הרצה מקומית של הקובץ
#     import sys
#     import os
#
#     sys.path.append(os.path.dirname(__file__))
#     from linear_solver import solve_linear_steps
#     from quadratic_solver import solve_quadratic_steps
#
#
# class SystemSubstitutionSolver:
#     def __init__(self, eq1_str, eq2_str):
#         self.steps = []
#         trans = standard_transformations + (implicit_multiplication_application, convert_xor)
#         self.x, self.y = sp.symbols('x y')
#
#         # ניקוי ופירוק
#         l1, r1 = eq1_str.replace('^', '**').split('=')
#         l2, r2 = eq2_str.replace('^', '**').split('=')
#
#         self.lhs1 = parse_expr(l1, transformations=trans, evaluate=False)
#         self.rhs1 = parse_expr(r1, transformations=trans, evaluate=False)
#         self.lhs2 = parse_expr(l2, transformations=trans, evaluate=False)
#         self.rhs2 = parse_expr(r2, transformations=trans, evaluate=False)
#
#     def _rule_clean_floats(self, expr):
#         if not hasattr(expr, 'atoms'): return expr
#         return expr.subs({n: sp.Integer(n) for n in expr.atoms(sp.Float) if n == int(n)})
#
#     def solve(self):
#         self.steps.append("### שלב 1: הכנת המערכת להצבה")
#
#         # חיפוש בידוד נוח (איפה שיש מקדם 1 או -1)
#         best_iso = None
#         all_eqs = [(self.lhs1, self.rhs1, "I"), (self.lhs2, self.rhs2, "II")]
#
#         for i, (l, r, label) in enumerate(all_eqs):
#             for var in [self.y, self.x]:
#                 try:
#                     coeff = sp.collect(l - r, var).coeff(var)
#                     if abs(coeff) == 1:
#                         best_iso = {"idx": i, "var": var, "expr": sp.solve(l - r, var)[0], "label": label}
#                         break
#                 except:
#                     continue
#             if best_iso: break
#
#         if not best_iso:
#             best_iso = {"idx": 0, "var": self.y, "expr": sp.solve(self.lhs1 - self.rhs1, self.y)[0], "label": "I"}
#
#         self.steps.append(f"נבודד את המשתנה ${sp.latex(best_iso['var'])}$ ממשוואה {best_iso['label']}:")
#         iso_expr_clean = self._rule_clean_floats(best_iso["expr"])
#         self.steps.append(f"$${sp.latex(best_iso['var'])} = {sp.latex(iso_expr_clean)}$$")
#
#         # שלב 2: הצבה
#         other_idx = 1 if best_iso["idx"] == 0 else 0
#         other_l, other_r, other_label = all_eqs[other_idx]
#         other_eq = other_l - other_r
#
#         self.steps.append(f"### שלב 2: הצבה במשוואה {other_label}")
#         self.steps.append(f"נציב את הביטוי שקיבלנו במקום ${sp.latex(best_iso['var'])}$:")
#
#         iso_var = best_iso["var"]
#         # תצוגה ויזואלית של ההצבה
#         sub_visual = sp.latex(other_eq).replace(str(iso_var), f"\\left({sp.latex(iso_expr_clean)}\\right)")
#         self.steps.append(f"$${sub_visual} = 0$$")
#
#         # פתרון המשוואה שנוצרה (נעלם אחד)
#         substituted_eq = other_eq.subs(iso_var, best_iso["expr"])
#         substituted_eq_str = f"{str(sp.expand(substituted_eq))} = 0"
#
#         other_var = self.x if iso_var == self.y else self.y
#         self.steps.append(f"קיבלנו משוואה בנעלם אחד (${sp.latex(other_var)}$). נפתור אותה:")
#
#         # שימוש בפותרים הקיימים
#         # --- תיקון השגיאה כאן ---
#         if "**2" in substituted_eq_str:
#             # אם יש חזקה, שולחים לפותר הריבועי (הוא כן מקבל 2 ארגומנטים אצלך)
#             sol_data = solve_quadratic_steps(substituted_eq_str, str(other_var))
#         else:
#             # תיקון: שולחים רק את המשוואה לפותר הליניארי
#             sol_data = solve_linear_steps(substituted_eq_str)
#
#         self.steps.extend(sol_data["steps"])
#
#         # חילוץ תוצאות הנעלם הראשון
#         raw_solutions = sol_data["result"]
#         if "Error" in str(raw_solutions) or "אין פתרון" in str(raw_solutions):
#             return "אין פתרון", self.steps
#
#         # שלב 3: מציאת הנעלם השני
#         self.steps.append(f"### שלב 3: מציאת הנעלם השני (${sp.latex(iso_var)}$)")
#
#         # המרת תוצאות לרשימה
#         if isinstance(raw_solutions, str):
#             sols_list = [s.strip() for s in raw_solutions.split(',')]
#         else:
#             sols_list = [raw_solutions]
#
#         final_pairs = []
#         for sol_val_str in sols_list:
#             try:
#                 sol_val = sp.sympify(sol_val_str)
#                 val_second = iso_expr_clean.subs(other_var, sol_val)
#                 val_second = self._rule_clean_floats(val_second)
#
#                 self.steps.append(f"עבור ${sp.latex(other_var)} = {sp.latex(sol_val)}$, נציב ונקבל:")
#                 self.steps.append(f"$${sp.latex(iso_var)} = {sp.latex(val_second)}$$")
#
#                 if str(other_var) == 'x':
#                     final_pairs.append(f"({sp.latex(sol_val)}, {sp.latex(val_second)})")
#                 else:
#                     final_pairs.append(f"({sp.latex(val_second)}, {sp.latex(sol_val)})")
#             except:
#                 continue
#
#         final_res_str = ", ".join(final_pairs)
#         self.steps.append(f"**הפתרון הסופי: $ {final_res_str} $**")
#         return final_res_str, self.steps
#
#
# def solve_substitution_steps(equations_text):
#     try:
#         # פיצול הטקסט ל-2 משוואות
#         clean_text = equations_text.replace('\n', ',').replace('and', ',')
#         parts = [p.strip() for p in clean_text.split(',') if '=' in p]
#         if len(parts) < 2:
#             return {"result": "Error", "steps": ["נא לספק שתי משוואות מופרדות בפסיק"]}
#
#         solver = SystemSubstitutionSolver(parts[0], parts[1])
#         result, steps = solver.solve()
#         return {"result": result, "steps": steps}
#     except Exception as e:
#         return {"result": "Error", "steps": [f"שגיאה במערכת המשוואות: {str(e)}"]}


import sympy as sp
from solvers.math_utils import MathUtils
from solvers.linear_solver import UniversalStepSolver
from solvers.quadratic_solver import QuadraticStepSolver


class SystemSubstitutionSolver:
    def __init__(self, eq1_str, eq2_str):
        self.steps = []

        # שימוש ב-MathUtils לפירוק ראשוני של המשוואות
        self.lhs1, self.rhs1, _ = MathUtils.parse_equation(eq1_str)
        self.lhs2, self.rhs2, _ = MathUtils.parse_equation(eq2_str)

        # זיהוי דינמי של המשתנים מתוך הביטויים עצמם
        all_symbols = self.lhs1.free_symbols | self.rhs1.free_symbols | self.lhs2.free_symbols | self.rhs2.free_symbols
        vars_found = sorted(list(all_symbols), key=lambda s: s.name)

        # הגדרת המשתנים (תומך ב-x,y או u,v או כל זוג אותיות אחר)
        self.var1 = vars_found[0] if len(vars_found) > 0 else sp.Symbol('x')
        self.var2 = vars_found[1] if len(vars_found) > 1 else sp.Symbol('y')

    def _add_step(self, text):
        """מונע כפילות של שלבים עוקבים זהים"""
        if not self.steps or self.steps[-1] != text:
            self.steps.append(text)

    def solve(self):
        self._add_step("## פתרון מערכת משוואות בשיטת ההצבה")
        self._add_step("המערכת הנתונה:")
        self._add_step(f"I) {MathUtils.render_equation(self.lhs1, self.rhs1)}")
        self._add_step(f"II) {MathUtils.render_equation(self.lhs2, self.rhs2)}")

        # --- שלב 1: בידוד משתנה ---
        best_iso = (0, self.var2, "I")  # ברירת מחדל למשתנה השני (לרוב y או v)
        all_eqs = [(self.lhs1, self.rhs1, "I"), (self.lhs2, self.rhs2, "II")]

        for i, (l, r, label) in enumerate(all_eqs):
            diff = sp.simplify(l - r)
            for v in [self.var2, self.var1]:
                if abs(diff.coeff(v)) == 1:
                    best_iso = (i, v, label)
                    break
            if best_iso[2] == label and i == best_iso[0]: break

        idx, iso_var, label = best_iso
        self._add_step(f"### שלב 1: בידוד משתנה במשוואה {label}")

        curr_l, curr_r = (self.lhs1, self.rhs1) if idx == 0 else (self.lhs2, self.rhs2)

        # בידוד משתנה באמצעות המנוע המשותף
        final_l, final_r = MathUtils.apply_algebraic_steps(curr_l, curr_r, iso_var, self.steps)

        coeff = final_l.coeff(iso_var)
        iso_expr = sp.simplify(final_r / coeff) if coeff != 1 and coeff != 0 else final_r
        if coeff != 1 and coeff != 0:
            self._add_step(
                f"נחלק במקדם של {sp.latex(iso_var)} ונקבל: $${sp.latex(iso_var)} = {sp.latex(MathUtils.clean_floats(iso_expr))}$$")

        # --- שלב 2: הצבה במשוואה השנייה ---
        other_idx = 1 if idx == 0 else 0
        other_l, other_r, other_label = all_eqs[other_idx]

        # המשתנה שלא בודדנו
        other_var = self.var1 if iso_var == self.var2 else self.var2

        self._add_step(f"### שלב 2: הצבה במשוואה {other_label}")
        self._add_step(
            f"נציב $${sp.latex(iso_var)} = {sp.latex(MathUtils.clean_floats(iso_expr))}$$ במשוואה {other_label}:")

        # פתרון הבעיה הויזואלית: החלפת מחרוזת לייצוג סוגריים מושלם ב-LaTeX
        l_str = sp.latex(MathUtils.clean_floats(other_l)).replace(str(iso_var),
                                                                  f"\\left({sp.latex(MathUtils.clean_floats(iso_expr))}\\right)")
        r_str = sp.latex(MathUtils.clean_floats(other_r)).replace(str(iso_var),
                                                                  f"\\left({sp.latex(MathUtils.clean_floats(iso_expr))}\\right)")
        self._add_step(f"$${l_str} = {r_str}$$")

        # שימוש ב-UnevaluatedExpr כדי לאפשר את צעדי האלגברה מתחת לפני השטח
        new_l = other_l.subs(iso_var, sp.UnevaluatedExpr(iso_expr))
        new_r = other_r.subs(iso_var, sp.UnevaluatedExpr(iso_expr))

        # פתרון המשוואה בנעלם אחד באמצעות הכלים שבנינו
        res_l, res_r = MathUtils.apply_algebraic_steps(new_l, new_r, other_var, self.steps)

        # בדיקת מקרים מיוחדים (פסוק אמת/שקר)
        diff_final = sp.simplify(res_l - res_r)
        if diff_final == 0:
            self._add_step("קיבלנו פסוק אמת, לכן למערכת יש **אינסוף פתרונות**.")
            return "אינסוף פתרונות", self.steps
        elif not diff_final.has(other_var):
            self._add_step("קיבלנו פסוק שקר, לכן למערכת **אין פתרון**.")
            return "אין פתרון", self.steps

        # פתרון משוואה רגילה (ליניארית או ריבועית)
        eq_to_solve = f"{str(res_l)} = {str(res_r)}"
        if sp.degree(diff_final, other_var) <= 1:
            sub_solver = UniversalStepSolver(eq_to_solve, var_symbol=str(other_var))
        else:
            sub_solver = QuadraticStepSolver(eq_to_solve, var_symbol=str(other_var))

        sol_val, sub_steps = sub_solver.solve()

        # מוסיפים רק את השלבים הרלוונטיים (מונע כפילות כותרות מ-UniversalStepSolver)
        for s in sub_steps:
            if "##" not in s and "התוצאה הסופית" not in s:
                self._add_step(s)

        # --- שלב 3: מציאת הנעלם השני ---
        self._add_step(f"### שלב 3: מציאת ערך $${sp.latex(iso_var)}$$")

        # תמיכה בפתרון אחד (ליניארי) או שניים (ריבועי)
        sols = str(sol_val).split(", ")
        final_pairs = []

        for s in sols:
            try:
                val_other = sp.sympify(s)
                val_iso = MathUtils.clean_floats(iso_expr.subs(other_var, val_other))
                self._add_step(f"עבור $${sp.latex(other_var)} = {sp.latex(val_other)}$$, נציב בביטוי המבודד:")
                self._add_step(f"$${sp.latex(iso_var)} = {sp.latex(val_iso)}$$")

                # סדר הופעת המשתנים בתשובה (לפי סדר א"ב, למשל u לפני v, או x לפני y)
                pair = (val_other, val_iso) if other_var == self.var1 else (val_iso, val_other)
                final_pairs.append(f"({sp.latex(pair[0])}, {sp.latex(pair[1])})")
            except:
                continue

        res_str = ", ".join(final_pairs)
        self._add_step("---")
        self._add_step(f"**הפתרון הסופי: $ {res_str} $**")
        return res_str, self.steps


def solve_substitution_steps(equations_text):
    """פונקציית הממשק עבור ה-Flask"""
    try:
        clean_text = equations_text.replace('\n', ',').replace('and', ',')
        parts = [p.strip() for p in clean_text.split(',') if '=' in p]
        if len(parts) < 2:
            return {"result": "Error", "steps": ["נא לספק שתי משוואות מופרדות בפסיק"]}

        solver = SystemSubstitutionSolver(parts[0], parts[1])
        result, steps = solver.solve()
        return {"result": result, "steps": steps}
    except Exception as e:
        return {"result": "Error", "steps": [f"שגיאה במערכת: {str(e)}"]}


from solvers.substitution_solver import solve_substitution_steps


def run_test(name, equations):
    print(f"\n{'=' * 20}")
    print(f"בדיקה: {name}")
    print(f"משוואות: {equations}")
    print(f"{'=' * 20}\n")

    result_data = solve_substitution_steps(equations)

    if result_data["result"] == "Error":
        print(f"שגיאה: {result_data['steps'][0]}")
    else:
        print(f"תוצאה סופית: {result_data['result']}")
        print("\nשלבי הפתרון:")
        for i, step in enumerate(result_data["steps"], 1):
            print(f"{step}")


if __name__ == "__main__":
    # 1. בדיקת מערכת רגילה (פתרון יחיד)
    run_test("מערכת רגילה", "u + v = 5, 2u - v = 1")

    # # 2. בדיקת מערכת עם אינסוף פתרונות (הדוגמה הקריטית)
    # run_test("אינסוף פתרונות", "5x + 10y = 540, 5x + 10y = 540")
    #
    # # 3. בדיקת מערכת ללא פתרון
    # run_test("אין פתרון", "x + y = 5, x + y = 10")
    #
    # # 4. בדיקת מערכת עם משוואה ריבועית (בונוס)
    # run_test("מערכת ריבועית", "y = x^2, y = 4")