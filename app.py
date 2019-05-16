import json
from flask import Flask, render_template, request, jsonify, flash, session
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
            institution_Id = rpc.test.get_institutionId(schoolName, institutionName)
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

@app.route("/team",methods=['GET','POST'])
def team():
    import time
    if request.method == 'POST':
        schoolName = request.form.get('schoolName')
        institutionName = request.form.get('institutionName')
    with ClusterRpcProxy(CONFIG) as rpc:
        try:
            institutionId = rpc.document.get_institutionId(schoolName,institutionName)
        except BaseException as e:
            return render_template("error.html")
        maindis = rpc.document.get_maindis(institutionId)
        # print(maindis)
    for i in maindis:
        try:
            with ClusterRpcProxy(CONFIG) as rpc:
                discipline_name = rpc.document.get_discipline(int(i[0]))
                i[0] = discipline_name
        except:
            pass
    # print(maindis)
    with ClusterRpcProxy(CONFIG) as rpc:
        mainlab = rpc.document.get_lab(schoolName,institutionName)
    # print(mainlab)

    #TODO 处理院系老师之间的关系
    with ClusterRpcProxy(CONFIG) as rpc:
        teacher = rpc.document.get_teacher_info(institutionId)
    teacherlist = []
    for i in teacher:
        teacherlist.append(i[1])
    projectlist = []

    with ClusterRpcProxy(CONFIG) as rpc:
        project = rpc.document.get_project(schoolName)
    for i in project:
        if i[0] in teacherlist:
            projectlist.append(i)
    projectlist.sort(key=lambda ele: ele[2], reverse=True)
    # print(projectlist)

    if len(projectlist) != 0:
        project_name = []
        for i in projectlist:
            project_name.append(i[1])
        headname = projectlist[0][0]
        with ClusterRpcProxy(CONFIG) as rpc:
            head_id = rpc.document.get_teacher_id(headname, institutionId)
            paper = rpc.document.get_paper_info_2(head_id[0])
            honor = rpc.document.get_honor_2(head_id[0])
        #print(head_id[0])
        papername = []
        paperauthor = []
        member = []
        # print(paper)
        for i in paper:
            papername.append(i[1])
            paperauthor.append(i[0])
        # print(papername)
        # print(paperauthor)
        for i in paperauthor:
            a = i.lstrip("[").rstrip("]").strip("{").split(",")
            for i in a:
                if i.strip("{")[1:5] == "name":
                    member.append(i[i.index(":") + 2:len(i) - 1])
        member = list(set(member))
        # print(member)
        academician = []
        outyouth = []
        changjiang = []

        for i in member:
            for j in teacher:
                if i == j[1]:
                    if j[2] and j[2] > 0:
                        academician.append(i)
                        if i in member:
                            member.remove(i)
                    if j[3] and j[3] > 0 :
                        outyouth.append(i)
                        if i in member:
                            member.remove(i)
                    if j[4] and j[4] > 0:
                        changjiang.append(i)
                        if i in member:
                            member.remove(i)
        honorlist = []
        for i in honor:
            if i[-1:] == '奖':
                honorlist.append(i)
    else:
        project_name = [[]]
        papername = []
        member = []
        honorlist = []
        academician = []
        outyouth = []
        changjiang = []


    time = time.strftime("%Y:%m")
    a = time.split(":")
    if len(str(int(a[1]) - 2)) == 1:
        mouth = "0" + str(int(a[1]) - 2)
    else:
        mouth = str(int(a[1]) - 2)
    time = str(int(a[0]) - 2) + mouth + "-" + a[0] + a[1]
    # print(time)
    info_maindis = {}
    for i in maindis:
        info_maindis[i[0]] = i[1]
    # print(info_maindis)
    info = {
        "school_name": schoolName,
        "institution_name": institutionName,
        "data": time,
        "discipline_name": info_maindis,
        "mainlab": mainlab,
        "picture": "1.png",
        "project_name": project_name[0],
        "academician_list": academician,
        "changjiang_list": changjiang,
        "outyouth_list": outyouth,
        "other_list": member,
        "paper": papername,
        "invention": [],
        "award": honorlist
    }
    session['doc_info'] = info
    return render_template("a.html",schoolName=schoolName,institutionName=institutionName,time=time,maindis=maindis,mainlab=mainlab,project=project_name[0],paper=papername,academician=academician,changjiang=changjiang,outyouth=outyouth,member=member,honor=honorlist)


