import sympy as sp
from solvers.math_utils import MathUtils

class QuadraticStepSolver:
    def __init__(self, equation_str, var_symbol=None):
        self.steps = []
        # שימוש בפונקציה המשותפת לאתחול (בדיוק כמו בליניארית!)
        self.lhs, self.rhs, self.var = MathUtils.parse_equation(equation_str, var_symbol)

    def solve(self):
        current_lhs = self.lhs
        current_rhs = self.rhs
        v_str = sp.latex(self.var)

        # 1. טיפול במכנה משותף (שימוש בפונקציית העזר)
        lcm = MathUtils.get_common_denominator([current_lhs, current_rhs])
        if lcm > 1:
            self.steps.append(f"נכפיל את כל המשוואה במכנה המשותף ({lcm}) כדי להיפטר מהשברים:")
            current_lhs = sp.expand(current_lhs * lcm)
            current_rhs = sp.expand(current_rhs * lcm)
            self.steps.append(MathUtils.render_equation(current_lhs, current_rhs))

        # 2. פתיחת סוגריים ופישוט
        if "(" in str(current_lhs) or "(" in str(current_rhs):
            self.steps.append("נפתח סוגריים ונכנס איברים דומים:")
            current_lhs = sp.expand(current_lhs)
            current_rhs = sp.expand(current_rhs)
            self.steps.append(MathUtils.render_equation(current_lhs, current_rhs))

        # 3. העברת אגפים לצורה סטנדרטית
        if current_rhs != 0:
            self.steps.append(f"נעביר את כל האיברים לאגף שמאל כדי לבדוק את סוג המשוואה:")
            final_expr = sp.expand(current_lhs - current_rhs)
            current_rhs = sp.Integer(0)
            self.steps.append(MathUtils.render_equation(final_expr, current_rhs))
        else:
            final_expr = sp.expand(current_lhs)

        # 4. זיהוי מקדמים ובדיקה אם המשוואה ליניארית
        final_expr = sp.collect(final_expr, self.var)
        a = final_expr.coeff(self.var, 2)

        if a == 0:
            linear_eq_str = f"{sp.latex(final_expr)} = 0"
            try:
                from solvers.linear_solver import UniversalStepSolver
            except ImportError:
                from linear_solver import UniversalStepSolver

            linear_solver = UniversalStepSolver(linear_eq_str, var_symbol=self.var)
            linear_res, linear_steps = linear_solver.solve()
            self.steps.extend(linear_steps)
            return linear_res, self.steps

        b = final_expr.coeff(self.var, 1)
        c = final_expr.coeff(self.var, 0)

        self.steps.append(f"נזהה את המקדמים של המשוואה הריבועית: $$a = {a}, b = {b}, c = {c}$$")

        # 5. דיסקרימיננטה
        delta = b ** 2 - 4 * a * c
        self.steps.append(f"נחשב את הדיסקרימיננטה ($\Delta = b^2 - 4ac$):")
        self.steps.append(f"$$\Delta = ({b})^2 - 4 \cdot ({a}) \cdot ({c}) = {delta}$$")

        if delta < 0:
            self.steps.append(f"קיבלנו $\Delta = {delta}$. כיוון שהערך שלילי, למשוואה **אין פתרון ממשי**.")
            return "אין פתרון", self.steps

        # 6. נוסחת השורשים
        sqrt_delta = sp.sqrt(delta)
        sol1 = sp.simplify((-b + sqrt_delta) / (2 * a))
        sol2 = sp.simplify((-b - sqrt_delta) / (2 * a))

        self.steps.append("נציב את הערכים בנוסחת השורשים:")
        self.steps.append(f"$${v_str}_{{1,2}} = \\frac{{-({b}) \\pm \\sqrt{{{delta}}}}}{{2 \\cdot {a}}}$$")

        if delta == 0:
            res = MathUtils.clean_floats(sol1)
            self.steps.append(f"קיבלנו פתרון יחיד: $${v_str} = {sp.latex(res)}$$")
            return str(res), self.steps

        res1 = MathUtils.clean_floats(sol1)
        res2 = MathUtils.clean_floats(sol2)

        # 7. לוגיקה לסינון פתרונות
        try:
            val1, val2 = float(res1), float(res2)
            if (val1 > 0 and val2 <= 0) or (val2 > 0 and val1 <= 0):
                positive_res = res1 if val1 > 0 else res2
                self.steps.append(f"הפתרונות שהתקבלו הם: $${v_str}_1 = {sp.latex(res1)}, {v_str}_2 = {sp.latex(res2)}$$")
                self.steps.append("בבעיה אין ערך למשתנים שלילים, נבחר בפתרון החיובי בלבד.")
                return str(positive_res), self.steps
        except:
            pass

        self.steps.append(f"הפתרונות הם: $${v_str}_1 = {sp.latex(res1)}, {v_str}_2 = {sp.latex(res2)}$$")
        return f"{res1}, {res2}", self.steps

