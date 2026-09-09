import sympy as sp
import re
from solvers.math_utils import MathUtils
from solvers.linear_solver import UniversalStepSolver
from solvers.substitution_solver import SystemSubstitutionSolver
from solvers.elimination_solver import EliminationSolver


class AdvancedSystemSolver:
    def __init__(self, eq1_str, eq2_str):
        self.eq1_raw = eq1_str
        self.eq2_raw = eq2_str
        self.var_x = sp.Symbol('x')
        self.var_y = sp.Symbol('y')
        self.steps = []

    def simplify_side_task(self, eq_str, name):
        """מפשט משוואה אחת ומציג את הדרך צעד אחר צעד רק אם יש צורך בפישוט"""
        # רשימה זמנית לאיסוף שלבים עבור המשוואה הספציפית
        local_steps = []

        try:
            lhs, rhs, _ = MathUtils.parse_equation(eq_str)
        except Exception as e:
            self.steps.append(f"### פישוט משוואה {name}")
            self.steps.append(f"שגיאה בפענוח המשוואה: {str(e)}")
            return eq_str

        # שמירת המצב המקורי לצורך השוואה בסוף
        initial_lhs, initial_rhs = lhs, rhs
        initial_render = MathUtils.render_equation(lhs, rhs)

        # 1. טיפול במכנה משותף
        lcm = MathUtils.get_common_denominator([lhs, rhs])
        if lcm > 1:
            local_steps.append(f"המשוואה המקורית: {initial_render}")
            local_steps.append(f"נכפיל את כל אגפי המשוואה במכנה המשותף {lcm} כדי לבטל את השברים:")
            lhs = sp.simplify(lhs * lcm)
            rhs = sp.simplify(rhs * lcm)
            local_steps.append(MathUtils.render_equation(lhs, rhs))

        # 2. פתיחת סוגריים
        if "(" in str(lhs) or "(" in str(rhs):
            # אם עוד לא הצגנו את המקור (כי לא היה LCM), נציג אותו עכשיו
            if not local_steps:
                local_steps.append(f"המשוואה המקורית: {initial_render}")
            local_steps.append("נפתח סוגריים ונכנס איברים דומים:")
            lhs = sp.expand(lhs)
            rhs = sp.expand(rhs)
            local_steps.append(MathUtils.render_equation(lhs, rhs))

        # 3. חישוב הצורה הסופית (AX + BY = C)
        full_expr = lhs - rhs
        constant_term = full_expr.subs({self.var_x: 0, self.var_y: 0})

        final_lhs = MathUtils.clean_floats(sp.simplify(full_expr - constant_term))
        final_rhs = MathUtils.clean_floats(sp.simplify(-constant_term))

        # 4. בדיקת צורך בסידור (האם הצורה הנוכחית שונה מהצורה התקנית?)
        # אנחנו בודקים אם אגף שמאל או ימין השתנו מבחינה ויזואלית/מבנית
        if sp.simplify(lhs - final_lhs) != 0 or sp.simplify(rhs - final_rhs) != 0:
            local_steps.append("נסדר את המשוואה (נעלמים בשמאל, מספרים בימין):")
            local_steps.append(MathUtils.render_equation(final_lhs, final_rhs))

        # --- השלב הקריטי: האם להוסיף את הכל לרשימה הראשית? ---
        if local_steps:
            self.steps.append(f"### שלב א: פישוט משוואה {name}")
            self.steps.extend(local_steps)

        # תמיד מחזירים את המחרוזת המפושטת עבור שלב הפתרון הבא
        return f"{final_lhs} = {final_rhs}"

    def solve(self):
        self.steps.append("## תהליך פתרון מערכת משוואות מורכבת")

        # שלב הפישוט עבור שתי המשוואות
        eq1_simple = self.simplify_side_task(self.eq1_raw, "I")
        eq2_simple = self.simplify_side_task(self.eq2_raw, "II")

        # החלטה על אסטרטגיית פתרון: אלימינציה או הצבה?
        try:
            # נשתמש באובייקט זמני כדי לבדוק את המקדמים לאחר הפישוט
            temp_elim = EliminationSolver(eq1_simple, eq2_simple)
            coeffs = [temp_elim.a1, temp_elim.b1, temp_elim.a2, temp_elim.b2]

            # אם יש מקדם שהוא 1 או 1-, שיטת ההצבה תהיה נוחה יותר (לא תייצר שברים)
            has_unit_coeff = any(abs(c) == 1 for c in coeffs)

            if has_unit_coeff:
                self.steps.append("נבחר ב**שיטת ההצבה**, כיוון שזיהינו משתנה עם מקדם 1 המאפשר בידוד קל.")
                final_solver = SystemSubstitutionSolver(eq1_simple, eq2_simple)
            else:
                self.steps.append(
                    "נבחר ב**שיטת השוואת מקדמים (אלימינציה)**, כיוון שהיא יעילה יותר עבור מקדמים מורכבים.")
                final_solver = temp_elim

        except Exception:
            # גיבוי במקרה של בעיה בזיהוי המקדמים
            self.steps.append("נפתור באמצעות שיטת ההצבה הכללית.")
            final_solver = SystemSubstitutionSolver(eq1_simple, eq2_simple)

        # הרצת הפתרון הנבחר ואיסוף השלבים
        result, solver_steps = final_solver.solve()

        # הסרת כותרות כפולות אם ישנן (אופציונלי)
        clean_solver_steps = [s for s in solver_steps if "## פתרון מערכת משוואות" not in s]
        self.steps.extend(clean_solver_steps)

        return result, self.steps


def solve_advanced_system_steps(eq_text):
    """פונקציית המעטפת שנקראת מה-API או מהבדיקות"""
    try:
        # הפרדה בין המשוואות
        parts = re.split(r',|and', eq_text)
        if len(parts) < 2:
            return {"result": "Error", "steps": ["יש לספק שתי משוואות מופרדות בפסיק."]}

        solver = AdvancedSystemSolver(parts[0].strip(), parts[1].strip())
        result, steps = solver.solve()

        # מחזירים מילון כדי להתאים ל-run_test ול-API
        return {"result": result, "steps": steps}

    except Exception as e:
        return {"result": "Error", "steps": [f"שגיאה במערכת המורכבת: {str(e)}"]}
#
# from solvers.complex_system_solver import solve_advanced_system_steps
# def run_test(name, equations):
#     print(f"\n{'=' * 20}")
#     print(f"בדיקה: {name}")
#     print(f"משוואות: {equations}")
#     print(f"{'=' * 20}\n")
#
#     result_data = solve_advanced_system_steps(equations)
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
#     # 1. בדיקת מערכת רגילה (פתרון יחיד)
#     run_test("מערכת רגילה", "x + y = 10, 2x - y = 8")
#
#     # 2. בדיקת מערכת עם אינסוף פתרונות (הדוגמה הקריטית)
#     run_test("אינסוף פתרונות", "5x + 10y = 540, 5x + 10y = 540")
#
#     # 3. בדיקת מערכת ללא פתרון
#     run_test("אין פתרון", "x + y = 5, x + y = 10")
#
#     # 4. בדיקת מערכת עם משוואה ריבועית (בונוס)
#     run_test("מערכת ריבועית", "y = x^2, y = 4")