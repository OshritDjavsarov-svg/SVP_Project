# ייבוא ספריית PyTesseract עבור מנוע ה-OCR של גוגל (Tesseract), ומאפשרת חילוץ טקסט מתמונות
import pytesseract

# ייבוא ספריית OpenCV (תחת השם cv2), ספריית קוד פתוח מובילה לעיבוד תמונה וראייה ממוחשבת, המשמשת במקרה זה לטיפול במטריצות הפיקסלים והמרתן לאפור
import cv2

# ייבוא ספריית NumPy (תחת הכינוי np) המיועדת לניהול מערכים רב-ממדיים וחישובים וקטוריים, המשמשת במקרה זה להמרת רצף הבתים הבינארי של הקובץ למבנה נתונים של מערך פיקסלים
import numpy as np

# ייבוא המודול המובנה os המאפשר אינטראקציה מול מערכת ההפעלה של השרת, ניהול נתיבי קבצים והגדרת משתני סביבה
import os

# ייבוא הרכיב GoogleTranslator מתוך ספריית deep_translator לצורך תרגום אוטומטי של הטקסט שחולץ לעברית, במידה והתלמיד צילם שאלה באנגלית
from deep_translator import GoogleTranslator

# 1. הגדרת נתיבים
# הגדרת משתנה קבוע המכיל את נתיב התיקייה שבה מותקן מנוע ה-Tesseract במערכת הקבצים של השרת
TESS_PATH = r'D:\flask'
# הגדרת נתיב קשיח לתיקיית tessdata, המכילה את קובצי השפה המאומנים (Traineddata) עבור עברית ואנגלית שבהם המנוע משתמש לצורך זיהוי התווים
TESSDATA_PATH = r'D:\flask\tessdata'

# 2. הגדרת ה-EXE ומשתנה הסביבה
# שיוך נתיב הרצה קשיח עבור ספריית pytesseract, כדי שתדע בדיוק היכן נמצא קובץ ההרצה (Executable) של מנוע ה-OCR על השרת
pytesseract.pytesseract.tesseract_cmd = os.path.join(TESS_PATH, 'tesseract.exe')
# הגדרת משתנה סביבה במערכת ההפעלה המכוון את Tesseract ישירות למיקום של קובצי השפות, כדי למנוע שגיאות טעינה של חבילות השפה בזמן הריצה
os.environ['TESSDATA_PREFIX'] = TESSDATA_PATH

# הגדרת הפונקציית  שמקבלת אובייקט קובץ תמונה (מתוך בקשת ה-HTTP) ומחזירה את הטקסט המפוענח והמתורגם
def get_text_from_image(image_file):
    # פתיחת בלוק try-except לטיפול בחריגות ושגיאות בזמן הרצת ה-OCR כדי להבטיח יציבות ולא להקריס את השרת
    try:
        image_file.seek(0)
        file_bytes = image_file.read()
        if not file_bytes:
            return None

        # המרת רצף הבתים הבינאריים למערך חד-ממדי של NumPy המורכב מטיפוס נתונים של בתים לא חתומים - לייצוג ערכי הפקסלים
        img_array = np.frombuffer(file_bytes, np.uint8)
        # פענוח מערך הפיקסלים באמצעות OpenCV והפיכתו למטריצת תמונה צבעונית בפורמט הסטנדרטי BGR
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        # בדיקת תקינות נוספת המוודאת ש-OpenCV אכן הצליח לפענח את המערך בצורה מוצלחת למטריצת תמונה חוקית
        if img is None:
            return None

        # שלב קדם-עיבוד : המרת התמונה הצבעונית לתמונת גווני אפור
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # הפעלת מנוע ה-OCR על תמונת האפור,
        #  תוך הגדרת פרמטר השפה לעבודה משולבת ומקבילה של עברית ואנגלית ('heb+eng') לחילוץ מחרוזת הטקסט
        extracted_text = pytesseract.image_to_string(gray, lang='heb+eng')

        # ניקוי מחרוזת הטקסט שהתקבלה
        cleaned_text = extracted_text.strip()

        # בדיקה האם לאחר הניקוי נשאר טקסט כלשהו, או שמנוע ה-OCR החזיר מחרוזת ריקה מחוסר זיהוי תווים
        if not cleaned_text:
            # החזרת ערך ריק במידה ולא זוהה שום תו מילולי בתמונה
            return None

        # --- מנגנון התרגום לעברית ---
        # פתיחת בלוק try פנימי המיועד ספציפית להגנה על תהליך התרגום, כדי שבעיות תקשורת ברשת או מול ה-API לא יכשילו את כל שלב ה-OCR
        try:
            # יצירת מופע של המתרגם, הגדרת זיהוי שפה אוטומטי במקור ('auto'), קביעת שפת היעד לעברית ('iw'), והפעלת התרגום על הטקסט שחולץ
            translated = GoogleTranslator(source='auto', target='iw').translate(cleaned_text)

            # שורת בדיקה (Debugging) המדפיסה לקונסול של השרת את הטקסט המקורי שחולץ מהתמונה לפני תהליך התרגום
            print(f"DEBUG: Original OCR: {cleaned_text}")
            # שורת בדיקה המדפיסה לקונסול של השרת את תוצאת הטקסט לאחר שעבר בהצלחה את תהליך התרגום לעברית
            print(f"DEBUG: Translated: {translated}")
            # החזרת הטקסט הסופי, המיושר והמתורגם לעברית כפלט הרשמי של הפונקציה
            return translated

        # תפיסת שגיאות ייעודיות לתהליך התרגום (כמו בעיות זמינות רשת, חסימת בקשות או שגיאות של ספריית deep_translator)
        except Exception as trans_error:
            # הדפסת תיאור שגיאת התרגום בשרת (Console) לצורך בקרה ומעקב
            print(f"Translation Error: {trans_error}")
            # במקרה של שגיאת תרגום, נחזיר את טקסט המקור כדי לא לתקוע את התהליך
            return cleaned_text

    # תפיסת שגיאות כלליות וקריטיות שקרו בבלוק ה-try הראשי (בעיות זיכרון, קריסה של OpenCV או כשל של מנוע Tesseract המקומי)
    except Exception as e:
        # הדפסת הודעת השגיאה הכללית לקונסול של השרת לצורך דיבאגינג
        print(f"OCR Error: {e}")
        # החזרת ערך ריק המציין כי חלה שגיאה בתהליך ה-OCR והעיבוד נכשל לחלוטין
        return None