from flask import Flask, session, request, render_template, redirect, make_response, flash
# from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

app = Flask(__name__, template_folder = 'templates')
# app.debug = True


# secret key for session
app.config["SECRET_KEY"] = "donotforgetthis!"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# toolbar = DebugToolbarExtension(app)


CURRENT_SURVEY_KEY = 'current_survey'
RESPONSES_KEY = 'responses'


@app.route("/")
def pick_survey_form():
    '''show form to pick a survey.'''
    return render_template("pick-survey.html", surveys=surveys)


@app.route("/", methods=["POST"])
def pick_survey():
    '''select a survey'''
    survey_id = request.form['survey_code']

    # don't let them re-take a survey until cookies cleared
    if request.cookies.get(f"completed_{survey_id}"):
        return render_template("already-done.html")

    survey = surveys[survey_id]
    session[CURRENT_SURVEY_KEY] = survey_id

    return render_template("survey_start.html", survey=survey)


# begin survey show 1st question
@app.route("/begin", methods = ["POST"])
def start_survey():
    '''session of responses'''
    session[RESPONSES_KEY] = []

    return redirect("/questions/0")

@app.route("/answer", methods=["POST"])
def handle_question():
    ''' save response and redirect to next question.'''
    
    choice = request.form['answer']
    text = request.form.get("text", "")

    # add response to list in session
    responses = session[RESPONSES_KEY]
    responses.append({"choice": choice, "text": text})

    # add response to session
    session[RESPONSES_KEY] = responses
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]

    if(len(responses) == len(survey.questions)):
        # thank for answering all questions
        return render_template('complete.html')
    else: 
        return redirect(f"/questions/{len(responses)}")


@app.route("/questions/<int:qid>")
def show_question(qid):
    '''current question display'''
    responses = session.get(RESPONSES_KEY)
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]

    if (responses is None):
        # question must be completed to move to next
        return redirect("/")
    if (len(responses) == len(survey.questions)):
        return redirect("/complete")
    if (len(responses) != qid):
        # flash message for access question page too soon
        flash(f"Invalid question id: {qid}.")
        return redirect(f"/questions/{len(responses)}")

    question = survey.questions[qid]

    return render_template("question.html", question_num=qid, question=question)


    @app.route("/complete")
    def say_thanks():
        '''Thank user and list responses.'''

        survey_id = session[CURRENT_SURVEY_KEY]
        survey = surveys[survey_id]
        responses = session[RESPONSES_KEY]

        html = render_template("complete.html", survey=survey, responses=responses)

        # set cookie noting this survey is done so they can't re-do it
        response = make_response(html)
        response.set_cookie(f"completed_{survey_id}", "yes", max_age=60)
        return response
