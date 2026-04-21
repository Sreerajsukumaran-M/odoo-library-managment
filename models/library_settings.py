# -*- coding: utf-8 -*-
from odoo import fields, models


class LibrarySettings(models.TransientModel):
    _inherit = 'res.config.settings'

    name = fields.Char(string='Name')
    max_borrowed_days = fields.Integer(string="Maximum number of days to borrow", required=True,
                                       config_parameter='library_settings.max_borrowed_days')
    reminder_days = fields.Integer(string="Reminder", required=True,
                                   config_parameter='library_settings.reminder_days')
    penality_amount = fields.Float(string="Penalty amount", required=True,
                                   config_parameter='library_settings.penality_amount')
    maximum_book = fields.Integer(string="Maximum book amount", default=1, required=True,
                                  config_parameter='library_settings.maximum_book')

    maximum_late_return = fields.Integer(string="Maximum late return", default=1, required=True,
                                         config_parameter='library_settings.maximum_late_return',
                                         help="maximum no of late return books ,you cannot borrow more books")
