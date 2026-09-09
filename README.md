# S.V.P - Solving Verbal Problems

A technological system designed to solve mathematical word problems step-by-step with detailed explanations. The system bridges the gap between natural language and mathematical syntax, providing students with clear, instructional guidance throughout the entire problem-solving process.

## Key Features
* **Natural Language Processing (NLP):** Analyzes free-form text and translates it into precise mathematical equations using the **Llama 3.1** language model.
* **Detailed Symbolic Solving:** Solves equations and systems of equations using the **SymPy** library, maintaining absolute mathematical rigor and presenting the full step-by-step solution.
* **Standard Mathematical Rendering:** Uses **LaTeX** to render formulas, fractions, and equations cleanly within the user interface.
* **Broad Problem Category Support:** Tailored to handle various problem types, including motion, financial/commercial, work rate, geometric, and probability word problems.

## Tech Stack
* **Frontend:** Angular, TypeScript
* **Backend & Math Processing:** Python, Flask
* **AI Model:** Llama 3.1
* **Symbolic Engine:** SymPy (Expression Tree parsing, algebraic manipulations)

## System Workflow
1. **Input:** User submits a mathematical word problem via the Angular frontend.
2. **NLP Extraction:** The problem is translated to English and fed into Llama 3.1 to extract logical context, variables, and equation structures.
3. **Symbolic Resolution:** Equations are passed to the Flask backend, built into an Expression Tree, and solved sequentially via SymPy.
4. **Rendering & Output:** The step-by-step solution is translated, formatted using LaTeX, and rendered back to the user.

---
**Developer:** Oshrit Djavsarov  
*Final Software Engineering Capstone Project, Navat Israel Seminar*
