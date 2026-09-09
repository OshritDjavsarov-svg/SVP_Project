import sympy as sp
# ייבוא הרכיבים המרכזיים של Flask: ליצירת השרת (Flask), לקבלת נתוני קלט  (request) ולהחזרת תשובות מובנות בפורמט JSON לצד הלקוח (jsonify)
from flask import Flask, request, jsonify
from llama_cpp import Llama
# ייבוא המודול המובנה בפייתון לעבודה עם ביטויים רגולריים (RegEx)
import re

# ייבוא פונקציות המעטפת (Wrappers) מתוך תיקיית solvers
from solvers.linear_solver import solve_linear_steps
from solvers.quadratic_solver import solve_quadratic_steps
from solvers.elimination_solver import solve_elimination_steps
from solvers.probability_solver import solve_probability_steps
from solvers.complex_system_solver import solve_advanced_system_steps
from solvers.rational_substitution_solver import solve_rational_substitution_steps
from solvers.substitution_solver import solve_substitution_steps
from ocr_handler import get_text_from_image
from deep_translator import GoogleTranslator

app = Flask(__name__)

# טעינת מודל השפה המקומי
print("--- טוען מודל בינה מלאכותית... ---")
llm = Llama(model_path="Meta-Llama-3.1-8B.Q4_K_M.gguf", n_ctx=2048)

