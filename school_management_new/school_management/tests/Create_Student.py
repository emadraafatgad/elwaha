import json
import requests
from pprint import pprint
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient


class RestAPI:
    def __init__(self):
        self.url = 'https://erp.classera.com'
        self.client_id = "PeualOqN4yqQwLwtZ3tcpr8i5tXHox"
        self.client_secret = "IUkgK3XQ0bA4KNMfVKr6F6LLID39lH"
        self.client = BackendApplicationClient(client_id=self.client_id)
        print(self.client)
        self.oauth = OAuth2Session(client=self.client)
        print(self.oauth)
    def route(self,url):
        if url.startswith('/'):
            url = "%s%s" % (self.url,url)
            print("URL=" , url)
        return url

    def authenticate(self):
        self.oauth.fetch_token(
            token_url='https://erp.classera.com/api/authentication/oauth2/token',
            client_secret = "IUkgK3XQ0bA4KNMfVKr6F6LLID39lH",
            client_id = "PeualOqN4yqQwLwtZ3tcpr8i5tXHox",
            username="admin",
            password="admin",
        )

    def execute(self,endpoint,type="GET",data=()):
        if type == "POST":
            response = self.oauth.post(self.route(endpoint),data=data)
        elif type=="PUt":
            response = self.oauth.put(self.route(endpoint),data=data)
        elif type == "DELETE":
            response = self.oauth.delete(self.route(endpoint), data=data)
        else:
            response = self.oauth.get(self.route(endpoint), data=data)
        if response.status_code != 200:
            raise Exception(pprint((response.json())))
        else:
            return response.json()
api = RestAPI()
api.authenticate()
stage_date = {
    'model': "education.stage",

    'fields':json.dumps(['name','id']),
    'limit':1,
}
stage_response = api.execute('/api/search_read', "GET", data=stage_date)
print(stage_response[0]['id'])
Stage_ID = stage_response[0]['id']

# parent_data = {
#     'model': "res.partner",
#     'values': json.dumps({'name':'Parents',
#                           'is_parent':True,
#                           'phone':'+201096846883'})}
# parent_response = api.execute('/api/create/', "POST", data=parent_data)
#
# print(parent_response)
# Parent_ID = parent_response[0]
# print(Parent_ID)
#
# student_date = {
#     'model': "student.student",
#     'values': json.dumps({'name': 'Name Student',
#                          'parent_id': Parent_ID,
#                           'gender':'male',
#                           'date_of_birth': '2010-05-15',
#                           'education_stage':Stage_ID,
# })}
#
# student_response = api.execute('/api/create/',"POST",data=student_date)
# Student_ID = student_response[0]
# print(Student_ID)


# data = {
#     'model':"hr.employee",
#     'domain':json.dumps([['name','=',"Emad Gad"]]),
#     'fields':json.dumps(['name','department_id']),
#     'limit':1
# }

# response = api.execute('/api/search_read','GET',data=data)
# postdata = {
#     'model':"res.partner",
#     'values':json.dumps({'name':'test from code'})
# }
# responsat = api.execute('/api/create/',"POST",data=postdata)
# pprint(response)
# for entiry in response:
#     print(entiry)
#     print(entiry.department)
#     print("--------------------------------")

#
# for entiry in response:
#     entiry['id'] = entiry.get('id')
#     id = entiry.get('id')
#     name = entiry.get('name')
#     department_id = entiry.get('department_id')
#     print(id, "========", "id", id)
#     print(id, "========", "name", name)
#     print(id, "========", "department_id", department_id[1])
