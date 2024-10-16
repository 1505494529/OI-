from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash, abort
from threading import Lock
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'xujiawei05@corp.netease.com'
file_lock = Lock()

# 加载用户数据
def load_users():
    with open('users.txt') as f:
        return dict(line.strip().split(':') for line in f)

# 加载标题数据
def load_titles():
    with open('titles.txt') as f:
        return [line.strip() for line in f]
    
@app.before_request
def require_login():
    # 如果用户未登录，且访问的页面不是登录页面或静态文件
    if 'username' not in session and request.endpoint not in ['login', 'static']:
        return redirect(url_for('login'))    

@app.route('/')
def index():
    return redirect(url_for('upload') if 'username' in session else url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username, name, password = request.form['username'], request.form['name'], request.form['password']
        users = load_users()

        if username not in users or users[username] != password:
            flash("用户名或密码错误", "error")
        else:
            session['username'] = username

            # 保存签到信息
            date_str = datetime.now().strftime("%Y-%m-%d")
            file_name = os.path.join('signins', f"{date_str}.txt")
            os.makedirs('signins', exist_ok=True)

            with file_lock:
                with open(file_name, 'a') as f:
                    f.write(f"{username} {name} {datetime.now().strftime('%H:%M:%S')}\n")

            return redirect(url_for('upload'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))

    titles = load_titles()
    user_folder = os.path.join('uploads', session['username'])
    uploaded_files = os.listdir(user_folder) if os.path.exists(user_folder) else []
    download_files = os.listdir('downloads')
    file_status = [(title, '已上传' if title in uploaded_files else '待上传') for title in titles]

    return render_template('upload.html', download_files=download_files, file_status=file_status, uploaded_files=uploaded_files)

@app.route('/downloads/<path:filename>')
def download_file(filename):
    return send_from_directory('downloads', filename)

@app.route('/download_uploaded_file/<filename>')
def download_uploaded_file(filename):
    username = session.get('username')
    file_path = os.path.join('uploads', username, filename)
    if not os.path.exists(file_path):
        abort(404)

    with open(file_path) as file:
        file_content = file.read()

    return render_template('view.html', code=file_content, title=filename)

@app.route('/upload_file/<filename>')
def upload_file(filename):
    username = session.get('username')
    file_path = os.path.join('uploads', username, filename)
    file_content = ''
    if os.path.exists(file_path):
        with open(file_path) as file:
            file_content = file.read()

    return render_template('upload_file.html', code=file_content, username=username, title=filename)

@app.route('/upload_code', methods=['POST'])
def upload_code():
    data = request.get_json()
    code = data.get('code')
    file_name = data.get('file_name')

    if not code or not file_name:
        flash("未提交任何代码或文件名", "error")
        return redirect(url_for('upload'))

    user_folder = os.path.join('uploads', session['username'])
    os.makedirs(user_folder, exist_ok=True)

    with open(os.path.join(user_folder, file_name), 'w') as file:
        file.write(code)

    return redirect(url_for('upload'))

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    app.run('0.0.0.0', 80)
