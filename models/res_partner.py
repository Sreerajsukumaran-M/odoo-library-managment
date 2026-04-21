# -*- coding: utf-8 -*-


from odoo import fields, models, api


# from odoo.addons.test_convert.tests.test_env import record
# from odoo.orm.types import ValuesType
# from odoo.release import product_name


class ResPartner(models.Model):
    _inherit = 'res.partner'

    maximum_limit = fields.Integer(string="Maximum Book")
    book_id = fields.Many2one(comodel_name='library.book', string='Book')
    book_count = fields.Integer(string="Books")
    total_penalty = fields.Integer(string="Total Penalty", compute='_compute_total_penalty')
    late_return = fields.Integer(string="late Return", compute='_compute_late_return')

    @api.model_create_multi
    def create(self, vals_list):
        """setting default values for maximum book limit"""

        limit = int(self.env['ir.config_parameter'].sudo().get_param('library_settings.maximum_book'))

        if limit > 0:
            for val in vals_list:
                val['maximum_limit'] = limit

            return super().create(vals_list)

    def action_book_smarticon(self):
        """smart icon for total books"""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'library.checkout.line',
            'view_mode': 'list,form',
            'domain': [('checkout_id.customer_id', '=', self.id)],
            'target': 'current'
        }

    def action_late_return_smarticon(self):
        """smart icon for total late return"""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'library.checkout',
            'view_mode': 'list,form',
            'domain': [('customer_id', '=', self.id), ('late_return', '=', True)],
            'target': 'current'
        }

    def action_total_penalty_smarticon(self):
        """smart icon for total_penalty"""
        self.ensure_one()

    def calculate_count(self):
        """calculating the total book count"""

        for record in self:
            record.book_count = len(self.env['library.checkout.line']
                                    .search([('checkout_id.customer_id', '=', record.id)]))
            print(record.book_count)

    @api.depends('late_return')
    def _compute_late_return(self):
        """calculating the total late return and total penalty"""

        for record in self:
            checkouts = self.env['library.checkout'].search(
                [('customer_id', '=', record.id), ('late_return', '=', True)])

            record.late_return = len(checkouts)
            print(record.late_return)
            print(checkouts)

    def _compute_total_penalty(self):
        for record in self:
            checkouts = self.env['library.checkout'].search(
                [('customer_id', '=', record.id), ('late_return', '=', True)])

        record.total_penalty = sum(checkouts.mapped('penalty'))
        print(record.total_penalty, "penalty")
