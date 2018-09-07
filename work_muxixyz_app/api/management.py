from flask import jsonify, request, current_app, url_for
from . import api
from .. import db
from ..models import Team, Group, User, Project, User2Project, Message, Statu, File, Comment, Apply
from ..decorator import login_required
from ..timetools import to_readable_time
from ..mq import newfeed
import time

import requests


#role: 000
@api.route('/user/2bSuperuser/', methods = ['POST'], endpoint = '2BSuperUser')
#@login_required(role = 0)
def user_2b_super_user():
    username = request.get_json().get("name")
    usr = User.query.filter_by(name = username).first()
    usr.role = 7
    db.session.add(usr)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200
    return response

#role: 100
@api.route('/group/new/', methods = ['POST'], endpoint = 'NewGroup')
@login_required(role = 4)
def new_group(uid):
    gname = request.get_json().get('groupName')
    ulist = request.get_json().get('userlist')
    group = Group(
        time = to_readable_time(str(int(time.time()))),
        name = gname, count = 0
    )
    db.session.add(group)
    db.session.commit()
    for u in ulist:
        usr = User.query.filter_by(id = u).first()
        if usr is None:
            continue
        group.count += 1
        usr.group_id = group.id
        db.session.add(usr)
    db.session.add(group)
    db.session.commit()
    response = jsonify({
        "msg": 'successful!', 
    })
    response.status_code = 200
    return response

@api.route('/group/<int:gid>/', methods = ['DELETE'], endpoint = 'GroupDelete')
@login_required(role = 2)
def group_delete(uid, gid):
    grp = Group.query.filter_by(id = gid).first()
    for u in grp.users:
        u.group_id = None
        db.session.add(u)
    db.session.delete(grp)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200
    return response

#role: 001
@api.route('/group/<int:gid>/userList/', methods = ['GET'], endpoint = 'GroupUserList')
@login_required(role = 1)
def group_user_list(uid, gid):
    role = 1
    page = 1
    if request.args.get('page') is not None:
        page = int(request.args.get('page'))
    counter = 0
    usrs = list([None, None, None, None, None, None, None, None, None, None, None])
    if gid  ==  0 :
        # get all users
        team = Team.query.filter_by(id = 1).first()
        users = team.users
    else:
        grp = Group.query.filter_by(id = gid).first()
        users = grp.users
    for u in users:
        grp=Group.query.filter_by(id=u.group_id).first()
        c = int(counter)//10
        if (c+1)  == page:
            usrs[counter%10] = {
                "username": u.name,
                "userID": u.id,
                "role": u.role,
                "email": u.email,
                "avatar": u.avatar,
                "groupName": grp.name,
            }
        counter += 1
    response = jsonify({
                 "count": counter, 
                 "list": usrs, 
             })
    response.status_code = 200
    return response

#role: 110
@api.route('/group/<int:gid>/manageUser/', methods = ['POST'], endpoint = 'GroupManageUser')
@login_required(role = 2)
def group_manage_user(uid, gid):
    newUList = request.get_json().get('userList')
    oldUList = Group.query.filter_by(id = gid).first().users
    for u in newUList:
        usr = User.query.filter_by(id = u).first()
        if usr not in oldUList:
            usr.group_id = gid
            db.session.add(usr)
    for usr in oldUList:
        if usr.id not in newUList:
            usr.group_id=None
            db.session.add(usr)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200
    return response

#role: 001
@api.route('/group/list/', methods = ['GET'], endpoint = 'GroupList')
@login_required(role = 1)
def group_list(uid):
    gid = 1
    l = list([])
    while True:
        grp = Group.query.filter_by(id = gid).first()
        if grp is None:
            break
        l.append({
            "groupID": gid, 
            "groupName": grp.name, 
            "userCount": grp.count, 
        })
        gid += 1
    response = jsonify({
        "groupList": l, 
    })
    response.status_code = 200
    return response

#role: 001
@api.route('/project/<int:pid>/userList/', methods = ['GET'], endpoint = 'ProjectUserList')
@login_required(role = 1)
def project_user_list(uid, pid):
    page = 1
    if request.args.get('page') is not None:
        page = int(request.args.get('page'))
    user = User2Project.query.filter_by(project_id = pid).all()
    counter = 0
    usrs = list([None, None, None, None, None, None, None, None, None, None, None])
    for U in user:
        c = int(counter)//10
        if (c+1)  == page:
            u = User.query.filter_by(id = U.user_id).first()
            usrs[counter%10]  =  {
                "username": u.name, 
                "userID": u.id, 
                "avatar": u.avatar, 
                }
        counter += 1
    pjc = Project.query.filter_by(id = pid).first()
    pjc.count = counter
    db.session.add(pjc)
    db.session.commit()
    response = jsonify({
                 "count": counter, 
                 "list": usrs, 
             })
    response.status_code = 200
    return response

#role: 001
@api.route('/user/project/list/', methods = ['GET'], endpoint = 'UserProjectList')
@login_required(role = 1)
def user_project_list(uid):
    page = 1
    if request.args.get('page') is not None:
        page = int(request.args.get('page'))
    counter = 0
    pjcs = list([None, None, None, None, None, None, None, None, None, None, None])
