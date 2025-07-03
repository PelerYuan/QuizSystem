import json
import os
import uuid

from flask import Flask, render_template, redirect, request, url_for, session, send_from_directory, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.urandom(24)

admin_config = json.loads(open('configure.json').read())

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__name__)),
                                                                    'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Quiz(db.Model):
    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=False, nullable=False)
    description = db.Column(db.String(256), unique=False, nullable=False)
    file_path = db.Column(db.String(256), unique=False, nullable=False)

    entrance = db.relationship('Entrance', backref='quiz')

    def __repr__(self):
        return f'<Quiz ID:{self.username}, Name:{self.name}, Description:{self.description}>'


class Entrance(db.Model):
    __tablename__ = 'entrance'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    name = db.Column(db.String(256), unique=False, nullable=False)
    description = db.Column(db.String(256), unique=False, nullable=False)

    result = db.relationship('Result', backref='entrance')

    def __repr__(self):
        return f'<Entrance ID: {self.id}, Name: {self.name}, Description: {self.description}>'


class Result(db.Model):
    __tablename__ = 'result'
    id = db.Column(db.Integer, primary_key=True)
    entrance_id = db.Column(db.Integer, db.ForeignKey('entrance.id'))
    student_name = db.Column(db.String(256), unique=False, nullable=False)
    score = db.Column(db.Float, unique=False, nullable=False)
    file_path = db.Column(db.String(256), unique=False, nullable=False)

    def __repr__(self):
        return f'<Entrance ID: {self.id}, Name: {self.name}, Description: {self.description}>'


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
    if session.get('name') is not None:
        quiz_id = Entrance.query.filter_by(id=entrance_id).first().id
        file_path = Quiz.query.filter_by(id=quiz_id).first().file_path
        with open(file_path, 'r', encoding='utf-8') as f:
            quiz = json.loads(f.read())
            for i in range(len(quiz['questions'])):
                quiz['questions'][i]['index'] = (i + 1)
        return render_template('quiz.html', quiz=quiz, entrance_id=entrance_id)
    else:
        return redirect(url_for('login', entrance_id=entrance_id))


@app.route('/submit/<entrance_id>', methods=['POST'])
def submit(entrance_id):
    selection = {}
    for key in request.form.keys():
        selection[key] = request.form.getlist(key)

    quiz_id = Entrance.query.filter_by(id=entrance_id).first().id
    file_path = Quiz.query.filter_by(id=quiz_id).first().file_path
    with open(file_path, 'r', encoding='utf-8') as f:
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

    file_path = os.path.join('result/', str(uuid.uuid4())) + '.json'
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(selection, f, ensure_ascii=False, indent=4)
    result = Result(entrance_id=entrance_id, student_name=session['name'], score=total_score,
                    file_path=file_path)
    db.session.add(result)
    db.session.commit()

    session['quiz'] = quiz
    session['answer'] = selection
    session['score'] = f"{total_score} / {score * question_count}"
    return redirect(url_for('review', entrance_id=entrance_id))


@app.route('/review/<entrance_id>')
def review(entrance_id):
    if session.get('name') is not None:
        session['name'] = None
        quiz = session.get('quiz')
        answer = session.get('answer')
        score = session.get('score')
        return render_template('review.html', quiz=quiz, answer=answer, score=score)
    return redirect(url_for('login', entrance_id=entrance_id))


@app.route('/img/<folder>/<filename>')
def img(folder, filename):
    return send_from_directory(folder, filename)


def is_answered(answer):
    return len(answer) > 1


app.jinja_env.globals['is_answered'] = is_answered


@app.route('/admin')
def admin():
    if session.get('admin', False):
        tests = []
        for quiz in Quiz.query.all():
            tests.append(
                {'id': quiz.id, 'name': quiz.name, 'description': quiz.description, 'file_path': quiz.file_path})
        return render_template('admin/admin.html', tests=tests)
    return redirect(url_for('admin_login'))


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form['password']
        if password == admin_config['admin password']:
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('admin/login.html', wrong_password=True)
    return render_template('admin/login.html', wrong_password=False)


@app.route('/admin_trial/<quiz_id>')
def admin_trial(quiz_id):
    if session.get('admin', False):
        file_path = Quiz.query.filter_by(id=quiz_id).first().file_path
        with open(file_path, 'r', encoding='utf-8') as f:
            quiz = json.loads(f.read())
            for i in range(len(quiz['questions'])):
                quiz['questions'][i]['index'] = (i + 1)
        return render_template('admin/trial.html', quiz=quiz)
    return redirect(url_for('admin_login'))


@app.route('/quiz_add', methods=['GET', 'POST'])
def quiz_add():
    if session.get('admin', False):
        if request.method == 'POST':
            json_ = request.files.get('json')
            image_dir = {}
            json_path = ""
            try:
                if json_:
                    json_path = os.path.join('quiz/', str(uuid.uuid4())) + '.json'
                    json_.save(json_path)
                    with open(json_path, 'r', encoding='utf-8') as f:
                        quiz = json.loads(f.read())
                        quiz['image_folder'] = 'img'
                        for i in range(len(quiz['questions'])):
                            question = quiz['questions'][i]
                            image = question.get('image', False)
                            if image:
                                code = str(uuid.uuid4())+ '.' + image.split('.')[-1]
                                image_dir[image] = code
                                question['image'] = code
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(quiz, f, ensure_ascii=False, indent=4)
            except Exception as e:
                return render_template('admin/add.html', error="Json File invalid: " + e.args[0])

            try:
                images = request.files.getlist('images')
                for image in images:
                    if image:
                        filename = image_dir[image.filename]
            except KeyError as e:
                return render_template('admin/add.html', error="Image invalid: " + e.args[0])

            for image in images:
                if image:
                    filename = image_dir[image.filename]
                    image_dir.pop(image.filename)
                    image.save(os.path.join('img/', filename))

            if image_dir:
                return render_template('admin/add.html', error="Lack of image: " + str(list(image_dir.keys())))

            quiz = Quiz(name=request.form['name'], description=request.form['description'], file_path=json_path)
            db.session.add(quiz)
            db.session.commit()

            return redirect(url_for('admin'))
        return render_template('admin/add.html', error='')
    return redirect(url_for('admin_login'))


if __name__ == '__main__':
    app.run()
