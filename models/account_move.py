# -*- coding: utf-8 -*-
from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    checkout_id = fields.Many2one('library.checkout', string="Checkout")
