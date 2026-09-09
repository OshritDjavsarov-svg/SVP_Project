# import sympy as sp
# from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, \
#     convert_xor
#
#
# class EliminationSolver:
#     def __init__(self, eq1_str, eq2_str):
#         self.steps = []
#         trans = standard_transformations + (implicit_multiplication_application, convert_xor)
#
#         # 1. ניקוי והפיכה לביטויים
#         self.expr1 = parse_expr(eq1_str.replace('=', '-(') + ')', transformations=trans)
#         self.expr2 = parse_expr(eq2_str.replace('=', '-(') + ')', transformations=trans)
#
#         # 2. זיהוי אוטומטי של המשתנים
#         vars_found = sorted(list(self.expr1.free_symbols | self.expr2.free_symbols), key=lambda s: s.name)
#
#         if len(vars_found) < 2:
#             self.x = vars_found[0] if vars_found else sp.Symbol('x')
#             self.y = sp.Symbol('y')
#         else:
#             self.x = vars_found[0]
#             self.y = vars_found[1]
#
#         # 3. חילוץ מקדמים (a, b, c) לצורה ax + by = c
#         self.a1 = self.expr1.coeff(self.x)
#         self.b1 = self.expr1.coeff(self.y)
#         self.c1 = -self.expr1.subs({self.x: 0, self.y: 0})
#
#         self.a2 = self.expr2.coeff(self.x)
#         self.b2 = self.expr2.coeff(self.y)
#         self.c2 = -self.expr2.subs({self.x: 0, self.y: 0})
#
#     def _clean(self, val):
#         """פונקציית עזר לניקוי מספרים עשרוניים (במקום MathRules)"""
#         if isinstance(val, (sp.Float, float)) and val == int(val):
#             return sp.Integer(val)
#         return val
#
#     def solve(self):
#         self.steps.append("### שיטת השוואת מקדמים (אלמינציה)")
#
#         # הצגת המערכת המסודרת
#         eq1_lhs = self.a1 * self.x + self.b1 * self.y
#         eq2_lhs = self.a2 * self.x + self.b2 * self.y
#         self.steps.append("המערכת לאחר סידור:")
#         self.steps.append(f"I) $${sp.latex(self._clean(eq1_lhs))} = {sp.latex(self._clean(self.c1))}$$")
#         self.steps.append(f"II) $${sp.latex(self._clean(eq2_lhs))} = {sp.latex(self._clean(self.c2))}$$")
#
#         # בדיקת פתרון
#         det = self.a1 * self.b2 - self.a2 * self.b1
#         if det == 0:
#             if self.a1 * self.c2 == self.a2 * self.c1:
#                 self.steps.append("למערכת יש **אינסוף פתרונות** (המשוואות זהות).")
#                 return "אינסוף פתרונות", self.steps
#             else:
#                 self.steps.append("למערכת **אין פתרון** (פסוק שקר).")
#                 return "אין פתרון", self.steps
#
#         # 1. בחירת נעלם לאיפוס
#         target = 'x' if abs(self.a1) == 1 or abs(self.a2) == 1 or self.a1 % self.a2 == 0 else 'y'
#         v1, v2 = (self.a1, self.a2) if target == 'x' else (self.b1, self.b2)
#         target_sym = self.x if target == 'x' else self.y
#         other_sym = self.y if target == 'x' else self.x
#
#         self.steps.append(f"נבחר לאפס את הנעלם **{target}**.")
#
#         # 2. מציאת גורמי כפל
#         lcm_val = abs(v1 * v2) / sp.gcd(v1, v2)
#         f1 = abs(lcm_val / v1)
#         f2 = abs(lcm_val / v2)
#
#         self.steps.append(
#             f"נכפיל את משוואה I ב-{sp.latex(self._clean(f1))} ואת משוואה II ב-{sp.latex(self._clean(f2))}:")
#
#         # 3. המערכת החדשה
#         na1, nb1, nc1 = self.a1 * f1, self.b1 * f1, self.c1 * f1
#         na2, nb2, nc2 = self.a2 * f2, self.b2 * f2, self.c2 * f2
#
#         self.steps.append(f"I) $${sp.latex(self._clean(na1 * self.x + nb1 * self.y))} = {sp.latex(self._clean(nc1))}$$")
#         self.steps.append(
#             f"II) $${sp.latex(self._clean(na2 * self.x + nb2 * self.y))} = {sp.latex(self._clean(nc2))}$$")
#
#         # 4. חיבור או חיסור
#         target_v1 = na1 if target == 'x' else nb1
#         target_v2 = na2 if target == 'x' else nb2
#
#         if target_v1 + target_v2 == 0:
#             self.steps.append(f"נחבר את המשוואות כדי לבטל את ${sp.latex(target_sym)}$:")
#             final_expr = (na1 + na2) * self.x + (nb1 + nb2) * self.y
#             final_c = nc1 + nc2
#         else:
#             self.steps.append(f"נחסר את המשוואות כדי לבטל את ${sp.latex(target_sym)}$:")
#             final_expr = (na1 - na2) * self.x + (nb1 - nb2) * self.y
#             final_c = nc1 - nc2
#
#         self.steps.append(f"$${sp.latex(self._clean(final_expr))} = {sp.latex(self._clean(final_c))}$$")
#
#         # 5. פתרון הנעלם הראשון
#         sol_other = sp.solve(sp.Eq(final_expr, final_c), other_sym)[0]
#         self.steps.append(f"נקבל: $${sp.latex(other_sym)} = {sp.latex(self._clean(sol_other))}$$")
#
#         # 6. מציאת הנעלם השני
#         self.steps.append(f"נציב את ${sp.latex(other_sym)}$ באחת המשוואות המקוריות:")
#         sol_target = sp.solve(self.a1 * self.x + self.b1 * self.y - self.c1, target_sym)[0].subs(other_sym, sol_other)
#
#         self.steps.append(f"$${sp.latex(target_sym)} = {sp.latex(self._clean(sol_target))}$$")
#
#         # תוצאה סופית
#         res_x = sol_target if target == 'x' else sol_other
#         res_y = sol_other if target == 'x' else sol_target
#         final_ans = f"({self._clean(res_x)}, {self._clean(res_y)})"
#         self.steps.append(f"**הפתרון הסופי: $${final_ans}$$**")
#
#         return final_ans, self.steps
#
#
# def solve_elimination_steps(equations_text):
#     try:
#         parts = [p.strip() for p in equations_text.replace('\n', ',').split(',') if '=' in p]
#         if len(parts) < 2: return {"result": "Error", "steps": ["נא לספק 2 משוואות"]}
#         result, steps = EliminationSolver(parts[0], parts[1]).solve()
#         return {"result": result, "steps": steps}
#     except Exception as e:
#         return {"result": "Error", "steps": [f"שגיאה: {str(e)}"]}
import sympy as sp
from solvers.math_utils import MathUtils
from solvers.linear_solver import UniversalStepSolver

