# -*- coding: utf-8 -*-
from odoo import fields, models


class LibraryGenres(models.Model):
    _name = 'library.genres'
    _description = 'Library Genres'

    name = fields.Char(required=True)
    description = fields.Text()
    book_ids = fields.One2many('library.book', 'genres_id', string='Book')
