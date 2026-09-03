from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from ai import generate_questions, evaluate_interview
import os
from dotenv import load_dotenv

load_dotenv()
import inspect
print(inspect.signature(generate_questions))
import sqlite3

from datetime import timedelta
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

app.permanent_session_lifetime = timedelta(days=30)
@app.route("/")
def home():

    if "user" in session:
        return redirect("/dashboard")

    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
                "SELECT * FROM users WHERE email=?",
                (email,)
            )


        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[3], password):

            remember = request.form.get("remember")

            if remember:
                session.permanent = True

            session["user"] = user[1]

            return redirect("/dashboard")
        else:
            return render_template(
                "login.html",
                error="Invalid Email or Password!"
        )

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users(name,email,password) VALUES(?,?,?)",
                (name, email, password)
            )

            conn.commit()
            conn.close()

            return redirect("/login")

        except sqlite3.IntegrityError:
            conn.close()
            return render_template(
                  "register.html",
                     error="Email already exists!"
            )

    return render_template("register.html")

@app.route("/interview", methods=["GET", "POST"])
def interview():

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":

        # Step 1: User selected interview type
        if "topic" in request.form:

            topic = request.form["topic"]

            questions = generate_questions(topic, count = 10)
            question_list = questions.split("\n")
            question_list = [q for q in question_list if q.strip()]

            # Store interview session
            session["topic"] = topic
            session["questions"] = question_list
            session["answers"] = []
            session["current_question"] = 0

            return render_template(
                "quiz.html",
                question=question_list[0],
                number=1
            )   

        # Step 2: User submitted answer
        else:

            question = request.form["question"]
            answer = request.form["answer"]
            action = request.form["action"]

            # Save current answer
            session["answers"].append({
                "question": question,
                "answer": answer
            })

            # ---------------- NEXT QUESTION ----------------

            if action == "next":

                session["current_question"] += 1

                current = session["current_question"]

                # Check if more questions are available
                if current < len(session["questions"]):

                    return render_template(
                        "quiz.html",
                        question=session["questions"][current],
                        number=current + 1
                    )

                # If no more questions, automatically finish
                action = "finish"

            # ---------------- FINISH INTERVIEW ----------------

            if action == "finish":

                interview_text = ""

                for qa in session["answers"]:

                    interview_text += f"""
            Question:
            {qa['question']}

            Answer:
            {qa['answer']}

            """

                feedback = evaluate_interview(interview_text)

                import re

                match = re.search(r"Overall Score:\s*(.*)", feedback)

                overall_score = match.group(1) if match else "N/A"

                conn = sqlite3.connect("database.db")
                cursor = conn.cursor()

                # Save interview session
                cursor.execute("""
                INSERT INTO interview_sessions
                (
                    user_name,
                    topic,
                    overall_score,
                    overall_feedback
                )
                VALUES(?,?,?,?)
                """,
                (
                    session["user"],
                    session["topic"],
                    overall_score,
                    feedback
                ))

                # Save every question & answer
                for qa in session["answers"]:

                    cursor.execute("""
                    INSERT INTO interview_results
                    (
                        user_name,
                        topic,
                        question,
                        answer,
                        score,
                        feedback
                    )
                    VALUES(?,?,?,?,?,?)
                    """,
                    (
                        session["user"],
                        session["topic"],
                        qa["question"],
                        qa["answer"],
                        overall_score,
                        feedback
                    ))

                conn.commit()
                conn.close()

                session.pop("questions", None)
                session.pop("answers", None)
                session.pop("current_question", None)
                session.pop("topic", None)

                return render_template(
                    "result.html",
                    feedback=feedback
                )
    return render_template("interview.html")
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Total completed interviews
    cursor.execute("""
    SELECT COUNT(*)
    FROM interview_sessions
    WHERE user_name=?
    """, (session["user"],))

    total = cursor.fetchone()[0]

    # Latest interview
    cursor.execute("""
    SELECT overall_score, topic
    FROM interview_sessions
    WHERE user_name=?
    ORDER BY interview_date DESC
    LIMIT 1
    """, (session["user"],))

    last = cursor.fetchone()

    conn.close()

    return render_template(
        "dashboard.html",
        username=session["user"],
        total=total,
        last=last[0] if last else "No Interviews",
        topic=last[1] if last else "-"
    )
@app.route("/history")
def history():

    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        id,
        topic,
        overall_score,
        interview_date
    FROM interview_sessions
    WHERE user_name=?
    ORDER BY interview_date DESC
    """, (session["user"],))

    interviews = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        interviews=interviews
    )
@app.route("/quiz")
def quiz():
    return render_template("quiz.html")
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)