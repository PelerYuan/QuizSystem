import json
import os
import uuid

from openpyxl import Workbook
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
    id = db.Column(db.String(256), primary_key=True, default=str(uuid.uuid4()))
    name = db.Column(db.String(256), unique=False, nullable=False)
    description = db.Column(db.String(256), unique=False, nullable=False)
    file_path = db.Column(db.String(256), unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    entrance = db.relationship('Entrance', backref='quiz')

    def __repr__(self):
        return f'<Quiz ID:{self.username}, Name:{self.name}, Description:{self.description}>'


class Entrance(db.Model):
    __tablename__ = 'entrance'
    id = db.Column(db.String(256), primary_key=True, default=str(uuid.uuid4()))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    name = db.Column(db.String(256), unique=False, nullable=False)
    description = db.Column(db.String(256), unique=False, nullable=False)
    create_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    result = db.relationship('Result', backref='entrance')

    def __repr__(self):
        return f'<Entrance ID: {self.id}, Name: {self.name}, Description: {self.description}>'


class Result(db.Model):
    __tablename__ = 'result'
    id = db.Column(db.String(256), primary_key=True, default=str(uuid.uuid4()))
    entrance_id = db.Column(db.Integer, db.ForeignKey('entrance.id'))
    student_name = db.Column(db.String(256), unique=False, nullable=False)
    score = db.Column(db.Float, unique=False, nullable=False)
    file_path = db.Column(db.String(256), unique=False, nullable=False)
    create_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<Entrance ID: {self.id}, Name: {self.name}, Description: {self.description}>'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login/<entrance_id>', methods=['GET', 'POST'])
def login(entrance_id):
    if request.method == 'POST':
        session['name'] = request.form['name']
        return redirect(url_for('quiz', entrance_id=entrance_id))
    return render_template('login.html', entrance_id=entrance_id)


@app.route('/quiz/<entrance_id>')
def quiz(entrance_id):
    if session.get('name') is not None:
        quiz_id = Entrance.query.filter_by(id=entrance_id).first().quiz_id
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
    if session.get('name') is not None:
        selection = {}
        for key in request.form.keys():
            selection[key] = request.form.getlist(key)

        quiz_id = Entrance.query.filter_by(id=entrance_id).first().quiz_id
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
                    correct_question_count_ = len([option for option in question['multioptions'] if option.get('correct', '') == 'true'])
                    for option in question['multioptions']:
                        if option['opt'] in selection[question['index']]:
                            if option.get('correct', '') == 'true':
                                selection[question['index']][-1] += score / correct_question_count_
                            else:
                                selection[question['index']][-1] -= score / correct_question_count_
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
        selection['points'] = str(score)
        file_path = os.path.join('result/', str(uuid.uuid4())) + '.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(selection, f, ensure_ascii=False, indent=4)
        result = Result(entrance_id=entrance_id, student_name=session['name'], score=total_score,
                        file_path=file_path)
        db.session.add(result)
        db.session.commit()

        return redirect(url_for('review', result_id=result.id))
    else:
        return redirect(url_for('login', entrance_id=entrance_id))


@app.route('/review/<result_id>')
def review(result_id):
    entrance_id = Result.query.filter_by(id=result_id).first().entrance_id
    if session.get('name') is not None or session.get('admin', False):
        session['name'] = None
        quiz_id = Entrance.query.filter_by(id=entrance_id).first().quiz_id
        file_path = Quiz.query.filter_by(id=quiz_id).first().file_path
        with open(file_path, 'r', encoding='utf-8') as f:
            quiz = json.loads(f.read())
            for i in range(len(quiz['questions'])):
                quiz['questions'][i]['index'] = str(i + 1)
        result_path = Result.query.filter_by(id=result_id).first().file_path
        with open(result_path, 'r', encoding='utf-8') as f:
            answer = json.loads(f.read())
        score = Result.query.filter_by(id=result_id).first().score
        return render_template('review.html', quiz=quiz, answer=answer, score=score)
    return redirect(url_for('login', entrance_id=entrance_id))


@app.route('/img/<folder>/<filename>')
def img(folder, filename):
    return send_from_directory(folder, filename)

@app.route('/img/<filename>')
def img_direct(filename):
    return send_from_directory('img', filename)


def is_answered(answer):
    return len(answer) > 1


app.jinja_env.globals['is_answered'] = is_answered


