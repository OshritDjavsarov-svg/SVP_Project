import sympy as sp
from solvers.math_utils import MathUtils  # ייבוא קובץ העזר שיצרנו

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

        if coeff != 1:
            div_desc = f"נחלק במקדם של {self.var} (שהוא {sp.latex(MathUtils.clean_floats(coeff))}) ונקבל:"
            self.steps.append(f"{div_desc} **התוצאה הסופית: $${final_eq_latex}$$**")
        else:
            final_step_text = f"**התוצאה הסופית: $${final_eq_latex}$$**"
            if not self.steps or final_eq_latex not in self.steps[-1]:
                self.steps.append(final_step_text)
            else:
                self.steps[-1] = f"**{self.steps[-1]}**"

        return str(res_clean), self.steps

def solve_linear_steps(equation_str):
    try:
        solver = UniversalStepSolver(equation_str)
        result, steps = solver.solve()
        return {"result": result, "steps": steps}
    except Exception as e:
        return {"result": "Error", "steps": [f"שגיאה בתהליך הפתרון: {str(e)}"]}


from linear_solver import solve_linear_steps
def run_test():
    # שלוש משוואות טסט שמייצגות מקרים שונים
    equations_to_test = [
        "3*w + 5 = 3w +5",  # מקרה קלאסי של העברת אגפים
        "2*(x + 3) = 14",  # מקרה של פתיחת סוגריים
        "x/2 + 3 = x/3 + 5"  # מקרה של שברים ומכנה משותף
    ]

    for eq in equations_to_test:
        print(f"=========================================")
        print(f"המשוואה המקורית: {eq}")
        print(f"=========================================")

        # קריאה לפונקציית הפתרון מהקובץ שלך
        solution_data = solve_linear_steps(eq)

        # הדפסת השלבים
        steps = solution_data.get("steps", [])
        for i, step in enumerate(steps):
            print(f"שלב {i + 1}: {step}")

        print(f"\nהערך שחזר מהפונקציה: {solution_data.get('result')}\n")


if __name__ == "__main__":
    run_test()

