from odoo import models, fields, api
from .choices import MIKOA, PLANES
from odoo.exceptions import UserError


class FleetApplication(models.Model):
    _name = 'imprest.fleet.application'
    _description = 'Fleet Application'
    _rec_name = 'fleet_applicant'
    
    fleet_applicant = fields.Many2one('hr.employee',string='Applicant')
    fleet_applicant_id = fields.Many2one('res.users', string='Applicant ID')
    imprest_ref_id = fields.Many2one('imprest.application',string='Imprest')
    certifier_id = fields.Many2one('hr.employee',string='Certifier ID',store=True, compute='_compute_certifier_id')
    approver_id = fields.Many2one('res.users',string='Approver ID',store=True, compute='_compute_approver_id')
    fleet_lines_ids = fields.One2many('imprest.application.fleet.lines', 'fleet_rel',string='Fleet Lines', store=True)
    date = fields.Date(string='Date', required=True)
    state = fields.Selection([('submitted','Submitted'),('approved','Approved'),('certified','Certified'),('cancelled','Cancelled')], string='State', default='submitted', track_visibility='onchange')
    fleet_total = fields.Float(string='Total Fleet Costs', store=True, compute='_compute_total')
    
    def _compute_total(self):
        fleet_total = 0
        for rec in self.fleet_lines_ids:
            self.fleet_total += rec.fleet_cost
    
    def _compute_certifier_id(self):
        for rec in self.imprest_ref_id.fleet_id:
            cert = rec.ids.id
            new = self.env['res.users'].search([('user_id','=',cert)])
            if new:
                for ax in new:
                    cert = ax.id
        self.certifier_id = cert
    # methods for the approvals
    # method to approve the application
    
    def action_approve(self):
        if self.imprest_ref_id.state != 'post':
            raise UserError('Imprest Application is not yet posted')
        if self.env.user.id not in self.imprest_ref_id.fleet_id.ids:
            for ax in self.imprest_ref_id.fleet_id:
                err_namez = ax.name
            raise UserError('Only %s can Certify or Reject this Application!' %err_namez)
        else:
            if self.state == 'submitted' and self.fleet_lines_ids:
                for rec in self.fleet_lines_ids:
                    if not rec.fleet_category:
                        raise UserError('please choose the fleet')
                    if rec.fleet_from == rec.fleet_to:
                        raise UserError('Locations can not be the same')
                    if rec.dep_date > rec.ret_date:
                        raise UserError('Dates are not well arranged')
                    if rec.fleet_cost <= 0:
                        raise UserError('please provide correct fleet amount')
                    if not rec.fleet_time:
                        raise UserError('please provide the time')
                    
                    
            self.state = 'approved'
        
    def action_certify(self):
        # err_namez = None
        # if self.env.user.id not in self.imprest_ref_id.fleet_id.ids:
        #     pass
        #     # for ax in self.imprest_ref_id.fleet_id:
        #     #     err_namez = ax.name
        #     # raise UserError('Only %s can Certify or Reject this Application!' %err_namez)
        # else:
        if self.state == 'approved':
            # now adding the fleet costs to the imprest application
            for rec in self.fleet_lines_ids:
                balance = rec.fleet_category.balance
                if balance < rec.fleet_cost:
                    raise UserError('There is not enough balance in the assigned fleet budget '+str(rec.fleet_rel.name))
                else:
                    # adding the logic to record transaction out
                    
                    self.env['imprest.fleet.plane.transaction.out'].create({
                        'name':rec.fleet_category.id,
                        'amount':rec.fleet_cost,
                        'date':fields.Date.today(),
                        'fleet_line':rec.id
                    })
                    balance = balance - rec.fleet_cost
            self.state = 'certified'
                
                
                
    
    def action_reject(self):
        if self.env.user.id not in self.imprest_ref_id.fleet_id.ids:
            for ax in self.imprest_ref_id.fleet_id:
                err_namez = ax.name
            raise UserError('Only %s can Certify or Reject this Application!' %err_namez)
        else:
            self.state = 'cancelled'
            
            
    def action_reset(self):
        if self.env.user.id not in self.imprest_ref_id.fleet_id.ids:
            for ax in self.imprest_ref_id.fleet_id:
                err_namez = ax.name
            raise UserError('Only %s can Rollback this Application!' %err_namez)
        else:
            self.state = 'submitted'
        

    
class ImplestFleetLinesApplication(models.Model):
    _name='imprest.application.fleet.lines'
    _description="Imprest application fleet lines application"

    fleet_rel = fields.Many2one('imprest.fleet.application')
    applicant = fields.Many2one('hr.employee',string="Fleet Applicant")
    fleet_from = fields.Selection(MIKOA, string = 'From')
    fleet_to = fields.Selection(MIKOA, string= "To")
    fleet_time = fields.Selection([('day','DAY'),('night', 'NIGHT')], string='Time')
    fleet_cost = fields.Float(string='Approximated Trip Cost')
    dep_date = fields.Date(string='Departure Date', track_visibility='always')
    ret_date = fields.Date(string='Return Date', track_visibility='always')
    # fleet_category = fields.Selection(PLANES, string='Fleet Category')
    fleet_category = fields.Many2one('imprest.fleet.planes', string='Fleet Category')
    
    
    
    