@app.route('/admin')
def admin():
    if session.get('admin', False):
        tests = []
        for quiz in Quiz.query.all():
            # Try to get subtitle from quiz JSON
            subtitle = ''
            try:
                with open(quiz.file_path, 'r', encoding='utf-8') as f:
                    quiz_data = json.loads(f.read())
                    subtitle = quiz_data.get('subtitle', '')
            except:
                subtitle = ''

            tests.append(
                {'id': quiz.id, 'name': quiz.name, 'description': quiz.description,
                 'subtitle': subtitle, 'file_path': quiz.file_path})
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


@app.route('/quiz_trial/<quiz_id>')
def quiz_trial(quiz_id):
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
            quiz_id = None
            
            try:
                if json_:
                    # Read and process the uploaded JSON
                    json_path = os.path.join('quiz/', str(uuid.uuid4())) + '.json'
                    json_.save(json_path)
                    
                    with open(json_path, 'r', encoding='utf-8') as f:
                        quiz_data = json.loads(f.read())
                        
                    # Ensure required fields exist
                    quiz_data['image_folder'] = 'img'
                    if 'title' not in quiz_data or not quiz_data['title']:
                        quiz_data['title'] = request.form['name']
                    if 'subtitle' not in quiz_data:
                        quiz_data['subtitle'] = request.form['name']  # Use name as fallback
                    if 'description' not in quiz_data:
                        quiz_data['description'] = request.form['description']
                    if 'points' not in quiz_data:
                        quiz_data['points'] = '1'
                    
                    # Process image references in questions
                    if 'questions' in quiz_data:
                        for i, question in enumerate(quiz_data['questions']):
                            image = question.get('image', False)
                            if image:
                                # Generate new UUID-based filename
                                code = str(uuid.uuid4()) + '.' + image.split('.')[-1]
                                image_dir[image] = code
                                question['image'] = code
                    
                    # Save the processed JSON
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(quiz_data, f, ensure_ascii=False, indent=4)
                        
            except Exception as e:
                if json_path and os.path.exists(json_path):
                    os.remove(json_path)
                return render_template('admin/add_quiz.html', error="JSON file invalid: " + str(e))

            # Handle image uploads
            try:
                images = request.files.getlist('images')
                
                # Check if all referenced images are provided
                for image in images:
                    if image and image.filename not in image_dir:
                        return render_template('admin/add_quiz.html', error=f"Unexpected image: {image.filename}")
                
                # Save uploaded images with new names
                for image in images:
                    if image and image.filename in image_dir:
                        filename = image_dir[image.filename]
                        image.save(os.path.join('img/', filename))
                        image_dir.pop(image.filename)
                
                # Check if any referenced images are missing
                if image_dir:
                    # Clean up saved JSON file
                    if json_path and os.path.exists(json_path):
                        os.remove(json_path)
                    return render_template('admin/add_quiz.html', error="Missing images: " + str(list(image_dir.keys())))
                    
            except Exception as e:
                # Clean up saved JSON file
                if json_path and os.path.exists(json_path):
                    os.remove(json_path)
                return render_template('admin/add_quiz.html', error="Image processing error: " + str(e))

            # Save quiz to database
            try:
                quiz_id = str(uuid.uuid4())
                quiz = Quiz(id=quiz_id, name=request.form['name'], description=request.form['description'], file_path=json_path)
                db.session.add(quiz)
                db.session.commit()
                
                # Redirect to visual editor for further editing
                return redirect(url_for('quiz_edit_visual', quiz_id=quiz_id))
                
            except Exception as e:
                # Clean up files if database save fails
                if json_path and os.path.exists(json_path):
                    os.remove(json_path)
                return render_template('admin/add_quiz.html', error="Database error: " + str(e))
                
        return render_template('admin/add_quiz.html', error='')
    return redirect(url_for('admin_login'))


@app.route('/entrance_manage/<quiz_id>')
def entrance_manage(quiz_id):
    if session.get('admin', False):
        entrances = []
        quiz_name  = Quiz.query.filter_by(id=quiz_id).first().name
        for entrance in Entrance.query.filter_by(quiz_id=quiz_id).all():
            entrances.append(
                {'id': entrance.id, 'quiz_id': entrance.quiz_id, 'name': entrance.name, 'description': entrance.description})
        return render_template('admin/manage_entrance.html', entrances=entrances, quiz_id=quiz_id, quiz_name=quiz_name,hostname=request.host)
    return redirect(url_for('admin_login'))