# import sympy as sp
# from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, \
#     convert_xor
#
#
# class MathRules:
#     @staticmethod
#     def rule_clean_floats(expr):
#         """מנקה מספרים עשרוניים שהם בעצם שלמים ומבצע חישובים תקועים (כמו -1*7)"""
#         if not hasattr(expr, 'atoms'): return expr
#         # המרת 5.0 ל-5 וביצוע .doit() לחיסול מבנים כמו (-1)*7
#         cleaned = expr.subs({n: sp.Integer(n) for n in expr.atoms(sp.Float) if n == int(n)})
#         return cleaned.doit()
#
#     @staticmethod
#     def get_terms(expr):
#         """מפרק ביטוי לרשימת האיברים שלו"""
#         return list(sp.Add.make_args(expr))
#
#     @staticmethod
#     def rule_move_terms(lhs, rhs, var):
#         """הלוגיקה של העברת אגפים עם ניסוח פדגוגי"""
#         lhs_terms = MathRules.get_terms(lhs)
#         rhs_terms = MathRules.get_terms(rhs)
#
#         # בדיקה אם כבר הגענו לפתרון סופי x = מספר
#         if len(lhs_terms) == 1 and lhs_terms[0] == var and \
#                 len(rhs_terms) == 1 and not rhs_terms[0].has(var):
#             return None, lhs, rhs
#
#         # 1. העברת נעלמים שמאלה
#         for i, term in enumerate(rhs_terms):
#             if term.has(var):
#                 moved = rhs_terms.pop(i)
#                 lhs_terms.append(-moved)
#                 desc = f"נעביר את {sp.latex(MathRules.rule_clean_floats(moved))} לאגף שמאל בסימן מנוגד:"
#                 return desc, sp.Add(*lhs_terms), sp.Add(*rhs_terms)
#
#         # 2. העברת מספרים ימינה
#         for i, term in enumerate(lhs_terms):
#             if not term.has(var) and term != 0:
#                 moved = lhs_terms.pop(i)
#                 rhs_terms.append(-moved)
#                 desc = f"נעביר את {sp.latex(MathRules.rule_clean_floats(moved))} לאגף ימין בסימן מנוגד:"
#                 return desc, sp.Add(*lhs_terms), sp.Add(*rhs_terms)
#
#         return None, lhs, rhs
#
#
# class UniversalStepSolver:
#     def __init__(self, equation_str, var_symbol=None):
#         self.steps = []
#         clean_str = equation_str.replace('^', '**')
#         lhs_s, rhs_s = clean_str.split('=')
#         trans = standard_transformations + (implicit_multiplication_application, convert_xor)
#
#         # זיהוי נעלם משופר: בודקים את שני האגפים לפני הצמצום
#         if var_symbol:
#             self.var = sp.Symbol(str(var_symbol))
#         else:
#             # מנתחים את האגפים בנפרד כדי למצוא את האותיות
#             temp_lhs = parse_expr(lhs_s, transformations=trans)
#             temp_rhs = parse_expr(rhs_s, transformations=trans)
#             all_symbols = temp_lhs.free_symbols | temp_rhs.free_symbols
#
#             if all_symbols:
#                 # לוקחים את הנעלם הראשון שנמצא (לפי סדר אלפביתי)
#                 self.var = sorted(list(all_symbols), key=lambda s: s.name)[0]
#             else:
#                 self.var = sp.Symbol('x')  # ברירת מחדל אחרונה בהחלט
#
#         # טעינה של האגפים להמשך הפתרון
#         self.lhs = parse_expr(lhs_s, transformations=trans, evaluate=False)
#         self.rhs = parse_expr(rhs_s, transformations=trans, evaluate=False)
#
#     def _render(self, l, r):
#         """הצגה נקייה עם ניקוי מספרים וביצוע חישובים"""
#         l_clean = MathRules.rule_clean_floats(l)
#         r_clean = MathRules.rule_clean_floats(r)
#         return f"$${sp.latex(l_clean)} = {sp.latex(r_clean)}$$"
#
#     def get_common_denominator(self):
#         """מציאת מכנה משותף (LCM) מכל חלקי המשוואה"""
#         denoms = set()
#         for expr in [self.lhs, self.rhs]:
#             for sub in sp.preorder_traversal(expr):
#                 d = sp.denom(sub)
#                 if d != 1: denoms.add(d)
#         return sp.lcm(list(denoms)) if denoms else 1
#
#     def solve(self):
#         current_lhs = self.lhs
#         current_rhs = self.rhs
#
#         # 1. טיפול בשברים (המנוע של קוד 1)
#         lcm = self.get_common_denominator()
#         if lcm > 1:
#             self.steps.append(f"נכפיל את כל אגפי המשוואה במכנה המשותף {lcm} כדי להיפטר מהשברים:")
#             # הכפלה "ויזואלית"
#             current_lhs = sp.Mul(lcm, current_lhs, evaluate=False)
#             current_rhs = sp.Mul(lcm, current_rhs, evaluate=False)
#             self.steps.append(self._render(current_lhs, current_rhs))
#
#             # צמצום המכנים
#             current_lhs = sp.simplify(current_lhs)
#             current_rhs = sp.simplify(current_rhs)
#             self.steps.append(f"לאחר צמצום המכנים נקבל: {self._render(current_lhs, current_rhs)}")
#
#         # 2. פתיחת סוגריים (שילוב לוגיקה)
#         if "(" in str(current_lhs) or "(" in str(current_rhs):
#             expanded_lhs = sp.expand(current_lhs)
#             expanded_rhs = sp.expand(current_rhs)
#             if expanded_lhs != current_lhs or expanded_rhs != current_rhs:
#                 current_lhs, current_rhs = expanded_lhs, expanded_rhs
#                 self.steps.append(f"נפתח סוגריים לפי חוק הפילוג: {self._render(current_lhs, current_rhs)}")
#
#         # 3. כינוס איברים דומים לפני העברה
#         simplified_lhs = sp.simplify(current_lhs)
#         simplified_rhs = sp.simplify(current_rhs)
#         if sp.latex(simplified_lhs) != sp.latex(current_lhs) or sp.latex(simplified_rhs) != sp.latex(current_rhs):
#             current_lhs, current_rhs = simplified_lhs, simplified_rhs
#             self.steps.append(f"נכנס איברים דומים בכל אגף: {self._render(current_lhs, current_rhs)}")
#
#         # 4. העברת אגפים (התצוגה של קוד 2)
#         while True:
#             desc, next_lhs, next_rhs = MathRules.rule_move_terms(current_lhs, current_rhs, self.var)
#             if not desc:
#                 break
#             current_lhs, current_rhs = next_lhs, next_rhs
#             # פישוט קל כדי שלא יצטברו ביטויים כמו 7-5 בתצוגה
#             current_lhs = sp.simplify(current_lhs)
#             current_rhs = sp.simplify(current_rhs)
#             self.steps.append(f"{desc} {self._render(current_lhs, current_rhs)}")
#
#         # 5. חישוב סופי ומקרי קצה
#         final_lhs = sp.simplify(current_lhs)
#         final_rhs = sp.simplify(current_rhs)
#         coeff = final_lhs.coeff(self.var)
#
#         if coeff == 0:
#             var_name = str(self.var)  # מקבל את 'w' או כל אות אחרת
#             if sp.simplify(final_lhs - final_rhs) == 0:
#                 self.steps.append(
#                     f"קיבלנו מצב שבו שני אגפי המשוואה שווים תמיד (${sp.latex(final_rhs)} = {sp.latex(final_rhs)}$). "
#                     f"זה אומר שכל מספר שנבחר להציב במקום ה-**{var_name}** יהיה נכון, ולכן יש **אינסוף פתרונות**."
#                 )
#                 return "אינסוף פתרונות", self.steps
#             else:
#                 self.steps.append(
#                     f"קיבלנו תוצאה שאינה הגיונית (${sp.latex(final_lhs)} = {sp.latex(final_rhs)}$). "
#                     f"מכיוון שהמספרים האלו לא באמת שווים, אין אף מספר שנוכל להציב ב-**{var_name}** כדי לפתור את המשוואה, "
#                     f"ולכן **אין פתרון**."
#                 )
#                 return "אין פתרון", self.steps
#
#         exact_result = final_rhs / coeff
#         res_clean = MathRules.rule_clean_floats(exact_result)
#
#         # עיצוב התוצאה (שילוב עיגול נומרי מקוד 1 והדגשה מקוד 2)
#         numeric_val = float(res_clean)
#         if numeric_val == int(numeric_val):
#             res_latex = sp.latex(int(numeric_val))
#         else:
#             # אם זה שבר, נציג גם שבר וגם עשרוני מעוגל
#             rounded = round(numeric_val, 4)
#             res_latex = f"{sp.latex(res_clean)} \\approx {rounded}"
#
#         final_eq_latex = f"{self.var} = {res_latex}"
#
#         if coeff != 1:
#             div_desc = f"נחלק במקדם של {self.var} (שהוא {sp.latex(MathRules.rule_clean_floats(coeff))}) ונקבל:"
#             self.steps.append(f"{div_desc} **התוצאה הסופית: $${final_eq_latex}$$**")
#         else:
#             # מניעת כפילות של שורת התוצאה
#             final_step_text = f"**התוצאה הסופית: $${final_eq_latex}$$**"
#             if not self.steps or final_eq_latex not in self.steps[-1]:
#                 self.steps.append(final_step_text)
#             else:
#                 self.steps[-1] = f"**{self.steps[-1]}**"
#
#         return str(res_clean), self.steps
#
#
# def solve_linear_steps(equation_str):
#     try:
#         solver = UniversalStepSolver(equation_str)
#         result, steps = solver.solve()
#         return {"result": result, "steps": steps}
#     except Exception as e:
#         return {"result": "Error", "steps": [f"שגיאה בתהליך הפתרון: {str(e)}"]}








