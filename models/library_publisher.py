# -*- coding: utf-8 -*-
from odoo import fields, models


class LibraryPublisher(models.Model):
    _name = 'library.publisher'
    _description = 'Library Publisher'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    book_ids = fields.One2many('library.book', 'publisher_id', string='Book')