@app.route('/entrance_add/<quiz_id>', methods=['GET', 'POST'])
def entrance_add(quiz_id):
    if session.get('admin', False):
        if request.method == 'POST':
            entrance = Entrance(quiz_id=quiz_id, name=request.form['name'], description=request.form['description'])
            db.session.add(entrance)
            db.session.commit()

            return redirect(url_for('entrance_manage', quiz_id=quiz_id))
        return render_template('admin/add_entrance.html', error='', quiz_id=quiz_id)
    return redirect(url_for('admin_login'))

@app.route('/result_manage/<entrance_id>')
def result_manage(entrance_id):
    if session.get('admin', False):
        # Get basic information
        entrance = Entrance.query.filter_by(id=entrance_id).first()
        quiz = Quiz.query.filter_by(id=entrance.quiz_id).first()
        
        # Get quiz data to calculate max possible score
        with open(quiz.file_path, 'r', encoding='utf-8') as f:
            quiz_data = json.loads(f.read())
        
        points_per_question = float(quiz_data.get('points', 1))
        graded_questions = 0
        for question in quiz_data.get('questions', []):
            if 'options' in question or 'multioptions' in question:
                graded_questions += 1
        max_possible_score = points_per_question * graded_questions
        
        # Get all results and calculate statistics
        results = Result.query.filter_by(entrance_id=entrance_id).all()
        
        if not results:
            return render_template('admin/result_analytics.html', 
                                 quiz_name=quiz.name, entrance_name=entrance.name,
                                 quiz_id=entrance.quiz_id, entrance_id=entrance_id,
                                 total_students=0, statistics={}, best_students=[], 
                                 dangerous_students=[], score_distribution=[])
        
        # Calculate statistics
        scores = [result.score for result in results]
        total_students = len(scores)
        average_score = sum(scores) / total_students
        max_score = max(scores)
        min_score = min(scores)
        
        # Calculate pass rate (assuming 60% is passing)
        passing_score = max_possible_score * 0.6
        pass_count = sum(1 for score in scores if score >= passing_score)
        pass_rate = (pass_count / total_students) * 100
        
        # Score distribution for charts
        score_ranges = ['0-20%', '21-40%', '41-60%', '61-80%', '81-100%']
        distribution = [0, 0, 0, 0, 0]
        
        for score in scores:
            percentage = (score / max_possible_score) * 100 if max_possible_score > 0 else 0
            if percentage <= 20:
                distribution[0] += 1
            elif percentage <= 40:
                distribution[1] += 1
            elif percentage <= 60:
                distribution[2] += 1
            elif percentage <= 80:
                distribution[3] += 1
            else:
                distribution[4] += 1
        
        # Categorize students
        # Best students: top performers
        excellent_threshold = max_possible_score * 0.8
        good_threshold = max_possible_score * 0.7
        
        best_students = []
        dangerous_students = []
        
        # Sort results by score
        sorted_results = sorted(results, key=lambda x: x.score, reverse=True)
        
        # Get top performers (top 20% or minimum 1, maximum 10)
        top_count = max(1, min(10, int(total_students * 0.2)))
        for result in sorted_results[:top_count]:
            if result.score >= excellent_threshold:
                best_students.append({
                    'name': result.student_name,
                    'score': result.score,
                    'percentage': round((result.score / max_possible_score) * 100, 1) if max_possible_score > 0 else 0,
                    'category': 'Excellent'
                })
            elif result.score >= good_threshold:
                best_students.append({
                    'name': result.student_name,
                    'score': result.score,
                    'percentage': round((result.score / max_possible_score) * 100, 1) if max_possible_score > 0 else 0,
                    'category': 'Good'
                })
        
        # Get dangerous students: bottom 4 students (or all if less than 4)
        bottom_count = min(4, total_students)
        for result in sorted_results[-bottom_count:]:
            dangerous_students.append({
                'name': result.student_name,
                'score': result.score,
                'percentage': round((result.score / max_possible_score) * 100, 1) if max_possible_score > 0 else 0,
                'category': 'Needs Attention'
            })
        
        # Reverse dangerous students list to show lowest scores first
        dangerous_students = dangerous_students[::-1]
        
        statistics = {
            'total_students': total_students,
            'average_score': round(average_score, 2),
            'max_score': max_score,
            'min_score': min_score,
            'max_possible_score': max_possible_score,
            'pass_rate': round(pass_rate, 1),
            'average_percentage': round((average_score / max_possible_score) * 100, 1) if max_possible_score > 0 else 0
        }
        
        return render_template('admin/result_analytics.html',
                             quiz_name=quiz.name, entrance_name=entrance.name,
                             quiz_id=entrance.quiz_id, entrance_id=entrance_id,
                             total_students=total_students, statistics=statistics,
                             best_students=best_students, dangerous_students=dangerous_students,
                             score_distribution=list(zip(score_ranges, distribution)),
                             scores_data=scores)
    return redirect(url_for('admin_login'))