class EliminationSolver:
    def __init__(self, eq1_str, eq2_str):
        self.steps = []

        # 1. שימוש ב-MathUtils לקריאת המשוואות הראשוניות
        self.lhs1, self.rhs1, _ = MathUtils.parse_equation(eq1_str)
        self.lhs2, self.rhs2, _ = MathUtils.parse_equation(eq2_str)

        # 2. זיהוי המשתנים מתוך הביטויים בצורה דינמית
        all_symbols = self.lhs1.free_symbols | self.rhs1.free_symbols | self.lhs2.free_symbols | self.rhs2.free_symbols
        vars_found = sorted(list(all_symbols), key=lambda s: s.name)

        self.x = vars_found[0] if len(vars_found) > 0 else sp.Symbol('x')
        self.y = vars_found[1] if len(vars_found) > 1 else sp.Symbol('y')

    def _is_linear(self, lhs, rhs):
        """בדיקה האם המשוואה ליניארית ביחס למשתנים שלה"""
        poly = sp.Poly(lhs - rhs)
        if poly.total_degree() > 1:
            return False
        return True

    def _arrange_to_standard_form(self, lhs, rhs, eq_name):
        """
        מביא משוואה לצורה המסודרת ax + by = c בצורה פדגוגית
        """
        curr_l, curr_r = lhs, rhs

        # 1. טיפול במכנה משותף במידת הצורך
        lcm = MathUtils.get_common_denominator([curr_l, curr_r])
        if lcm > 1:
            self.steps.append(f"נכפיל את משוואה {eq_name} במכנה המשותף {lcm}:")
            curr_l = sp.expand(curr_l * lcm)
            curr_r = sp.expand(curr_r * lcm)
            self.steps.append(MathUtils.render_equation(curr_l, curr_r))

        # 2. פתיחת סוגריים במידה ויש
        if "(" in str(curr_l) or "(" in str(curr_r):
            self.steps.append(f"נפתח סוגריים במשוואה {eq_name}:")
            curr_l = MathUtils.manual_expand(curr_l)
            curr_r = MathUtils.manual_expand(curr_r)
            self.steps.append(MathUtils.render_equation(curr_l, curr_r))

        # 3. כינוס והעברת אגפים
        simp_l = sp.simplify(curr_l)
        simp_r = sp.simplify(curr_r)

        # הפרדה בין משתנים למספרים חופשיים
        l_terms = MathUtils.get_terms(simp_l)
        r_terms = MathUtils.get_terms(simp_r)

        new_l_terms = []
        new_r_terms = []

        for t in l_terms:
            if t.has(self.x) or t.has(self.y):
                new_l_terms.append(t)
            else:
                new_r_terms.append(-t)

        for t in r_terms:
            if t.has(self.x) or t.has(self.y):
                new_l_terms.append(-t)
            else:
                new_r_terms.append(t)

        final_l = sp.simplify(sp.Add(*new_l_terms))
        final_r = sp.simplify(sp.Add(*new_r_terms))

        if sp.latex(final_l) != sp.latex(simp_l) or sp.latex(final_r) != sp.latex(simp_r):
             self.steps.append(f"נסדר את משוואה {eq_name} (משתנים בשמאל, מספרים בימין):")
             self.steps.append(MathUtils.render_equation(final_l, final_r))

        # חילוץ המקדמים לאחר הסידור
        a = final_l.coeff(self.x)
        b = final_l.coeff(self.y)
        c = final_r

        return final_l, final_r, a, b, c

    def solve(self):
        self.steps.append("## פתרון מערכת משוואות בשיטת השוואת מקדמים (אלימינציה)")
        self.steps.append("המערכת הנתונה:")
        self.steps.append(f"I) {MathUtils.render_equation(self.lhs1, self.rhs1)}")
        self.steps.append(f"II) {MathUtils.render_equation(self.lhs2, self.rhs2)}")

        # מניעת קריסה במקרה של משוואות לא ליניאריות
        if not self._is_linear(self.lhs1, self.rhs1) or not self._is_linear(self.lhs2, self.rhs2):
            raise ValueError("שיטת האלימינציה מתאימה למשוואות ליניאריות בלבד (ללא חזקות או מכפלות משתנים).")

        # סידור שתי המשוואות
        self.steps.append("### שלב 1: סידור המשוואות לצורה התקנית")
        eq1_l, eq1_r, self.a1, self.b1, self.c1 = self._arrange_to_standard_form(self.lhs1, self.rhs1, "I")
        eq2_l, eq2_r, self.a2, self.b2, self.c2 = self._arrange_to_standard_form(self.lhs2, self.rhs2, "II")

        self.steps.append("המערכת לאחר סידור:")
        self.steps.append(f"I) {MathUtils.render_equation(eq1_l, eq1_r)}")
        self.steps.append(f"II) {MathUtils.render_equation(eq2_l, eq2_r)}")

        # בדיקת מקרי קצה (אינסוף פתרונות / אין פתרון)
        det = self.a1 * self.b2 - self.a2 * self.b1
        if det == 0:
            if self.a1 * self.c2 == self.a2 * self.c1:
                self.steps.append("קיבלנו משוואות בעלות פרופורציה זהה, לכן למערכת יש **אינסוף פתרונות**.")
                return "אינסוף פתרונות", self.steps
            else:
                self.steps.append("הגענו למצב של קווים מקבילים (פסוק שקר), לכן למערכת **אין פתרון**.")
                return "אין פתרון", self.steps

        # בחירת נעלם לאיפוס
        target = self.x if (abs(self.a1) == 1 or abs(self.a2) == 1 or (self.a2 != 0 and self.a1 % self.a2 == 0)) else self.y
        v1, v2 = (self.a1, self.a2) if target == self.x else (self.b1, self.b2)
        target_sym = target
        other_sym = self.y if target == self.x else self.x

        self.steps.append(f"### שלב 2: איפוס הנעלם $${sp.latex(target_sym)}$$")

        # מציאת גורמי כפל
        try:
            lcm_val = abs(v1 * v2) / sp.gcd(abs(v1), abs(v2))
            f1 = sp.Integer(abs(lcm_val / v1)) if v1 != 0 else 1
            f2 = sp.Integer(abs(lcm_val / v2)) if v2 != 0 else 1
        except:
            f1, f2 = sp.Integer(1), sp.Integer(1)

        na1, nb1, nc1 = self.a1 * f1, self.b1 * f1, self.c1 * f1
        na2, nb2, nc2 = self.a2 * f2, self.b2 * f2, self.c2 * f2

        if f1 != 1 or f2 != 1:
            mult_text = []
            if f1 != 1: mult_text.append(f"משוואה I ב-{MathUtils.clean_floats(f1)}")
            if f2 != 1: mult_text.append(f"משוואה II ב-{MathUtils.clean_floats(f2)}")
            self.steps.append(f"נכפיל את {' ואת '.join(mult_text)}:")

            self.steps.append(f"I) {MathUtils.render_equation(na1 * self.x + nb1 * self.y, nc1)}")
            self.steps.append(f"II) {MathUtils.render_equation(na2 * self.x + nb2 * self.y, nc2)}")

        # חיבור או חיסור המשוואות
        target_v1 = na1 if target == self.x else nb1
        target_v2 = na2 if target == self.x else nb2

        if target_v1 + target_v2 == 0:
            self.steps.append(f"המקדמים נגדיים, לכן נחבר את המשוואות כדי לבטל את $${sp.latex(target_sym)}$$:")
            final_expr = sp.simplify((na1 + na2) * self.x + (nb1 + nb2) * self.y)
            final_c = sp.simplify(nc1 + nc2)
        else:
            self.steps.append(f"המקדמים שווים, לכן נחסר את המשוואות (I - II) כדי לבטל את $${sp.latex(target_sym)}$$:")
            final_expr = sp.simplify((na1 - na2) * self.x + (nb1 - nb2) * self.y)
            final_c = sp.simplify(nc1 - nc2)

        self.steps.append(MathUtils.render_equation(final_expr, final_c))

        # פתרון הנעלם הראשון
        sol_other = sp.solve(sp.Eq(final_expr, final_c), other_sym)[0]
        sol_other_clean = MathUtils.clean_floats(sol_other)
        self.steps.append(f"נחלק במקדם ונקבל: $${sp.latex(other_sym)} = {sp.latex(sol_other_clean)}$$")

        # מציאת הנעלם השני
        self.steps.append(f"### שלב 3: מציאת הנעלם השני ($${sp.latex(target_sym)}$$)")
        self.steps.append(f"נציב את $${sp.latex(other_sym)} = {sp.latex(sol_other_clean)}$$ במשוואה I המסודרת:")

        # הצבה פדגוגית עם סוגריים לתצוגה
        sub_l_str = sp.latex(MathUtils.clean_floats(eq1_l)).replace(
            str(other_sym), f"\\left({sp.latex(sol_other_clean)}\\right)"
        )
        self.steps.append(f"$${sub_l_str} = {sp.latex(MathUtils.clean_floats(self.c1))}$$")

        # פתרון משוואה ליניארית למציאת המשתנה השני באמצעות UniversalStepSolver
        eq_to_solve = f"{str(eq1_l.subs(other_sym, sol_other_clean))} = {str(self.c1)}"
        sub_solver = UniversalStepSolver(eq_to_solve, var_symbol=target_sym)
        sol_target_val, sub_steps = sub_solver.solve()

        for s in sub_steps:
            # מניעת כפילות טקסטואלית משורות הסיום של הפותר הליניארי
            if "##" not in s and "התוצאה הסופית" not in s and "נחלק במקדם" not in s:
                self.steps.append(s)

        sol_target_clean = MathUtils.clean_floats(sp.sympify(sol_target_val))
        self.steps.append(f"נקבל: $${sp.latex(target_sym)} = {sp.latex(sol_target_clean)}$$")

        # תוצאה סופית
        res_x = sol_target_clean if target == self.x else sol_other_clean
        res_y = sol_other_clean if target == self.x else sol_target_clean

        final_ans = f"({sp.latex(res_x)}, {sp.latex(res_y)})"
        self.steps.append("---")
        self.steps.append(f"**הפתרון הסופי: $ {final_ans} $**")

        return final_ans, self.steps


