
# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import content_disposition, request
from odoo.tools import html_escape


class XLSXReportController(http.Controller):

    @http.route('/xlsx_reports', type='http', auth='user')
    def xlsx_reports(self, options, output_format, report_name):
        options = json.loads(options)
        try:
            if output_format == 'xlsx':
                response = request.make_response(
                    None,
                    headers=[
                        ('Content-Type', 'application/vnd.ms-excel'),
                        ('Content-Disposition',
                         content_disposition(f"{report_name}.xlsx")),
                    ]
                )
                abc = request.env['library.report.wizard'].with_user(
                    request.session.uid
                ).create({
                    'members_id':    options.get('members_id') or False,
                    'book_id':       options.get('book_id') or False,
                    'category_id':   options.get('category_id') or False,
                    'genre_id':      options.get('genre_id') or False,
                    'checkout_date': options.get('checkout_date') or False,
                    'return_date':   options.get('return_date') or False,
                    'sort':          options.get('sort') or 'library_checkout.checkout_date',
                    'sort_by':       options.get('sort_by') or 'ASC',
                })
                abc.generate_xlsx_report(options, response)
                return response

        except Exception as e:
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': html_escape(str(e)),
            }
            return request.make_response(
                json.dumps(error),
                headers=[('Content-Type', 'application/json')],
            )