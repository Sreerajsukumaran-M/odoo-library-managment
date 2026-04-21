# -*- coding: utf-8 -*-
from email.policy import default

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'

    reference_number = fields.Char(string="Reference Number", default=lambda self: _('New'), readonly=True, copy=False,
                                   help="Reference Number of the book")
    name = fields.Char(required=True)
    image = fields.Image(max_width=500, max_height=50)
    isbn = fields.Char(string="ISBN", required=True)
    price = fields.Char(string="Price")
    cost = fields.Char(string="Cost")
    publication_date = fields.Datetime(string="Publication Date")
    status = fields.Selection([
        ('available', 'Available'),
        ('unavailable', 'Unavailable'),
        ('coming_soon', 'Coming Soon'),
    ], default='available')

    book_author_id = fields.Many2one('library.author', string="Author")
    publisher_id = fields.Many2one('library.publisher', string="Publisher")
    genres_id = fields.Many2one('library.genres', string="Genre")
    tag_ids = fields.Many2many('library.tags', string="Tag")
    books_count = {}
    user_id = fields.Many2one('res.users', string="User")
    product_id = fields.Many2one('product.product', string="Product")

    @api.model_create_multi
    def create(self, vals_list):
        """reference number calculation"""

        for vals in vals_list:
            if vals.get('reference_number', _('New')) == _('New'):
                vals['reference_number'] = self.env['ir.sequence'].next_by_code('library.book')

            product = self.env['product.product'].create({
                'name': vals.get('name'),
                'list_price': vals.get('price'),
                'standard_price': vals.get('cost'),

            })
            vals['product_id'] = product.id
        return super().create(vals_list)

    @api.constrains('isbn')
    def _check_name(self):
        """ making isbn number unique"""
        for record in self:
            existing = self.search([
                ('isbn', '=', record.isbn),
                ('id', '!=', record.id)
            ])
            if existing:
                raise ValidationError("ISBN already exists")
