

import requests

# כתובת השרת
url = "http://127.0.0.1:5000/ask"

# שאלות "מבחן מאמץ" (Stress Test) ברמת בחינה
hard_test_questions = [
    # בדיקת 2 הפרומפטים החכמים להנפקת פתרון מלא ומשפט סיכום
    # "A merchant has two types of coffee: one costing $6 per kg and another costing $9 per kg. How many kg of each should be mixed to obtain 50 kg of a blend costing $7.20 per kg?"
    # 👌"Two trains start 400km apart and travel toward each other. Train A travels at 60km/h and Train B at 40km/h. When will they meet?"
    #  "Worker A can finish a job in 6 hours, and Worker B can finish it in 12 hours. How long will it take them together?"
    # 👌"If the length of a rectangle is increased by 2 and the width is decreased by 3, the area remains the same. The original perimeter is 20."
# "A farm has chickens and cows. There are a total of 30 animals and 100 legs. How many hickens and how many cows are on the farm?"
# "There are chickens and cows on the farm. There are a total of 30 animals and 100 legs. How many chickens and how many cows are there on the farm?"
    # בעיות שכתבתי לבדיקת המנהלים
    # "A father is 4 times older than his son. In 5 years, the sum of their ages will be 60. How old is the son now?"
    # "notebooks and 2 pencils cost 18 shekels. 5 notebooks and 1 pencil cost 23 shekels. Find the price of one notebook and one pencil."
    # "A basketball player has a 0.8 chance of scoring a free throw. If he shoots 6 times, what is the probability that he scores exactly 4 times?"


    # בעיות שכתבתי לבדיקת זרימת ביצוע המנהלים במערכת
    #  !!!!!!!!!!!!!!!!!!!"The sum of two fractions is 1/6. If we double the first and triple the second, the sum becomes 1/2. Find the denominators x and y."
    # "The sum of two fractions is 5/6. If the first is doubled and the second is tripled, the sum is 2. Find x and y."
     # "In a farm, if we add 3 to the number of cows (x) and multiply by 2, it equals the number of chickens (y). Also, half the sum of cows and chickens plus the number of cows is 10. Find x and y."
    # "Hi, how are you' I've a quetion:The probability of a seed germinating is 0.7. If a gardener plants 5 seeds, what is the probability that exactly 3 of them will germinate?"
    # "The area of a rectangle is 24 square meters. The length is 2 meters longer than the width (x). Find the width of the rectangle."
    # "I thought of a number, multiplied it by 3, added 7, and got 22. What is the number?"


    # בעיות שכתבתי לבדיקת תוצאות המודל ושיפור הפרומפט שנשלח למודל עם הבעיה המילולית
    #  "There were 3 times more blue balls in the box than red balls. After removing 10 blue balls from the box and adding 2 red balls, the number of blue balls was equal to the number of red balls. How many red balls were in the box at the beginning?"
    # # אחוזים עם שינוי כפול
    # "A coat's price was increased by 20%, then decreased by 20%. The final price is 96 NIS. What was the original price?",
    #
    # # תערובות מורכבות
    # "How many liters of a 10% acid solution must be mixed with 20 liters of a 40% acid solution to get a 30% solution?",

    # בעיית גילאים עם "לפני" ו"אחרי"
    # "Five years ago, a man was 7 times as old as his son. In five years, he will be 3 times as old as his son.",

    # # בעיית הספק (Work Rate)
    # "Worker A can finish a job in 6 hours, and Worker B can finish it in 12 hours. How long will it take them together?",
    #
    # # גיאומטריה עם שינוי מידות
    # "If the length of a rectangle is increased by 2 and the width is decreased by 3, the area remains the same. The original perimeter is 20.",
    #
    # # בעיית תנועה עם פגישה
    # "Two trains start 400km apart and travel toward each other. Train A travels at 60km/h and Train B at 40km/h. When will they meet?",
    #
    # # מספרים עם יחסים הפוכים
    # "The sum of the digits of a two-digit number is 9. If the digits are reversed, the new number is 27 more than the original.",
    #
    # # כספים עם יחסים
    # "A jar contains only quarters (0.25$) and dimes (0.10$). There are 40 coins in total, worth 7 dollars.",
    #
    # # שברים והשוואה
    # "One-third of a number is 15 less than half of the same number. Find the number.",
    #
    # # בעיית "יותר מ-" ו"פי-" משולבת
    # "In a class, there are 5 more girls than twice the number of boys. The total number of students is 35."
]

print("=" * 60)
print("🔥 Stress Test: Exam Level Challenge (via Flask)")
print("=" * 60)

for i, q in enumerate(hard_test_questions, 1):
    print(f"\nQuestion {i}: {q}")
    payload = {"prompt": q}

    try:
        response = requests.post(url, json=payload)

        # בתוך הלולאה של client.py
        if response.status_code == 200:
            data = response.json()

            equations = data.get('extracted_equations', 'No equations found')
            solution = data.get('final_answer', 'No solution found')
            steps = data.get('solution_steps', [])
            summary = data.get('final_summary', 'No summary generated')  # שליפת הסיכום

            print(f"📝 Equations Extracted: {equations}")
            print(f"🔢 Final Numeric Result: {solution}")

            if steps:
                print("🔍 Mathematical Steps:")
                for step in steps:
                    print(f"  {step}")

            print(f"🌟 AI Concluding Summary: {summary}")  # הדפסת הסיכום
        else:
            print(f"❌ Error: Status code {response.status_code}")

    except Exception as e:
        print(f"❌ Connection Error: {e}")

    print("-" * 40)




