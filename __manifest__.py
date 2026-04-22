# -*- coding: utf-8 -*-
{
    'name': 'library management',
    'version': '1.0',
    'category': 'Real Estate',
    'summary': 'library managment',
    'depends': ['base', 'mail', 'contacts', 'sale', 'account'],
    'application': True,
    'installable': True,
    'sequence': 3,
    'data': [
        'security/library_security_groups.xml',
        'security/ir.model.access.csv',
        'data/library_genres_data.xml',
        'views/library_book_view.xml',
        'views/library_checkout_view.xml',
        'views/library_author_view.xml',
        'views/library_publisher_view.xml',
        'views/library_genres_view.xml',

        'views/library_tag_view.xml',
        'views/library_settings_view.xml',
        'data/email_remainder_template_view.xml',
        'data/remainder_action_view.xml',
        'data/email_overdue_template.xml',
        'data/res_partner_custom_view.xml',
        'data/account_move_custom_view.xml',
        'wizard/library_checkout_wizard_view.xml',
        'wizard/library_report_wizard_view.xml',
        'report/library_management_report_view.xml',
        'report/library_report_template.xml',
        'views/library_menu_view.xml',
    ],
    'assets': {
    'web.assets_backend': [
        'library_management/static/src/js/action_manager.js',
    ],
},

}
