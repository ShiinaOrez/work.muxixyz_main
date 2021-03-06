import unittest
import os
from work_muxixyz_app import create_app, db
from flask import current_app, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from work_muxixyz_app.models import Team, Group, User, Project, User2Project, Message, Statu, File, Comment
import random
import json
import time

class BasicTestCase(unittest.TestCase):

    def get_api_headers(self, ifToken):
        if ifToken is True:
            return {
                'token': TOKEN, 
                'Accept': 'application/json', 
                'Content-Type': 'application/json', 
            }
        else:
            return {
                'Accept': 'application/json', 
                'Content-Type': 'application/json', 
            }


    def setUp(self):
        self.app  =  create_app(os.getenv('FLASK_CONFIG') or 'default')
        self.app_context  =  self.app.app_context()
        self.app_context.push()
        self.client  =  self.app.test_client()
        db.create_all()

    def test_z_tearDown(self):
        db.session.remove()
        db.drop_all()
#        db.create_all()
        self.app_context.pop()

    def test_app_exist(self):
        self.assertFalse(current_app is None)

# API FOR GET A TOKEN AND PREPARTION

    def test_message_a_auth(self):
        muxi = Team(name = 'test', count = 3)
        superuser = User(name = 'cat', email = 'cat@test.com', tel = '11111111111', role = 7, team_id = 1)
        muxi.creator = 1
        admin = User(name = 'dog', email = 'dog@test.com', tel = '22222222222', role = 1, team_id = 1)
        usr = User(name = 'pig', email = 'pig@test.com', tel = '33333333333', role = 1, team_id = 1)
        project = Project(name = 'test')
        rela = User2Project(user_id = 1, project_id = 1)
        f = File(filename = 'test', creator_id = 1, project_id = 1, time = str(time.time()))
        db.session.add(muxi)
        db.session.add(superuser)
        db.session.add(admin)
        db.session.add(usr)
        db.session.add(project)
        db.session.add(rela)
        db.session.add(f)
        db.session.commit()
        response = self.client.post(
            url_for('api.login', _external = True), 
            data = json.dumps({
                "username": 'cat', 
            }), 
            headers = self.get_api_headers(False), 
        )
        s = json.loads(response.data.decode('utf-8'))['token']
        global TOKEN
        TOKEN = s
        print ('OK')
# END
    def test_message_b_userattention(self):
        response = self.client.post(
            url_for('api.UserAttention', _external = True), 
            data = json.dumps({
                "fileID": 1, 
            }), 
            headers = self.get_api_headers(True), 
        )
        self.assertTrue(response.status_code == 200)
    
    def test_message_c_newmessage(self):
        response = self.client.post(
            url_for('api.MessageNew', _external = True), 
            data = json.dumps({
                "receiver": "cat", 
                "maker": "dog", 
                "action": "edit", 
                "sourceID": 1, 
            }), 
            headers = self.get_api_headers(True), 
        )
        m = Message(time = str(time.time()), action = 'change', from_id = 3, receive_id = 1, file_id = 1)
        db.session.add(m)
        db.session.commit()
        self.assertTrue(response.status_code == 200)
    
    def test_message_f_readall(self):
        response = self.client.post(
            url_for('api.ReadAll', _external = True), 
            data = json.dumps({
                "username": 'cat', 
            }), 
            headers = self.get_api_headers(True), 
        )
        self.assertTrue(response.status_code == 200)
    
    def test_message_e_messageinfo(self):
        response = self.client.get(
            url_for('api.MessageInfo', username = 'cat', mid = 1, _external = True), 
            headers = self.get_api_headers(True), 
        )
        self.assertTrue(response.status_code == 200)
    
    def test_message_d_messagelist(self):
        data = {
            "type": 0, 
        }
        response = self.client.get(
            url_for('api.MessageList', _external = True), 
            headers = self.get_api_headers(True), 
            query_string = data, 
        )
#        print (response.json)
#        print (response.status_code)
        self.assertTrue(response.status_code == 200)

    def test_message_g_attentionlist(self):
        response = self.client.get(
            url_for('api.UserAttention', _external = True), 
            headers = self.get_api_headers(True), 
        )
        self.assertTrue(response.status_code == 200)
    
    def test_message_h_deleteattention(self):
        data = {
            "fileName": 'test',
        }
        response = self.client.delete(
            url_for('api.UserAttention', _external = True),
            headers = self.get_api_headers(True),
            query_string = data,
        )
        print (response.__dict__)
        self.assertTrue(response.status_code == 200)
