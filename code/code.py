
# coding: utf-8

# In[1]:


#製作flask環境
from flask import Flask, request, jsonify
import datetime
import pymysql


#呼叫出Flask
app = Flask(__name__)

#建立與mysql的連線
conn = pymysql.connect(host='db', port=3306, user='root', passwd='iii', db='chatbot_db',charset='utf8mb4')

#方便用來跟mysql互動
cur = conn.cursor()


# In[2]:


#接口功能：新增使用者
#接口位置：/users，使用post的http method
@app.route('/users',methods=['POST'])
def add_user():
    #抓跑function時的時間
    time = datetime.datetime.utcnow().strftime("%Y%m%d%H%M")
    #將傳過來的json檔擷取出來
    a = request.get_json()
    #方便錯誤排除
    error = None
    #對ststus跟img還沒啥想法先不設定
    
    if not a['user_register_menu']:
        #對menu完全沒想法先填一
        a['user_register_menu'] = 1
        
    if not a['user_open_id']:
        #id沒填的話改變顯示的錯誤訊息
        error = 'Userid is required.'
    elif not a['user_nick_name']:
        #name沒填的話改變顯示的錯誤訊息
        error = 'Username is required.'
        
    #看看資料庫內是否有重複的id
    cur.execute('SELECT user_open_id FROM chatbot_db.users WHERE user_open_id = ("%s")' % (a['user_open_id']))
    test = cur.fetchone() 
    if test:
        #有重複的話改變顯示的錯誤訊息
        error = 'User {} is already registered.'.format(a['user_open_id'])
    
    #沒有錯誤的話，將資料新增進資料庫
    if error is None:
        #插入資料庫中
        insertsql=("INSERT INTO chatbot_db.users VALUES ( %s,%s,%s,%s,%s,%s )") 
        value = (a['user_open_id'],a['user_nick_name'],a['user_status'],a['user_img'],time,a['user_register_menu'])
        cur.execute(insertsql , value)
        #將資料送進資料庫中
        conn.commit()
        #回傳一個正確的描述
        result =  { "status_describe":"success add user" }
        return jsonify(result)
    
    
    #回傳一個錯誤的描述
    result = {"status_describe":"{}".format(error)}
    
    return jsonify(result)


# In[3]:


#接口功能：檢視單一使用者
#接口位置：/users/<userid>，運用了url parameter，使用get的http method
@app.route('/users/<userid>',methods=['GET'])
#特別注意這邊有打userid，url parameter就是這樣使用
def read_user(userid):
    #找出資料庫符合userid的資料
    cur.execute(
        'SELECT * FROM chatbot_db.users WHERE user_open_id = ("%s")' % (userid)
        )
    #將剛剛execute的資料取出來
    user = cur.fetchone()
    #假如有找到符合的資料
    if user is not None:
        user = {
            "user_open_id":user[0],
            "user_nick_name":user[1],
            "user_status" : user[2],
            "user_img" : user[3],
            "user_register_date" : user[4],
            "user_register_menu" : user[5]
        }
        #轉成line要的json格式
        return jsonify(user)
    #假如沒有找到符合的資料
    else:
        result = {
            "status_describe":"Please enter the right id!!"
        }
        return jsonify(result)


# In[4]:


#接口功能：檢視所有使用者
#接口位置：/users，使用get的http method
@app.route('/users',methods=['GET'])
def read_users():
    #找出資料庫內的所有user資料
    cur.execute(
        'SELECT * FROM chatbot_db.users'
        )
    #由於是多筆，使用fetchall
    user = cur.fetchall()
    #假如一個user都沒
    if not user:
        answer = {
          "status_describe":"query string is incompatible"
        }
    else:
        #裝成矩陣格式
        answer = []
        for i in user:
            result = {
                "user_open_id":i[0],
                "user_nick_name":i[1],
                "user_status" : i[2],
                "user_img" : i[3],
                "user_register_date" : i[4],
                "user_register_menu" : i[5]
            }
            answer.append(result)
    
        
    #轉成json格式
    return jsonify(answer)


# In[5]:


