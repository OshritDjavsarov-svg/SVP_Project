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



#
# # סקריפט בדיקה ל-QuadraticStepSolver
#
# from quadratic_solver import QuadraticStepSolver
#
#
# def run_tests():
#     test_cases = [
#         # 1. משוואה ריבועית סטנדרטית (שני פתרונות)
#         "x^2 - 5x + 6 = 0",
#
#         # 2. משוואה עם משתנה שונה (w)
#         "w^2 + 4w + 4 = 0",
#
#         # 3. משוואה ללא פתרון ממשי (דיסקרימיננטה שלילית)
#         "x^2 + x + 5 = 0",
#
#         # 4. משוואה עם שברים (בדיקת מכנה משותף)
#         "x^2/2 + x/2 = 3",
#
#         # 5. מקרה גיאומטרי (פתרון אחד חיובי ואחד שלילי)
#         "x^2 - x - 6 = 0",
#
#         # 6. מקרה קצה: משוואה שהופכת לליניארית
#         "x^2 + 3x + 2 = x^2 + 5",
#
#         # 7. משוואה עם סוגריים
#         "2*(x^2 - 1) + 3*x = x^2 + 7"
#     ]
#
#     print(f"{'=' * 20} הרצת בדיקות למשוואות ריבועיות {'=' * 20}\n")
#
#     for i, eq in enumerate(test_cases, 1):
#         print(f"בדיקה {i}: המשוואה היא {eq}")
#         try:
#             solver = QuadraticStepSolver(eq)
#             result, steps = solver.solve()
#
#             print(f"תוצאה סופית: {result}")
#             print("שלבי הפתרון:")
#             for step_num, step_text in enumerate(steps, 1):
#                 # ניקוי סימני ה-$$ לתצוגה נקייה בטרמינל
#                 clean_step = step_text.replace('$$', '')
#                 print(f"  {step_num}. {clean_step}")
#
#         except Exception as e:
#             print(f"שגיאה בהרצת הבדיקה: {e}")
#
#         print("-" * 60)
#
#
# if __name__ == "__main__":
#     run_tests()
