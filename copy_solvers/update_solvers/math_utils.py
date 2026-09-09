# import sympy as sp
# from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, \
#     convert_xor
#
#
# class MathUtils:
#     @staticmethod
#     def clean_floats(expr):
#         """מנקה מספרים עשרוניים שהם בעצם שלמים ומבצע חישובים תקועים"""
#         if not hasattr(expr, 'atoms'): return expr
#         cleaned = expr.subs({n: sp.Integer(n) for n in expr.atoms(sp.Float) if n == int(n)})
#         return cleaned.doit()
#
#     @staticmethod
#     def get_terms(expr):
#         """מפרק ביטוי לרשימת האיברים שלו"""
#         return list(sp.Add.make_args(expr))
#
#     @staticmethod
#     def render_equation(lhs, rhs):
#         """הצגה נקייה עם ניקוי מספרים וביצוע חישובים"""
#         l_clean = MathUtils.clean_floats(lhs)
#         r_clean = MathUtils.clean_floats(rhs)
#         return f"$${sp.latex(l_clean)} = {sp.latex(r_clean)}$$"
#
#     @staticmethod
#     def get_common_denominator(exprs_list):
#         """מציאת מכנה משותף (LCM) מתוך רשימת ביטויים"""
#         denoms = set()
#         for expr in exprs_list:
#             for sub in sp.preorder_traversal(expr):
#                 d = sp.denom(sub)
#                 if d != 1: denoms.add(d)
#         return sp.lcm(list(denoms)) if denoms else 1
#
#     @staticmethod
#     def parse_equation(equation_str, var_symbol=None):
#         """
#         פונקציה מרכזית: מקבלת מחרוזת משוואה,
#         ומחזירה את אגף שמאל, אגף ימין, ואת הנעלם.
#         """
#         clean_str = equation_str.replace('^', '**')
#
#         if '=' in clean_str:
#             lhs_s, rhs_s = clean_str.split('=')
#         else:
#             lhs_s, rhs_s = clean_str, "0"
#
#         trans = standard_transformations + (implicit_multiplication_application, convert_xor)
#
#         temp_lhs = parse_expr(lhs_s, transformations=trans)
#         temp_rhs = parse_expr(rhs_s, transformations=trans)
#
#         # זיהוי נעלם
#         if var_symbol:
#             var = sp.Symbol(str(var_symbol))
#         else:
#             all_symbols = temp_lhs.free_symbols | temp_rhs.free_symbols
#             if all_symbols:
#                 var = sorted(list(all_symbols), key=lambda s: s.name)[0]
#             else:
#                 var = sp.Symbol('x')
#
#         # בניית הביטויים ללא פתרון מיידי (evaluate=False)
#         lhs = parse_expr(lhs_s, transformations=trans, evaluate=False)
#         rhs = parse_expr(rhs_s, transformations=trans, evaluate=False)
#
#         return lhs, rhs, var
#
#     @staticmethod
#     def rule_move_terms(lhs, rhs, var):
#         """הלוגיקה של העברת אגפים עם ניסוח פדגוגי"""
#         lhs_terms = MathUtils.get_terms(lhs)
#         rhs_terms = MathUtils.get_terms(rhs)
#
#         if len(lhs_terms) == 1 and lhs_terms[0] == var and \
#                 len(rhs_terms) == 1 and not rhs_terms[0].has(var):
#             return None, lhs, rhs
#
#         for i, term in enumerate(rhs_terms):
#             if term.has(var):
#                 moved = rhs_terms.pop(i)
#                 lhs_terms.append(-moved)
#                 desc = f"נעביר את {sp.latex(MathUtils.clean_floats(moved))} לאגף שמאל בסימן מנוגד:"
#                 return desc, sp.Add(*lhs_terms), sp.Add(*rhs_terms)
#
#         for i, term in enumerate(lhs_terms):
#             if not term.has(var) and term != 0:
#                 moved = lhs_terms.pop(i)
#                 rhs_terms.append(-moved)
#                 desc = f"נעביר את {sp.latex(MathUtils.clean_floats(moved))} לאגף ימין בסימן מנוגד:"
#                 return desc, sp.Add(*lhs_terms), sp.Add(*rhs_terms)
#
#         return None, lhs, rhs
#
#     @staticmethod
#     def apply_algebraic_steps(lhs, rhs, var, steps_list):
#         """מבצע פתיחת סוגריים, כינוס והעברת אגפים בצורה פדגוגית"""
#         curr_l, curr_r = lhs, rhs
#
#         # 1. פתיחת סוגריים
#         if "(" in str(curr_l) or "(" in str(curr_r):
#             # פתיחה מבוקרת כדי למנוע צמצום מיידי
#             expanded_l = sp.expand(curr_l)
#             expanded_r = sp.expand(curr_r)
#             if expanded_l != curr_l or expanded_r != curr_r:
#                 curr_l, curr_r = expanded_l, expanded_r
#                 steps_list.append(f"נפתח סוגריים לפי חוק הפילוג: {MathUtils.render_equation(curr_l, curr_r)}")
#
#         # 2. כינוס איברים דומים
#         simp_l = sp.simplify(curr_l)
#         simp_r = sp.simplify(curr_r)
#         if sp.latex(simp_l) != sp.latex(curr_l) or sp.latex(simp_r) != sp.latex(curr_r):
#             curr_l, curr_r = simp_l, simp_r
#             steps_list.append(f"נכנס איברים דומים בכל אגף: {MathUtils.render_equation(curr_l, curr_r)}")
#
#         # 3. העברת אגפים (לופ עד שסיימנו)
#         while True:
#             desc, next_l, next_r = MathUtils.rule_move_terms(curr_l, curr_r, var)
#             if not desc: break
#             curr_l, curr_r = sp.simplify(next_l), sp.simplify(next_r)
#             steps_list.append(f"{desc} {MathUtils.render_equation(curr_l, curr_r)}")
#
#         return curr_l, curr_r

