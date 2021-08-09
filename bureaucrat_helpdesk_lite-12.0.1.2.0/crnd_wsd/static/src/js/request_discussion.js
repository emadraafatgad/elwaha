odoo.define('crnd_wsd.discussion', function (require) {
    'use strict';

    var trumbowyg = require('crnd_wsd.trumbowyg');
    var web_editor_base = require('web_editor.base');
    var portal_chatter = require('portal.chatter');


    // Extend mail thread widget
    var RequestChatter = portal_chatter.PortalChatter.extend({

        start: function () {
            this._super.apply(this, arguments);
            self.$(
                '.o_portal_chatter_composer textarea[name="message"]'
            ).each(function () {
                var $textarea = $(this);
                $textarea.trumbowyg(trumbowyg.trumbowygOptions);
            });
            self.$(
                '.o_portal_chatter_composer ' +
                'form.o_portal_chatter_composer_form'
            ).each(function () {
                $(this).attr('action', '/mail/request_chatter_post');
            });
        },
    });

    web_editor_base.ready().then(function () {
        $('.request_comments_chatter').each(function () {
            var $elem = $(this);
            var chatter = new RequestChatter(null, $elem.data());
            chatter.appendTo($elem);
        });
    });

});
