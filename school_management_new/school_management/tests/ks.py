import json
import requests
from pprint import pprint
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient


class RestAPI:
    def __init__(self):
        self.url = 'https://erp.classera.com'
        self.client_id = "nNoxGfaoDdgEmyQeKuqLo8Bh23oQ1V"
        self.client_secret = "xLyFpWl2AZq52Wja7LViAQF1urojfU"
        self.client = BackendApplicationClient(client_id=self.client_id)
        self.oauth = OAuth2Session(client=self.client)

    def route(self,url):
        if url.startswith('/'):
            url = "%s%s" % (self.url,url)
            print("URL=" , url)
        return url

    def authenticate(self):
        self.oauth.fetch_token(
            token_url=self.route('/api/authentication/oauth2/token'),
            client_secret=self.client_secret,
            client_id=self.client_id,
            username="admin",
            password="admin",
        )
        print("OOK OOKOOK OOKOOK OOKOOK OOKOOK OOK")

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
    #init API

api = RestAPI()
api.authenticate()
# pprint(api.execute('/api'))
# pprint(api.execute('/api/database/list'))


parents_data = {
    'model': "res.partner",
'fields': json.dumps(['name', 'parent_relation_id',]),
    'domain': json.dumps([['is_parent', '=', True]]),}
parents_respone = api.execute('/api/search_read', 'GET', data=parents_data )
print(parents_respone, "---------==========----------")
pprint(parents_respone)


# payslip_data = {
#     'model': "hr.payslip",
#     'domain': json.dumps([['employee_id.name', '=', "Emad Gad"]]),
#     'fields': json.dumps(['name', 'line_ids']),
#     'limit': 1}
#
# payslip_response = api.execute('/api/search_read', 'GET', data=payslip_data)
# for entity in payslip_response:
#     payslip_line_ids = entity.get('line_ids')
#     print(payslip_line_ids)
#     for line in payslip_line_ids:
#         print(line)
#         payslip_line_data = {
#             'model': "hr.payslip.line",
#             'domain': json.dumps([['id', '=',line]]),
#             'fields': json.dumps(['name', 'total']),
#                 }
#         payslip_line_response = api.execute('/api/search_read', 'GET', data=payslip_line_data)
#         print(payslip_line_response, "---------==========----------")
# pprint(payslip_response)

# for line in payslip_response:
#     print(line)
#     lines = line.get('line_ids')
#     for rec in lines:
#         print(rec)

# data = {
#     'model':"hr.employee",
#     'domain':json.dumps([['name','=',"Emad Gad"]]),
#     'fields':json.dumps(['name','department_id','leaves_count']),
#     'limit':1
# }


student_data = {
    'model': "student.student",
    'domain': json.dumps([['name', '=', "Emad"]]),
    'fields': json.dumps(['name', 'education_stage', 'stage_year', 'residual' , 'student_sequence']),
    'limit': 1
}
student_response = api.execute('/api/search_read', 'GET', data=student_data)
print(student_response, "---------==========----------")

for entiry in student_response:
    name = entiry.get('name')
    id = entiry.get('id')
    payment_data = {
    'model': "fees.payment",
    'domain': json.dumps([['student_id.name', '=', "Emad Raafat"]]),
    'fields': json.dumps(['name', 'student_id','fees_to_invoice']),
    }
    payment_response = api.execute('/api/search_read', 'GET', data=payment_data)

    for line in payment_response [0].fees_to_invoice:
        to_invoice_data = {
            'model': "fees.payment",
            'domain': json.dumps([['student_id.name', '=', "Emad Raafat"]]),
            'fields': json.dumps(['fees_type.name', 'installments', 'due_date','amount','state']),
        }
        to_invoice_response = api.execute('/api/search_read', 'GET', data=to_invoice_data )
        print(to_invoice_response)
# for entiry in student_response:
#     name = entiry.get('name')
#     id = entiry.get('id')
#     education_stage = entiry.get('education_stage')
#     stage_year = entiry.get('stage_year')
#     student_sequence = entiry.get('student_sequence')
#     print(name, student_sequence, education_stage, stage_year)

#
# invoice_data = {
#     'model':"account.invoice",
#     'domain':json.dumps([['partner_id.name','=',"Emad"]]),
#     'fields':json.dumps(['number','state','amount_total','residual']),
#     'limit':1
# }
# invoice_response = api.execute('/api/search_read','GET',data=invoice_data)
# print(invoice_response,"---------==========----------")
#
# for entiry in invoice_response:
#     name = entiry.get('number')
#     state = entiry.get('state')
#     residual = entiry.get('residual')
#     amount_total = entiry.get('amount_total')
#     print(name , amount_total, state, residual)

# print(data)
# search_date = {
#     'model': 'hr.leave',
#     'values': {'id':1}
# }
# sponse = api.execute('/api/search','GET',data=search_date)
# print(sponse,"---------==========----------")
#
# response = api.execute('/api/search_read','GET',data=data)
#
# pprint(response)


# for entiry in response:
#     entiry['id'] = entiry.get('id')
#     id = entiry.get('id')
#     name = entiry.get('name')
#     leaves_count = entiry.get('leaves_count')
#     department_id = entiry.get('department_id')
#
#     print(id, "========", "id", id)
#     print(id, "========", "name", name)
#     print(id, "========", "department_id", department_id[1])
#     print(leaves_count,'=======')
#     values ={'name': "EMAD RAAFAT ID"}
#     create_date = {
#         'model': 'hr.employee',
#         'values': json.dumps(values)
#     }
#     print("create",create_date)
#     # pprint("create_date",create_date)
#     sponse = api.execute('/api/create', 'POST', data=create_date)
#     print(sponse)
#     # print(sponse)