def solve_quadratic_steps(eq_str, var_name=None):
    try:
        solver = QuadraticStepSolver(eq_str, var_name)
        return solver.solve()
    except Exception as e:
        return "שגיאה", [f"לא הצלחתי לנתח את המשוואה: {str(e)}"]




# סקריפט בדיקה ל-QuadraticStepSolver

from quadratic_solver import QuadraticStepSolver


def run_tests():
    test_cases = [
        # 1. משוואה ריבועית סטנדרטית (שני פתרונות)
        "x^2 - 5x + 6 = 0",

        # 2. משוואה עם משתנה שונה (w)
        "w^2 + 4w + 4 = 0",

        # 3. משוואה ללא פתרון ממשי (דיסקרימיננטה שלילית)
        "x^2 + x + 5 = 0",

        # 4. משוואה עם שברים (בדיקת מכנה משותף)
        "x^2/2 + x/2 = 3",

        # 5. מקרה גיאומטרי (פתרון אחד חיובי ואחד שלילי)
        "x^2 - x - 6 = 0",

        # 6. מקרה קצה: משוואה שהופכת לליניארית
        "x^2 + 3x + 2 = x^2 + 5",

        # 7. משוואה עם סוגריים
        "2*(x^2 - 1) + 3*x = x^2 + 7"
    ]

    print(f"{'=' * 20} הרצת בדיקות למשוואות ריבועיות {'=' * 20}\n")

    for i, eq in enumerate(test_cases, 1):
        print(f"בדיקה {i}: המשוואה היא {eq}")
        try:
            solver = QuadraticStepSolver(eq)
            result, steps = solver.solve()

            print(f"תוצאה סופית: {result}")
            print("שלבי הפתרון:")
            for step_num, step_text in enumerate(steps, 1):
                # ניקוי סימני ה-$$ לתצוגה נקייה בטרמינל
                clean_step = step_text.replace('$$', '')
                print(f"  {step_num}. {clean_step}")

        except Exception as e:
            print(f"שגיאה בהרצת הבדיקה: {e}")

        print("-" * 60)


if __name__ == "__main__":
    run_tests()






