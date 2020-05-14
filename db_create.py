from project import db
from project.models import Project, User, Role, Data, Result
import json


db.drop_all()
db.create_all()

user_role = Role(name='user')
super_user_role = Role(name='superuser')
db.session.add(user_role)
db.session.add(super_user_role)



u1 = User("user1", "user1@email.com", "username1", "haslo", [user_role,])
db.session.add(u1)

u2 = User("user2", "user2@email.com", "username2", "haslo", [user_role,])
db.session.add(u2)

u3 = User("user3", "user3@email.com", "username3", "haslo", [user_role,])
db.session.add(u3)


p1 = Project("Project 1", "Description 1", u1.id, "convergence behaviour")
db.session.add(p1)

#create result table
result_1 = Result(p1)
db.session.add(result_1)

p2 = Project("Project 2", "Description 2", u2.id, "convergence behaviour")
db.session.add(p2)

#create result table
result_2 = Result(p2)
db.session.add(result_2)

p3 = Project("Project 3", "Description 3", u3.id, "convergence behaviour")
db.session.add(p3)

#create result table
result_3 = Result(p3)
db.session.add(result_3)


admin = User("admin", "admin@email.com", "admin", "admin", [user_role, super_user_role])
db.session.add(admin)


u1.projects.append(p1)
u1.projects.append(p2)

u2.projects.append(p2)
u2.projects.append(p3)

u3.projects.append(p1)
u3.projects.append(p3)

db.session.commit()


# #create dummy data
# dict_1 = {'test_data': '1, 2, 3'}
# js_obj_1 = json.dumps(dict_1)
# dict_2 = {'test_data': '4, 5, 6'}
# js_obj_2 = json.dumps(dict_2)

# d_1 = Data(data=js_obj_1, result_id=result_1.id)
# d_2 = Data(data=js_obj_2, result_id=result_1.id) 

# db.session.add(d_1)
# db.session.add(d_2)



# result_1.data.append(d_1)
# result_1.data.append(d_2)

# db.session.commit()


# db.session.query(Data).delete()
# db.session.execute("ALTER SEQUENCE data_id_seq RESTART WITH 1")


# #new dummy data
# dict_3 = {'test_data': 'a, b, c'}
# js_obj_3 = json.dumps(dict_3)
# dict_4 = {'test_data': 'd, e, f'}
# js_obj_4 = json.dumps(dict_4)
# d_3 = Data(data=js_obj_3, result_id=result_1.id)
# d_4 = Data(data=js_obj_4, result_id=result_1.id)

# db.session.add(d_3)
# db.session.add(d_4)

# result_1.data.append(d_3)
# result_1.data.append(d_4)


# db.session.commit()




# for d in p1.results.data:
#     print(type(d.data))
#     new_d = json.loads(d.data)
#     print(new_d)
#     print(type(new_d))




