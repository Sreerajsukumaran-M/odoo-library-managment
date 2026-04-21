# -*- coding: utf-8 -*-
from odoo import fields, models


class LibraryReportWizard(models.TransientModel):
    _name = 'library.report.wizard'
    _description = 'Library Report Wizard'

    members_id = fields.Many2one('res.partner', string='Member')
    checkout_date = fields.Datetime(string='Checkout Date')
    return_date = fields.Datetime(string='Return Date')
    book_id = fields.Many2one('library.book', string='Book')
    category_id = fields.Many2one('library.tags', string='Category')
    genre_id = fields.Many2one('library.genres', string='Genre')
    sort_by = fields.Selection([
        ('library_checkout.checkout_date', 'Checkout Date'),
        ('library_checkout.checkout_due_date', 'Due Date'),
    ], string='Sort', default='library_checkout.checkout_date')

    def _fetch_report_data(self):
        query = """
            SELECT
                library_checkout.cust_reference_number AS reference_id,
                res_partner.name AS member_name, 
                library_book.name AS book_name,
                library_author.name AS author,
                library_checkout.checkout_date AS checkout_date,
                library_checkout.checkout_return AS return_date,
                library_checkout.checkout_due_date AS due_date,
                STRING_AGG( library_tags.name, ', ') AS category,
                library_genres.name AS genre
                
            FROM library_checkout 
                JOIN res_partner  ON res_partner.id = library_checkout.customer_id
                JOIN library_checkout_line ON library_checkout_line.checkout_id = library_checkout.id
                JOIN library_book ON library_book.id = library_checkout_line.book_id
                LEFT JOIN library_author ON library_author.id = library_book.book_author_id
                LEFT JOIN library_genres ON library_genres.id = library_book.genres_id
                LEFT JOIN library_book_library_tags_rel ON library_book_library_tags_rel.library_book_id = library_book.id
                LEFT JOIN library_tags ON library_tags.id = library_book_library_tags_rel.library_tags_id
            WHERE 1=1
        """
        params = []

        if self.members_id:
            query += " AND library_checkout.customer_id = %s"
            params.append(self.members_id.id)
            print(params)

        if self.checkout_date:
            query += " AND library_checkout.checkout_date >= %s"
            params.append(self.checkout_date)
            print(params)

        if self.return_date:
            query += " AND library_checkout.checkout_return <= %s"
            params.append(self.return_date)

            print(params)

        if self.book_id:
            query += " AND library_checkout_line.book_id = %s"
            params.append(self.book_id.id)
            print(params)

        if self.category_id:
            query += " AND library_tags.id = %s"
            params.append(self.category_id.id)
            print(params)

        if self.genre_id:
            query += " AND library_genres.id = %s"
            params.append(self.genre_id.id)
            print(params)
        query += """
            GROUP BY
                library_checkout.cust_reference_number,
                res_partner.name,
                library_book.name,
                library_author.name,
                library_checkout.checkout_date,
                library_checkout.checkout_return,
                library_checkout.checkout_due_date,
                library_genres.name
        """

        query += f" ORDER BY {self.sort_by} ASC"

        self.env.cr.execute(query, params)
        print(query)

        rows = self.env.cr.dictfetchall()
        print(rows)
        return rows

    def add_report_action(self):
        values = self._fetch_report_data()
        data = {'lines': values}
        print(data)
        return self.env.ref(
            'library_management.action_library_report_print'
        ).report_action(self, data=data)