# הגדרת פונקציית הנתב המרכזית שמקבלת כמחרוזת טקסט את המשוואה או המערכת משוואות שחולצו מהבעיה המילולית
def equation_router(eq_text):
    """
    מנתב חכם המשתמש בבדיקות לוגיות וב-Sympy כדי לזהות את הפותר המתאים ביותר.
    """
    # ניקוי הטקסט: הסרת כל הרווחים והמרת האותיות לקטנות
    clean_eq = eq_text.replace(" ", "").lower()
    # הגדרת ביטוי רגולרי (Regex) המחפש קו נטוי ולאחריו סוגריים אופציונליים והאות x או y - לזיהוי נעלם במכנה
    rational_pattern = r"/\(?[xy]"

    # 1
    # 1. זיהוי הסתברות (ברנולי)
    if 'c(' in clean_eq or 'p(' in clean_eq:
        print("--- נותב למנהל הסתברות ---")
        # קריאה לפותר הייעודי של בעיות הסתברות והחזרת שלבי הפתרון של נוסחת ברנולי
        return solve_probability_steps(eq_text)

    # 2
    # 2. זיהוי מערכות משוואות (מכילות פסיק)
    if ',' in clean_eq:
        # בדיקה באמצעות ה-Regex האם יש נעלם (x או y) במכנה של אחת מהמשוואות במערכת
        if re.search(rational_pattern, clean_eq):
            print("--- נותב למנהל החלפת משתני עזר (Rational Substitution) ---")
            # הפעלה של פותר מערכות רציונליות המשתמש בטכניקת הצבת משתני עזר (u = 1/x, v = 1/y)
            return solve_rational_substitution_steps(eq_text)

        # בדיקה האם המשוואות במערכת מכילות סוגריים, כפל או חזקות, המעידים על צורך בפישוט אלגברי מקדים
        if '(' in clean_eq or '*' in clean_eq or '^' in clean_eq:
            print("--- נותב למנהל מערכת מתקדם (Advanced) ---")
            return solve_advanced_system_steps(eq_text)

        print("--- נותב למנהל מערכות מורכב ---")
        return solve_advanced_system_steps(eq_text)

    # 3
    # 3. טיפול במשוואה בודדת עם נעלם במכנה
    # בדיקה באמצעות ה-Regex האם משוואה בודדת זו מכילה חילוק בנעלם x או y במכנה
    if re.search(rational_pattern, clean_eq):
        print("--- נותב לטיפול במשוואה רציונלית בודדת ---")
        try:
            if '=' in eq_text:
                # פיצול מחרוזת המשוואה לשני אגפים: אגף שמאל (lhs) ואגף ימין (rhs)
                lhs, rhs = eq_text.split('=')
                # המרת האגפים לביטויים סימבוליים של SymPy - עץ, תוך החלפת סימן החזקה הטקסטואלי לפורמט פייתון (**), והחסרתם ליצירת משוואה השקולה לאפס
                expr = sp.parse_expr(lhs.replace('^', '**')) - sp.parse_expr(rhs.replace('^', '**'))
            # במידה ולא נמצא סימן שוויון, נתייחס לקלט כולו כביטוי שמשווה בברירת מחדל לאפס
            else:
                # המרת הביטוי כולו לאובייקט סימבולי מופשט של SymPy
                expr = sp.parse_expr(eq_text.replace('^', '**'))

            # קריאה לפונקציית הפתרון המובנית של SymPy כדי לחלץ ישירות את ערכי הנעלם עבור התוצאה הסופית
            sol = sp.solve(expr)
            # בניית מערך שלבים מותאם אישית ב-LaTeX כדי להציג לתלמיד את זיהוי הבעיה ותוצאתה בצורה פדגוגית
            steps = [
                "זיהוי משוואה עם נעלם במכנה.",
                f"המשוואה שהתקבלה: $${sp.latex(expr)} = 0$$",
                "נכפיל במכנה המשותף כדי לבטל את השברים.",
                f"הפתרון שהתקבל: $${sp.latex(sol[0]) if sol else 'אין פתרון'}$$"
            ]
            # החזרת מילון המכיל את ערך הפתרון שנמצא (אם קיים) יחד עם מערך שלבי התצוגה
            return {"result": sol[0] if sol else "אין פתרון", "steps": steps}
        # תפיסת שגיאות והדפסת בקרה בשרת במקרה של כשל בפענוח או בפתרון המשוואה
        except Exception as e:
            print(f"שגיאה בפתרון רציונלי: {e}")

    # 4
    # 4. זיהוי משוואה ריבועית (לפי דרגה דינמית או תווים)
    try:
        # המרת תו החזקה לפורמט פייתון לצורך עיבוד סימבולי של מחרוזת הבדיקה
        test_str = clean_eq.replace('^', '**')
        # בדיקה האם המשוואה כוללת סימן שוויון לצורך העברת אגפים ואיחוד הביטוי
        if '=' in test_str:
            # פיצול מחרוזת הבדיקה לאגף שמאל ואגף ימין
            lhs_s, rhs_s = test_str.split('=')
            # יצירת ביטוי סימבולי מאוחד (שמאל פחות ימין) ופתיחת כל הסוגריים באמצעות expand כדי לחשוף את המבנה הפולינומי האמיתי
            expr_test = sp.expand(sp.parse_expr(lhs_s) - sp.parse_expr(rhs_s))
        # במידה ואין סימן שוויון, המרת הביטוי כולו ופתיחת סוגריים ישירה
        else:
            expr_test = sp.expand(sp.parse_expr(test_str))

        # שליפת קבוצת המשתנים החופשיים (free_symbols) המופיעים בביטוי והמרתה לרשימה לצורך תמיכה בנעלמים שאינם x
        symbols = list(expr_test.free_symbols)
        # חילוץ האיבר הראשון ברשימה כמשתנה הנבדק, או הגדרת x כברירת מחדל סימבולית אם הביטוי מכיל מספרים בלבד
        var = symbols[0] if symbols else sp.Symbol('x')

        # שימוש בפונקציית sp.degree כדי לבדוק באופן דינמי האם החזקה הגבוהה ביותר של המשתנה היא בדיוק 2
        if sp.degree(expr_test, gen=var) == 2:
            print("--- נותב לפותר ריבועי (זוהה לפי דרגה) ---")
            # ניתוב המשוואה לפותר הצעדים הריבועי (המשתמש בנוסחת השורשים)
            return solve_quadratic_steps(eq_text)

    # בלוק catch/except המשמש כרשת ביטחון במידה והבדיקה הדינמית נכשלה עקב מבנה טקסט מורכב או חריג
    except Exception:
        # בדיקה סטטית מבוססת תווים גולמיים: חיפוש סימני חזקה שנייה או תבנית של מכפלת משתנה בסוגריים x(x
        if '^2' in clean_eq or '**2' in clean_eq or 'x(x' in clean_eq:
            print("--- נותב לפותר ריבועי (גיבוי תווים) ---")
            # ניתוב המשוואה לפותר הצעדים הריבועי (המשתמש בנוסחת השורשים)
            return solve_quadratic_steps(eq_text)

    # 5
    # 5. ברירת מחדל: משוואה ליניארית
    print("--- נותב לפותר ליניארי ---")
    return solve_linear_steps(eq_text)


