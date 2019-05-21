import json
from flask import Flask, render_template, request, jsonify, flash, session
from flasgger import Swagger
from nameko.standalone.rpc import ClusterRpcProxy
import urllib.request
import os

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
            flash(u"没有此学院信息")
            return render_template("index.html")
        maindis = rpc.document.get_maindis(institutionId)

    for i in maindis:
        try:
            with ClusterRpcProxy(CONFIG) as rpc:
                discipline_name = rpc.document.get_discipline(int(i[0]))
                i[0] = discipline_name
        except:
            pass
    info_maindis = {}
    for i in maindis:
        info_maindis[i[0]] = i[1]
    with ClusterRpcProxy(CONFIG) as rpc:
        mainlab = rpc.document.get_lab(schoolName,institutionName)

    time = time.strftime("%Y:%m")
    a = time.split(":")
    if len(str(int(a[1]) - 2)) == 1:
        mouth = "0" + str(int(a[1]) - 2)
    else:
        mouth = str(int(a[1]) - 2)
    time = str(int(a[0]) - 2) + mouth + "-" + a[0] + a[1]
    #学院信息
    institution_info = {}
    institution_info['school_name'] = schoolName
    institution_info['institution_name'] = institutionName
    institution_info['date'] = time
    institution_info['maindis'] = info_maindis
    institution_info['mainlab'] = mainlab
    # print(institution_info)


    #TODO 处理院系老师之间的关系
    #获取学院中所有老师的名字
    with ClusterRpcProxy(CONFIG) as rpc:
        teacher = rpc.document.get_teacher_info(institutionId)
    teacherlist = []
    for i in teacher:
        teacherlist.append(i[1])

    #获取学院所做过的项目及项目带头人信息
    projectlist = []
    with ClusterRpcProxy(CONFIG) as rpc:
        project = rpc.document.get_project(schoolName)
    for i in project:
        if i[0] in teacherlist:
            projectlist.append(i)
    projectlist.sort(key=lambda ele: ele[2], reverse=True)
    #项目带头人
    head_name = []
    #团队信息
    team = []

    if len(projectlist) != 0:
        for i in projectlist:
            head_name.append(i[0])
        for i in head_name[0:3]:
            head = i
            teaminfo = {}

            with ClusterRpcProxy(CONFIG) as rpc:
                a = rpc.document.get_title(head, institutionId)
                if a[1] and a[1] > 0:
                    head = head + "(院士)"
                if a[3] and a[3] > 0:
                    if ")" in head:
                        index1 = head.index(")")
                        head = head[0:index1] + "长江学者" + head[index1:]
                    else:
                        head = head + "(长江学者)"
                if a[2] and a[2] > 0:
                    if ")" in head:
                        index1 = head.index(")")
                        head = head[0:index1] + ",杰出青年" + head[index1:]
                    else:
                        head = head + "(杰出青年)"


            with ClusterRpcProxy(CONFIG) as rpc:
                # invention = rpc.document.get_invention(i)
                head_id = rpc.document.get_teacher_id(i, institutionId)
                paper = rpc.document.get_paper_info_2(head_id[0])
                honor = rpc.document.get_honor_2(head_id[0])

            # invention.sort(key=lambda ele: ele[1], reverse=True)
            # invention_info = []
            # for i in invention:
            #     invention_info.append(i[0])
            # invention_info = list(set(invention_info))[0:10]
            papername = []
            paperauthor = []
            member = []
            for i in paper:
                papername.append(i[1])
                paperauthor.append(i[0])
            for i in paperauthor:
                a = i.lstrip("[").rstrip("]").strip("{").split(",")
                for i in a:
                    if i.strip("{")[1:5] == "name":
                        member.append(i[i.index(":") + 2:len(i) - 1])
            member = list(set(member))
            if "(" in head and head[0:head.index("(")] in member:
                member.remove(head[0:head.index("(")])
            elif head in member:
                member.remove(head)
            if len(member) == 0:
                continue
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

            teaminfo['head_name'] = head
            teaminfo['academician_list'] = academician
            teaminfo['changjiang_list'] = changjiang
            teaminfo['outyouth_list'] = outyouth
            teaminfo['other_list'] = member
            teaminfo['team_direction'] = "智能制造"
            teaminfo['paper'] = papername
            teaminfo['invention'] = []
            teaminfo['award'] = honorlist
            team.append(teaminfo)
    session['institution_info'] = institution_info
    session['team'] = team
    return render_template("a.html",institution_info = institution_info,team = team)

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
    institution_info = session['institution_info']
    team = session['team']
    with ClusterRpcProxy(CONFIG) as rpc:
        rpc.document.createdocument(institution_info,team)
    return render_template("a.html",institution_info = institution_info,team = team)

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
