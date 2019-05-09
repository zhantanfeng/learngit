# -*- coding: UTF-8 -*-
from nameko.rpc import rpc
import pymysql

class team(object):
    name = "team"

    @rpc
    #根据学校名和学院名获取学院id
    def get_institutionId(self, schoolName, institutionName):
        db = pymysql.connect(host='47.106.83.33', db='eds_base', user='root', password='111111', port=3306,
                             charset='utf8')
        cursor = db.cursor()
        sql = "select ID,SCHOOL_ID from es_institution where SCHOOL_NAME = %s and NAME = %s "
        cursor.execute(sql, (schoolName, institutionName))
        institution = cursor.fetchone()
        return institution

    @rpc
    #根据学校名获取学院名获取这个学院所有老师
    def get_teacher(self,school_id):
        db = pymysql.connect(host='47.106.83.33', db='eds_base', user='root', password='111111', port=3306,
                             charset='utf8')
        cursor = db.cursor()
        sql = "select NAME from es_teacher where SCHOOL_ID = %s"
        cursor.execute(sql,(school_id))
        teacher_list = cursor.fetchall()
        return teacher_list

    @rpc
    #根据老师名，学校名，学院名获取老师的id
    def get_teacher_id(self,teacher_name,school_id,institution_id):
        db = pymysql.connect(host='47.106.83.33', db='eds_base', user='root', password='111111', port=3306,
                             charset='utf8')
        cursor = db.cursor()
        sql = "select ID from es_teacher where NAME = %s and SCHOOL_ID = %s and INSTITUTION_ID = %s"
        cursor.execute(sql,(teacher_name,school_id,institution_id))
        teacher_id = cursor.fetchone()
        return teacher_id

    @rpc
    #根据老师id,获取所有论文的作者
    def get_member(self,author_id):
        db = pymysql.connect(host='47.104.236.183', db='eds_base', user='root', password='SLX..eds123', port=3306,
                             charset='utf8')
        cursor = db.cursor()
        sql  = "select author from es_paper where author_id = %s"
        cursor.execute(sql,(author_id))
        member = cursor.fetchall()
        return member