#
# import sympy as sp
# from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, \
#     convert_xor
#
#
# class MathUtils:
#     @staticmethod
#     def clean_floats(expr):
#         """מנקה מספרים עשרוניים ללא ביצוע חישובים גורפים (doit) שעלולים לצמצם איברים"""
#         if not hasattr(expr, 'atoms'): return expr
#         replacements = {n: sp.Integer(n) for n in expr.atoms(sp.Float) if n == int(n)}
#         return expr.subs(replacements)
#
#     @staticmethod
#     def get_terms(expr):
#         return list(sp.Add.make_args(expr))
#
#     @staticmethod
#     def render_equation(lhs, rhs):
#         """מציג משוואה בצורה נקייה"""
#         return f"$${sp.latex(MathUtils.clean_floats(lhs))} = {sp.latex(MathUtils.clean_floats(rhs))}$$"
#
#     @staticmethod
#     def get_common_denominator(exprs_list):
#         """מציאת מכנה משותף (LCM) מתוך רשימת ביטויים"""
#         denoms = set()
#         for expr in exprs_list:
#             for sub in sp.preorder_traversal(expr):
#                 d = sp.denom(sub)
#                 if d != 1: denoms.add(d)
#         return sp.lcm(list(denoms)) if denoms else 1
#
#     @staticmethod
#     def parse_equation(equation_str, var_symbol=None):
#         clean_str = equation_str.replace('^', '**')
#         lhs_s, rhs_s = clean_str.split('=') if '=' in clean_str else (clean_str, "0")
#         trans = standard_transformations + (implicit_multiplication_application, convert_xor)
#         lhs = parse_expr(lhs_s, transformations=trans, evaluate=False)
#         rhs = parse_expr(rhs_s, transformations=trans, evaluate=False)
#
#         if var_symbol:
#             var = sp.Symbol(str(var_symbol))
#         else:
#             all_symbols = lhs.free_symbols | rhs.free_symbols
#             var = sorted(list(all_symbols), key=lambda s: s.name)[0] if all_symbols else sp.Symbol('x')
#         return lhs, rhs, var
#
#     @staticmethod
#     def expand_pedagogically(expr):
#         """פותח סוגריים לכל איבר בנפרד ושומר אותם כסכום לא מחושב כדי למנוע צמצום מיידי של נעלמים"""
#         terms = sp.Add.make_args(expr)
#         expanded_terms = []
#         for t in terms:
#             # מבצע פתיחת סוגריים רק על האיבר הנוכחי
#             expanded = sp.expand(t)
#             if isinstance(expanded, sp.Add):
#                 expanded_terms.extend(expanded.args)
#             else:
#                 expanded_terms.append(expanded)
#         # החזרה כסכום ללא הערכה (evaluate=False)
#         return sp.Add(*expanded_terms, evaluate=False)
#
#     @staticmethod
#     def rule_move_terms(lhs, rhs, var):
#         """העברת נעלמים לשמאל ומספרים לימין"""
#         # עובדים על גרסה מפושטת לצורך הלוגיקה, אך מחזירים ביטויים נקיים
#         curr_l = sp.simplify(lhs)
#         curr_r = sp.simplify(rhs)
#
#         lhs_terms = MathUtils.get_terms(curr_l)
#         rhs_terms = MathUtils.get_terms(curr_r)
#
#         # 1. העברת נעלמים לשמאל
#         for i, term in enumerate(rhs_terms):
#             if term.has(var):
#                 moved = rhs_terms.pop(i)
#                 new_l = sp.Add(*(lhs_terms + [-moved]), evaluate=False)
#                 new_r = sp.Add(*rhs_terms, evaluate=False)
#                 return f"נעביר את {sp.latex(MathUtils.clean_floats(moved))} לאגף שמאל בסימן מנוגד:", new_l, new_r
#
#         # 2. העברת מספרים לימין
#         for i, term in enumerate(lhs_terms):
#             if not term.has(var) and term != 0:
#                 moved = lhs_terms.pop(i)
#                 new_l = sp.Add(*lhs_terms, evaluate=False)
#                 new_r = sp.Add(*(rhs_terms + [-moved]), evaluate=False)
#                 return f"נעביר את {sp.latex(MathUtils.clean_floats(moved))} לאגף ימין בסימן מנוגד:", new_l, new_r
#
#         return None, lhs, rhs
#
#     @staticmethod
#     def apply_algebraic_steps(lhs, rhs, var, steps_list):
#         """מנוע צעדים מאוחד לכל סוגי המשוואות"""
#         curr_l, curr_r = lhs, rhs
#
#         # 1. פתיחת סוגריים (עם תצוגה מורחבת)
#         if "(" in str(curr_l) or "(" in str(curr_r):
#             exp_l = MathUtils.expand_pedagogically(curr_l)
#             exp_r = MathUtils.expand_pedagogically(curr_r)
#             if exp_l != curr_l or exp_r != curr_r:
#                 curr_l, curr_r = exp_l, exp_r
#                 steps_list.append(f"נפתח סוגריים לפי חוק הפילוג: {MathUtils.render_equation(curr_l, curr_r)}")
#
#         # 2. כינוס איברים דומים
#         simp_l = sp.simplify(curr_l)
#         simp_r = sp.simplify(curr_r)
#         if sp.latex(MathUtils.clean_floats(simp_l)) != sp.latex(MathUtils.clean_floats(curr_l)) or \
#                 sp.latex(MathUtils.clean_floats(simp_r)) != sp.latex(MathUtils.clean_floats(curr_r)):
#             curr_l, curr_r = simp_l, simp_r
#             steps_list.append(f"נכנס איברים דומים בכל אגף: {MathUtils.render_equation(curr_l, curr_r)}")
#
#         # 3. העברת אגפים
#         while True:
#             desc, next_l, next_r = MathUtils.rule_move_terms(curr_l, curr_r, var)
#             if not desc: break
#             curr_l, curr_r = sp.simplify(next_l), sp.simplify(next_r)
#             steps_list.append(f"{desc} {MathUtils.render_equation(curr_l, curr_r)}")
#
#         return curr_l, curr_r

