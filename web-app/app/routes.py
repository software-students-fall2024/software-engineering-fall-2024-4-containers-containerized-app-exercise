from flask import render_template, request, redirect, url_for
from app import app
from app.models import Database
from datetime import datetime

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    db = Database()
    result = None
    history = []
    
    if request.method == 'POST':
        if 'image' in request.files:
            # 这里后续需要添加图片处理和情绪检测的逻辑
            pass
    
    # 获取历史记录
    history = db.get_latest_results()
    
    return render_template('dashboard.html', result=result, history=history)
