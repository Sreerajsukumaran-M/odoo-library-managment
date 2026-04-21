# -*- coding: utf-8 -*-
from odoo import fields, models


class LibraryAuthor(models.Model):
    _name = 'library.author'
    _description = 'Library Author'

    name = fields.Char(string='Author', required=True)
    description = fields.Text(string='Description')
    book_ids = fields.One2many('library.book', 'book_author_id', string='Book')