def solve_elimination_steps(equations_text):
    """פונקציית הממשק עבור ה-Flask"""
    try:
        parts = [p.strip() for p in equations_text.replace('\n', ',').replace('and', ',').split(',') if '=' in p]
        if len(parts) < 2:
            return {"result": "Error", "steps": ["נא לספק שתי משוואות מופרדות בפסיק"]}

        solver = EliminationSolver(parts[0], parts[1])
        result, steps = solver.solve()
        return {"result": result, "steps": steps}
    except Exception as e:
        return {"result": "Error", "steps": [f"שגיאה במערכת האלמינציה: {str(e)}"]}

from solvers.elimination_solver import solve_elimination_steps


def run_test(name, equations):
    print(f"\n{'=' * 20}")
    print(f"בדיקה: {name}")
    print(f"משוואות: {equations}")
    print(f"{'=' * 20}\n")

    result_data = solve_elimination_steps(equations)

    if result_data["result"] == "Error":
        print(f"שגיאה: {result_data['steps'][0]}")
    else:
        print(f"תוצאה סופית: {result_data['result']}")
        print("\nשלבי הפתרון:")
        for i, step in enumerate(result_data["steps"], 1):
            print(f"{step}")


if __name__ == "__main__":
    # 1. בדיקת מערכת רגילה (פתרון יחיד)
    run_test("מערכת רגילה", "x + y = 10, 2x - y = 8")

    # 2. בדיקת מערכת עם אינסוף פתרונות (הדוגמה הקריטית)
    run_test("אינסוף פתרונות", "5x + 10y = 540, 5x + 10y = 540")

    # 3. בדיקת מערכת ללא פתרון
    run_test("אין פתרון", "x + y = 5, x + y = 10")

    # 4. בדיקת מערכת עם משוואה ריבועית (בונוס)
    run_test("מערכת ריבועית", "y = x^2, y = 4")