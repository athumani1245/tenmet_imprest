from odoo import models,fields,api

class FleetPlanes(models.Model):
    _name = 'imprest.fleet.planes'
    _description = 'Fleet Planes'
    
    name = fields.Char(string='Airline Name', required=True)
    budget_invisible = fields.Float(string='Budget', readonly=True)
    budget = fields.Float(string='Added Amount', required=True)
    balance = fields.Float(string='Balance',readonly=True, compute='_compute_balance')
    fleet_line = fields.One2many('imprest.application.fleet.lines', 'fleet_category', string='Fleet Line')
    transact_in = fields.One2many('imprest.fleet.plane.transaction.in', 'name', string='Transaction In')
    @api.onchange('budget')
    def onchange_budget(self):
        for record in self:
            if record.budget:
                record.budget_invisible += record.budget
    
    @api.constrains('budget')
    def check_budget(self):
        for record in self:
            if record.budget:
                self.env['imprest.fleet.plane.transaction.in'].create({
                    'name': record.id,
                    'amount': record.budget,
                    'date': fields.Date.today()
                })
    
                
    @api.depends('budget_invisible','fleet_line')
    def _compute_balance(self):
        for record in self:
            record.balance = record.budget_invisible - sum(record.fleet_line.mapped('fleet_cost'))
            
        
    
class PlaneTransactionIn(models.Model):
    _name = 'imprest.fleet.plane.transaction.in'
    _description = 'Plane Transaction In'
    
    name = fields.Many2one('imprest.fleet.planes', string='Airline Name')
    amount = fields.Float(string='Amount', required=True)
    date = fields.Date(string='Date', required=True)
    
class PlaneTransactionOut(models.Model):
    _name = 'imprest.fleet.plane.transaction.out'
    _description = 'Plane Transaction Out'
    
    name = fields.Many2one('imprest.fleet.planes', string='Airline Name', required=True)
    amount = fields.Float(string='Amount', required=True)
    date = fields.Date(string='Date', required=True)
    fleet_line = fields.Many2one('imprest.application.fleet.lines', string='Fleet Line')
    
    