import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, \
    convert_xor


class MathUtils:
    @staticmethod
    def clean_floats(expr):
        """מנקה מספרים עשרוניים ללא ביצוע חישובים גורפים (ללא .doit)"""
        if not hasattr(expr, 'atoms'): return expr
        replacements = {n: sp.Integer(n) for n in expr.atoms(sp.Float) if n == int(n)}
        return expr.subs(replacements)

    @staticmethod
    def get_terms(expr):
        return list(sp.Add.make_args(expr))

    @staticmethod
    def render_equation(lhs, rhs):
        return f"$${sp.latex(MathUtils.clean_floats(lhs))} = {sp.latex(MathUtils.clean_floats(rhs))}$$"

    @staticmethod
    def parse_equation(equation_str, var_symbol=None):
        clean_str = equation_str.replace('^', '**')
        lhs_s, rhs_s = clean_str.split('=') if '=' in clean_str else (clean_str, "0")
        trans = standard_transformations + (implicit_multiplication_application, convert_xor)
        lhs = parse_expr(lhs_s, transformations=trans, evaluate=False)
        rhs = parse_expr(rhs_s, transformations=trans, evaluate=False)
        if var_symbol:
            var = sp.Symbol(str(var_symbol))
        else:
            all_symbols = lhs.free_symbols | rhs.free_symbols
            var = sorted(list(all_symbols), key=lambda s: s.name)[0] if all_symbols else sp.Symbol('x')
        return lhs, rhs, var

    @staticmethod
    def get_common_denominator(exprs_list):
        """מציאת מכנה משותף (LCM) מתוך רשימת ביטויים"""
        denoms = set()
        for expr in exprs_list:
            for sub in sp.preorder_traversal(expr):
                d = sp.denom(sub)
                if d != 1: denoms.add(d)
        return sp.lcm(list(denoms)) if denoms else 1

    @staticmethod
    def manual_expand(expr):
        """
        פתיחה ידנית של סוגריים (לפי הלוגיקה מהקולאב)
        הפונקציה מכפילה מקדם בסוגריים ושומרת על האיברים נפרדים.
        """
        if not expr.has(sp.Add):
            return expr

        new_terms = []
        args = sp.Add.make_args(expr)
        for arg in args:
            # בדיקה אם יש ביטוי של כפל (למשל 10 כפול סוגריים)
            if isinstance(arg, sp.Mul):
                coeff_list = []
                add_part = None
                for factor in arg.args:
                    # אם זה UnevaluatedExpr (מההצבה), נסתכל מה יש בפנים
                    real_f = factor.doit() if isinstance(factor, sp.UnevaluatedExpr) else factor
                    if isinstance(real_f, sp.Add):
                        add_part = real_f
                    else:
                        coeff_list.append(factor)

                if add_part:
                    coeff = sp.Mul(*coeff_list)
                    for a in add_part.args:
                        # כאן קורה הקסם: יוצרים איברים חדשים בלי לחבר אותם עדיין
                        new_terms.append(coeff * a)
                else:
                    new_terms.append(arg)
            else:
                new_terms.append(arg)

        # החזרה כסכום קפוא (evaluate=False)
        return sp.Add(*new_terms, evaluate=False)

    @staticmethod
    def apply_algebraic_steps(lhs, rhs, var, steps_list):
        curr_l, curr_r = lhs, rhs

        # 1. שלב פתיחת סוגריים (שימוש ב-manual_expand)
        if "(" in str(curr_l) or "(" in str(curr_r):
            exp_l = MathUtils.manual_expand(curr_l)
            exp_r = MathUtils.manual_expand(curr_r)

            # בדיקה אם התצוגה השתנתה (כלומר נפתחו סוגריים)
            if sp.latex(MathUtils.clean_floats(exp_l)) != sp.latex(MathUtils.clean_floats(curr_l)) or \
                    sp.latex(MathUtils.clean_floats(exp_r)) != sp.latex(MathUtils.clean_floats(curr_r)):
                curr_l, curr_r = exp_l, exp_r
                steps_list.append(f"נפתח סוגריים לפי חוק הפילוג: {MathUtils.render_equation(curr_l, curr_r)}")

        # 2. שלב כינוס איברים (כאן מותר ל-SymPy לחשב ולצמצם)
        simp_l = sp.simplify(curr_l)
        simp_r = sp.simplify(curr_r)
        if sp.latex(MathUtils.clean_floats(simp_l)) != sp.latex(MathUtils.clean_floats(curr_l)) or \
                sp.latex(MathUtils.clean_floats(simp_r)) != sp.latex(MathUtils.clean_floats(curr_r)):
            curr_l, curr_r = simp_l, simp_r
            steps_list.append(f"נכנס איברים דומים בכל אגף: {MathUtils.render_equation(curr_l, curr_r)}")

        # 3. העברת אגפים
        while True:
            from solvers.math_utils import MathUtils as MU
            desc, next_l, next_r = MU.rule_move_terms(curr_l, curr_r, var)
            if not desc: break
            curr_l, curr_r = sp.simplify(next_l), sp.simplify(next_r)
            steps_list.append(f"{desc} {MU.render_equation(curr_l, curr_r)}")

        return curr_l, curr_r

    @staticmethod
    def rule_move_terms(lhs, rhs, var):
        # לוגיקת העברת אגפים הקיימת שלך (בלי שינוי מהותי)
        temp_l, temp_r = sp.simplify(lhs), sp.simplify(rhs)
        l_terms, r_terms = MathUtils.get_terms(temp_l), MathUtils.get_terms(temp_r)

        for i, term in enumerate(r_terms):
            if term.has(var):
                moved = r_terms.pop(i)
                return f"נעביר את {sp.latex(MathUtils.clean_floats(moved))} לאגף שמאל בסימן מנוגד:", sp.Add(
                    *(l_terms + [-moved])), sp.Add(*r_terms)
        for i, term in enumerate(l_terms):
            if not term.has(var) and term != 0:
                moved = l_terms.pop(i)
                return f"נעביר את {sp.latex(MathUtils.clean_floats(moved))} לאגף ימין בסימן מנוגד:", sp.Add(
                    *l_terms), sp.Add(*(r_terms + [-moved]))
        return None, lhs, rhs