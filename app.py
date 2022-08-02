from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

# 여기부터
import certifi

ca = certifi.where()

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.o3af5.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta
# 여기까지는 보안설정 때문에 필요!




@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route("/petlist", methods=["POST"])
def petinfo_post():

    file = request.files["file_give"]
    ownername_receive = request.form['ownername_give']
    phone_receive = request.form['phone_give']
    petname_receive = request.form['petname_give']
    petnum_receive = request.form['petnum_give']
    pettype_receive = request.form['pettype_give']
    breed_receive = request.form['breed_give']
    lostdate_receive = request.form['lostdate_give']
    losttime_receive = request.form['losttime_give']
    lostplace_receive = request.form['lostplace_give']
    state_receive = request.form['state_give']
    comment_receive = request.form['comment_give']

    extension = file.filename.split('.')[-1]
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
        'petnum' : petnum_receive,
        'pettype': pettype_receive,
        'breed' : breed_receive,
        'lostdate' : lostdate_receive,
        'losttime' : losttime_receive,
        'lostplace' : lostplace_receive,
        'state' : state_receive,
        'comment' : comment_receive
    }
    db.find_my_pet.insert_one(doc)

    return jsonify({'msg':'등록 완료!'})

@app.route("/petlist", methods=["GET"])
def petinfo_get():
    all_list = list(db.find_my_pet.find({}, {'_id': False}))
    return jsonify({'allinform':all_list})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
