from odoo import models, fields, api, _


class GeneralRetirement(models.Model):

    _name = 'general.retirement'
    _description = 'General Retirement'

    item_description = fields.Char(
        string='Item Description',
        required=True
    )
    obligated_budget = fields.Float(string='Obligated Budget')
    amount_spent = fields.Float(string='Amount Spent')
    balance = fields.Float(string='Balance', compute='_compute_amount',store=True)
    doc_ref_number = fields.Char(string='Doc. Ref #')
    imprest_id = fields.Many2one(
        'imprest.retirement',
        string='Application',
    )
    @api.depends('obligated_budget', 'amount_spent')
    def _compute_amount(self):
        for rec in self:
            rec.balance = rec.obligated_budget - rec.amount_spent




class NonMstStaff(models.Model):

    _name = 'nonmst.retirement'
    _description = 'Non MST Staffs'

    item_description = fields.Char(
        string='Staff Description',
        required=True
    )

    obligated_budget = fields.Float(string='Obligated Budget')
    amount_spent = fields.Float(string='Amount Spent')
    balance = fields.Float(string='Balance', compute='_compute_amount', store=True)
    doc_ref_number = fields.Char(string='Doc. Ref #')
    imprest_id = fields.Many2one(
        'imprest.retirement',
        string='Application',
    )

    @api.depends('obligated_budget', 'amount_spent')
    def _compute_amount(self):
        for rec in self:
            rec.balance = rec.obligated_budget - rec.amount_spent

    imprest_id2 = fields.Many2one(
        'imprest.retirement',
        string='Non MST staff',
    )

class BankDetails(models.Model):
    _name = 'bank.details'
    _description = 'Bank details'

    bank=fields.Char(string='Name of bank')
    attachment = fields.Char(string="Doc REF")
    amount=fields.Float(string='amount depositeds')
    imprest_id3 = fields.Many2one(
        'imprest.retirement',
        string='Bank Details'
    )