# page
    usr = User.query.filter_by(id = uid).first()
    if usr.role > 1: # 111 superuser 7
        pid = 1        # 011 admin     3
        l = list([])   # 001 user      1
        while True:
            pjc = Project.query.filter_by(id = pid).first()
            if pjc is None:
                break
            l.append({
                "projectID": pid, 
                "projectName": pjc.name, 
                "intro": pjc.intro,
                "userCount": pjc.count, 
            })
            counter += 1
            pid += 1
        response = jsonify({
        	"count": counter, 
            "projectList": l, 
        })
        response.status_code = 200
        return response
    for p in usr.projects:
        c = int(counter)//10
        if (c+1)  == page:
            usrs[counter%10] = {
                "projectID": p.id, 
                "projectName": p.name, 
                "userCount": p.count, 
            }
        counter += 1
    response = jsonify({
        "count": counter, 
        "projectList": pjcs, 
    })
    response.status_code = 200
    return response

#role: 110
@api.route('/user/2bmember/', methods = ['POST'], endpoint = 'User2bMember')
@login_required(role = 2)
def user_2b_member(uid):
    user_id = request.get_json().get('userID')
    usr = User.query.filter_by(id = user_id).first()
    if usr.role !=  0:
        response = jsonify({
            "msg": 'user already be a member!', 
        })
        response.status_code = 402
        return response
    usr.role = 1
    db.session.add(usr)
    db.session.commit()
    action = 'User: ' + usr.name + 'is a member of MUXI!'
    newfeed(uid, action, 5, user_id)
    response = jsonify({
        "msg": 'successful!', 
    })
    response.status_code = 200
    return response

# role: 100
@api.route('/user/admins/', methods = ['GET'], endpoint = 'AdminList')
@login_required(role = 4)
def admin_list(uid):
    admins = User.query.filter_by(role = 3).all()
    if admins is None:
        response = jsonify({})
        response.status_code = 201
        return response
    l=list([])
    for admin in admins:
        l.append({
            "userID": admin.id,
            "userName": admin.name,
        })
    response = jsonify({
        "list": l,
    })
    response.status_code = 200
    return response

#role: 100
@api.route('/user/addAdmin/', methods = ['POST'], endpoint = 'AddAdmin')
@login_required(role = 4)
def add_admin(uid):
    lid = request.get_json().get('luckydog')
    luckydog = User.query.filter_by(id = lid).first()
    luckydog.role = 3
    db.session.add(luckydog)
    db.session.commit()
    action = 'User: ' + luckydog.name + 'is ADMINISTRATOR now!'
    newfeed(uid, action, 5, lid)
    response = jsonify({})
    response.status_code = 200
    return response

#role: 110
@api.route('/user/<int:id>/managePro/', methods = ['POST'], endpoint = 'ManageProject')
@login_required(role = 2)
def manage_project(uid, id):
    newPList = request.get_json().get('projectList')
    oldPList = User2Project.query.filter_by(user_id = id).all()
    for pid in newPList:
        pjc = Project.query.filter_by(id = pid).first()
        if pjc not in oldPList:
            record = User2Project(user_id = id, project_id = pid)
            db.session.add(record)
    for pjc in oldPList:
        if pjc.id not in newPList:
            record = User2Project.query.filter_by(user_id = id, project_id = pid).first()
            db.session.delete(record)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200
    return response

#role: 110
@api.route('/user/<int:id>/manageGroup/', methods = ['POST'], endpoint = 'ManageGroup')
@login_required(role = 2)
def manage_group(uid, id):
    gid = request.get_json().get('groupID')
    usr = User.query.filter_by(id = id).first()
    usr.group_id = gid
    db.session.add(usr)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200.
    return response

#role: 100
@api.route('/user/<int:id>/setRole/', methods = ['POST'], endpoint = 'SetRole')
@login_required(role = 4)
def set_role(uid, id):
    role = request.get_json().get('role')
    usr = User.query.filter_by(id = id).first()
    usr.role = role
    db.session.add(usr)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200
    return response

#role: 001
@api.route('/user/<int:id>/setting/', methods = ['POST'], endpoint = 'EditSetting')
@login_required(role = 1)
def editsetting(uid, id):
    if uid !=  id:
        response = jsonify({
            "msg": 'this is others personal setting!', 
        })
        response.status_code = 401
        return response

    username = request.get_json().get('username')
    address = request.get_json().get('address')
    tel = request.get_json().get('tel')
    email = request.get_json().get('email')
    message = request.get_json().get('message')
    usr = User.query.filter_by(id = id).first()
    usr.username = username
    usr.email = address
    usr.tel = tel
    usr.email_service = email
    usr.message = message
    db.session.add(usr)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200
    return response

# role 110
@api.route('/user/<int:id>/', methods = ['DELETE'], endpoint = 'DeleteMember')
@login_required(role = 2)
def delete_member(uid,id):
    if uid == id :
        response = jsonify({
            "msg": 'Never give up yourself!',
        })
        response.status_code = 402
        return response
    usr = User.query.filter_by(id=id).first()
    usr.role = 0
    db.session.add(usr)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200
    return response

# role 110
@api.route('/team/applyList/', methods = ['GET'], endpoint = 'ApplyList')
@login_required(role = 2)
def apply_list(uid):
    usrs = db.session.query(Apply).all()
    l = list([])
    if usrs is None:
        response = jsonify({
            "msg": 'Application all done!',
        })
        response.status_code = 201
        return response
    for u in usrs:
        l.append({
            "userID": u.id,
            "userName": u.name,
            "userEmail": u.email,
        })
    response = jsonify({
        "msg": "successful",
    })
    response.status_code = 200
    return response

# role: 110
@api.route('/team/apply/<int:id>/', methods = ['DELETE'], endpoint = "RefuseApply")
@login_required(role = 2)
def refuse_apply(uid,id):
    record = Apply.query.filter_by(user_id = id).first()
    if record is None:
        response = jsonify({})
        response.status_code = 403
        return response
    db.session.delete(record)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200
    return response
