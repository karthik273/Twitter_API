from flask import Flask, request, render_template, redirect, url_for, jsonify
from pymongo import MongoClient
import jwt,datetime, time

app = Flask(__name__)
client = MongoClient('localhost',27017)
db=client.twitter
#{"name":"qwert", "email":"qwe@qwe", "age":24, "password":"qwert", "confirm-password":"qwert"}
#{"username":"asdf@asdf","password":"asdf"}


@app.route('/',methods=['POST','GET'])
def create_account():
    if request.method == 'POST':
        name = request.json['name']
        email = request.json['email']
        age = request.json['age']
        password=request.json['password']
        con_password = request.json['confirm-password']
        if(password ==con_password):
            collection = db.user_login
            test_di = {}
            test_di['Name']=name
            test_di['Email'] = email
            test_di['Age'] = age
            test_di['Password'] = password
            collection.insert(test_di)
            print('FIrst step done')
            return redirect(url_for('login'))
        else:
            message="Password and Confirm Password don't match"
            #message = request.args.get("msg")
            return render_template("create_account.html",msg = message)

    else:
        return render_template('create_account.html',)

@app.route('/login',methods=['POST','GET'])
def login():
    collection = db.user_login
    if request.method == 'POST':
        '''
            if method is post then we send parameter from body. then we can extract data as shown below. when sending in postman
            we go to body, select raw format and keep all the values that you want to send as key:value pairs of a single dictionary.
            other method to retrieve data in this case is incom_Data = json.loads(request.data)
        '''
        username = request.json['username']
        passwordd = request.json['password']
        print('username is '+username+" password is "+passwordd)
        record = []
        record = collection.find_one({"$and": [{"Email": username}, {"Password": passwordd}]})
        if record == None:
            message = "Username and Password don't match"
            return render_template('login.html', msg=message)
        else:
            try:
                payload = {
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=86400),
                    'iat': datetime.datetime.utcnow(),
                    'sub': username
                }
                token_value = jwt.encode(payload,'hello secret',algorithm='HS256')
                return jsonify({"token":token_value})
            except Exception as e:
                return e
    else:
        return render_template('login.html')

def check(old):
    def new_f():
        token = request.headers['token']
        a = jwt.decode(token, "hello secret")
        if (a['exp'] < time.time()):
            return "YOu need to login agian"
        else:
            old()

@check
@app.route('/allTweets',methods=['GET'])
def get_tweets():

    args = request.headers['userid']
    #args=request.args['userid']   Use this if parameters are sent in URL than as in headers
    '''
    in get method there wont be any body. so we will pass parameters through header. so in postman we will go to headers tab and 
    add the key and value in the spaces below. to extract them we will do as shown in the above and below statements.
    '''
    print("args are ")
    print (args)
   # print (name)
    userid = int(args)
    collection = db.tweet_info
    #import pdb; pdb.set_trace()  #N to move to next step execution
    a = collection.find_one({"userid":userid})#{"userid":userid})["text"] #collection.find returns curson object. find_one give a dict
    #import pdb;pdb.set_trace()
    if a:
        print (a)
    else:
        print ("Nothing returned")
    b = dict(a)
    b.pop('_id')
    return jsonify({"tweets":b})

@check
@app.route('/likes',methods=['GET'])
def like_for_tweets():
    userid = request.headers['userid']
    tweetid = request.headers['tweetid']
    collection = db.tweet_info
    a = collection.find_one({"$and":[{"userid": int(userid)},{"tweetid":float(tweetid)}]})
    collection1 = db.user_profiles
    c = a['like']
    b=[]
    for i in c:
        print "i is ",i
        print collection1.find_one({"userid":i})['name']
        b.append(collection1.find_one({"userid":i})['name'])
    return jsonify({"Liked users":b})

@check
@app.route('/comments',methods=['GET'])
def comment_for_tweets():
    userid = request.headers['userid']
    tweetid = request.headers['tweetid']
    collection = db.tweet_info
    a = collection.find_one({"$and": [{"userid": int(userid)}, {"tweetid": float(tweetid)}]})
    print "a is ",a
    com={}
    x=[]
    for i in a["comment"]:
        com.update(i)
    for i in a:  #if find() is used to retrieve data from mongodb it returns cursor objects. we can convert it to a list of dict as shown beside
        if i == 'comment':
            x.append(a[i])#['comment'])
    print "x is ",x
    return jsonify({"Comments": com})

if __name__=='__main__':
    app.run()