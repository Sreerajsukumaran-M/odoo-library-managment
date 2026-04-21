# -*- coding: utf-8 -*-
from odoo import fields, models


class LibraryTags(models.Model):
    _name = 'library.tags'
    _description = 'Library Tags'

    name = fields.Char(string="Book Tags", required=True)
    color = fields.Integer()
