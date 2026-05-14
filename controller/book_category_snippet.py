# -- coding: utf-8 --
from odoo import http
from odoo.http import request

class WebsiteProduct(http.Controller):

   @http.route('/get_product_categories', auth="public", type='jsonrpc',website=True)
   def get_product_category(self):
       """Get the website categories for the snippet."""

       categories = self.env[
           'library.book'].search_read([('sale_count','>',0)],order='sale_count desc')
       values = {
           'categories': categories,
       }
       return values
