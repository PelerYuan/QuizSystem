import json
import os

from flask import Flask, render_template, redirect, request, url_for, session, send_from_directory, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.urandom(24)
config = json.loads(open('configure.json').read())

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__name__)),
                                                                    'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route('/')
def hello_world():  # put application's code here
    return f'Welcome to QuizSystem!'


@app.route('/login/<entrance_id>', methods=['GET', 'POST'])
def login(entrance_id):
    if request.method == 'POST':
        session['name'] = request.form['name']
        return redirect(url_for('quiz', entrance_id=entrance_id))
    return render_template('login.html', entrance_id=entrance_id)


@app.route('/quiz/<entrance_id>')
def quiz(entrance_id):
    if session.get('name', None) is not None:
        with open('Quiz1.json', 'r', encoding='utf-8') as f:
            quiz = json.loads(f.read())
            for i in range(len(quiz['questions'])):
                quiz['questions'][i]['index'] = (i + 1)
        return render_template('quiz.html', quiz=quiz, entrance_id=entrance_id)
    else:
        return redirect(url_for('login', entrance_id=entrance_id))


@app.route('/submit/<entrance_id>', methods=['GET', 'POST'])
def submit(entrance_id):
    if session.get('name', None) is not None:
        if request.method == 'POST':
            selection = {}
            for key in request.form.keys():
                selection[key] = request.form.getlist(key)

            with open('Quiz1.json', 'r', encoding='utf-8') as f:
                quiz = json.loads(f.read())
                quiz['points'] = float(quiz['points'])
                for i in range(len(quiz['questions'])):
                    quiz['questions'][i]['index'] = str(i + 1)

            score = quiz['points']
            total_score = 0
            question_count = 0
            for question in quiz['questions']:
                if 'options' in question.keys():
                    question_count += 1
                    if selection.get(question['index'], False):
                        selection[question['index']].append(0)  # last one to be the score
                        for option in question['options']:
                            print(option.get('correct', ''))
                            if option['opt'] == selection[question['index']][0] and option.get('correct', '') == 'true':
                                selection[question['index']][-1] = score
                                total_score += score
                                break
                    else:
                        selection[question['index']] = [0]

                elif 'multioptions' in question.keys():
                    question_count += 1
                    if selection.get(question['index'], False):
                        selection[question['index']].append(0)
                        question_count = len(question['multioptions'])
                        for option in question['multioptions']:
                            print(option.get('correct', ''))
                            print(option['opt'])
                            print(selection[question['index']])
                            if option['opt'] in selection[question['index']]:
                                if option.get('correct', '') == 'true':
                                    selection[question['index']][-1] += score / question_count
                                else:
                                    selection[question['index']][-1] -= score / question_count
                        if selection[question['index']][-1] < 0:
                            selection[question['index']][-1] = 0
                        total_score += selection[question['index']][-1]
                    else:
                        selection[question['index']] = [0]

                elif 'itext' in question.keys():
                    if selection.get(question['index'], False):
                        selection[question['index']].append(-404)
                    else:
                        selection[question['index']] = [-404]

                selection['score'] = str(total_score)
                selection['total_score'] = str(score * question_count)  # Ignore itext

            with open('result.json', 'w', encoding='utf-8') as f:
                json.dump(selection, f, ensure_ascii=False, indent=4)

            session['quiz'] = quiz
            session['answer'] = selection
            session['score'] = f"{total_score} / {score * question_count}"
            return redirect(url_for('review'))
    return redirect(url_for('login'))


@app.route('/review')
def review():
    if session.get('name', None) is not None:
        quiz = session.get('quiz')
        answer = session.get('answer')
        score = session.get('score')
        return render_template('review.html', quiz=quiz, answer=answer, score=score)
    return redirect(url_for('login'))


@app.route('/img/<folder>/<filename>')
def img(folder, filename):
    return send_from_directory(folder, filename)


def is_answered(answer):
    return len(answer) > 1


app.jinja_env.globals['is_answered'] = is_answered

if __name__ == '__main__':
    app.run()