@app.route('/result_detailed/<entrance_id>')
def result_detailed(entrance_id):
    if session.get('admin', False):
        # Get search and sort parameters
        search_query = request.args.get('search', '').strip()
        sort_by = request.args.get('sort', 'date')  # default sort by date
        sort_order = request.args.get('order', 'desc')  # default descending

        results = []
        quiz_id = Entrance.query.filter_by(id=entrance_id).first().quiz_id
        quiz_name = Quiz.query.filter_by(id=quiz_id).first().name
        entrance_name = Entrance.query.filter_by(id=entrance_id).first().name

        # Base query
        query = Result.query.filter_by(entrance_id=entrance_id)

        # Apply search filter if provided
        if search_query:
            query = query.filter(Result.student_name.contains(search_query))

        # Apply sorting
        if sort_by == 'name':
            if sort_order == 'asc':
                query = query.order_by(Result.student_name.asc())
            else:
                query = query.order_by(Result.student_name.desc())
        elif sort_by == 'score':
            if sort_order == 'asc':
                query = query.order_by(Result.score.asc())
            else:
                query = query.order_by(Result.score.desc())
        else:  # sort by date (default)
            if sort_order == 'asc':
                query = query.order_by(Result.create_at.asc())
            else:
                query = query.order_by(Result.create_at.desc())

        # Get results
        for result in query.all():
            results.append(
                {'id': result.id, 'entrance_id': result.entrance_id, 'student_name': result.student_name,
                 'score': result.score, 'create_at': result.create_at})

        return render_template('admin/manage_result.html', results=results, quiz_id=quiz_id,
                             entrance_id=entrance_id, quiz_name=quiz_name, entrance_name=entrance_name,
                             search_query=search_query, sort_by=sort_by, sort_order=sort_order)
    return redirect(url_for('admin_login'))


@app.route('/result_download/<entrance_id>')
def result_download(entrance_id):
    if session.get('admin', False):
        wb = Workbook()
        ws = wb.active
        # 添加表头
        ws.append(['Name', 'Score'])
        # 添加数据
        for result in Result.query.filter_by(entrance_id=entrance_id).all():
            ws.append([result.student_name, result.score])
        # 保存工作簿到文件
        wb.save('tmp/Result.xlsx')
        return send_file('tmp/Result.xlsx', as_attachment=True)
    return redirect(url_for('admin_login'))

@app.route('/entrance_delete/<entrance_id>')
def entrance_delete(entrance_id):
    if session.get('admin', False):
        # delete related results
        for result in Result.query.filter_by(entrance_id=entrance_id).all():
            result_delete(result.id)
        entrance = Entrance.query.filter_by(id=entrance_id).first()
        db.session.delete(entrance)
        db.session.commit()
        return redirect(url_for('entrance_manage', quiz_id=entrance.quiz_id))
    return redirect(url_for('admin_login'))

@app.route('/result_delete/<result_id>')
def result_delete(result_id):
    if session.get('admin', False):
        result = Result.query.filter_by(id=result_id).first()
        db.session.delete(result)
        db.session.commit()
        return redirect(url_for('result_manage', entrance_id=result.entrance_id))
    return redirect(url_for('admin_login'))

