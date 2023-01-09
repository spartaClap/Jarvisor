from flask import Flask, render_template, request, jsonify, redirect, url_for
app = Flask(__name__)

from pymongo import MongoClient
import pymongo
import certifi

import hashlib
import datetime
from datetime import datetime as dt
import jwt

ca = certifi.where()


db = client.dbsparta



# JWT 토큰을 만들 때 필요한 비밀문자열입니다. 아무거나 입력해도 괜찮습니다.
# 이 문자열은 서버만 알고있기 때문에, 내 서버에서만 토큰을 인코딩(=만들기)/디코딩(=풀기) 할 수 있습니다.
SECRET_KEY = 'SPARTA'

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        return render_template('indexIndex.html', nickname=user_info["id"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/register')
def register():
   return render_template('register.html')


@app.route('/login')
def login():
   return render_template('loginIndex.html')


@app.route('/differ')
def differ():
   return render_template('differ.html')

############################################

@app.route('/canvas1')
def canvas1():
   return render_template('canvas1.html')


@app.route('/canvas2')
def canvas2():
   return render_template('canvas2.html')


@app.route('/canvas3')
def canvas4():
   return render_template('canvas3.html')




@app.route("/bstorming", methods=["POST"])
def bstorming_post():
    storming_list = list(db.bstorming.find({"unique":unique}, {'_id': False}))

    no = len(storming_list)+1
    print(no)
    name_receive = request.form['name_give']
    summary_receive = request.form['summary_give']
    comment_receive = request.form['comment_give']
    doc = {
        'no' : no,
        'name' : name_receive,
        'summary' : summary_receive,
        'comment' : comment_receive,
        'unique' : unique
    }
    db.bstorming.insert_one(doc)

    return jsonify({'msg': '등록 완료!'})

@app.route("/bstorming", methods=["GET"])
def bstorming_get():
    contents_list = list(db.bstorming.find({"unique":unique}, {'_id': False}))
    return jsonify({'contents':contents_list})



@app.route("/planner", methods=["POST"])
def plan_post():
    plan_list = list(db.planner.find({"unique":unique}, {'_id': False}))

    if plan_list == []:
        no = 1
    else:
        no = plan_list[-1]['no']+1

    print(no)
    name_receive = request.form['name_give']
    s_day_receive = request.form['s_day_give']
    f_day_receive = request.form['f_day_give']
    comment_receive = request.form['comment_give']

    if f_day_receive < s_day_receive:
        return jsonify({'msg': '시작날짜는 종료날짜보다 빨라야 합니다.'})

    doc = {
        'no' : no,
        'name' : name_receive,
        's_day' : s_day_receive,
        'f_day' : f_day_receive,
        'comment' : comment_receive,
        'unique' : unique
    }
    db.planner.insert_one(doc)
    print(doc)
    return jsonify({'msg': '등록 완료!'})


@app.route("/planner", methods=["PUT"])
def plan_put():
    no_receive = request.form['no_give']
    print(no_receive)
    name_receive = request.form['name_give']
    s_day_receive = request.form['s_day_give']
    f_day_receive = request.form['f_day_give']
    comment_receive = request.form['comment_give']

    if f_day_receive < s_day_receive:
        return jsonify({'msg': '시작날짜는 종료날짜보다 빨라야 합니다.'})

    doc = {
        'name' : name_receive,
        's_day' : s_day_receive,
        'f_day' : f_day_receive,
        'comment' : comment_receive
    }
    db.planner.update_one({'no':int(no_receive), 'unique':unique},{"$set":doc})
    print(doc)
    return jsonify({'msg': '수정 완료!'})



@app.route("/planner", methods=["GET"])
def plan_get():
    plans_list = list(db.planner.find({"unique":unique}, {'_id': False}))
    print(plans_list)

    # D-day 계산
    format = '%Y-%m-%d'
    d_days = []
    for i in range(len(plans_list)):
        f_day = plans_list[i]['f_day']
        if f_day != '':
            dt = datetime.datetime.strptime(f_day, format).date()
            d_days.append((dt-dt.today()).days)
        else:
            d_days.append('null')                
    return jsonify({'plans':plans_list, 'd_days':d_days})


@app.route("/planner", methods=["DELETE"])
def plan_delete():
    no_receive = request.form['no_give']
    print(no_receive)

    db.planner.delete_one({'no':int(no_receive), 'unique':unique})
    return jsonify({'msg': '삭제 완료!'})

@app.route("/idea", methods=["POST"])
def idea_post():
    name_receive = request.form['name_give']
    comment_receive = request.form['comment_give']
    doc = {
        'name' : name_receive,
        'comment' : comment_receive,
        'unique' : unique
    }
    db.idea.insert_one(doc)

    return jsonify({'msg': '등록 완료!'})




@app.route("/idea", methods=["GET"])
def idea_get():

    idea_list = list(db.idea.find({"unique":unique}, {'_id': False}))
    return jsonify({'ideas':idea_list})





#########################[회원가입 API]############################## 


### ID 중복 체크
@app.route('/idcheck', methods=['POST'])
def idcheck():
    id_receive = request.form['id_give']
    print(id_receive)

    aa = db.user.find_one({'id': id_receive}, {'_id': False})
    print(aa)
    if aa is not None:
        print('동일한 ID가 존재합니다. 다른 ID를 입력해주세요.')
        return jsonify({'msg': '동일한 ID가 존재합니다. 다른 ID를 입력해주세요.'})
    else:
        print('사용 가능한 ID입니다.')
        return jsonify({'msg': '사용 가능한 ID입니다.'})



# id, pw을 받아서, mongoDB에 저장합니다.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@app.route('/register', methods=['POST'])
def api_register():
    name_receive = request.form['name_give']
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    pw2_receive = request.form['pw2_give']

    aa = db.user.find_one({'id': id_receive})
    if aa is not None:
        print(aa)
        print('동일한 ID가 존재합니다. 다른 ID를 입력해주세요.')
        return jsonify({'result': 'fail', 'msg': '동일한 ID가 존재합니다. 다른 ID를 입력해주세요.'})

    elif pw_receive != pw2_receive:
        print('비밀번호가 일치하지 않습니다. 다시 확인해주세요.')
        return jsonify({'result': 'fail', 'msg': '비밀번호가 일치하지 않습니다. 다시 확인해주세요.'})

    else:
        print(id_receive)
        pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
        doc = {
            'name' : name_receive,
            'id' : id_receive,
            'pw' : pw_hash,
        }
        db.user.insert_one(doc)

        return jsonify({'result': 'success', 'msg': '회원가입이 완료 되었습니다! 로그인 페이지로 이동합니다.'})


# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    if (id_receive=='') or (pw_receive==''):
        return jsonify({'result': 'fail', 'msg': '아이디,패스워드를 입력하세요.'})
    
    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})
   

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요합니다.
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
        # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
        # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=5)    #언제까지 유효한지
        }
        #jwt를 암호화
        # token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        

        # 모든 문서를 불러오는 고유 Primary key는 id로 설정
        global unique
        unique = id_receive
        print(unique)

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})



if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)

