from odoo.tools.sql import column_exists


def migrate(cr, installed_version):
    if not column_exists(cr, 'res_company', 'event_live_time'):
        return
    cr.execute("""
        ALTER TABLE res_company
        RENAME COLUMN event_live_time TO request_event_live_time;

        ALTER TABLE res_company
        RENAME COLUMN event_live_time_uom TO request_event_live_time_uom;

        ALTER TABLE res_company
        RENAME COLUMN event_auto_remove TO request_event_auto_remove;

        UPDATE ir_model_fields
        SET name='field_res_company_request_event_live_time'
        WHERE name='field_res_company_event_live_time';

        UPDATE ir_model_fields
        SET name='field_res_company_request_event_live_time_uom'
        WHERE name='field_res_company_event_live_time_uom';

        UPDATE ir_model_fields
        SET name='field_res_company_request_event_auto_remove'
        WHERE name='field_res_company_event_auto_remove';

        UPDATE ir_model_fields
        SET name='field_res_config_settings_request_event_live_time'
        WHERE name='field_res_config_settings_event_live_time';

        UPDATE ir_model_fields
        SET name='field_res_config_settings_request_event_live_time_uom'
        WHERE name='field_res_config_settings_event_live_time_uom';

        UPDATE ir_model_fields
        SET name='field_res_config_settings_request_event_auto_remove'
        WHERE name='field_res_config_settings_event_auto_remove';

        UPDATE ir_model_data
        SET name='field_res_company_request_event_live_time'
        WHERE name='field_res_company_event_live_time';

        UPDATE ir_model_data
        SET name='field_res_company_request_event_live_time_uom'
        WHERE name='field_res_company_event_live_time_uom';

        UPDATE ir_model_data
        SET name='field_res_company_request_event_auto_remove'
        WHERE name='field_res_company_event_auto_remove';

        UPDATE ir_model_data
        SET name='field_res_config_settings_request_event_live_time'
        WHERE name='field_res_config_settings_event_live_time';

        UPDATE ir_model_data
        SET name='field_res_config_settings_request_event_live_time_uom'
        WHERE name='field_res_config_settings_event_live_time_uom';

        UPDATE ir_model_data
        SET name='field_res_config_settings_request_event_auto_remove'
        WHERE name='field_res_config_settings_event_auto_remove';
    """)
