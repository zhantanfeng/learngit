import json

from flask import Flask,render_template,request,jsonify
from flasgger import Swagger
from nameko.standalone.rpc import ClusterRpcProxy

app = Flask(__name__)
app.config['SECRET_KEY'] = "dfdfdffdad"
Swagger(app)
CONFIG = {'AMQP_URI': "amqp://guest:guest@localhost"}

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/compute',methods=['GET','POST'])
def compute():
    if request.method == 'POST':
        schoolName = request.form.get('schoolName')
        institutionName = request.form.get('institutionName')
    if institutionName:
        with ClusterRpcProxy(CONFIG) as rpc:
            institution_Id = rpc.test.get_institutionId(schoolName,institutionName)
            try:
                teacher_name = rpc.test.get_academicianName(institution_Id[0])
                for i in teacher_name:
                    i[0] = i[0].lstrip("['").rstrip("']")
                if len(teacher_name) == 0:
                    teacher_name = ["",""]
            except BaseException as e:
                teacher_name = ["",""]
            return render_template("outcome.html", teacher_name = teacher_name)
    else:
        with ClusterRpcProxy(CONFIG) as rpc:
            school_Id = rpc.test.get_schoolId(schoolName)
            try:
                teacher = rpc.test.get_teacher_name_and_insId(school_Id)
                for i in teacher:
                    institutionName = rpc.test.get_institution_name(i[1])
                    i[1] = institutionName[0].lstrip("['").rstrip("']")
                if len(teacher) == 0:
                    teacher = [["","",""]]
            except BaseException as e:
                teacher = [["","",""]]
            return render_template("outcome.html", teacher = teacher)


@app.route('/test',methods=['GET','POST'])
def test():
    with ClusterRpcProxy(CONFIG) as rpc:
        t = rpc.test.test()
        print(t)
    return render_template("a.html",t = t)

@app.route("/get_institutionNamebyschoolName",methods=['GET','POST'])
def get_institutionNamebyschoolName():
    username = request.get_data()
    if isinstance(username, bytes):
        username = str(username, encoding='utf-8')
    else:
        username = json.JSONEncoder.default(username)
    with ClusterRpcProxy(CONFIG) as rpc:
        name = rpc.test.get_institutionNamebyschoolName(username)
    name1 = []
    for i in name:
         name1.append(i[0].lstrip("['").rstrip("']"))
    return jsonify(name1)

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.run(host='0.0.0.0' ,debug=True)