@app.route('/quiz_create_visual', methods=['GET', 'POST'])
def quiz_create_visual():
    if session.get('admin', False):
        if request.method == 'POST':
            try:
                print("[DEBUG] Received POST request to create quiz")
                quiz_data = request.get_json()
                print(f"[DEBUG] Quiz data received: {quiz_data}")
                
                if not quiz_data:
                    print("[DEBUG] No data received")
                    return jsonify({'success': False, 'error': 'No data received'})
                
                # Create quiz JSON structure
                quiz_json = {
                    "title": quiz_data.get('title', ''),
                    "subtitle": quiz_data.get('subtitle', ''), 
                    "description": quiz_data.get('description', ''),
                    "points": str(quiz_data.get('points', '1')),
                    "image_folder": "img",
                    "questions": quiz_data.get('questions', [])
                }
                
                print(f"[DEBUG] Quiz JSON structure: {quiz_json}")
                
                # Save JSON file
                json_path = os.path.join('quiz/', str(uuid.uuid4())) + '.json'
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(quiz_json, f, ensure_ascii=False, indent=4)
                
                print(f"[DEBUG] Saved JSON to: {json_path}")
                
                # Save to database
                quiz_id = str(uuid.uuid4())
                quiz = Quiz(id=quiz_id, name=quiz_data.get('title', ''), description=quiz_data.get('description', ''), file_path=json_path)
                db.session.add(quiz)
                db.session.commit()
                
                print(f"[DEBUG] Saved to database with ID: {quiz_id}")
                
                return jsonify({'success': True, 'quiz_id': quiz.id})
            except Exception as e:
                print(f"[DEBUG] Error creating quiz: {str(e)}")
                return jsonify({'success': False, 'error': str(e)})
        
        return render_template('admin/visual_editor.html', mode='create')
    return redirect(url_for('admin_login'))

@app.route('/quiz_edit_visual/<quiz_id>')
def quiz_edit_visual(quiz_id):
    if session.get('admin', False):
        quiz = Quiz.query.filter_by(id=quiz_id).first()
        if quiz:
            with open(quiz.file_path, 'r', encoding='utf-8') as f:
                quiz_data = json.loads(f.read())
            return render_template('admin/visual_editor.html', mode='edit', quiz_id=quiz_id, quiz_data=quiz_data)
        return redirect(url_for('admin'))
    return redirect(url_for('admin_login'))

@app.route('/quiz_save_visual', methods=['POST'])
def quiz_save_visual():
    if session.get('admin', False):
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'success': False, 'error': 'No data received'})
                
            quiz_id = data.get('quiz_id')
            
            if quiz_id:  # Edit existing quiz
                quiz = Quiz.query.filter_by(id=quiz_id).first()
                if quiz:
                    # Update quiz JSON
                    quiz_json = {
                        "title": data.get('title', ''),
                        "subtitle": data.get('subtitle', ''),
                        "description": data.get('description', ''), 
                        "points": str(data.get('points', '1')),
                        "image_folder": "img",
                        "questions": data.get('questions', [])
                    }
                    
                    with open(quiz.file_path, 'w', encoding='utf-8') as f:
                        json.dump(quiz_json, f, ensure_ascii=False, indent=4)
                    
                    # Update database record
                    quiz.name = data.get('title', '')
                    quiz.description = data.get('description', '')
                    db.session.commit()
                    
                    return jsonify({'success': True})
                else:
                    return jsonify({'success': False, 'error': 'Quiz not found'})
            
            return jsonify({'success': False, 'error': 'Quiz ID not provided'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    return jsonify({'success': False, 'error': 'Unauthorized'})

@app.route('/upload_question_image', methods=['POST'])
def upload_question_image():
    if session.get('admin', False):
        try:
            if 'image' not in request.files:
                return jsonify({'success': False, 'error': 'No image file'})
            
            file = request.files['image']
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No file selected'})
            
            if file:
                # Generate unique filename
                file_extension = file.filename.rsplit('.', 1)[1].lower()
                filename = str(uuid.uuid4()) + '.' + file_extension
                file_path = os.path.join('img/', filename)
                file.save(file_path)
                
                return jsonify({'success': True, 'filename': filename})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    return jsonify({'success': False, 'error': 'Unauthorized'})

@app.route('/quiz_delete/<quiz_id>')
def quiz_delete(quiz_id):
    if session.get('admin', False):
        quiz = Quiz.query.filter_by(id=quiz_id).first()
        if quiz:
            # Delete related entrances and results
            for entrance in Entrance.query.filter_by(quiz_id=quiz_id).all():
                for result in Result.query.filter_by(entrance_id=entrance.id).all():
                    if os.path.exists(result.file_path):
                        os.remove(result.file_path)
                    db.session.delete(result)
                db.session.delete(entrance)
            
            # Delete quiz file
            if os.path.exists(quiz.file_path):
                os.remove(quiz.file_path)
            
            # Delete quiz record
            db.session.delete(quiz)
            db.session.commit()
        
        return redirect(url_for('admin'))
    return redirect(url_for('admin_login'))

# Health check endpoint for Docker
@app.route('/health')
def health_check():
    """Health check endpoint for container monitoring"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'message': 'Quiz system is running properly',
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'message': f'Health check failed: {str(e)}',
            'database': 'disconnected'
        }), 503

if __name__ == '__main__':
    app.run()