#接口功能：更新使用者
#接口位置：/users/<userid>，使用put的http method
@app.route('/users/<userid>',methods=['PUT'])
def update_user(userid):
    #取出傳過來的資料
    a = request.get_json()
    #方便錯誤排除
    error = None
    
    #看看資料庫內是否有重複的id
    cur.execute('SELECT user_open_id FROM chatbot_db.users WHERE user_open_id = ("%s")' % (userid))
    test = cur.fetchone()
    #沒有重複的話
    if not test:
        error = 'Please enter the right id.'
    #沒有nick_name的話
    elif not a['user_nick_name']:
        #name沒填的話改變顯示的錯誤訊息
        error = 'Username is required.'
    #img沒填的話
    elif not a['user_img']:
        error = 'Where is your picture?'
    #menu沒填的話
    elif not a['user_register_menu']:
        #對menu完全沒想法先填一
        a['user_register_menu'] = 1

    #沒有錯誤的話，將資料更新進資料庫
    if error is None:
        #更新資料庫
        insertsql=('UPDATE chatbot_db.users SET user_nick_name=("%s"),user_status=("%s"),user_img=("%s"),user_register_menu=("%s") WHERE user_open_id=("%s")') % (a['user_nick_name'],a['user_status'],a['user_img'],a['user_register_menu'],userid)
        cur.execute(insertsql)
        conn.commit()
        #回傳一個正確的描述
        result =  { "status_describe":"success update user" }
        return jsonify(result)
    
    
    #回傳一個錯誤的描述
    result = {"status_describe":"{}".format(error)}
    
    return jsonify(result)


# In[6]:


#接口功能：新增menu資料
#接口位置：/menu，使用post的http method
@app.route('/menu',methods=['POST'])
def add_menu():
    #擷取出傳過來的json格式
    a = request.get_json()
    #方便書寫錯誤格式
    error = None
        
    if not a['menu_id']:
        #id沒填的話改變顯示的錯誤訊息
        error = 'Id is required!!'
    elif not a['menu_content']:
        #content沒填的話改變顯示的錯誤訊息
        error = 'Content is required!!'
    
    #看有沒有重複的id
    cur.execute('SELECT menu_id FROM chatbot_db.menus WHERE menu_id = ("%s")' % (a['menu_id']))
    #擷取出execute的資料
    test = cur.fetchone()
    #有重複的話
    if test:
        error = 'Menu {} is already registered.'.format(a['menu_id'])
    
    #沒有錯誤的話
    if error is None:
        #插入資料
        insertsql=("INSERT INTO chatbot_db.menus VALUES ( %s,%s)") 
        value = (a['menu_id'],a['menu_content'])
        cur.execute(insertsql , value)
        #將資料送進資料庫中
        conn.commit()
        #回傳成功訊息
        result =  { "status_describe":"success add menu" }
        #轉檔
        return jsonify(result)
    
    
    #書寫錯誤訊息
    result = {"status_describe":"{}".format(error)}
    #轉檔
    return jsonify(result)
    
    


# In[7]:


#接口功能：檢視question sa的資料
#接口位置：/question/sa，使用get的http method
@app.route('/question/sa',methods=['GET'])
def test_sa():
    #使用了query string的方法，擷取出變數值
    question = request.args.get('question_id')
    #方便書寫錯誤的訊息
    error = None
    #假如沒收到變數
    if question is None:
        error = 'Please enter the question_id.'
    
    #看有沒有重複的資料
    cur.execute('SELECT question_id FROM chatbot_db.assoc_sa_questions WHERE question_id = ("%s")' % (question))
    #擷取execute的資料
    test = cur.fetchone()
    #假如沒有重複的
    if not test:
        error = 'Please enter the right question_id'
    
    #假如沒有出錯
    if error is None:
        #抓出符合id的資料
        readsql=('SELECT * FROM chatbot_db.assoc_sa_questions WHERE question_id=("%s")' % (question))
        cur.execute(readsql)
        result=cur.fetchone()
        result = {
          "question_id":result[0],
          "question_content":result[1],
          "answer1_content":result[2],
          "answer2_content":result[3],
          "answer3_content":result[4],
          "answer4_content":result[5],
          "true_answer":result[6],
          "true_answer_decribe_content" : result[7],
          "external_link": result[8]
        }
        
        
        return jsonify(result)
    
    #書寫錯誤的訊息
    result = {"status_describe":"{}".format(error)}
    
    return jsonify(result)
    