# import sympy as sp
# from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, \
#     convert_xor
#
#
# class MathRules:
#     @staticmethod
#     def rule_clean_floats(expr):
#         if not hasattr(expr, 'atoms'): return expr
#         return expr.subs({n: sp.Integer(n) for n in expr.atoms(sp.Float) if n == int(n)})
#
#     @staticmethod
#     def get_terms(expr):
#         return list(sp.Add.make_args(expr))
#
#     @staticmethod
#     def rule_move_terms(lhs_terms, rhs_terms, var):
#         """העברת אגפים חכמה: רק אם יש צורך באמת"""
#         # בדיקה: האם אנחנו כבר במצב של ax = b?
#         if len(lhs_terms) == 1 and lhs_terms[0].has(var) and \
#                 len(rhs_terms) == 1 and not rhs_terms[0].has(var):
#             return None
#
#         # 1. העברת נעלמים שמאלה
#         for i, term in enumerate(rhs_terms):
#             if term.has(var):
#                 moved = rhs_terms.pop(i)
#                 lhs_terms.append(-moved)
#                 return f"נעביר את {sp.latex(moved)} לאגף שמאל"
#
#         # 2. העברת מספרים ימינה
#         for i, term in enumerate(lhs_terms):
#             if not term.has(var) and term != 0:
#                 moved = lhs_terms.pop(i)
#                 rhs_terms.append(-moved)
#                 return f"נעביר את {sp.latex(moved)} לאגף ימין"
#         return None
#
#
# class UniversalStepSolver:
#     def __init__(self, equation_str, var_symbol=None):
#         self.steps = []  # רשימה לאיסוף השלבים עבור השרת
#
#         # שלב א: פיצול אגפים וטיפול בחזקות
#         lhs_s, rhs_s = equation_str.replace('^', '**').split('=')
#
#         # שלב ב: הגדרת הטרנספורמציות
#         trans = standard_transformations + (implicit_multiplication_application, convert_xor)
#
#         # שלב ג: זיהוי אוטומטי של הנעלם
#         if var_symbol is not None:
#             self.var = var_symbol
#         else:
#             full_expr = parse_expr(equation_str.replace('=', '-'), transformations=trans)
#             found_symbols = list(full_expr.free_symbols)
#             if found_symbols:
#                 self.var = found_symbols[0]
#             else:
#                 self.var = sp.Symbol('x')
#
#         # שלב ד: פירוק לאיברים
#         self.lhs_list = MathRules.get_terms(parse_expr(lhs_s, transformations=trans, evaluate=False))
#         self.rhs_list = MathRules.get_terms(parse_expr(rhs_s, transformations=trans, evaluate=False))
#
#     def _render(self):
#         l_sum = sp.Add(*self.lhs_list, evaluate=False)
#         r_sum = sp.Add(*self.rhs_list, evaluate=False)
#         return f"$${sp.latex(MathRules.rule_clean_floats(l_sum))} = {sp.latex(MathRules.rule_clean_floats(r_sum))}$$"
#
#     def get_common_denominator(self):
#         denoms = set()
#         for term in self.lhs_list + self.rhs_list:
#             for sub in sp.preorder_traversal(term):
#                 d = sp.denom(sub)
#                 if d != 1: denoms.add(d)
#         return sp.lcm(list(denoms)) if denoms else 1
#
#     def solve(self):
#         # 1. מכנה משותף
#         lcm = self.get_common_denominator()
#         if lcm > 1:
#             self.steps.append(f"נכפיל את כל אגפי המשוואה במכנה המשותף {lcm}:")
#             self.lhs_list = [sp.Mul(lcm, t, evaluate=False) for t in self.lhs_list]
#             self.rhs_list = [sp.Mul(lcm, t, evaluate=False) for t in self.rhs_list]
#             self.steps.append(self._render())
#
#             self.lhs_list = [sp.simplify(t) for t in self.lhs_list]
#             self.rhs_list = [sp.simplify(t) for t in self.rhs_list]
#             self.steps.append(f"נצמצם את המכנים:")
#             self.steps.append(self._render())
#
#         # 2. פתיחת סוגריים
#         expanded = False
#         new_lhs, new_rhs = [], []
#         for term in self.lhs_list:
#             if any(isinstance(a, sp.Add) for a in sp.preorder_traversal(term)):
#                 new_lhs.extend(MathRules.get_terms(sp.expand(term)))
#                 expanded = True
#             else:
#                 new_lhs.append(term)
#         for term in self.rhs_list:
#             if any(isinstance(a, sp.Add) for a in sp.preorder_traversal(term)):
#                 new_rhs.extend(MathRules.get_terms(sp.expand(term)))
#                 expanded = True
#             else:
#                 new_rhs.append(term)
#
#         if expanded:
#             self.lhs_list, self.rhs_list = new_lhs, new_rhs
#             self.steps.append(f"נפתח סוגריים לפי חוק הפילוג:")
#             self.steps.append(self._render())
#
#         # 3. כינוס איברים דומים
#         old_tex = self._render()
#         self.lhs_list = [sp.simplify(sp.Add(*self.lhs_list))]
#         self.rhs_list = [sp.simplify(sp.Add(*self.rhs_list))]
#         if self._render() != old_tex:
#             self.steps.append(f"נכנס איברים דומים:")
#             self.steps.append(self._render())
#
#         # 4. העברת אגפים
#         while True:
#             self.lhs_list = MathRules.get_terms(sp.simplify(sp.Add(*self.lhs_list)))
#             self.rhs_list = MathRules.get_terms(sp.simplify(sp.Add(*self.rhs_list)))
#
#             if len(self.lhs_list) == 1 and self.lhs_list[0].has(self.var) and \
#                     len(self.rhs_list) == 1 and not self.rhs_list[0].has(self.var):
#                 break
#
#             desc = MathRules.rule_move_terms(self.lhs_list, self.rhs_list, self.var)
#             if not desc: break
#
#             self.lhs_list = [sp.simplify(sp.Add(*self.lhs_list))]
#             self.rhs_list = [sp.simplify(sp.Add(*self.rhs_list))]
#             self.steps.append(f"{desc}:")
#             self.steps.append(self._render())
#
#         # 5. חלוקה סופית
#         final_lhs = self.lhs_list[0]
#         final_rhs = self.rhs_list[0]
#         coeff = final_lhs.coeff(self.var)
#
#         if coeff == 0:
#             if sp.simplify(final_lhs - final_rhs) == 0:
#                 self.steps.append("קיבלנו פסוק אמת ($0 = 0$): לכן, למשוואה יש **אינסוף פתרונות**.")
#                 return "אינסוף פתרונות", self.steps
#             else:
#                 self.steps.append(
#                     f"קיבלנו פסוק שקר (${sp.latex(final_lhs)} = {sp.latex(final_rhs)}$): לכן, למשוואה **אין פתרון**.")
#                 return "אין פתרון", self.steps
#
#         exact_result = final_rhs / coeff
#         if coeff != 1:
#             self.steps.append(f"נחלק במקדם של {self.var} (שהוא {sp.latex(MathRules.rule_clean_floats(coeff))}):")
#
#         numeric_val = float(exact_result)
#         rounded_val = round(numeric_val, 4)
#
#         if numeric_val == int(numeric_val):
#             final_display = sp.latex(int(numeric_val))
#         else:
#             final_display = f"{sp.latex(exact_result)} = {rounded_val}"
#
#         self.steps.append(f"התוצאה הסופית: $${self.var} = {final_display}$$")
#         return str(exact_result), self.steps
#
#
# # פונקציית העזר שתקראי לה מה-main.py
# def solve_linear_steps(equation_str):
#     try:
#         solver = UniversalStepSolver(equation_str)
#         result, steps = solver.solve()
#         return {"result": result, "steps": steps}
#     except Exception as e:
#         return {"result": "Error", "steps": [f"שגיאה בפתרון: {str(e)}"]}
#