@app.route("/team1",methods=['GET','POST'])
def team1():
    if request.method == 'POST':
        schoolName = request.form.get('schoolName')
        institutionName = request.form.get('institutionName')
        teachername = request.form.get('teacherName')
    with ClusterRpcProxy(CONFIG) as rpc:
        try:
            school = rpc.team.get_institutionId(schoolName,institutionName)
            school_id = school[1]
            institution_id = school[0]
            with ClusterRpcProxy(CONFIG) as rpc:
                teacherlist = rpc.team.get_teacher(school_id)
            teacherlist1 = []
            for i in teacherlist:
                teacherlist1.append(i[0])
            with ClusterRpcProxy(CONFIG) as rpc:
                try:
                    teahcher_id = rpc.team.get_teacher_id(teachername, school_id, institution_id)
                    author = rpc.team.get_member(teahcher_id)
                    paperauthor = []
                    for i in author:
                        paperauthor.append(i[0])
                    member = []
                    for i in paperauthor:
                        a = i.lstrip("[").rstrip("]").strip("{").split(",")
                        for i in a:
                            if i.strip("{")[1:5] == "name":
                                member.append(i[i.index(":") + 2:len(i) - 1])
                    member = list(set(member))
                    for i in member:
                        if i not in teacherlist1:
                            member.remove(i)
                    member.remove(teachername)
                    title = []
                    with ClusterRpcProxy(CONFIG) as rpc:
                        a = rpc.title_search.get_title(teachername,institution_id)
                        if a[1] and a[1] > 0:
                            teachername = teachername+"(院士)"
                        if a[2] and a[2] > 0:
                            if ")" in teachername:
                                index1 = teachername.indexof(")")
                                teachername = teachername[0:index1]+"杰出青年"+teachername[index1:]
                            else:
                                teachername = teachername+"(杰出青年)"
                        if a[3] and a[3] > 0:
                            if ")" in teachername:
                                index1 = teachername.indexof(")")
                                teachername = teachername[0:index1]+"长江学者"+teachername[index1:]
                            else:
                                teachername = teachername+"(长江学者)"

                    for i in member:
                        with ClusterRpcProxy(CONFIG) as rpc:
                            a = rpc.title_search.get_title(i, institution_id)
                            title.append(a)

                    academician = []
                    outyouth = []
                    changjiang = []
                    other = []
                    for i in title:
                        if i:
                            if i[1] and i[1] > 0:
                                academician.append(i[0])
                            if i[2] and i[2] > 0:
                                outyouth.append(i[0])
                            if i[3] and i[3] > 0:
                                changjiang.append(i[0])
                    for i in member:
                        if i not in academician and i not in outyouth and i not in changjiang:
                            other.append(i)
                    return render_template("team.html", headname=teachername, academician=academician,
                                           outyouth=outyouth, changjiang=changjiang, other=other)
                except BaseException as e:
                    flash(u"没有此老师信息")
                    return render_template("index.html")
        except BaseException as e:
            flash(u"没有此学院信息")
            return render_template("index.html")


@app.route("/document",methods=['GET','POST'])
def document():
    info = session['doc_info']
    print(info)
    # info = {
    #     "school_name": "清华大学",
    #     "institution_name": "物理系",
    #     "data": time,
    #     "discipline_name": {
    #         "物理学": "A+",
    #         "天体物理": "A+"
    #     },
    #     "mainlab": "低维量子物理国家重点实验室",
    #     "picture": "1.png",
    #     "project_name": "层状关联电子体系中的宏观量子物性",
    #     "academician_list": ["顾秉林", "朱邦芬", "范守善", "李家明", "陈难先", "薛其坤"],
    #     "changjiang_list": ["尤力", "翁征宇", "张广铭", "王亚愚", "王向斌", "段文晖", "陈曦", "姜开利", "龙桂鲁", "赵永刚", "马旭村", "何珂", "鲁巍",
    #                         "姚宏"],
    #     "outyouth_list": ["陈宇林", "周树云", "刘峥", "于浦"],
    #     "other_list": ["郑盟锟", "宋灿立", "徐勇", "何联毅", "江万军", "李渭"],
    #     "paper": ["体心立方铁中裂纹扩展的结构演化研究", "bcc Fe中刃型位错的结构及能量学研究"],
    #     "invention": ["一种受激拉曼差分方法及其装置制造方法及图纸"],
    #     "award": ["国家科技进步一等奖"]
    # }
    with ClusterRpcProxy(CONFIG) as rpc:
        rpc.document.createdocument(info)

    return render_template("index.html")


@app.route("/title_search",methods=['GET','POST'])
def title_search():
    if request.method == 'POST':
        schoolName = request.form.get('schoolName')
        institutionName = request.form.get('institutionName')
        teachername = request.form.get('teacherName')
    with ClusterRpcProxy(CONFIG) as rpc:
        institution_id = rpc.title_search.get_institutionId(schoolName, institutionName)
    if "," in teachername:
        teacher = teachername.split(",")
    elif "，" in teachername:
        teacher = teachername.split("，")
    else:
        teacher = teachername.split(" ")
    title = []

    for i in teacher:
        with ClusterRpcProxy(CONFIG) as rpc:
            a = rpc.title_search.get_title(i,institution_id)
            title.append(a)
    academician = []
    outyouth = []
    changjiang = []
    for i in title:
        if i:
            if i[1] and i[1] > 0:
                academician.append(i[0])
            if i[2] and i[2] > 0:
                outyouth.append(i[0])
            if i[3] and i[3] > 0:
                changjiang.append(i[0])

    return render_template("title_search.html",academician = academician,outyouth = outyouth,changjiang = changjiang)

@app.route("/paper_search",methods=["GET","POST"])
def paper_search():
    if request.method == 'POST':
        school_name = request.form.get('schoolName')
        institution_name = request.form.get('institutionName')
        teacher_name = request.form.get('teacherName')
    with ClusterRpcProxy(CONFIG) as rpc:
        institution_id = rpc.paper_search.get_institutionId(school_name,institution_name)
        teacher_id = rpc.paper_search.get_teacherid(teacher_name,institution_id)
        if teacher_id:
            paper = rpc.paper_search.get_paper(teacher_id)
            paper.sort(key=lambda ele: ele[1], reverse=True)
            return render_template("paper_search.html",paper = paper)
        else:
            flash(u"没有此老师信息")
            return render_template("index.html")
                   

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.run(host='0.0.0.0' ,debug=True)