# In[8]:


@app.route('/question/sysops',methods=['GET'])
def test_sys():
    question = request.args.get('question_id')
    error = None
    if question is None:
        error = 'Please enter the question_id.'
    
    cur.execute('SELECT question_id FROM chatbot_db.assoc_sys_questions WHERE question_id = ("%s")' % (question))
    test = cur.fetchone()
    if not test:
        error = 'Please enter the right question_id'
    
    if error is None:
        readsql=('SELECT * FROM chatbot_db.assoc_sys_questions WHERE question_id=("%s")' % (question))
        cur.execute(readsql)
        result=cur.fetchone()
        result = {
          "question_id":result[0],
          "question_content":result[1],
          "answer1_content":result[2],
          "answer2_content":result[3],
          "answer3_content":result[4],
          "answer4_content":result[5],
          "true_answer":result[6],
          "true_answer_decribe_content" : result[7],
          "external_link": result[8]
        }
        
        
        return jsonify(result)
    
    
    result = {"status_describe":"{}".format(error)}
    
    return jsonify(result)


# In[9]:


@app.route('/question/devlop',methods=['GET'])
def test_dev():
    question = request.args.get('question_id')
    error = None
    if question is None:
        error = 'Please enter the question_id.'
    
    cur.execute('SELECT question_id FROM chatbot_db.assoc_dev_questions WHERE question_id = ("%s")' % (question))
    test = cur.fetchone()
    if not test:
        error = 'Please enter the right question_id'
    
    if error is None:
        readsql=('SELECT * FROM chatbot_db.assoc_dev_questions WHERE question_id=("%s")' % (question))
        cur.execute(readsql)
        result=cur.fetchone()
        result = {
          "question_id":result[0],
          "question_content":result[1],
          "answer1_content":result[2],
          "answer2_content":result[3],
          "answer3_content":result[4],
          "answer4_content":result[5],
          "true_answer":result[6],
          "true_answer_decribe_content" : result[7],
          "external_link": result[8]
        }
        
        
        return jsonify(result)
    
    
    result = {"status_describe":"{}".format(error)}
    
    return jsonify(result)


# In[10]:


import logging
from logging.handlers import TimedRotatingFileHandler

def log():
    #請你給我一個 Log 的分身，他的名字叫做.... __name__ (function 的名稱)！！
    logger = logging.getLogger( __name__ )
    #設定這個檔案要處理的情報等級，只要是 info 等級或以上的就寫入檔案
    logger.setLevel(logging.INFO)
    #關於 log 將要輸出的檔案，請你按照下面的設定logging.FileHandler(檔名,動作,格式)
    fh = logging.FileHandler(datetime.datetime.utcnow().strftime("%Y%m%d")+'.log', 'w', 'utf-8')
    #設定這個檔案要處理的情報等級，只要是 debug 等級或以上的就寫入檔案
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    #關於 console(也就是cmd 那個黑黑的畫面)，請你按照下面的設定，幫我處理一下
    ch = logging.StreamHandler()
    #設定 Console 要處理的情報等級，只要是 Info 等級的就印出來
    ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    # log 印出來的格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #將 印出來的格式和 File Handle, Console Handle 物件組合在一起
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    #加上這個!!!!!每天深夜換檔案，檔名就使用日期.log
    logHandler = TimedRotatingFileHandler(datetime.datetime.utcnow().strftime("%Y%m%d")+".log",when="midnight")
    #log 的分身組合 File Handle 和 Console Handle 和 logHandler
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.addHandler(logHandler) 


# In[ ]:


#__name__ == __main__ 代表你執行這個模塊（py檔）時會成立
#假如你是被別的檔案import的話，__name__ == 檔案名稱，這個if就不會成立
if __name__=='__main__':
    #運行log
    log()
    #運行flask server，運行在0.0.0.0:5000
    #要特別注意假如運行在127.0.0.1的話，會變成只有本機連的到，外網無法
    app.run(host='0.0.0.0',port=5000)


# In[ ]:


#做一個測試接口，接口位置在/hello，使用GET的http method
@app.route('/hello',methods=['GET'])
def hello():
    a = 'Hello , World!!'
    return a

