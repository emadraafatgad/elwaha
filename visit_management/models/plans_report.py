# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

#
# Please note that these reports are not multi-currency !!!
#

from odoo import api, fields, models, tools


class PlanReport(models.Model):
    _name = "visit.report"
    _description = "Plans Report"
    _auto = False
    _order = 'start_date desc'

    name = fields.Char(string='visit Title', readonly=True)
    start_date = fields.Datetime(string="Date",readonly=True)
    class_id = fields.Many2one(related="customer_id.class_id",store=True,readonly=True)
    employee_id =fields.Many2one('hr.employee',readonly=True)
    customer_id = fields.Many2one('res.partner', readonly=True, string="Doctor", domain="[('customer','=',True)]")
    total_visits = fields.Integer("Total Visits",readonly=True)
    done_visits = fields.Integer("Completed Visits",readonly=True)
    cancel = fields.Integer("Cancel",readonly=True)
    postpone = fields.Integer("Postpone",readonly=True)
    state = fields.Selection([('New', 'New'), ('Postpone', 'Postpone'), ('Done', 'Completed'), ('Canceled', 'Cancel')],
                             readonly=True)

    def _select(self):
        select_str = """
             SELECT
                    t.id as id,
                    t.start_date as start_date,
                    t.employee_id,
                    t.customer_id,
                    t.class_id,
                    t.name as name,
        """
        return select_str

    def _group_by(self):
        group_by_str = """
                GROUP BY
                    t.id,
                    t.start_date,
                    t.employee_id,
                    t.class_id,
                    t.customer_id,
                    name,
                    t.state,
        """
        return group_by_str

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE OR REPLACE VIEW visit_report AS
              (SELECT t.id as id,
                    t.employee_id,
                    t.customer_id,
                    t.class_id,
                    t.start_date,
                    t.state as state,
                    count(*) AS total_visits,
                    COUNT(CASE WHEN t.state='Done' THEN 2 ELSE null END) AS done_visits,
                    COUNT(CASE WHEN t.state='Postpone' THEN 1 ELSE null END)  AS postpone,
                    COUNT(CASE WHEN t.state='Canceled' THEN 1 ELSE null END)  AS cancel
            FROM customer_visit AS t
            GROUP BY 
            t.id,
            t.employee_id,
            t.customer_id,
            t.class_id)""")