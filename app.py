from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import datetime

app = Flask(__name__)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('timeline.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home route
@app.route('/')
def index():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)

# Add task route
@app.route('/add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        task = request.form['task']
        task_description = request.form['task_description']
        subtask = request.form['subtask']
        subtask_description = request.form['subtask_description']
        date = request.form['date']
        priority = request.form['priority']
        weight = request.form['weight']

        conn = get_db_connection()
        conn.execute('INSERT INTO tasks (date, task, task_description, subtask, subtask_description, priority, weight) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (date, task, task_description, subtask, subtask_description, priority, weight))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('add.html')

# Remove task route
@app.route('/remove/<int:id>')
def remove(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Search tasks route
@app.route('/search', methods=('GET', 'POST'))
def search():
    keyword = request.form.get('keyword', '')
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks WHERE task LIKE ? OR task_description LIKE ? OR subtask LIKE ? OR subtask_description LIKE ?',
                         ('%' + keyword + '%', '%' + keyword + '%', '%' + keyword + '%', '%' + keyword + '%')).fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)

if __name__ == '__main__':
    app.run(debug=True)
