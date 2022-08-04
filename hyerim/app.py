import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

from pymongo import MongoClient
import certifi
ca = certifi.where()

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('mongodb+srv://test:sparta@cluster0.o3af5.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta_week1_teamproject


@app.route('/')
def home():
    all_list = list(db.find_my_pet.find({}, {'_id': False}))
    token_receive = request.cookies.get('mytoken')

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 페이로드에서 id를 꺼내서 어떤 유저가 로그인했는지 알아서 유저의 정보를 읽어옴
        user_info = db.users.find_one({"username": payload["id"]})
        # 읽어온 실제 유저의 정보를 클라이언트에 던져줌
        # 이 줄을 추가함으로써 index.html에서 유저의 정보를 마음껏 진자템플릿을 이용해서 사용할 수 있음
        return render_template('index.html', user_info=user_info, allinforms=all_list)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))




@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')  # .decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "profile_name": username_receive,  # 프로필 이름 기본값은 아이디
        "profile_pic": "",  # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png",  # 프로필 사진 기본 이미지
        "profile_info": ""  # 프로필 한 마디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route("/get_posts", methods=['GET'])
def get_posts():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username_receive = request.args.get("username_give")
        if username_receive == "":
            posts = list(db.posts.find({}).sort("date", -1).limit(20))
        else:
            posts = list(db.posts.find({"username": username_receive}).sort("date", -1).limit(20))
        for post in posts:
            post["_id"] = str(post["_id"])
            post["count_heart"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"})
            post["heart_by_me"] = bool(
                db.likes.find_one({"post_id": post["_id"], "type": "heart", "username": payload['id']}))
        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "posts": posts})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))



@app.route("/api/save_petinfo", methods=["POST"])
def petinfo_post():
    # 반려동물 실종정보 등록하기
    phone_receive = request.form['phone_give']
    ownername_receive = request.form['ownername_give']
    petname_receive = request.form['petname_give']
    lostdate_receive = request.form['lostdate_give']
    losttime_receive = request.form['losttime_give']
    lostplace_receive = request.form['lostplace_give']
    comment_receive = request.form['comment_give']

    all_list = list(db.find_my_pet.find({}, {'_id': False}).distinct('register_num'))
    if len(all_list) == 0:
        count = 1
    else:
        count = max(all_list) + 1

    file = request.files["file_give"]
    # 확장자명 분리
    extension = file.filename.split('.')[-1]

    # 파일명에 시간 추가
    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
    filename = f'file-{mytime}' + str(count)

    save_to = f'static/{filename}.{extension}'
    file.save(save_to)

    doc = {
        'register_num': count,
        'file': f'{filename}.{extension}',
        'ownername': ownername_receive,
        'phone': phone_receive,
        'petname': petname_receive,
        'lostdate': lostdate_receive,
        'losttime': losttime_receive,
        'lostplace': lostplace_receive,
        'comment': comment_receive,
    }

    db.find_my_pet.insert_one(doc)

    return jsonify({'msg': '정보 등록 완료!'})


@app.route("/petlist", methods=["GET"])
def petinfo_get():
    all_list = list(db.find_my_pet.find({}, {'_id': False}))
    return jsonify({'allinform' : all_list})


@app.route('/detail/', methods=["GET"])
def detail_show():
    pet_list = list(db.find_my_pet.find({}, {'_id': False}))
    return jsonify({'pets': pet_list})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)