# -*- coding: utf-8 -*-
import io
import json
import xlsxwriter
from odoo import fields, models
from odoo.tools import json_default


class LibraryReportWizard(models.TransientModel):
    _name = 'library.report.wizard'
    _description = 'Library Report Wizard'

    members_id = fields.Many2one('res.partner', string='Member')
    checkout_date = fields.Datetime(string='Checkout Date')
    return_date = fields.Datetime(string='Return Date')
    book_id = fields.Many2one('library.book', string='Book')
    category_id = fields.Many2one('library.tags', string='Category')
    genre_id = fields.Many2one('library.genres', string='Genre')
    sort = fields.Selection([
        ('library_checkout.checkout_date', 'Checkout Date'),
        ('library_checkout.checkout_due_date', 'Due Date'),
    ], string='Sort', default='library_checkout.checkout_date')
    sort_by = fields.Selection([
        ('ASC', 'Ascending'),
        ('DESC', 'Descending'),
    ], string='Sort By', default='ASC')

    def _fetch_report_data(self):
        query = """
            SELECT
                library_checkout.cust_reference_number AS reference_id,
                res_partner.name                        AS member_name,
                library_book.name                       AS book_name,
                library_author.name                     AS author,
                library_checkout.checkout_date          AS checkout_date,
                library_checkout.checkout_return        AS return_date,
                library_checkout.checkout_due_date      AS due_date,
                STRING_AGG(DISTINCT library_tags.name, ', ') AS category,
                library_genres.name                     AS genre
            FROM library_checkout
            JOIN res_partner
                ON res_partner.id = library_checkout.customer_id
            JOIN library_checkout_line
                ON library_checkout_line.checkout_id = library_checkout.id
            JOIN library_book
                ON library_book.id = library_checkout_line.book_id
            LEFT JOIN library_author
                ON library_author.id = library_book.book_author_id
            LEFT JOIN library_genres
                ON library_genres.id = library_book.genres_id
            LEFT JOIN library_book_library_tags_rel
                ON library_book_library_tags_rel.library_book_id = library_book.id
            LEFT JOIN library_tags
                ON library_tags.id = library_book_library_tags_rel.library_tags_id
            WHERE 1=1
        """
        params = []

        if self.members_id:
            query += " AND library_checkout.customer_id = %s"
            params.append(self.members_id.id)
        if self.checkout_date:
            query += " AND library_checkout.checkout_date >= %s"
            params.append(self.checkout_date)
        if self.return_date:
            query += " AND library_checkout.checkout_return <= %s"
            params.append(self.return_date)
        if self.book_id:
            query += " AND library_checkout_line.book_id = %s"
            params.append(self.book_id.id)
        if self.category_id:
            query += " AND library_tags.id = %s"
            params.append(self.category_id.id)
        if self.genre_id:
            query += " AND library_genres.id = %s"
            params.append(self.genre_id.id)

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
        query += f" ORDER BY {self.sort} {self.sort_by}"

        self.env.cr.execute(query, params)
        return self.env.cr.dictfetchall()

    def add_report_action(self):
        values = self._fetch_report_data()
        data = {
            'lines': values,
            'partner_name': self.members_id.name if self.members_id else None,
            'book_name': self.book_id.name if self.book_id else None,
            'genres_name': self.genre_id.name if self.genre_id else None,
            'tag_name': self.category_id.name if self.category_id else None,
        }
        return self.env.ref(
            'library_management.action_library_report_print'
        ).report_action(self, data=data)

    def add_report_xlsx_action(self):
        """Trigger XLSX download via JS"""
        data = {
            'members_id': self.members_id.id or False,
            'book_id': self.book_id.id or False,
            'category_id': self.category_id.id or False,
            'genre_id': self.genre_id.id or False,
            'checkout_date': str(self.checkout_date) if self.checkout_date else False,
            'return_date': str(self.return_date) if self.return_date else False,
            'sort': self.sort or 'library_checkout.checkout_date',
            'sort_by': self.sort_by or 'ASC',
        }
        return {
            'type': 'ir.actions.report',
            'data': {
                'options': json.dumps(data, default=json_default),
                'output_format': 'xlsx',
                'report_name': 'Library Management Report',
            },
            'report_type': 'xlsx',
        }

    def generate_xlsx_report(self, options, response):
        """Generate xlsx report — called from controller"""
        lines = self._fetch_report_data()
        print(options)
        print(options['members_id'])
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Library Report')

        head = workbook.add_format({
            'align': 'center', 'bold': True, 'font_size': 16,
        })
        head_colour = workbook.add_format({
            'align': 'center', 'bold': True, 'font_size': 14, 'bg_color': '#AAAAAA'
        })
        col_head = workbook.add_format({
            'bold': True, 'align': 'center',
            'font_size': 12, 'border': 1,
        })
        cell_fmt = workbook.add_format({
            'align': 'center', 'font_size': 11, 'border': 1,
        })
        cell_fmt_colour = workbook.add_format({
            'align': 'center', 'font_size': 11, 'border': 1,'bg_color': '#FFAA12'
        })
        sheet.merge_range('A1:H3', 'Library Management Report', head)

        headers = [
            'Reference ID', 'Member', 'Book Name', 'Author',
            'Checkout Date', 'Return Date', 'Category', 'Genre',
        ]

        option_keys = [
            None, 'members_id', 'book_id', 'author',
            'checkout_date', 'return_date', 'category_id', 'genre_id'
        ]

        headers1 = []

        for header, key in zip(headers, option_keys):
            if key is None or not options.get(key):
                headers1.append(header)

        print(headers1)
        for col, header in enumerate(headers1):
            sheet.write(7, col, header, col_head)
            sheet.set_column(col, col, 20)

        for i, record in enumerate(lines, start=9):
            checkout = record.get('checkout_date')
            return_d = record.get('return_date')
            member_name = record.get('member_name')
            book_name = record.get('book_name')
            category_id = record.get('category')
            genre_id = record.get('genre')
            print(category_id)
            print(genre_id)
            a=0
            b=0
            c=0
            d=0
            for j in range(4):
                if a==0:
                    if options['members_id']:
                        a=1
                        sheet._write(4,j,'member_name', head_colour)
                        sheet.write(5, j, member_name, cell_fmt_colour)
                        continue
                if b==0:
                    if options['book_id']:
                        b=1
                        sheet._write(4, j, 'book_name ', head_colour)
                        sheet.write(5, j, book_name, cell_fmt_colour)
                        continue
                if c==0:
                    if options['genre_id']:
                        c=1
                        sheet._write(4, j, 'genres ', head_colour)
                        sheet.write(5, j, genre_id, cell_fmt_colour)
                        continue
                if d==0:
                    if options['category_id']:
                        sheet._write(4, j, 'category ', head_colour)
                        sheet.write(5, j, category_id, cell_fmt_colour)
                        d=1
                        continue

            column = 0
            sheet.write(i, column, record.get('reference_id') or '', cell_fmt)
            column += 1
            if not options['members_id']:
                sheet.write(i, column, record.get('member_name') or '', cell_fmt)
                member_name = record.get('member_name')
                column += 1
            if not options['book_id']:
                sheet.write(i, column, record.get('book_name') or '', cell_fmt)
                column += 1
            sheet.write(i, column, record.get('author') or '', cell_fmt)
            column += 1
            sheet.write(i, column, str(checkout)[:16] if checkout else '', cell_fmt)
            column += 1
            sheet.write(i, column, str(return_d)[:16] if return_d else '', cell_fmt)
            column += 1
            if not options['category_id']:
                sheet.write(i, column, record.get('category') or '', cell_fmt)
                column += 1
            if not options['genre_id']:
                sheet.write(i, column, record.get('genre') or '', cell_fmt)

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
