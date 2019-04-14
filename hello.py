# -*- coding: UTF-8 -*-
from nameko.rpc import rpc
import pymysql

class Compute(object):
    name = "test"

    @rpc
    def test(self):
        return "hello"

    @rpc
    def compute(self):
        db = pymysql.connect(host='47.106.83.33', db='eds_base', user='root', password='111111', port=3306,
                             charset='utf8')
        cursor = db.cursor()
        sql = "select TEACHER_ID from es_honor where HONOR like '%院士%' "
        cursor.execute(sql)
        teacher_id = cursor.fetchall()
        return teacher_id

    @rpc
    def compute1(self,id):
        db = pymysql.connect(host='47.106.83.33', db='eds_base', user='root', password='111111', port=3306,charset='utf8')
        cursor = db.cursor()
        sql = "select NAME from es_teacher where ID = %s "
        cursor.execute(sql,(id))
        teacher_name = cursor.fetchone()
        return teacher_name

    @rpc
    def compute2(self):
        teacher_name = []
        teacher_id = self.compute()
        for i in teacher_id:
            teacher_name.append(self.compute1(i))
        return teacher_name

    @rpc
    def get_institutionId(self,schoolName,institutionName):
        db = pymysql.connect(host='47.106.83.33', db='eds_base', user='root', password='111111', port=3306, charset='utf8')
        cursor = db.cursor()
        sql = "select ID from es_institution where SCHOOL_NAME = %s and NAME = %s "
        cursor.execute(sql, (schoolName,institutionName))
        institution_id = cursor.fetchone()
        return institution_id

    @rpc
    def get_academicianName(self,institution_id):
        db = pymysql.connect(host='47.106.83.33', db='eds_base', user='root', password='111111', port=3306, charset='utf8')
        cursor = db.cursor()
        sql = "select NAME from es_teacher where INSTITUTION_ID = %s and ACADEMICIAN > 0 "
        cursor.execute(sql, (institution_id))
        teacher_name = cursor.fetchall()
        return teacher_name