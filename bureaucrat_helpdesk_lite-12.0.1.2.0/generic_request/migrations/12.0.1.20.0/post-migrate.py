from odoo import api, SUPERUSER_ID


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    cron_job = env.ref(
        'generic_request.ir_cron_request_vacuum_events')
    cron_job.write({'code': 'model._scheduler_vacuum()'})
