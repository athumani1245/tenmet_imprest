from odoo import models, fields, api, _


class CertifyLimit(models.Model):

    _name = 'certify.limit'
    _description = 'Certify Limits'

    name = fields.Selection(
        [('pm', 'Project Manager'), ('pl', 'Project Lead')])
    user_id = fields.Many2many('res.users', string='Users')
    initial_amount = fields.Float()
    final_amount = fields.Float()
    date = fields.Date()

    