# !!!!!!!!!!!!!!!





# בדיקת הקלטים של הקובץ הזה
# test_linear.py
# import sympy as sp
# from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, \
#     convert_xor
#
#
# class MathRules:
#     @staticmethod
#     def rule_clean_floats(expr):
#         """מנקה מספרים עשרוניים שהם בעצם שלמים (5.0 -> 5) ומבצע חישוב של ביטויים פשוטים"""
#         if not hasattr(expr, 'atoms'): return expr
#         # הפעולה .doit() מכריחה את Sympy לחשב ביטויים כמו (-1)*7
#         cleaned = expr.subs({n: sp.Integer(n) for n in expr.atoms(sp.Float) if n == int(n)})
#         return cleaned.doit()
#
#     @staticmethod
#     def get_terms(expr):
#         return list(sp.Add.make_args(expr))
#
#     @staticmethod
#     def rule_move_terms(lhs_terms, rhs_terms, var):
#         # האם הגענו למצב של x = מספר?
#         if len(lhs_terms) == 1 and lhs_terms[0] == var and \
#                 len(rhs_terms) == 1 and not rhs_terms[0].has(var):
#             return None
#
#         # 1. העברת נעלמים שמאלה
#         for i, term in enumerate(rhs_terms):
#             if term.has(var):
#                 moved = rhs_terms.pop(i)
#                 lhs_terms.append(-moved)
#                 return f"נעביר את {sp.latex(MathRules.rule_clean_floats(moved))} לאגף שמאל בסימן מנוגד:"
#
#         # 2. העברת מספרים ימינה
#         for i, term in enumerate(lhs_terms):
#             if not term.has(var):
#                 moved = lhs_terms.pop(i)
#                 rhs_terms.append(-moved)
#                 return f"נעביר את {sp.latex(MathRules.rule_clean_floats(moved))} לאגף ימין בסימן מנוגד:"
#         return None
#
#
# class UniversalStepSolver:
#     def __init__(self, equation_str, var_symbol='x'):
#         self.steps = []
#         self.var = sp.Symbol(str(var_symbol))
#         clean_str = equation_str.replace('^', '**')
#         lhs_s, rhs_s = clean_str.split('=')
#         trans = standard_transformations + (implicit_multiplication_application, convert_xor)
#         # טוענים בלי הערכה ראשונית כדי לשמור על מבנה הסוגריים המקורי
#         self.lhs = parse_expr(lhs_s, transformations=trans, evaluate=False)
#         self.rhs = parse_expr(rhs_s, transformations=trans, evaluate=False)
#
#     def _render(self, l, r):
#         """מציג את המשוואה בצורה נקייה ומחושבת"""
#         l_clean = MathRules.rule_clean_floats(l)
#         r_clean = MathRules.rule_clean_floats(r)
#         return f"$${sp.latex(l_clean)} = {sp.latex(r_clean)}$$"
#
#     def solve(self):
#         current_lhs = self.lhs
#         current_rhs = self.rhs
#
#         # 1. פתיחת סוגריים (רק אם יש)
#         if "(" in str(current_lhs) or "(" in str(current_rhs):
#             expanded_lhs = sp.expand(current_lhs)
#             expanded_rhs = sp.expand(current_rhs)
#             if expanded_lhs != current_lhs or expanded_rhs != current_rhs:
#                 current_lhs, current_rhs = expanded_lhs, expanded_rhs
#                 self.steps.append(f"נפתח סוגריים לפי חוק הפילוג: {self._render(current_lhs, current_rhs)}")
#
#         # 2. כינוס איברים (לפני העברה)
#         simplified_lhs = sp.simplify(current_lhs)
#         simplified_rhs = sp.simplify(current_rhs)
#         if sp.latex(simplified_lhs) != sp.latex(current_lhs) or sp.latex(simplified_rhs) != sp.latex(current_rhs):
#             current_lhs, current_rhs = simplified_lhs, simplified_rhs
#             self.steps.append(f"נכנס איברים דומים בכל אגף: {self._render(current_lhs, current_rhs)}")
#
#         # 3. העברת אגפים
#         while True:
#             lhs_terms = MathRules.get_terms(current_lhs)
#             rhs_terms = MathRules.get_terms(current_rhs)
#             desc = MathRules.rule_move_terms(lhs_terms, rhs_terms, self.var)
#             if not desc:
#                 break
#             # יצירת ביטויים חדשים מהרשימות המעודכנות
#             current_lhs = sp.Add(*lhs_terms)
#             current_rhs = sp.Add(*rhs_terms)
#             self.steps.append(f"{desc} {self._render(current_lhs, current_rhs)}")
#
#         # 4. חישוב סופי
#         final_lhs = sp.simplify(current_lhs)
#         final_rhs = sp.simplify(current_rhs)
#         coeff = final_lhs.coeff(self.var)
#
#         # בדיקת מקרי קצה (0=0 או 0=7)
#         if coeff == 0:
#             if sp.simplify(final_lhs - final_rhs) == 0:
#                 self.steps.append("קיבלנו פסוק אמת ($0 = 0$): לכן, יש **אינסוף פתרונות**.")
#                 return "אינסוף פתרונות", self.steps
#             else:
#                 self.steps.append(f"קיבלנו פסוק שקר: לכן, **אין פתרון**.")
#                 return "אין פתרון", self.steps
#
#         exact_result = final_rhs / coeff
#         res_clean = MathRules.rule_clean_floats(exact_result)
#
#         # מניעת כפילות: אם המשוואה כבר נראית כמו x = תוצאה, לא מוסיפים שלב חילוק
#         current_eq_latex = sp.latex(sp.Eq(final_lhs, final_rhs))
#         final_eq_latex = f"{self.var} = {sp.latex(res_clean)}"
#
#         if coeff != 1:
#             div_desc = f"נחלק במקדם של {self.var} (שהוא {sp.latex(coeff)}) ונקבל:"
#             self.steps.append(f"{div_desc} **התוצאה הסופית: $${final_eq_latex}$$**")
#         else:
#             # אם כבר הגענו לתוצאה, רק נוודא שהשלב האחרון שנוסף לא זהה לתוצאה הסופית
#             final_step_text = f"**התוצאה הסופית: $${final_eq_latex}$$**"
#             # בדיקה אם השלב האחרון ברשימה כבר מכיל את התוצאה הזו
#             if not self.steps or final_eq_latex not in self.steps[-1]:
#                 self.steps.append(final_step_text)
#             else:
#                 # אם השלב האחרון כבר היה x=12, פשוט נהפוך אותו למודגש (אופציונלי)
#                 self.steps[-1] = f"**{self.steps[-1]}**"
#
#         return res_clean, self.steps
#
#
# # פונקציית העזר שתקראי לה מה-main.py
# def solve_linear_steps(equation_str):
#     try:
#         solver = UniversalStepSolver(equation_str)
#         result, steps = solver.solve()
#         return {"result": result, "steps": steps}
#     except Exception as e:
#         return {"result": "Error", "steps": [f"שגיאה בפתרון: {str(e)}"]}




# !!!!!!!!!!!!!!!


