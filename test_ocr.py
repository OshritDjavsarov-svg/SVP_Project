import requests

# כתובת השרת שלך
url = 'http://127.0.0.1:5000/solve_image'

# נתיב לתמונה
image_path = 'problem_screenshot.png'

try:
    with open(image_path, 'rb') as img:
        files = {'image': img}
        response = requests.post(url, files=files)

        if response.status_code == 200:
            data = response.json()

            print("--- טקסט שזוהה בתמונה (עברית) ---")
            print(data.get('detected_text_heb'))

            print("\n--- תרגום לאנגלית שנשלח ל-AI ---")
            print(data.get('translated_text_eng'))

            print("\n--- משוואות שהוצאו על ידי Llama ---")
            print(data.get('extracted_equations'))

            print("\n--- צעדי פתרון ---")
            for step in data.get('solution_steps', []):
                print(f"- {step}")

            print(f"\nתוצאה סופית: {data.get('final_answer')}")

            # --- הוספת ההדפסה של המשפט המסכם כאן ---
            print("\n--- סיכום מילולי של ה-AI ---")
            print(data.get('final_summary', 'לא הופק סיכום'))
            # ------------------------------------------

        else:
            print(f"שגיאה בשרת: {response.status_code}")
            print(response.json())

except FileNotFoundError:
    print(f"לא נמצא קובץ תמונה בנתיב: {image_path}")
except Exception as e:
    print(f"קרתה שגיאה בתקשורת: {e}")