# import sympy as sp
# from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, \
#     convert_xor
#
#
# class QuadraticStepSolver:
#     def __init__(self, equation_str, var_symbol=None):
#         self.steps = []
#         clean_str = equation_str.replace('^', '**')
#
#         if '=' in clean_str:
#             lhs_s, rhs_s = clean_str.split('=')
#         else:
#             lhs_s, rhs_s = clean_str, "0"
#
#         trans = standard_transformations + (implicit_multiplication_application, convert_xor)
#
#         # זיהוי הנעלם - בודקים את האגפים לפני הצמצום
#         temp_lhs = parse_expr(lhs_s, transformations=trans)
#         temp_rhs = parse_expr(rhs_s, transformations=trans)
#         all_symbols = temp_lhs.free_symbols | temp_rhs.free_symbols
#
#         if var_symbol:
#             self.var = sp.Symbol(str(var_symbol))
#         elif all_symbols:
#             self.var = sorted(list(all_symbols), key=lambda s: s.name)[0]
#         else:
#             self.var = sp.Symbol('x')
#
#         self.lhs = parse_expr(lhs_s, transformations=trans, evaluate=False)
#         self.rhs = parse_expr(rhs_s, transformations=trans, evaluate=False)
#
#     def _clean(self, expr):
#         if not hasattr(expr, 'atoms'): return expr
#         return expr.subs({n: sp.Integer(n) for n in expr.atoms(sp.Float) if n == int(n)})
#
#     def _render(self, l, r):
#         return f"$${sp.latex(self._clean(l))} = {sp.latex(self._clean(r))}$$"
#
#     def solve(self):
#         current_lhs = self.lhs
#         current_rhs = self.rhs
#         v_str = sp.latex(self.var)
#
#         # 1. טיפול במכנה משותף
#         all_expr = current_lhs + current_rhs
#         denoms = [sp.denom(t) for t in sp.preorder_traversal(all_expr) if sp.denom(t) != 1]
#         if denoms:
#             lcm = sp.lcm(denoms)
#             if lcm != 1:
#                 self.steps.append(f"נכפיל את כל המשוואה במכנה המשותף ({lcm}) כדי להיפטר מהשברים:")
#                 current_lhs = sp.expand(current_lhs * lcm)
#                 current_rhs = sp.expand(current_rhs * lcm)
#                 self.steps.append(self._render(current_lhs, current_rhs))
#
#         # 2. פתיחת סוגריים ופישוט
#         if "(" in str(current_lhs) or "(" in str(current_rhs):
#             self.steps.append("נפתח סוגריים ונכנס איברים דומים:")
#             current_lhs = sp.expand(current_lhs)
#             current_rhs = sp.expand(current_rhs)
#             self.steps.append(self._render(current_lhs, current_rhs))
#
#         # 3. העברת אגפים לצורה סטנדרטית
#         if current_rhs != 0:
#             self.steps.append(f"נעביר את כל האיברים לאגף שמאל כדי לבדוק את סוג המשוואה:")
#             final_expr = sp.expand(current_lhs - current_rhs)
#             current_rhs = sp.Integer(0)
#             self.steps.append(self._render(final_expr, current_rhs))
#         else:
#             final_expr = sp.expand(current_lhs)
#
#         # 4. זיהוי מקדמים ובדיקה אם המשוואה ליניארית
#         final_expr = sp.collect(final_expr, self.var)
#         a = final_expr.coeff(self.var, 2)
#
#         # --- תיקון לוגיקת הניתוב ל-linear_solver ---
#         if a == 0:
#             # ניצור מחרוזת של המשוואה שנותרה (למשל "3x - 3 = 0")
#             linear_eq_str = f"{sp.latex(final_expr)} = 0"
#
#             # ייבוא מקומי של הפותר הליניארי
#             try:
#                 from solvers.linear_solver import UniversalStepSolver
#             except ImportError:
#                 from linear_solver import UniversalStepSolver
#
#             # יצירת פותר ליניארי והעברת הנעלם הנכון (למשל w או x)
#             linear_solver = UniversalStepSolver(linear_eq_str, var_symbol=self.var)
#             linear_res, linear_steps = linear_solver.solve()
#
#             self.steps.extend(linear_steps)
#             return linear_res, self.steps
#         # -------------------------------------------
#
#         b = final_expr.coeff(self.var, 1)
#         c = final_expr.coeff(self.var, 0)
#
#         self.steps.append(f"נזהה את המקדמים של המשוואה הריבועית: $$a = {a}, b = {b}, c = {c}$$")
#
#         # 5. דיסקרימיננטה
#         delta = b ** 2 - 4 * a * c
#         self.steps.append(f"נחשב את הדיסקרימיננטה ($\Delta = b^2 - 4ac$):")
#         self.steps.append(f"$$\Delta = ({b})^2 - 4 \cdot ({a}) \cdot ({c}) = {delta}$$")
#
#         if delta < 0:
#             self.steps.append(f"קיבלנו $\Delta = {delta}$. כיוון שהערך שלילי, למשוואה **אין פתרון ממשי**.")
#             return "אין פתרון", self.steps
#
#         # 6. נוסחת השורשים
#         sqrt_delta = sp.sqrt(delta)
#         sol1 = sp.simplify((-b + sqrt_delta) / (2 * a))
#         sol2 = sp.simplify((-b - sqrt_delta) / (2 * a))
#
#         self.steps.append("נציב את הערכים בנוסחת השורשים:")
#         self.steps.append(f"$${v_str}_{{1,2}} = \\frac{{-({b}) \\pm \\sqrt{{{delta}}}}}{{2 \\cdot {a}}}$$")
#
#         if delta == 0:
#             res = self._clean(sol1)
#             self.steps.append(f"קיבלנו פתרון יחיד: $${v_str} = {sp.latex(res)}$$")
#             return str(res), self.steps
#
#         res1 = self._clean(sol1)
#         res2 = self._clean(sol2)
#
#         # 7. לוגיקה לסינון פתרונות
#         try:
#             val1 = float(res1)
#             val2 = float(res2)
#             if (val1 > 0 and val2 <= 0) or (val2 > 0 and val1 <= 0):
#                 positive_res = res1 if val1 > 0 else res2
#                 self.steps.append(
#                     f"הפתרונות שהתקבלו הם: $${v_str}_1 = {sp.latex(res1)}, {v_str}_2 = {sp.latex(res2)}$$")
#                 self.steps.append("בבעיות המייצגות מידות פיזיקליות (כמו אורך או זמן), נבחר בפתרון החיובי בלבד.")
#                 return str(positive_res), self.steps
#         except:
#             pass
#
#         self.steps.append(f"הפתרונות הם: $${v_str}_1 = {sp.latex(res1)}, {v_str}_2 = {sp.latex(res2)}$$")
#         return f"{res1}, {res2}", self.steps
#
#
# def solve_quadratic_steps(eq_str, var_name=None):
#     try:
#         solver = QuadraticStepSolver(eq_str, var_name)
#         return solver.solve()
#     except Exception as e:
#         return "שגיאה", [f"לא הצלחתי לנתח את המשוואה: {str(e)}"]













