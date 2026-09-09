import sympy as sp
import re
from solvers.math_utils import MathUtils
from solvers.complex_system_solver import AdvancedSystemSolver


class SubstitutionSystemSolver:
    def __init__(self, eq1_str, eq2_str):
        self.steps = []
        self.eq1_raw = eq1_str
        self.eq2_raw = eq2_str
        self.x, self.y = sp.symbols('x y')
        self.u, self.v = sp.symbols('u v')

    def solve(self):
        self.steps.append("## פתרון מערכת משוואות עם נעלמים במכנה")
        self.steps.append("המשתנים נמצאים במכנה. נשתמש בשיטת **הצבת משתני עזר**.")

        # --- שלב 1: הגדרת משתני עזר ---
        self.steps.append("### שלב 1: הגדרת משתני עזר")
        self.steps.append(f"נגדיר: $$u = \\frac{{1}}{{x}}, \\quad v = \\frac{{1}}{{y}}$$")

        try:
            # פירוק וסידור ראשוני של המקוריות
            lhs1, rhs1, _ = MathUtils.parse_equation(self.eq1_raw)
            lhs2, rhs2, _ = MathUtils.parse_equation(self.eq2_raw)

            # הצבה מתמטית נקייה
            u_eq1_lhs = lhs1.subs({1 / self.x: self.u, 1 / self.y: self.v})
            u_eq1_rhs = rhs1.subs({1 / self.x: self.u, 1 / self.y: self.v})
            u_eq2_lhs = lhs2.subs({1 / self.x: self.u, 1 / self.y: self.v})
            u_eq2_rhs = rhs2.subs({1 / self.x: self.u, 1 / self.y: self.v})

            self.steps.append("המשוואות לאחר הצבת המשתנים החדשים:")
            self.steps.append(f"I) {MathUtils.render_equation(u_eq1_lhs, u_eq1_rhs)}")
            self.steps.append(f"II) {MathUtils.render_equation(u_eq2_lhs, u_eq2_rhs)}")

            # --- שלב 2: פתרון המערכת הליניארית ---
            self.steps.append("### שלב 2: פתרון המערכת עבור $u$ ו-$v$")

            # שליחה לפותר המערכות המורכב
            uv_solver = AdvancedSystemSolver(f"{u_eq1_lhs}={u_eq1_rhs}", f"{u_eq2_lhs}={u_eq2_rhs}")

            # עדכון המשתנים בתוך הפותר כדי שלא יחפש x,y
            uv_solver.var_x = self.u
            uv_solver.var_y = self.v

            # קבלת התוצאה והשלבים
            uv_res_str, uv_steps = uv_solver.solve()

            # סינון שלבים כפולים או כותרות מיותרות מהפותר הפנימי
            for s in uv_steps:
                if "תהליך פתרון" not in s and "הפתרון הסופי" not in s:
                    self.steps.append(s)

            # פתרון ישיר ב-SymPy כדי לקבל ערכים מדויקים להמשך (למניעת טעויות parsing מהטקסט)
            sol_uv = sp.solve([u_eq1_lhs - u_eq1_rhs, u_eq2_lhs - u_eq2_rhs], [self.u, self.v])

            if not sol_uv:
                return "אין פתרון", self.steps

            val_u = MathUtils.clean_floats(sol_uv[self.u])
            val_v = MathUtils.clean_floats(sol_uv[self.v])

            if val_u == 0 or val_v == 0:
                self.steps.append(" אחד מערכי העזר יצא 0. לא ניתן לחלק ב-0, לכן אין פתרון למערכת המקורית.")
                return "אין פתרון", self.steps

            # --- שלב 3: חזרה למקור ---
            self.steps.append("### שלב 3: חזרה למשתנים המקוריים ($x, y$)")

            res_x = MathUtils.clean_floats(1 / val_u)
            res_y = MathUtils.clean_floats(1 / val_v)

            self.steps.append(f"נציב בחזרה את הערכים שמצאנו:")
            self.steps.append(f"$$x = \\frac{{1}}{{u}} = \\frac{{1}}{{{sp.latex(val_u)}}} = {sp.latex(res_x)}$$")
            self.steps.append(f"$$y = \\frac{{1}}{{v}} = \\frac{{1}}{{{sp.latex(val_v)}}} = {sp.latex(res_y)}$$")

            final_res = f"({sp.latex(res_x)}, {sp.latex(res_y)})"
            self.steps.append("---")
            self.steps.append(f"**הפתרון הסופי: ${final_res}$**")

            return final_res, self.steps

        except Exception as e:
            return "Error", [f"שגיאה בפתרון המערכת: {str(e)}"]


def solve_rational_substitution_steps(eq_text):
    """השער הראשי למערכת - מחזיר Tuple לעבודה חלקה עם שאר המערכת"""
    try:
        parts = re.split(r',|and', eq_text)
        if len(parts) < 2:
            # החזרת שגיאה במבנה של Tuple
            return "Error", ["נא לספק שתי משוואות מופרדות בפסיק"]

        solver = SubstitutionSystemSolver(parts[0].strip(), parts[1].strip())
        result, steps = solver.solve()

        return result, steps

    except Exception as e:
        # החזרת שגיאה במבנה של Tuple
        return "Error", [f"שגיאה בניתוב המערכת: {str(e)}"]

#
# from solvers.rational_substitution_solver import solve_rational_substitution_steps
# def run_test(name, equations):
#     print(f"\n{'=' * 20}")
#     print(f"בדיקה: {name}")
#     print(f"משוואות: {equations}")
#     print(f"{'=' * 20}\n")
#
#     result_data = solve_rational_substitution_steps(equations)
#
#     if result_data["result"] == "Error":
#         print(f"שגיאה: {result_data['steps'][0]}")
#     else:
#         print(f"תוצאה סופית: {result_data['result']}")
#         print("\nשלבי הפתרון:")
#         for i, step in enumerate(result_data["steps"], 1):
#             print(f"{step}")
#
#
# if __name__ == "__main__":
#     run_test("מערכת כלשהי", "1/x + 1/y = 5, 2/x - 1/y = 1")
