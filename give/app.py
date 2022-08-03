from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

import certifi
ca = certifi.where()
from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.o3af5.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta_week1_project

from datetime import datetime


@app.route('/')
def home():
    petinforms = list(db.find_my_pet.find({}, {"_id": False}))
    return render_template('index.html', petinforms=petinforms)


@app.route('/register')
def register():
    return render_template('register.html')


@app.route("/api/save_petinfo", methods=["POST"])
def petinfo_post():
    # 반려동물 실종정보 등록하기
    ownername_receive = request.form['ownername_give']
    phone_receive = request.form['phone_give']
    petname_receive = request.form['petname_give']
    lostdate_receive = request.form['lostdate_give']
    losttime_receive = request.form['losttime_give']
    lostplace_receive = request.form['lostplace_give']
    comment_receive = request.form['comment_give']

    file = request.files["file_give"]
    # 확장자명 분리
    extension = file.filename.split('.')[-1]
    # 파일명에 시간 추가
    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
    filename = f'file-{mytime}'

    save_to = f'static/{filename}.{extension}'
    file.save(save_to)

    doc = {
        'file': f'{filename}.{extension}',
        'ownername': ownername_receive,
        'phone' : phone_receive,
        'petname' : petname_receive,
        'lostdate' : lostdate_receive,
        'losttime' : losttime_receive,
        'lostplace': lostplace_receive,
        'comment' : comment_receive
    }
    db.find_my_pet.insert_one(doc)
    return jsonify({'msg': '정보 등록 완료!'})


@app.route("/petlist", methods=["GET"])
def petinfo_get():
    all_list = list(db.find_my_pet.find({}, {'_id': False}))
    return jsonify({'allinform':all_list})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
