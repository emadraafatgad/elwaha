def migrate(cr, installed_version):
    cr.execute("""
        DELETE FROM ir_model
        WHERE model IN (
            'request.mixin.name_with_code',
            'request.mixin.uniq_name_code'
        );
    """)