# import sympy as sp
# from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
#
# class QuadraticStepSolver:
#     def __init__(self, equation_str, var_symbol='x'):
#         self.steps = []  # רשימה לאיסוף השלבים
#         clean_str = equation_str.replace('^', '**')
#         lhs_s, rhs_s = clean_str.split('=')
#         trans = standard_transformations + (implicit_multiplication_application, convert_xor)
#
#         # הגדרת המשתנה
#         self.var = sp.Symbol(str(var_symbol))
#         self.lhs = parse_expr(lhs_s, transformations=trans)
#         self.rhs = parse_expr(rhs_s, transformations=trans)
#
#     def _render(self, l, r):
#         return f"$${sp.latex(self._clean_display(l))} = {sp.latex(self._clean_display(r))}$$"
#
#     def _clean_display(self, expr):
#         if not hasattr(expr, 'atoms'): return expr
#         return expr.subs({n: sp.Integer(n) for n in expr.atoms(sp.Float) if n == int(n)})
#
#     def solve(self):
#         current_lhs = self.lhs
#         current_rhs = self.rhs
#         v_str = sp.latex(self.var)
#
#         # 1. טיפול בשברים
#         denoms = [sp.denom(t) for t in sp.preorder_traversal(current_lhs + current_rhs) if sp.denom(t) != 1]
#         if denoms:
#             lcm = sp.lcm(denoms)
#             self.steps.append(f"נכפיל את כל המשוואה במכנה המשותף {lcm}:")
#             current_lhs = sp.expand(current_lhs * lcm)
#             current_rhs = sp.expand(current_rhs * lcm)
#             self.steps.append(f"{self._render(current_lhs, current_rhs)}")
#
#         # 2. פתיחת סוגריים
#         if "(" in str(self.lhs) or "(" in str(self.rhs):
#             self.steps.append("נפתח סוגריים ונפשט את האגפים:")
#             current_lhs = sp.expand(current_lhs)
#             current_rhs = sp.expand(current_rhs)
#             self.steps.append(f"{self._render(current_lhs, current_rhs)}")
#
#         # 3. העברת אגפים
#         if current_rhs != 0:
#             self.steps.append(f"נעביר את כל האיברים לאגף שמאל כדי להגיע לצורה $a{v_str}^2 + b{v_str} + c = 0$:")
#             final_expr = sp.expand(current_lhs - current_rhs)
#             current_rhs = sp.Integer(0)
#             self.steps.append(f"{self._render(final_expr, current_rhs)}")
#         else:
#             final_expr = current_lhs
#
#         # 4. זיהוי מקדמים
#         a = final_expr.coeff(self.var, 2)
#         b = final_expr.coeff(self.var, 1)
#         c = final_expr.coeff(self.var, 0)
#
#         if a == 0:
#             self.steps.append("זוהי משוואה ממעלה ראשונה.")
#             return "ליניארי", self.steps
#
#         self.steps.append(f"נזהה את המקדמים: $$a = {a}, b = {b}, c = {c}$$")
#
#         # 5. חישוב הדיסקרימיננטה
#         delta = b**2 - 4*a*c
#         self.steps.append(f"נחשב את הדיסקרימיננטה ($\Delta = b^2 - 4ac$):")
#         self.steps.append(f"$$\Delta = ({b})^2 - 4 \cdot ({a}) \cdot ({c}) = {delta}$$")
#
#         if delta < 0:
#             self.steps.append(f"קיבלנו $\Delta = {delta}$. כיוון שהדיסקרימיננטה שלילית, **אין פתרון ממשי** למשוואה.")
#             return "אין פתרון", self.steps
#
#         # 6. נוסחת השורשים
#         sqrt_delta = sp.sqrt(delta)
#         x1 = sp.simplify((-b + sqrt_delta) / (2 * a))
#         x2 = sp.simplify((-b - sqrt_delta) / (2 * a))
#
#         self.steps.append(f"נציב בנוסחת השורשים:")
#         if delta == 0:
#             self.steps.append(f"$$\Delta = 0$$, לכן יש פתרון יחיד: $${v_str} = \\frac{{-({b})}}{{2 \\cdot {a}}} = {sp.latex(x1)}$$")
#             return str(x1), self.steps
#         else:
#             self.steps.append(f"$${v_str}_{{1,2}} = \\frac{{-({b}) \\pm \\sqrt{{{delta}}}}}{{2 \\cdot {a}}}$$")
#             self.steps.append(f"הפתרונות הם: $${v_str}_1 = {sp.latex(x1)}, {v_str}_2 = {sp.latex(x2)}$$")
#             return f"{x1}, {x2}", self.steps
#
# # פונקציית השער לשרת
# def solve_quadratic_steps(eq_str, var_name='x'):
#     steps = []
#     try:
#         x = sp.Symbol(var_name)
#         # ניקוי בסיסי והפרדה לאגפים
#         if '=' not in eq_str:
#             return "Error", ["חסר סימן = במשוואה"]
#
#         lhs_str, rhs_str = eq_str.split('=')
#         # המרה לביטויים של Sympy ופתיחת סוגריים (קריטי!)
#         lhs = sp.expand(sp.parse_expr(lhs_str))
#         rhs = sp.expand(sp.parse_expr(rhs_str))
#
#         # העברת הכל לאגף שמאל
#         equation = lhs - rhs
#         steps.append(f"נסדר את המשוואה לצורה סטנדרטית: $${sp.latex(equation)} = 0$$")
#
#         # חילוץ מקדמים בצורה בטוחה
#         a = equation.coeff(x ** 2)
#         b = equation.coeff(x, 1)
#         c = equation.coeff(x, 0)
#
#         steps.append(f"נזהה את המקדמים: $$a={a}, b={b}, c={c}$$")
#
#         # חישוב הדיסקרימיננטה
#         delta = b ** 2 - 4 * a * c
#         steps.append(f"נחשב את הדיסקרימיננטה: $$\\Delta = b^2 - 4ac = {delta}$$")
#
#         if delta < 0:
#             steps.append("הדיסקרימיננטה שלילית, לכן אין פתרון ממשי.")
#             return "אין פתרון", steps
#
#         # חישוב השורשים
#         sqrt_delta = sp.sqrt(delta)
#         sol1 = sp.simplify((-b + sqrt_delta) / (2 * a))
#         sol2 = sp.simplify((-b - sqrt_delta) / (2 * a))
#
#         steps.append(f"נשתמש בנוסחת השורשים ונקבל:")
#         steps.append(f"$$x_{{1}} = {sp.latex(sol1)}$$")
#         steps.append(f"$$x_{{2}} = {sp.latex(sol2)}$$")
#
#         # --- תיקון השגיאה: המרה ל-float לצורך השוואה בלבד ---
#         try:
#             val1 = float(sol1)
#             val2 = float(sol2)
#
#             # בדיקה אם מדובר בבעיה גיאומטרית (שטח/אורך)
#             # אם אחד הפתרונות שלילי, נציע את החיובי
#             if val1 > 0 and val2 <= 0:
#                 steps.append("מכיוון שמדובר במידה גיאומטרית, נבחר בפתרון החיובי.")
#                 final_res = str(sol1)
#             elif val2 > 0 and val1 <= 0:
#                 steps.append("מכיוון שמדובר במידה גיאומטרית, נבחר בפתרון החיובי.")
#                 final_res = str(sol2)
#             else:
#                 final_res = f"{sol1}, {sol2}"
#         except:
#             # אם לא ניתן להמיר ל-float (למשל פתרון עם פרמטר), נחזיר את שניהם
#             final_res = f"{sol1}, {sol2}"
#
#         return final_res, steps
#
#     except Exception as e:
#         return "Error", [f"שגיאה בפתרון: {str(e)}"]













