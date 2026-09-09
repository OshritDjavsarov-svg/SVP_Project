import sympy as sp
from solvers.math_utils import MathUtils  # ייבוא קובץ העזר

class UniversalStepSolver:
    def __init__(self, equation_str, var_symbol=None):
        self.steps = []
        # שימוש בפונקציה המשותפת לאתחול
        self.lhs, self.rhs, self.var = MathUtils.parse_equation(equation_str, var_symbol)

    def solve(self):
        current_lhs = self.lhs
        current_rhs = self.rhs

        # 1. טיפול בשברים
        lcm = MathUtils.get_common_denominator([current_lhs, current_rhs])
        if lcm > 1:
            self.steps.append(f"נכפיל את כל אגפי המשוואה במכנה המשותף {lcm} כדי להיפטר מהשברים:")
            current_lhs = sp.Mul(lcm, current_lhs, evaluate=False)
            current_rhs = sp.Mul(lcm, current_rhs, evaluate=False)
            self.steps.append(MathUtils.render_equation(current_lhs, current_rhs))

            current_lhs = sp.simplify(current_lhs)
            current_rhs = sp.simplify(current_rhs)
            self.steps.append(f"לאחר צמצום המכנים נקבל: {MathUtils.render_equation(current_lhs, current_rhs)}")

        # 2. פתיחת סוגריים
        if "(" in str(current_lhs) or "(" in str(current_rhs):
            expanded_lhs = sp.expand(current_lhs)
            expanded_rhs = sp.expand(current_rhs)
            if expanded_lhs != current_lhs or expanded_rhs != current_rhs:
                current_lhs, current_rhs = expanded_lhs, expanded_rhs
                self.steps.append(f"נפתח סוגריים לפי חוק הפילוג: {MathUtils.render_equation(current_lhs, current_rhs)}")

        # 3. כינוס איברים דומים
        simplified_lhs = sp.simplify(current_lhs)
        simplified_rhs = sp.simplify(current_rhs)
        if sp.latex(simplified_lhs) != sp.latex(current_lhs) or sp.latex(simplified_rhs) != sp.latex(current_rhs):
            current_lhs, current_rhs = simplified_lhs, simplified_rhs
            self.steps.append(f"נכנס איברים דומים בכל אגף: {MathUtils.render_equation(current_lhs, current_rhs)}")

        # 4. העברת אגפים
        while True:
            desc, next_lhs, next_rhs = MathUtils.rule_move_terms(current_lhs, current_rhs, self.var)
            if not desc:
                break
            current_lhs = sp.simplify(next_lhs)
            current_rhs = sp.simplify(next_rhs)
            self.steps.append(f"{desc} {MathUtils.render_equation(current_lhs, current_rhs)}")

        # 5. חישוב סופי
        final_lhs = sp.simplify(current_lhs)
        final_rhs = sp.simplify(current_rhs)
        coeff = final_lhs.coeff(self.var)

        if coeff == 0:
            var_name = str(self.var)
            if sp.simplify(final_lhs - final_rhs) == 0:
                self.steps.append(f"קיבלנו מצב שבו שני אגפי המשוואה שווים תמיד. יש **אינסוף פתרונות**.")
                return "אינסוף פתרונות", self.steps
            else:
                self.steps.append(f"קיבלנו תוצאה שאינה הגיונית. לכן **אין פתרון**.")
                return "אין פתרון", self.steps

        exact_result = final_rhs / coeff
        res_clean = MathUtils.clean_floats(exact_result)

        numeric_val = float(res_clean)
        if numeric_val == int(numeric_val):
            res_latex = sp.latex(int(numeric_val))
        else:
            rounded = round(numeric_val, 4)
            res_latex = f"{sp.latex(res_clean)} \\approx {rounded}"

        final_eq_latex = f"{self.var} = {res_latex}"

        # if coeff != 1:
        #     div_desc = f"נחלק במקדם של {self.var} (שהוא {sp.latex(MathUtils.clean_floats(coeff))}) ונקבל:"
        #     self.steps.append(f"{div_desc} **התוצאה הסופית: $${final_eq_latex}$$**")
        # else:
        #     final_step_text =f"### התוצאה הסופית:\n$${final_eq_latex}$$"
        #     if not self.steps or final_eq_latex not in self.steps[-1]:
        #         self.steps.append(final_step_text)
        #     else:
        #         self.steps[-1] = f"**{self.steps[-1]}**"
        #
        # return str(res_clean), self.steps

        # --- עדכון ארכיטקטוני: הפרדת שלב החלוקה הפדגוגי מהתוצאה הסופית ---
        if coeff != 1 and coeff != -1:
            div_desc = f"נחלק את שני האגפים במקדם של {self.var} (שהוא {sp.latex(MathUtils.clean_floats(coeff))}):"
            self.steps.append(div_desc)

            # 1. הצגת פעולת החלוקה המקורית בצורת שבר ללא צמצום
            latex_fraction = f"\\frac{{{sp.latex(MathUtils.clean_floats(current_rhs))}}}{{{sp.latex(MathUtils.clean_floats(coeff))}}}"
            self.steps.append(f"$${sp.latex(self.var)} = {latex_fraction}$$")

            # 2. הוספת התוצאה המחושבת המצומצמת מיד לאחר מכן (למשל: x = 5)
            self.steps.append("לאחר ביצוע החישוב והצמצום נקבל:")
            self.steps.append(f"$${final_eq_latex}$$")

        elif coeff == -1:
            self.steps.append(f"נכפיל או נחלק את שני האגפים ב-(-1) כדי לקבל נעלם חיובי:")
            self.steps.append(f"$${final_eq_latex}$$")

        # הוספת שלב סיכום ברור עבור ערך המשתנה הנוכחי (משתמש בכותרת תת-שלב המותאמת ל-Pipe שלך)
        self.steps.append(f"### נמצא כי ערכו של {sp.latex(self.var)} הוא:\n$${final_eq_latex}$$")

        return str(res_clean), self.steps

def solve_linear_steps(equation_str):
    try:
        solver = UniversalStepSolver(equation_str)
        result, steps = solver.solve()
        return {"result": result, "steps": steps}
    except Exception as e:
        return {"result": "Error", "steps": [f"שגיאה בתהליך הפתרון: {str(e)}"]}

#
# from linear_solver import solve_linear_steps
# def run_test():
#     # שלוש משוואות טסט שמייצגות מקרים שונים
#     equations_to_test = [
#         "3*w + 5 = 3w +5",  # מקרה קלאסי של העברת אגפים
#         "2*(x + 3) = 14",  # מקרה של פתיחת סוגריים
#         "x/2 + 3 = x/3 + 5"  # מקרה של שברים ומכנה משותף
#     ]
#
#     for eq in equations_to_test:
#         print(f"=========================================")
#         print(f"המשוואה המקורית: {eq}")
#         print(f"=========================================")
#
#         # קריאה לפונקציית הפתרון מהקובץ שלך
#         solution_data = solve_linear_steps(eq)
#
#         # הדפסת השלבים
#         steps = solution_data.get("steps", [])
#         for i, step in enumerate(steps):
#             print(f"שלב {i + 1}: {step}")
#
#         print(f"\nהערך שחזר מהפונקציה: {solution_data.get('result')}\n")
#
#
# if __name__ == "__main__":
#     run_test()
