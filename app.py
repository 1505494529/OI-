from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash, abort
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def load_users():
    users = {}
    with open('users.txt', 'r') as f:
        for line in f:
            username, password = line.strip().split(':')
            users[username] = password
    return users

def load_titles():
    titles = []
    with open('titles.txt', 'r') as f:
        titles = [line.strip() for line in f]
    return titles

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('upload'))
    return redirect(url_for('login'))

import os
from datetime import datetime

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        password = request.form['password']
        users = load_users()

        if username not in users:
            flash("用户名不存在", "error")
        elif users[username] != password:
            flash("密码错误", "error")
        else:
            session['username'] = username
            
            # 获取当前日期并格式化为字符串
            date_str = datetime.now().strftime("%Y-%m-%d")
            folder_name = 'signins'  # 文件夹名称
            file_name = os.path.join(folder_name, f"{date_str}.txt")

            # 确保文件夹存在
            os.makedirs(folder_name, exist_ok=True)

            # 将签到信息写入文件
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

    expected_files = {title: title for title in titles}  # 这里可以根据需要修改

    if request.method == 'POST':
        files = request.files.getlist('files')  # 获取所有上传的文件
        if not any(file for file in files):  # 检查是否上传了文件
            flash("未上传任何文件", "error")
            return redirect(url_for('upload'))

        # 验证文件名和位置
        for file in files:
            if file and file.filename:  # 确保文件有效且文件名非空
                if file.filename not in expected_files:
                    flash(f"{file.filename} 不匹配题目", "error")
                    return redirect(url_for('upload'))

        # 保存文件
        os.makedirs(user_folder, exist_ok=True)
        for file in files:
            if file and file.filename:  # 确保文件有效
                file.save(os.path.join(user_folder, file.filename))  # 覆盖同名文件

        return redirect(url_for('upload'))

    file_status = [(title, '已上传' if title in uploaded_files else '待上传') for title in titles]

    return render_template('upload.html', download_files=download_files, file_status=file_status, uploaded_files=uploaded_files)

@app.route('/downloads/<path:filename>')
def download_file(filename):
    return send_from_directory('downloads', filename)

@app.route('/uploads/<username>/<filename>')
def download_uploaded_file(username, filename):
    if username != session['username']:
        abort(403)  # 返回403 Forbidden错误
    return send_from_directory(os.path.join('uploads', username), filename)


if __name__ == '__main__':
    app.run('0.0.0.0',80)
