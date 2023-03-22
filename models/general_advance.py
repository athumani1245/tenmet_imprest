from odoo import models, fields, api, _


class GeneralAdvance(models.Model):

    _name = 'general.advance'
    _description = 'General Advance'

    item_description = fields.Char(
        string='Item Description',
        required=True
    )

    price = fields.Float(
        string='Price',
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='UOM',
        default=lambda self:self.env['uom.uom'].search([('name', '=', 'Units')], limit=1).id
    )

    qty = fields.Float(
        string='Quantity', default=1.0
    )

    sub_total = fields.Float(
        string='Sub Total',
        compute='_onchange_unit_price'
    )

    imprest_id = fields.Many2one(
        'imprest.application',
        string='Application',
    )

    @api.depends('qty', 'price')
    def _onchange_unit_price(self):
        for rec in self:
            rec.sub_total = rec.qty * rec.price




class NonMstStaff(models.Model):

    _name = 'nonmst.staff'
    _description = 'Non MST Staffs'

    item_description = fields.Char(
        string='Staff Description',
        required=True
    )

    price = fields.Float(
        string='Price',
    )

    uom_id = fields.Many2one(
        'uom.uom',
        string='type',
        default=lambda self: self.env['uom.uom'].search([('name', '=', 'Units')], limit=1).id
    )

    qty = fields.Float(
        string='Quantity', default=1.0
    )

    sub_total = fields.Float(
        string='Sub Total',
        compute='_onchange_unit_price2'
    )

    imprest_id2 = fields.Many2one(
        'imprest.application',
        string='Application',
    )

    @api.depends('qty', 'price')
    def _onchange_unit_price2(self):
        for rec in self:
            rec.sub_total = rec.qty * rec.price
