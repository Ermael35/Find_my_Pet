from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

# 여기부터
import certifi
ca = certifi.where()

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.o3af5.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta_week1_project
# 여기까지는 보안설정 때문에 필요!

from datetime import datetime


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

# 단일객체 렌더링
# @app.route('/ObjectView/<num>')
# def view(num):
#     token_receive = request.cookies.get('mytoken')
#     try:
#         # 쿠키에 있는 유저의 정보를 읽어옴
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#
#         # 읽어온 유저의 id를 통해서 db에서 나머지 정보 찾기
#         user_info = db.users.find_one({"username": payload["id"]})
#
#         # board db에서 해당 num값에 해당하는 dic 찾아오기
#         post = db.board.find_one({'num': num}, {'_id': False})
#
#         # 쿠키에 있는 유저의 아이디와 board에 있는 게시물의 id가 같으면 Ture
#         status = post["nickname"] == user_info['nickname']
#
#         heart = {
#             "count_heart": db.likes.count_documents({"num": num}),
#             "heart_by_me": bool(db.likes.find_one({"num": num, "username": user_info["username"]}))
#         }
#
#         return render_template('ObjectView.html', user_info=user_info, post=post, num=num, status=status, heart=heart)
#
#     except jwt.ExpiredSignatureError:
#         return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
#     except jwt.exceptions.DecodeError:
#         return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route("/api/save_petinfo", methods=["POST"])
def petinfo_post():
    # 현재 시간을 primary 키 값으로 설정
    # num = request.form['num_give']
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


# @app.route("/api/re_petinfo", methods=['POST'])
# def delete_word():
#     # 단어 삭제하기
#     #     단어를 삭제하기 위해서는 단어만 있으면 되니까 뜻은 받을 필요 없음
#     word_receive = request.form["word_give"]
#     db.words.delete_one({'word': word_receive})
#     return jsonify({'result': 'success', 'msg': f'단어 {word_receive} 삭제'})


@app.route("/petlist", methods=["GET"])
def petinfo_get():
    all_list = list(db.find_my_pet.find({}, {'_id': False}))
    return jsonify({'allinform':all_list})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
