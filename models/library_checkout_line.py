# -*- coding: utf-8 -*-
from odoo import fields, models


class LibraryCheckoutLine(models.Model):
    _name = 'library.checkout.line'
    _description = 'Library checkout Line'

    checkout_id = fields.Many2one('library.checkout', string='Checkout ID', required=True)
    book_id = fields.Many2one('library.book', string='Book', domain=[('status', '=', 'available')])

    customer_id = fields.Many2one('res.partner', string='Customer')
    checkout_date = fields.Datetime(string='Checkout Date')
    referal_number = fields.Char(string='Referal Number', related='checkout_id.cust_reference_number')
    checkout_date = fields.Datetime(string='Checkout Date', related='checkout_id.checkout_date')
    return_date = fields.Datetime(string='Return Date', related='checkout_id.checkout_return')
    due_date = fields.Datetime(string='Due Date', related='checkout_id.checkout_due_date')
