import json
import os

from flask import Flask, render_template, redirect, request, url_for, session, send_from_directory, jsonify, send_file
from app import app, config

@app.route('/admin')
def admin():
    # if session.get('name') == 'admin':
        tests = []
        for quiz_name in os.listdir('data/quizs'):
            with open(f'data/quizs/{quiz_name}', 'r', encoding='utf-8') as f:
                quiz = json.loads(f.read())
                tests.append({'name': quiz_name[:-5], 'title': quiz['title'], 'subtitle': quiz['subtitle']})
        is_super = session['school'] == 'High School Affiliated to Nanjing Normal University'
        return render_template('admin/admin.html', tests=tests, is_super=is_super)
    # return redirect(url_for('admin_login'))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form['password']
        if password == config['admin password']:
            ...
            # return redirect(url_for('admin'))
    return render_template('admin/login.html')