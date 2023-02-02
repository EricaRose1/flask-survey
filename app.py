from flask import Flask, request, render_template, redirect, flash, session
# from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey as survey

res_key = "responses"

# app.debug = True

app=Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = "oh-so-secret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# debug = DebugToolbarExtension(app)

# 
@app.route("/")
def begin_survey():
    '''select a survey'''
    return render_template("survey_instructions.html", survey = survey)


@app.route("/begin", methods = ["POST"])
def start():
    '''session of responses'''
    session[res_key] = []

    return redirect("/questions/0")
    


@app.route('/questions/<int:qid>')
def show_question(qid):
    '''current question display'''
    responses = session.get(res_key)

    if (len(responses) != qid):
        # flash message for access question page too soon
        flash(f"Invalid question id: {qid}.")
        return redirect(f"/questions/{len(responses)}")

    if (len(responses) == len(survey.questions)):
        # They've answered all the questions! Thank them.
        return redirect("/complete")

    if (responses is None):
        #question must be completed to move to next
        return redirect("/")

    question = survey.questions[qid]
    return render_template(
        "questions.html", question_num = qid, question = question
    )


@app.route("/answer", methods = ["POST"])
def handle_question():
    ''' save answers and move to next question '''
    choice = request.form['answer']

    #add response to the session
    responses = session[res_key]
    responses.append(choice)
    session[res_key] = responses

    #next question
    if(len(responses) == len(survey.questions)):
        #answered all questions
        return redirect("/complete")
    else:
        return redirect(f"/questions/{len(responses)}")

@app.route('/complete')
def complete():
    ''' show completioiin html'''
    return render_template("complete.html")