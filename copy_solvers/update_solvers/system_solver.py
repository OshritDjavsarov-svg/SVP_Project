# כאן בקובץ זה אין מימוש נכון של כינוס איברים והעברת אגפים - הכל נעשה בבום!!!!!!!

import sympy as sp
from solvers.math_utils import MathUtils
from solvers.linear_solver import UniversalStepSolver
from solvers.quadratic_solver import QuadraticStepSolver


class SystemSubstitutionSolver:
    def __init__(self, eq1_str, eq2_str):
        self.steps = []
        self.x, self.y = sp.symbols('x y')
        self.lhs1, self.rhs1, _ = MathUtils.parse_equation(eq1_str)
        self.lhs2, self.rhs2, _ = MathUtils.parse_equation(eq2_str)

    def _add_step(self, text):
        if not self.steps or self.steps[-1] != text:
            self.steps.append(text)

    def solve(self):
        self._add_step("## פתרון מערכת משוואות בשיטת ההצבה")
        self._add_step("המערכת הנתונה:")
        self._add_step(f"I) {MathUtils.render_equation(self.lhs1, self.rhs1)}")
        self._add_step(f"II) {MathUtils.render_equation(self.lhs2, self.rhs2)}")

        # --- שלב 1: בידוד ---
        best_iso = (0, self.y, "I")
        for i, (l, r) in enumerate([(self.lhs1, self.rhs1), (self.lhs2, self.rhs2)]):
            diff = l - r
            for v in [self.y, self.x]:
                if abs(diff.coeff(v)) == 1:
                    best_iso = (i, v, "I" if i == 0 else "II")
                    break

        idx, iso_var, label = best_iso
        self._add_step(f"### שלב 1: בידוד משתנה במשוואה {label}")

        curr_l = self.lhs1 if idx == 0 else self.lhs2
        curr_r = self.rhs1 if idx == 0 else self.rhs2
        final_l, final_r = MathUtils.apply_algebraic_steps(curr_l, curr_r, iso_var, self.steps)

        coeff = final_l.coeff(iso_var)
        iso_expr = sp.simplify(final_r / coeff) if coeff != 1 else final_r
        if coeff != 1 and coeff != 0:
            self._add_step(
                f"נחלק במקדם של {sp.latex(iso_var)} ונקבל: $${sp.latex(iso_var)} = {sp.latex(MathUtils.clean_floats(iso_expr))}$$")

        # --- שלב 2: הצבה ---
        other_label = "II" if label == "I" else "I"
        other_l = self.lhs2 if label == "I" else self.lhs1
        other_r = self.rhs2 if label == "I" else self.rhs1
        other_var = self.x if iso_var == self.y else self.y

        self._add_step(f"### שלב 2: הצבה במשוואה {other_label}")
        self._add_step(
            f"נציב $${sp.latex(iso_var)} = {sp.latex(MathUtils.clean_floats(iso_expr))}$$ במשוואה {other_label}:")

        # שימוש ב-UnevaluatedExpr הכרחי כאן!
        new_l = other_l.subs(iso_var, sp.UnevaluatedExpr(iso_expr))
        new_r = other_r.subs(iso_var, sp.UnevaluatedExpr(iso_expr))
        self._add_step(MathUtils.render_equation(new_l, new_r))

        # מעבר על צעדי האלגברה שישתמשו עכשיו ב-manual_expand
        res_l, res_r = MathUtils.apply_algebraic_steps(new_l, new_r, other_var, self.steps)

        # בדיקת סיום (זהות או משוואה)
        final_diff = sp.simplify(res_l - res_r)
        if final_diff == 0:
            self._add_step("קיבלנו פסוק אמת, לכן למערכת יש **אינסוף פתרונות**.")
            return "אינסוף פתרונות", self.steps
        elif not final_diff.has(other_var):
            self._add_step("קיבלנו פסוק שקר, לכן למערכת **אין פתרון**.")
            return "אין פתרון", self.steps

        # המשך פתרון אם נשאר משתנה
        eq_str = f"{sp.latex(res_l)} = {sp.latex(res_r)}"
        solver = UniversalStepSolver(eq_str, var_symbol=other_var) if sp.degree(final_diff,
                                                                                other_var) == 1 else QuadraticStepSolver(
            eq_str, var_symbol=other_var)
        sol_val, sub_steps = solver.solve()
        for s in sub_steps:
            if "##" not in s and "התוצאה הסופית" not in s: self._add_step(s)

        # --- שלב 3: מציאת נעלם שני ---
        self._add_step(f"### שלב 3: מציאת ערך $${sp.latex(iso_var)}$$")
        sols = str(sol_val).split(", ")
        final_pairs = []
        for s in sols:
            try:
                val_other = sp.sympify(s)
                val_iso = MathUtils.clean_floats(iso_expr.subs(other_var, val_other))
                self._add_step(
                    f"נציב $${sp.latex(other_var)} = {sp.latex(val_other)}$$ בביטוי $${sp.latex(iso_var)} = {sp.latex(MathUtils.clean_floats(iso_expr))}$$:")
                self._add_step(f"$${sp.latex(iso_var)} = {sp.latex(val_iso)}$$")
                final_pairs.append((val_other, val_iso) if other_var == self.x else (val_iso, val_other))
            except:
                continue

        res_final = ", ".join([f"({sp.latex(p[0])}, {sp.latex(p[1])})" for p in final_pairs])
        self._add_step("---")
        self._add_step(f"**הפתרון הסופי: $$ {res_final} $$**")
        return res_final, self.steps

if __name__ == "__main__":
    test_eq1 = "5x + 10y = 540"
    test_eq2 = " 5x + 10y = 540"
    steps = SystemSubstitutionSolver(test_eq1, test_eq2).solve()
    for s in steps: print(s)







