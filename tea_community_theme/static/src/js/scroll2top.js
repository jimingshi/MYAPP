odoo.define('tea_community_theme.scroll2top', function (require) {
    "use strict";

    var ActionManager = require('web.ActionManager');

    var amountScrolled = 300;

    if (!$('.o_content').length) {
        return $.Deferred().reject("DOM doesn't contain '.o_content'");
    }

    $('.o_content').each(function() {
        var o_content = this;

        $(o_content).append('<a href="#" class="back-to-top">Back to Top</a>');

        $(window).scroll(function() {
            if ($(window).scrollTop() > amountScrolled) {
                $(o_content).find('a.back-to-top').fadeIn('slow');
            } else {
                $(o_content).find('a.back-to-top').fadeOut('slow');
            }
        });

        $(o_content).on('click', 'a.back-to-top', function() {
            $('body, html').animate({
                scrollTop: 0
            }, 500);
            return false;
        });
    });
});
