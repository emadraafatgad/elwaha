from odoo import api, SUPERUSER_ID
from odoo.addons.http_routing.models.ir_http import slugify


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    Kind = env['request.kind'].with_context(active_test=False)
    for record in Kind.search([('code', '=', False)]):
        record.code = slugify(record.display_name, max_length=0)