#
# import sympy as sp
# from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, \
#     convert_xor
#
#
# class QuadraticStepSolver:
#     def __init__(self, equation_str, var_symbol='x'):
#         self.steps = []
#         clean_str = equation_str.replace('^', '**')
#
#         # הפרדה לאגפים
#         if '=' in clean_str:
#             lhs_s, rhs_s = clean_str.split('=')
#         else:
#             lhs_s, rhs_s = clean_str, "0"
#
#         trans = standard_transformations + (implicit_multiplication_application, convert_xor)
#         self.var = sp.Symbol(str(var_symbol))
#
#         # פתיחת סוגריים ופישוט מיידי כבר בטעינה
#         self.lhs = sp.expand(parse_expr(lhs_s, transformations=trans))
#         self.rhs = sp.expand(parse_expr(rhs_s, transformations=trans))
#
#     def _render(self, l, r):
#         return f"$${sp.latex(l)} = {sp.latex(r)}$$"
#
#     def solve(self):
#         v_str = sp.latex(self.var)
#
#         # 1. העברת אגפים וסידור
#         self.steps.append(f"נפתח סוגריים ונעביר את כל האיברים לאגף שמאל:")
#         final_expr = sp.expand(self.lhs - self.rhs)
#         self.steps.append(f"{self._render(final_expr, 0)}")
#
#         # 2. זיהוי מקדמים
#         a = final_expr.coeff(self.var, 2)
#         b = final_expr.coeff(self.var, 1)
#         c = final_expr.coeff(self.var, 0)
#
#         if a == 0:
#             # אם אחרי הפישוט אין x^2, זו תקלה בניתוב או משוואה ליניארית
#             self.steps.append("המשוואה התגלתה כליניארית לאחר פישוט.")
#             return "ליניארי", self.steps
#
#         self.steps.append(f"נזהה את המקדמים: $$a = {a}, b = {b}, c = {c}$$")
#
#         # 3. דיסקרימיננטה
#         delta = b ** 2 - 4 * a * c
#         self.steps.append(f"נחשב את הדיסקרימיננטה ($\\Delta = b^2 - 4ac$):")
#         self.steps.append(f"$$\\Delta = ({b})^2 - 4 \\cdot ({a}) \\cdot ({c}) = {delta}$$")
#
#         if delta < 0:
#             self.steps.append(f"כיוון ש-$\\Delta < 0$, אין פתרון ממשי.")
#             return "אין פתרון", self.steps
#
#         # 4. נוסחת השורשים
#         sqrt_delta = sp.sqrt(delta)
#         x1 = sp.simplify((-b + sqrt_delta) / (2 * a))
#         x2 = sp.simplify((-b - sqrt_delta) / (2 * a))
#
#         self.steps.append(f"נציב בנוסחת השורשים:")
#         self.steps.append(f"$${v_str}_{{1,2}} = \\frac{{-({b}) \\pm \\sqrt{{{delta}}}}}{{2 \\cdot {a}}}$$")
#
#         if delta == 0:
#             return str(x1), self.steps
#
#         # לוגיקה לבעיות מילוליות - סינון פתרון שלילי
#         try:
#             val1, val2 = float(x1), float(x2)
#             if (val1 > 0) != (val2 > 0):  # אחד חיובי ואחד שלילי
#                 res = x1 if val1 > 0 else x2
#                 self.steps.append(f"הפתרונות הם: $${v_str}_1 = {sp.latex(x1)}, {v_str}_2 = {sp.latex(x2)}$$")
#                 self.steps.append("מכיוון שמדובר במידה גיאומטרית (אורך/שטח), נבחר בפתרון החיובי.")
#                 return str(res), self.steps
#         except:
#             pass
#
#         self.steps.append(f"הפתרונות הם: $${v_str}_1 = {sp.latex(x1)}, {v_str}_2 = {sp.latex(x2)}$$")
#         return f"{x1}, {x2}", self.steps
#
#
# def solve_quadratic_steps(eq_str, var_name='x'):
#     solver = QuadraticStepSolver(eq_str, var_name)
#     return solver.solve()