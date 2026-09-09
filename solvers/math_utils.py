import sympy as sp
# ייבוא כלים לניתוח (Parsing) של מחרוזות טקסט למבני נתונים מתמטיים של SymPy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, \
    convert_xor

class MathUtils:

    @staticmethod
    def clean_floats(expr):
        """מנקה ומעגל מספרים עשרוניים כדי למנוע בעיות דיוק בינאריות (כמו 0.019999999999999997)"""
        if not hasattr(expr, 'atoms'): return expr
        replacements = {}
        for n in expr.atoms(sp.Float):
            rounded = round(float(n), 4)
            if rounded == int(rounded):
                replacements[n] = sp.Integer(int(rounded))
            else:
                replacements[n] = sp.Float(rounded)

        return expr.subs(replacements)

    @staticmethod
    def get_terms(expr):
        return list(sp.Add.make_args(expr))

    @staticmethod
    def render_equation(lhs, rhs):
        return f"$${sp.latex(MathUtils.clean_floats(lhs))} = {sp.latex(MathUtils.clean_floats(rhs))}$$"

    @staticmethod
    def parse_equation(equation_str, var_symbol=None):
        """הפונקציה המרכזית להפיכת מחרוזת למשוואה מתמטית"""
        clean_str = equation_str.replace('^', '**')
        lhs_s, rhs_s = clean_str.split('=') if '=' in clean_str else (clean_str, "0")

        # הגדרת חוקי המרת הטקסט לביטוי מתמטי סימבולי
        trans = standard_transformations + (implicit_multiplication_application, convert_xor)
        lhs = parse_expr(lhs_s, transformations=trans, evaluate=False)
        rhs = parse_expr(rhs_s, transformations=trans, evaluate=False)

        # זיהוי המשתנה (x, y, z וכו') בצורה דינמית אם לא סופק משתנה מראש.
        if var_symbol:
            var = sp.Symbol(str(var_symbol))
        else:
            all_symbols = lhs.free_symbols | rhs.free_symbols
            var = sorted(list(all_symbols), key=lambda s: s.name)[0] if all_symbols else sp.Symbol('x')
        return lhs, rhs, var

    # פונקציית עזר למציאת מכנה משותף (LCM) עבור משוואות עם שברים.
    @staticmethod
    def get_common_denominator(exprs_list):
        """מציאת מכנה משותף הקטן ביותר(LCM) """
        denoms = set()
        # לולאה שעוברת על כל אגף במשוואה שסופק ברשימה.
        for expr in exprs_list:
            for sub in sp.preorder_traversal(expr):
                # sp.denom חילוץ המכנה של תת-הביטוי הנוכחי.
                d = sp.denom(sub)
                if d != 1: denoms.add(d)
        return sp.lcm(list(denoms)) if denoms else 1

    # פתיחת סוגריים ידנית: חשוב כדי שהמשתמש יראה את שלב הפילוג ולא רק את התוצאה הסופית.
    @staticmethod
    def manual_expand(expr):
        """
        פתיחה ידנית של סוגריים
        הפונקציה מכפילה מקדם בסוגריים ושומרת על האיברים נפרדים.
        """
        if not expr.has(sp.Add):
            return expr

        new_terms = []
        # פירוק הביטוי לרשימת איברים
        args = sp.Add.make_args(expr)
        for arg in args:
            if isinstance(arg, sp.Mul):
                coeff_list = []
                add_part = None
                for factor in arg.args:
                    # מציאת הביטוי בתוך הסוגריים המוכפלים
                    real_f = factor.doit() if isinstance(factor, sp.UnevaluatedExpr) else factor
                    if isinstance(real_f, sp.Add):
                        add_part = real_f
                    else:
                        coeff_list.append(factor)

                #  ביצוע פתיחת סוגריים (חוק הפילוג)
                if add_part:
                    coeff = sp.Mul(*coeff_list)
                    for a in add_part.args:
                        # הוספת האיברים החדשים שנוצרו מהפילוג לרשימה.
                        new_terms.append(coeff * a)
                else:
                    new_terms.append(arg)
            else:
                new_terms.append(arg)

        # החזרה כסכום קפוא (evaluate=False) לתצוגה מובנת למשתמש
        return sp.Add(*new_terms, evaluate=False)

    @staticmethod
    def apply_algebraic_steps(lhs, rhs, var, steps_list):
        """ניהול צעדי פתרון להבאת המשוואות למצב מופשט תוך הסבר פדגוגי"""
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

        # 3: העברת אגפים עד שאין מה להעביר יותר (לופ).
        while True:
            from solvers.math_utils import MathUtils as MU
            desc, next_l, next_r = MU.rule_move_terms(curr_l, curr_r, var)
            if not desc: break
            curr_l, curr_r = sp.simplify(next_l), sp.simplify(next_r)
            steps_list.append(f"{desc} {MU.render_equation(curr_l, curr_r)}")

        return curr_l, curr_r

    @staticmethod
    def rule_move_terms(lhs, rhs, var):
        """לוגיקת העברת אגפים"""
        # פישוט ראשוני של האגפים לניתוח.
        temp_l, temp_r = sp.simplify(lhs), sp.simplify(rhs)
        # פירוק האגפים לרשימת איברים בודדים.
        l_terms, r_terms = MathUtils.get_terms(temp_l), MathUtils.get_terms(temp_r)

        # חיפוש נעלם
        for i, term in enumerate(r_terms):
            if term.has(var):
                moved = r_terms.pop(i)
                return f"נעביר את {sp.latex(MathUtils.clean_floats(moved))} לאגף שמאל בסימן מנוגד:", sp.Add(
                    *(l_terms + [-moved])), sp.Add(*r_terms)

        # חיפוש איבר חופשי
        for i, term in enumerate(l_terms):
            if not term.has(var) and term != 0:
                moved = l_terms.pop(i)
                return f"נעביר את {sp.latex(MathUtils.clean_floats(moved))} לאגף ימין בסימן מנוגד:", sp.Add(
                    *l_terms), sp.Add(*(r_terms + [-moved]))
        return None, lhs, rhs