# בנק דוגמאות לצורך הזרקת הקשר (Few-Shot Prompting) למודל הלשון
EXAMPLES_BANK = {
    "system_money": """Example (System - Value): "A piggy bank contains 41 coins ($5 and $10 coins). Total value is $365."
Equation: x + y = 41, 5x + 10y = 365""",

    "motion": """Example (Motion - Meeting): "Two cars start 300km apart and travel toward each other. Car A at 70km/h and Car B at 80km/h. When will they meet?"
Equation: 70x + 80x = 300""",

    "geometry": """Example (Geometry - Perimeter): "The perimeter of a rectangular field is 118m. If length increases by 2m and width decreases by 3m, the new perimeter is 116m."
Equation: 2x + 2y = 118, 2(x + 2) + 2(y - 3) = 116""",

    "quadratic_geometry": """Example (Geometry - Area / Quadratic): "The length of a rectangular carpet is 5 meters greater than its width. The area of the carpet is exactly 84 square meters. Find the width of the carpet."
Equation: x * (x + 5) = 84""",

    "simple_arithmetic": """Example (Basic Arithmetic): "Rick has 129 Marbles. Dorothy gave him 71 more. How many Marbles does Rick have in all?"
Equation: x = 129 + 71""",

    "work_rate": """Example (Work Rate): "Two Technicians can finish preparing meals in 15.1 hours. One works 10 hours faster than the other."
Equation: 1/x + 1/(x-10) = 1/15.1""",

    "comparison": """Example (Comparison/Ratio): "There are 3 times more blue balls than red balls. Removing 10 blue and adding 2 red makes them equal."
Equation: 3x - 10 = x + 2""",

    "probability": """Example (Probability): "The chance of a seed germinating is 0.7. If 5 seeds are planted, what is the probability exactly 3 germinate?"
Equation: C(5,3)(0.7^3)(0.3^2)"""
}

def get_relevant_example(text):
    """
    בוחר בצורה דינמית את הדוגמה המתאימה ביותר מתוך בנק הדוגמאות על בסיס מילות מפתח.
    """
    # המרת אותיות הטקסט קטנות
    text = text.lower()

    # מספיק התאמה של מילת מפתח אחת
    if any(word in text for word in ['boat', 'upstream', 'downstream', 'current', 'km/h', 'train']):
        return EXAMPLES_BANK["motion"]

    if any(word in text for word in ['area', 'carpet', 'square meters']):
        return EXAMPLES_BANK["quadratic_geometry"]

    if any(word in text for word in ['perimeter', 'rectangle', 'area', 'length', 'width', 'dimensions']):
        return EXAMPLES_BANK["geometry"]

    if any(word in text for word in ['worker', 'finish', 'hours', 'task', 'together', 'technician']):
        return EXAMPLES_BANK["work_rate"]

    if any(word in text for word in ['coin', 'piggy bank', 'dollars', '$', 'price', 'cost']):
        return EXAMPLES_BANK["system_money"]

    if any(word in text for word in ['times more', 'equal', 'less than', 'added', 'removed']):
        return EXAMPLES_BANK["comparison"]

    if any(word in text for word in ['probability', 'chance', 'seeds', 'germinate', 'coin', 'dice', 'heads', 'tails']):
        return EXAMPLES_BANK["probability"]

    return EXAMPLES_BANK["simple_arithmetic"]


