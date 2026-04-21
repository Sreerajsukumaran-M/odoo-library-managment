# -*- coding: utf-8 -*-
from email.policy import default

from dateutil.relativedelta import relativedelta
from dateutil.utils import today
from docutils.utils.math.tex2mathml_extern import latexml

from odoo import api, fields, models, _, Command
from datetime import datetime, date, timedelta
import time

from odoo.exceptions import UserError


class LibraryCheckout(models.Model):
    _name = 'library.checkout'
    _description = 'Library Checkout'
    _rec_name = 'customer_id'

    cust_reference_number = fields.Char(string="Reference Number", default=lambda self: _('New'),
                                        readonly=True, copy=False,
                                        help="Reference Number of the customer")
    customer_id = fields.Many2one('res.partner', string="Customer", required=True)
    book_id = fields.Many2one('library.book', string="Book")
    email = fields.Char(string="Email", related='customer_id.email')
    phone = fields.Char(related="customer_id.phone", string="Phone")
    checkout_amount = fields.Float(string="Checkout Amount")
    checkout_date = fields.Datetime(string="Checkout Date")
    checkout_due_date = fields.Datetime(string="Checkout Due Date")
    checkout_return = fields.Datetime(string="Checkout Return Date")
    product_id = fields.Many2one('product.product', string="Product")
    account_id = fields.Many2one('account.move', string="Account")

    penalty = fields.Float(string="Penalty Amount", compute='_compute_penalty_amount', store=True)
    state = fields.Selection([('new', 'New'),
                              ('checkout', 'Checkout'),
                              ('returned', 'Returned'),
                              ('overdue', 'Overdue'),
                              ('cancel', 'Cancel')], default='new')
    books_ids = fields.Many2many('library.book', string="Books", required=True)
    checkout_line_ids = fields.One2many('library.checkout.line', 'checkout_id',
                                        string="Checkout Lines", required=True)
    checkout_remainder = fields.Datetime(string="Checkout remainder Date")
    company_id = fields.Many2one('res.company', string="Company")
    reminder_sent = fields.Boolean(default=False)
    overdue_sent = fields.Boolean(default=False)
    late_return = fields.Boolean(default=False)
    payment_bool = fields.Integer(string="Payment Status", compute='_compute_payment_status', default=0)

    @api.depends('checkout_return')
    def _compute_penalty_amount(self):
        """calculating the total late return"""
        for record in self:
            d_date = record.checkout_due_date
            r_date = record.checkout_return
            print(d_date, r_date)
            penalty_amount = float(
                self.env['ir.config_parameter'].sudo().get_param('library_settings.penality_amount'))
            print(penalty_amount, "penalty")
            if d_date < r_date:
                record.sudo().state = 'overdue'
                print(d_date, r_date)
                penalty = (r_date - d_date) / timedelta(hours=1)
                print(penalty)

                record.penalty = penalty_amount * penalty
                print(record.penalty)

    @api.model_create_multi
    def create(self, vals_list):

        """calculating reference number """
        self.env['res.partner'].calculate_count()
        for vals in vals_list:
            if vals.get('cust_reference_number', _('New')) == _('New'):
                vals['cust_reference_number'] = self.env['ir.sequence'].next_by_code('library.checkout')

        return super().create(vals_list)

    def confirm_action(self):

        """confirm button actions """
        for record in self:
            if record.checkout_line_ids:
                record.customer_id.calculate_count()

                record.checkout_date = datetime.now()

                for i in record.checkout_line_ids:
                    i.book_id.sudo().status = 'unavailable'

                max_borrowed = int(
                    self.env['ir.config_parameter'].sudo().get_param('library_settings.max_borrowed_days'))

                record.checkout_due_date = record.sudo().checkout_date + relativedelta(days=max_borrowed)
                remainder_date = int(
                    self.env['ir.config_parameter'].sudo().get_param('library_settings.reminder_days'))

                record.checkout_remainder = record.sudo().checkout_due_date - relativedelta(days=remainder_date)
                book = record.checkout_line_ids.mapped('book_id')

                book_overdue_count = self.search_count(
                    [('customer_id', '=', record.customer_id.id), ('overdue_sent', '=', True)])

                print(book_overdue_count, "helooooooo")

                book_limit = self.search_count([('customer_id', '=', record.customer_id.id),
                                                ('book_id', '=', record.book_id), ('state', '=', 'checkout')])

                maximum_book_limit = self.customer_id.maximum_limit
                print('maximum_book_limit', maximum_book_limit)
                print(book_limit)
                if book_limit:
                    raise UserError("you cannot rent book ,because you didn't return the book")

                if book_overdue_count:
                    raise UserError("you cannot rent book ,because you didn't return the book that has been overdue")

                if book_limit >= maximum_book_limit:
                    raise UserError("limit reached ,please return books already borrowed")

                late_return = record.customer_id.late_return

                print("late_return_count", late_return)
                max_late_return = int(
                    self.env['ir.config_parameter'].sudo().get_param('library_settings.maximum_late_return'))

                if late_return == max_late_return:
                    raise UserError("maximum late return reached")

                record.sudo().state = 'checkout'

            else:
                raise UserError("atleast one  book required")

            return {
                'type': 'ir.actions.act_window',
                'name': 'wizard',
                'res_model': 'library.checkout.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'all_book_id': book.sudo().ids,
                            'checkout': self.sudo().id,
                            }
            }

    def return_action(self):

        """return button actions """
        for record in self:
            record.checkout_return = datetime.now()
            if record.checkout_due_date < record.checkout_return:
                record.late_return = True
                print(record.late_return)

            record._compute_penalty_amount()
            record.sudo().state = 'returned'

            invoice_lines = []

            for line in record.checkout_line_ids:
                if not line.book_id.product_id:
                    raise UserError("product not found ")

                invoice_lines.append(Command.create({
                    'product_id': line.book_id.product_id.id,
                    'name': line.book_id.name,
                    'quantity': 1,
                    'price_unit': line.book_id.price,
                }))
            if record.penalty > 0:
                invoice_lines.append(Command.create({
                    'name': ' Penalty amount',
                    'quantity': 1,
                    'price_unit': record.penalty,
                }))

            invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'checkout_id': record.id,
                'partner_id': record.customer_id.id,
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': invoice_lines,
            })

            invoice.action_post()
            return True
    def cancel_action(self):

        """cancel button actions """
        for record in self:
            record.sudo().state = 'cancel'
            # record._compute_payment_status()

            for i in record.checkout_line_ids:
                i.book_id.sudo().status = 'available'

    def send_checkout_reminder(self):

        """sending  checkout remainder and email when book is overdue"""
        print("sending reminder")
        chekouts = self.search([('state', '=', 'checkout')])
        today = date.today()
        for rec in chekouts:
            if not rec.checkout_remainder:
                continue

            reminder_date = rec.checkout_remainder.date()
            due_date = rec.checkout_due_date.date()

            if today == reminder_date and rec.reminder_sent == False:
                template = self.env.ref(
                    'library_management.email_template_checkout_remainder',
                    raise_if_not_found=False
                )
                if template:
                    template.send_mail(rec.id, force_send=True)
                rec.reminder_sent = True

            if not rec.overdue_sent and due_date < today:
                template = self.env.ref('library_management.email_template_checkout_overdue')
                template.send_mail(rec.id, force_send=True)
                rec.overdue_sent = True
                rec.state = 'overdue'

    @api.onchange('customer_id')
    def late_return_warning(self):
        """late return warning for the customer"""
        for record in self:

            late_return = record.customer_id.late_return

            print("late_return_count", late_return)
            max_late_return = int(
                self.env['ir.config_parameter'].sudo().get_param('library_settings.maximum_late_return'))

            if late_return == max_late_return - 1:
                self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
                    'type': 'danger',
                    'title': _("Warning"),
                    'message': ('maximum late return reached ,this is the last chance '),
                })

    @api.depends('account_id.payment_state')
    def _compute_payment_status(self):
        """computing payment status and check the book available or not available"""
        for record in self:
            payment_check = self.env['account.move'].search(
                [('payment_state', '=', 'paid'), ('checkout_id', '=', record.id)])
            if payment_check:
                record.payment_bool = 1
                print(record.payment_bool)
                print(payment_check)
                print(payment_check.payment_state, "payment status")
                for i in record.checkout_line_ids:
                    i.book_id.sudo().status = 'available'
            else:
                record.payment_bool = 0
