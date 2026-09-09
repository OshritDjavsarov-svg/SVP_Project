import sympy as sp
import re
from solvers.math_utils import MathUtils


class ProbabilityBernoulliSolver:
    def __init__(self, equation_str):
        self.steps = []
        self.equation_str = equation_str

        # ניקוי בסיסי
        clean_eq = equation_str.replace(' ', '').replace('^', '**')

        # 1. שליפת n ו-k מתוך C(n,k) או משתנים דומים
        c_match = re.search(r'[Cc]\((\d+),(\d+)\)', clean_eq)
        if c_match:
            # שימוש ב-SymPy Integer במקום int רגיל
            self.n = sp.Integer(c_match.group(1))
            self.k = sp.Integer(c_match.group(2))
        else:
            # ברירת מחדל אם לא נמצא
            self.n, self.k = sp.Integer(5), sp.Integer(3)

        # 2. שליפת ההסתברויות p ו-q
        probs = re.findall(r'\((0\.\d+)\)', clean_eq)
        if len(probs) >= 2:
            self.p = sp.Float(probs[0])
            self.q = sp.Float(probs[1])
        else:
            # אם נמצא רק p אחד, נחשב את q כמשלים ל-1 בצורה מדויקת
            if len(probs) == 1:
                self.p = sp.Float(probs[0])
                self.q = sp.simplify(1 - self.p)
            else:
                self.p, self.q = sp.Float(0.5), sp.Float(0.5)

    def solve(self):
        self.steps.append("## פתרון בעיית הסתברות (נוסחת ברנולי)")

        # שימוש ב-MathUtils כדי לנקות את התצוגה של ההסתברויות (למשל למנוע אפסים מיותרים)
        p_clean = MathUtils.clean_floats(self.p)
        q_clean = MathUtils.clean_floats(self.q)

        # הצגת המשוואה בפורמט LaTeX
        display_eq = f"P(k={self.k}) = \\binom{{{self.n}}}{{{self.k}}} \\cdot {sp.latex(p_clean)}^{{{self.k}}} \\cdot {sp.latex(q_clean)}^{{{self.n - self.k}}}"
        self.steps.append(f"נפתור את המשוואה לפי נוסחת ברנולי:")
        self.steps.append(f"$${display_eq}$$")

        # שלב 1: המקדם הבינומי
        self.steps.append(f"### שלב 1: חישוב המקדם הבינומי $C({self.n},{self.k})$")

        # שימוש ב-SymPy במקום בספריית math לחישוב קומבינטוריקה אחיד
        combinations = sp.binomial(self.n, self.k)

        self.steps.append(f"מספר האפשרויות לבחור {self.k} מתוך {self.n} הוא:")
        self.steps.append(
            f"$$\\binom{{{self.n}}}{{{self.k}}} = \\frac{{{self.n}!}}{{{self.k}!({self.n}-{self.k})!}} = {combinations}$$")

        # שלב 2: חזקות
        self.steps.append("### שלב 2: חישוב ההסתברויות")

        # חישוב החזקות
        p_val = sp.simplify(self.p ** self.k)
        q_val = sp.simplify(self.q ** (self.n - self.k))

        # עיגול ל-6 ספרות אחרי הנקודה רק למטרות תצוגה פדגוגית, וניקוי דרך MathUtils
        p_val_display = MathUtils.clean_floats(sp.Float(p_val, 6))
        q_val_display = MathUtils.clean_floats(sp.Float(q_val, 6))

        self.steps.append(
            f"1. הסתברות להצלחות: $${sp.latex(p_clean)}^{{{self.k}}} \\approx {sp.latex(p_val_display)}$$")
        self.steps.append(
            f"2. הסתברות לכישלונות: $${sp.latex(q_clean)}^{{{self.n - self.k}}} \\approx {sp.latex(q_val_display)}$$")

        # שלב 3: תוצאה סופית
        final_result = combinations * p_val * q_val

        self.steps.append("### שלב 3: שילוב סופי")
        self.steps.append(f"נכפיל את כל הגורמים יחד:")
        self.steps.append(f"$$P = {combinations} \\cdot {sp.latex(p_val_display)} \\cdot {sp.latex(q_val_display)}$$")

        # הכנת התוצאה הסופית והאחוזים (ללא אפסים מיותרים)
        res_rounded = MathUtils.clean_floats(sp.Float(final_result, 5))
        percent = MathUtils.clean_floats(sp.Float(final_result * 100, 4))

        self.steps.append("---")
        self.steps.append(f"**התוצאה הסופית: $$P = {sp.latex(res_rounded)}$$**")
        self.steps.append(f"במילים אחרות, ישנו סיכוי של **{percent}%**.")

        return str(res_rounded), self.steps


def solve_probability_steps(text):
    """פונקציית הממשק לשרת"""
    try:
        solver = ProbabilityBernoulliSolver(text)
        result, steps = solver.solve()

        # החזרה כמילון כדי לשמור על אחידות עם כל שאר הפותרים במערכת
        return {"result": result, "steps": steps}
    except Exception as e:
        return {"result": "Error", "steps": [f"שגיאה בחישוב ההסתברות: {str(e)}"]}

#
# from solvers.probability_solver import solve_probability_steps
# def run_test(name, equations):
#     print(f"\n{'=' * 20}")
#     print(f"בדיקה: {name}")
#     print(f"משוואות: {equations}")
#     print(f"{'=' * 20}\n")
#
#     result_data = solve_probability_steps(equations)
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
#     # בדיקה 1: קלט עם n, k ו-p
#     run_test("ברנולי קלאסי", "C(6,2) p=(0.7)")
#
#     # בדיקה 2: קלט עם p ו-q מפורשים
#     run_test("ברנולי עם q מפורש", "C(4,3) p=(0.2) q=(0.8)")