# דקורטור (Decorator) של Flask המגדיר נתיב (Route) בכתובת 'ocr/' ומגביל אותו לקבלת בקשות מסוג POST בלבד (מכיוון שנשלח אליו קובץ תמונה)
@app.route('/ocr', methods=['POST'])
def process_ocr_only():
    try:
        # בדיקת תקינות ראשונית : בדיקה האם אובייקט הבקשה (request.files) בכלל מכיל קובץ תחת המפתח שנקרא 'file'
        if 'file' not in request.files:
            return "No file part in the request", 400

        # שליפת קובץ התמונה הגולמי מתוך הבקשה ושמירתו בתוך משתנה מקומי בשם file
        file = request.files['file']
        extracted_text = get_text_from_image(file)

        if extracted_text:
            return extracted_text
        else:
            return "Could not extract text from image", 500

    # תפיסת כל סוגי החריגות (Exceptions) שעלולות להתרחש במהלך הקריאה, הניתוח או הגישה לקובץ
    except Exception as e:
        print(f"Internal OCR error: {str(e)}")
        return str(e), 500


@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        question_heb = data.get('prompt', '')

        if not question_heb:
            return jsonify({"error": "No prompt provided"}), 400

        # שלב א:
        # שלב א: תרגום השאלה מעברית לאנגלית כדי שהמודל יבין את הלוגיקה בצורה מקסימלית
        try:
            question_eng = GoogleTranslator(source='auto', target='en').translate(question_heb)
            print(f"--- תרגום מוצלח: {question_eng} ---")
        except Exception as e:
            print(f"שגיאה בתרגום, נעשה שימוש בטקסט המקורי: {e}")
            question_eng = question_heb

        # שלב ב:
        # שלב ב: בחירת דוגמה דינמית על בסיס הטקסט המורגם באנגלית
        relevant_example = get_relevant_example(question_eng)
        # הגדרת הוראת המערכת (System Instruction) המגדירה למודל את תפקידו כמומחה מתמטי ומחייבת אותו להחזיר משוואות בלבד ללא מלל מיותר
        instruction = (
            "You are a math expert. Convert the problem into equations.\n"
            "Return ONLY the math. No explanations."
        )

        # הרכבת הפרומפט המלא (Prompt Construction) המשלב את ההנחיה, הדוגמה התואמת, והשאלה הנוכחית בפורמט מובנה וברור
        full_prompt = f"{instruction}\n\n{relevant_example}\n\n###Problem:\n{question_eng}\n###Equations:"
        # ביצוע הסקה מול מודל ה-Llama המקומי: הגבלת אסימונים ל-100, הגדרת סימני עצירה, וקביעת Temperature=0.0 לתוצאה דטרמיניסטית ומדויקת
        output = llm(full_prompt, max_tokens=2048, stop=["\n", "Problem:"], temperature=0.0)
        eq_extracted = output['choices'][0]['text'].strip().replace('"', '').replace("'", "")
        print(f"--- משוואות שהופקו: {eq_extracted} ---")

        # שלב ג:
        # שלב ג: פתרון אלגברי מדויק לפי ניתוב (SymPy)
        solution_data = equation_router(eq_extracted)
        # בדיקה דינמית של טיפוס הנתונים המוחזר: אם מדובר במילון (Dictionary) - מבנה הנתונים הסטנדרטי של רוב הפותרים במערכת
        if isinstance(solution_data, dict):
            # שליפת ערך התוצאה הסופית מתוך המילון, או קביעת הודעת ברירת מחדל אם אין פתרון
            final_res = solution_data.get("result", "No solution")
            # שליפת מערך שלבי הפתרון המפורטים (הכוללים LaTeX) מתוך המילון
            final_steps = solution_data.get("steps", [])
        # בלוק חלופי במידה והפותר החזיר את המידע כרשימה מפורקת (Tuple) של שני אלמנטים
        else:
            # פירוק ישיר של ערך התוצאה ומערך השלבים מתוך ה-Tuple שהתקבל
            final_res, final_steps = solution_data
        print(final_res,final_steps)

        # שלב ד:
        # --- שלב ד: הפקת משפט סיכום באנגלית עם טיפול במקרי קצה והנחיות קשיחות ---

        # המרת ערך התוצאה הסופית שחזרה מהפותר האלגברי למחרוזת נקייה (String) כדי להנגיש אותה למודל בצורה טקסטואלית
        final_res_eng = str(final_res).strip()
        if "אין פתרון" in final_res_eng or "no solution" in final_res_eng.lower():
            final_res_eng = "No solution"
        elif "אינסוף" in final_res_eng or "infinite" in final_res_eng.lower():
            final_res_eng = "Infinitely many solutions"

        # בניית הפרומפט למודל להנפקת משפט סיכום
        # בניית פרומפט המכיל הנחיות מפורשות ומקרי קצה (Few-Shot)
        prompt_summary = f"""You are a math expert. Below is a math word problem and its final algebraic result determined by a solver.
    Your task is to write exactly ONE natural-sounding concluding sentence in English that clearly answers the problem's question based on the provided result.

    CRITICAL RULES:
    1. If the result is "No solution", you MUST state clearly that there is no solution to the problem due to contradictory details. DO NOT invent numbers.
    2. If the result is "Infinitely many solutions", you MUST state clearly that there are infinitely many possible solutions.
    3. Use the exact objects/entities from the problem description (e.g., notebooks, pens, coins). Do NOT hallucinate or introduce new items like 'tickets'.

    Example 1 (Single Solution):
    Problem: "I have 10 USD and I spent 3 USD on a soda. How much is left?"
    Result: 7
    Summary: Therefore, you have 7 dollars remaining.

    Example 2 (No Solution):
    Problem: "Roey bought 2 notebooks and 3 pens for 25 NIS. Shira bought 4 notebooks and 6 pens for 60 NIS. What is the price of a notebook and a pen?"
    Result: No solution
    Summary: Therefore, there is no possible solution for the prices of the notebooks and pens because the given information is contradictory.

    Example 3 (Infinite Solutions):
    Problem: "Roey bought 2 notebooks and 3 pens for 25 NIS. Shira bought 4 notebooks and 6 pens for 50 NIS. What is the price of a notebook and a pen?"
    Result: Infinitely many solutions
    Summary: Therefore, there are infinitely many possible solutions for the prices of the notebooks and pens.

    ###Problem:
    {question_eng}
    ###Result:
    {final_res_eng}

    ###Summary:
    """
        # הרצת מודל ה-Llama המקומי בפעם השנייה לצורך הפקת משפט הסיכום המילולי בהתאם לחוקים הנוקשים ולנתונים שהוזרקו בפרומפט
        output_sum = llm(prompt_summary, max_tokens=100, stop=["\n", "###"], temperature=0.0)
        # חילוץ מחרוזת טקסט הסיכום שנוסחה על ידי המודל וניקוי רווחים מיותרים משני קצותיה
        final_summary_eng = output_sum['choices'][0]['text'].strip()
        print(f"--- סיכום שהופק באנגלית: {final_summary_eng} ---")

        # שלב ה:
        # --- שלב ה: תרגום הסיכום המפולטר מאנגלית חזרה לעברית ---
        try:
            final_summary = GoogleTranslator(source='en', target='iw').translate(final_summary_eng)
            print(f"--- תרגום הסיכום לעברית מוצלח: {final_summary} ---")
        except Exception as e:
            print(f"שגיאה בתרגום הסיכום לעברית, נעשה שימוש במקור: {e}")
            final_summary = final_summary_eng

        # החזרת התשובה לקליינט מותאמת בדיוק ל-Interface של Angular (SolverResponse)
        return jsonify({
            "extracted_equations": eq_extracted,
            "solution_steps": final_steps,
            "final_answer": str(final_res),
            "final_summary": final_summary
        })


    except Exception as e:
        return jsonify({
            "error": str(e),
            "solution_steps": [f"שגיאת מערכת: {str(e)}"]
        }), 500


# בדיקה כדי להטיח שהקוד ירוץ רק כשמפעילים את הקובץ הראשי ולא על ידי ייבוא מקובץ אחר
if __name__ == '__main__':
    # host='0.0.0.0':ip נגישות קבלת שירות מכל כתובת
    # port=5000: הפורט שבו השרת יאזין לבקשות
    # debug=False: כיבוי מצב הדיבאג (Debug Mode) - למניעת זליגת שגיאות
    app.run(host='0.0.0.0', port=5000, debug=False)
