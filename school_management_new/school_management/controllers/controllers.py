# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class Session(http.Controller):
    @http.route('/api/session/authenticate', type='json', auth="none")
    def authenticate(self, db, login, password, base_location=None):
        request.session.authenticate(db, login, password)
        return request.env['ir.http'].session_info()


class AcademicYear(http.Controller):

    def get_academic_year_data(self):
        academic_years_rec = request.env['academic.year'].search([])
        academic_years = []
        for rec in academic_years_rec:
            year_semesters = []
            for semester in rec.semester_ids:
                semester_values = {
                    'name': semester.name,
                    'start_date': semester.start_date,
                    'end_date': semester.end_date,
                }
                year_semesters.append(semester_values)
            values = {
                'name': rec.name,
                'start_date': rec.start_date,
                'end_date': rec.end_date,
                'semester_ids': year_semesters
            }
            academic_years.append(values)
        data = {'status': '200', 'response': academic_years, 'message': 'success'}

    @http.route('/api/academic-years', type='json', auth='user')
    def get_academic_years(self):
        response = self.get_academic_year_data()
        if response.error:
            return {'status': '400', 'response': "Theres is no Data", 'message': 'failed'}
        return response

    def create_academic_year_request(self, values):
        new_year = request.env['academic.year'].sudo().create(values)
        if new_year.error:
            return {'status': '400', 'response': "Theres is no Data", 'message': 'failed'}
        else:
            year = {'id': new_year.id,
                    'name': new_year.name,
                    'start_date': new_year.start_date,
                    'end_date': new_year.end_date, }
            return year

    @http.route('/api/create-academic-years', type='json', auth='user')
    def create_academic_year(self, **rec):
        if request.jsonrequest:
            if rec['name'] and rec['start_date'] and rec['end_date']:
                values = {
                    'name': rec['name'],
                    'start_date': rec['start_date'],
                    'end_date': rec['end_date'],
                    'current': rec['current'],
                }
                requests = self.create_academic_year_request(values)
                if requests.error:
                    return {'status': 400, 'response': "Theres is no Data", 'message': 'failed'}
                else:
                    args = {'status': 200, 'response': 'year created successfully', 'new_year': requests.year}
                    return args
            else:
                return {'status': 400, 'response': "error in parmeters", 'message': 'failed'}

    @http.route('/api/generate-year-semesters', type='json', auth='user')
    def generate_year_semester(self, **rec):
        if request.jsonrequest:
            if rec['id']:
                year = request.env['academic.year'].search([('id', '=', rec['id'])])
                if year:
                    year.sudo().generate_academic_semester()
                args = {'success': True, 'message': 'semesters generated successfully'}
            return args

    @http.route('/api/update-academic-year', type='json', auth='user')
    def update_academic_year(self, **rec):
        if rec['id']:
            year = request.env['academic.year'].search([('id', '=', rec['id'])])
            if year:
                year.sudo().write(rec)
                year_semesters = []
                for semester in year.semester_ids:
                    semester_values = {
                        'name': semester.name,
                        'start_date': semester.start_date,
                        'end_date': semester.end_date,
                    }
                    year_semesters.append(semester_values)
            updated_year = {
                'id': year.id,
                'name': year.name,
                'start_date': year.start_date,
                'end_date': year.end_date,
                'year_semesters': year_semesters
            }
            args = {'success': True, 'message': 'year updated successfully', "updated_year": updated_year}
        return args

    @http.route('/api/delete-academic-year', type='json', auth='user')
    def delete_academic_year(self, **rec):
        if rec['id']:
            year = request.env['academic.year'].search([('id', '=', rec['id'])])
            if year:
                year.sudo().unlink()
            args = {'success': True, 'message': 'year deleted successfully'}
        return args
