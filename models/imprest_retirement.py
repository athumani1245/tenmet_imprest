# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError


class ImprestRetirement(models.Model):
    _name = 'imprest.retirement'
    _description = 'Imprest Retirement'
    _order = 'name desc'
    _inherit = 'mail.thread'



    name = fields.Char(string='Payment Requisition', copy=False, default=lambda self: ('New'), readonly=True)
    imprest_ref = fields.Char(string='Imprest Application #')
    # imprest_ref_id = fields.Char(string='Imprest Application #')
    # imprest_reference = fields.Many2one('imprest.application',string='Imprest Reference')
    created_by_id = fields.Many2one('hr.employee', readonly=True, string='Created by')
    # new added
    imprest_ref_id = fields.Many2one('imprest.application',string='Imprest Application Refs#')
    currency_id = fields.Many2one('res.currency',string='company currency', default=lambda self: self.env.company.currency_id)
    #ben used it
    currency_used = fields.Text(string='company currency')
    #ben used it
    retirement_applicant_id = fields.Char(string='Applicant', required=True)
    retirement_applicant = fields.Many2one('hr.employee',string='Applicant', required=True)
    retirement_activity = fields.Char(string='Activity')
    retirement_project = fields.Char(string='Project')
    retirement_purpose = fields.Text(string='Purpose')
    jornal=fields.Char(string="Jurnal number")
    date = fields.Date(string='Date', default=datetime.today())
    imprest_amount = fields.Float(string='Imprest Amount')
    imprest_retirement_line_ids = fields.One2many('imprest.retirement.lines', 'imprest_retirement_id',
                                                  string='Imprest Lines')
    # newly added for drl and project lines
    imprest_application_project_line_drl = fields.One2many('imprest.retirement.project.drl',
                                                           'drl_rel', string='Drl', track_visibility='onchange')
    imprest_application_project_line_ids = fields.One2many('imprest.retirement.project.lines',
                                                           'imprest_application_project', string='Project',
                                                           track_visibility='onchange')
    drl_percent_total = fields.Float(compute='_compute_drl_perctage_total1', store=True, default=0.0,
                                     string='Total Drl %')
    project_parcentage_total = fields.Float(compute='_compute_project_perctage_total', store=True,
                                            string='Total Parcentage')


    nonmst_id= fields.One2many(
        'nonmst.retirement',
        'imprest_id2',
        string='Non MST STAFFS',
    )

    linezMst = fields.One2many(
        'general.retirement',
        'imprest_id',
        string='General',
    )

    bank_ids = fields.One2many(
        'bank.details',
        'imprest_id3',
        string='Bank Details',
    )

    general_total = fields.Float(
        string='General Total'
    )
    non_mst_total = fields.Float(
        string='Non MST Total')
    amount_advanced = fields.Float(string='Amount Advanced')
    imprest_activity=fields.Selection([
        ('single_project', "Funded by single project"),
        ('multiple_project', "Funded by multiple project")])
    total_amount_spent = fields.Float(string='Amount Spent', compute='_compute_amount_spent')
    retirement_balance = fields.Float(string='Balance', compute='_compute_balance')
    comment = fields.Text(string='Comment')



    #
    # loged_in=fields.Many2one('hr.employee',store=False,string='computed id',default=lambda self: self.env['hr.employee'].search(
    #                                     [('user_id', '=', self.env.uid)], limit=1))


    # @api.depends()
    # def _get_logedin_user(self):
    #     for recx in self:
    #        return recx.env['hr.employee'].search([('user_id'=recx.env.user.id)],limit=1)


    @api.model
    def compute_all_picking_confirmed(self):
        print('><'*1000)
        for datsx in self:
            if datsx.env.user.id==datsx.retirement_applicant.user_id.id:
                datsx.to_show = 1
            else:
                datsx.to_show = 0


    to_show=fields.Integer(compute='compute_all_picking_confirmed',default=0)

    @api.onchange('project_parcentage_total', 'imprest_application_project_line_ids')
    @api.depends('project_parcentage_total', 'imprest_application_project_line_ids')
    def check_project_parcentage_total1(self):
        if self.project_parcentage_total:
            if self.project_parcentage_total > 100:
                # if self.project_parcentage_total > 100 or self.project_parcentage_total < 100:
                raise UserError(
                    "The project parcent exceed's 100%")

    @api.onchange('drl_percent_total', 'imprest_application_project_line_drl')
    @api.depends('drl_percent_total', 'imprest_application_project_line_drl')
    def check_project_parcentage_total2(self):
        if self.drl_percent_total:
            if self.drl_percent_total > 100:
                # if self.project_parcentage_total > 100 or self.project_parcentage_total < 100:
                raise UserError(
                    "The project drl parcent exceed's 100%")


    @api.onchange('imprest_application_project_line_ids.project_percentage','project_parcentage_total', 'imprest_application_project_line_ids')
    @api.depends('imprest_application_project_line_ids.project_percentage','project_parcentage_total', 'imprest_application_project_line_ids')
    def _calc_amount(self):
        for benz in self.imprest_application_project_line_ids:
            if benz.project_percentage:
                tot=benz.project_percentage/100 * self.total_amount_spent
                benz.write({'project_amount': tot})



    # newly added for drl and project lines
    @api.depends('imprest_application_project_line_drl')
    def _compute_drl_perctage_total1(self):
        for items2 in self:
            total_parcentage = 0.0
            for line in items2.imprest_application_project_line_drl:
                total_parcentage += line.drl_percent
            items2.drl_percent_total = total_parcentage

    @api.depends('imprest_application_project_line_ids')
    def _compute_project_perctage_total(self):
        for items1 in self:
            total_parcentage = 0.0
            for line in items1.imprest_application_project_line_ids:
                total_parcentage += line.project_percentage
            items1.project_parcentage_total = total_parcentage
    #it4business_dms_file_id = fields.Many2one('it4business_dms.file', string="Document", store=True, default=lambda self: self.env['it4business_dms.file'].search([('user_id', '=', self.env.uid)]))
    state = fields.Selection([
        ('draft', "Draft"),
        ('submitted', "Submitted"),
        ('authorized', "Authorized"),
        ('certified', "Certified"),
        ('verify', "F.O Verified"),
        ('account2', "Completed Retirement"),
        ('posted', "View Claims"),
        ('pending', "Pending"),
        ('rejected', "Rejected")], default='draft', track_visibility='onchange')

    current_user = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.user.id)

    # who created only to be readonly

    #
    # authorizer_id = fields.Many2one('res.users', string='To Authorise (Line Manager)')
    # certifier_id = fields.Many2one('res.users', string='To Certify (Project Manager)')
    # approver_id = fields.Many2one('res.users', string='To Approve (Accountant 1/2)')

    # ben modifies
    authorizer_id = fields.Many2one('res.users', string='To Authorise (Line Manager)')
    # certifier_id = fields.Many2one('res.users', string='To Certify (Project Manager)')
    certifier_id = fields.Many2many('res.users' ,'cet_lef',string='To Certify (Project Manager)')
    approver_id = fields.Many2many('res.users', 'cet_rig',string='To Approve (Accountant 1/2)')
    # ben modifies
    account1_id = fields.Many2one('res.users',string='To Verify')
    account2_id = fields.Many2one('res.users',string='Account2')
    # verify_idz = fields.Many2one('res.users',string='Verify')
    is_authorizer = fields.Boolean(string='Is Authorizer', compute='_is_authorizer', default=False)
    is_certifier = fields.Boolean(string='Is Certifier', compute='_is_certifier', default=False)
    is_approver = fields.Boolean(string='Is Approver', compute='_is_approver', default=False)
    authorized_by = fields.Many2one('hr.employee', string='Authorized By')
    certified_by = fields.Many2many('hr.employee','rt_re', string='Certified By')
    approved_by = fields.Many2one('hr.employee', string='Approved By')

    date_authorized = fields.Datetime(string='Date Authorized')
    date_certified = fields.Datetime(string='Date Certified')
    date_approved = fields.Datetime(string='Date Approved')
    # @api.model
    # def default_get(self, fields):
    #     res = super(ImprestRetirement, self).default_get(fields)
    #     res['account1_id'] = 736


    # Determine if logged-in user is the one to authorize
    @api.depends('current_user')
    def _is_authorizer(self):
        if self.env.user.id == self.authorizer_id.id:
            self.is_authorizer = True
        else:
            self.is_authorizer = False

    # Determine if logged in user is the one to certify
    @api.depends('current_user')
    def _is_certifier(self):
        if self.env.user.id in self.certifier_id.ids:
            self.is_certifier = True
        else:
            self.is_certifier = False

    # Determine if logged in user is the one to approve
    @api.depends('current_user')
    def _is_approver(self):
        if self.env.user.id in self.approver_id.ids:
            self.is_approver = True
        else:
            self.is_approver = False

    @api.model
    def create(self, vals):
        if 'name' not in vals or vals['name'] == ('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('imprest.retirement') or ('New')
            return super(ImprestRetirement, self).create(vals)

    @api.depends('imprest_retirement_line_ids','nonmst_id','linezMst')
    def _compute_amount_spent(self):
        for retirement in self:
            total = 0.0
            for line in retirement.imprest_retirement_line_ids:
                total += line.amount_spent

            for lis in retirement.nonmst_id:
                total += lis.amount_spent
# kwa sababu general cost imetolewa
            # for liss in retirement.linezMst:
            #     total += liss.amount_spent

            retirement.total_amount_spent = total




    @api.depends('imprest_retirement_line_ids','nonmst_id','linezMst')
    def _compute_balance(self):
        for retirement in self:
            total = 0.0
            for line in retirement.imprest_retirement_line_ids:
                total += line.balance

            for lis in retirement.nonmst_id:
                total+=lis.balance
# kwa sababu ya kutoa general totat kwenye hesabu
            # for liss in retirement.linezMst:
            #     total+=liss.balance
            retirement.retirement_balance = total
 # for viewing testing

    def view_imprest_posting(self):
        return {
            'name': 'Retirement Posting',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('ref', '=', self.name)]
        }

    def view_retirement(self):
        return {
            'name': 'Retirement',
            'view_mode': 'tree,form',
            'res_model': 'imprest.retirement',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('imprest_ref', '=', self.name)]
        }

    # for viewing testing

    # def get_file(self):
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'it4business_dms_file_id',
    #         'view_mode': 'tree',
    #         'res_model': 'it4business_dms.file',
    #         'domain': [('id', '=', self.it4business_dms_file_id.id)],
    #         'context': "{'create': True}"
    #     }

    # to view requisition  by ben dev
    def view_requisition(self):
        return {
            'name': 'Claims',
            'view_mode': 'tree,form',
            'res_model': 'imprest.application',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('retirement_ref', '=', self.name)]
        }
    # to view requisition  by ben dev





    def action_draft(self):
        self.write({'state': 'draft'})

    def action_submitted(self):
        for retirements in self:
            if not retirements.imprest_retirement_line_ids:
                raise UserError('Retirement details are missing. Please fill the details before submitting!')
            if not retirements.authorizer_id:
                raise UserError('Include name of Person to authorize the Retirement')
            if not retirements.certifier_id:
                raise UserError('Include name of Person to Certify the Retirement')
            # if not retirements.approver_id:
            #     raise UserError('Include name of Person to Approve the Retirement')

        self.write({'state': 'submitted'})


    def action_authorized(self):
        authorizer = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if self.env.user.id != self.authorizer_id.id:
            raise UserError('Only %s can Authorize or Reject this Application!' % self.authorizer_id.name)
        self.write({'state': 'authorized'})
        self.date_authorized = fields.Datetime.now()

    def action_certified(self):
        certifier = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        if not self.imprest_application_project_line_ids:
            raise UserError('Add at least One Project')
        if self.project_parcentage_total<100:
            raise UserError('Project Contribution Must be 100%')
        if not self.imprest_application_project_line_drl:
            raise UserError(
                'Provide at least one DRL please!!')
        if self.drl_percent_total < 100:
            raise UserError('You can not proceed the application without complete on project DRL 100%.')
        if self.env.user.id not in self.certifier_id.ids:
            err_namez = []
            for ax in self.certifier_id:
                err_namez.append(ax.name)

            raise UserError('Only %s can Certify or Reject this Application!' %err_namez)
        self.write({'state': 'certified'})
        self.date_certified = fields.Datetime.now()



    def action_finance_approve(self):
        if self.env.user.id != self.account1_id.id:
            raise UserError('you can not authorise this request')
        if not self.account2_id:
            raise UserError('Choose accountant to review')
        else:
            self.write({'state': 'verify'})
            self.date_certified = fields.Datetime.now()




    def action_finance_lead_approve(self):
        if self.env.user.id == self.account2_id.id:
            for rec in self:
                if rec.retirement_balance < 0:
                    requisition_mod = self.env['imprest.application']
                    valz = {
                            'applicant_id': rec.retirement_applicant.id,
                            'purpose': rec.retirement_purpose,
                            'date': fields.Datetime.now(),
                            'dateStart': fields.Datetime.now(),
                            'dateEnd': fields.Datetime.now(),
                            'retirement_ref': rec.id,
                            'application_type':'claim',
                            'grand_total':abs(rec.retirement_balance),
                            'imprest_type':'individual',
                            'imprest_total':abs(rec.retirement_balance),
                            'imprest_activity':'single_project',
                            'retirement_ref': rec.id,
                            'imprest_application_line_ids': [(0, 0, {'name': "EXTRA COST (claims from retirement)",
                                                                'line_total':abs(rec.retirement_balance),
                                                                'unit_price': abs(rec.retirement_balance)})],
                            'state':'assign_project_codes'

                        }
                    retirement = requisition_mod.create(valz)
                    self.write({'state': 'posted'})
                    self.date_approved = fields.Datetime.now()
                else:
                    self.write({'state': 'account2'})
                    self.date_approved = fields.Datetime.now()
        else:
            # generating Requisition
            raise UserError('you can not authorise this request')

    def action_post(self):
        self.write({'state': 'posted'})

    def rejectRet(self):
        wizard_retirement_form = self.env.ref(
            'tenmet_imprest.view_retirement_wizard', False).id
        return {
            'name': 'Reject Reason',
            'view_mode': 'form',
            'view_id': wizard_retirement_form,
            'view_type': 'form',
            'res_model': 'reason.reason',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }





class ImprestRetirementLines(models.Model):
    _name = 'imprest.retirement.lines'
    _description = 'Imprest Retirement Lines'

    name = fields.Char(string='Item Description')
    # unit=fields.Many2one('uom.uom', string='Unit',default=lambda self:self.env['uom.uom'].search([('name', '=', 'Units')], limit=1).id)
    unit=fields.Many2one('uom.uom', string='Unit')
    imprest_retirement_id = fields.Many2one('imprest.retirement', string='Imprest Retirement')
    # date = fields.Date(string='Date')
    payee_name = fields.Char(string='Payee Name')
    obligated_budget = fields.Float(string='Obligated Budget')
    amount_spent = fields.Float(string='Amount Spent')
    balance = fields.Float(string='Balance', compute='_compute_amount',store=True)
    doc_ref_number = fields.Char(string='Doc. Ref #')

    state = fields.Selection(related='imprest_retirement_id.state', store=True)
    @api.depends('obligated_budget', 'amount_spent','name')
    def _compute_amount(self):
        for rec in self:
            rec.balance = rec.obligated_budget - rec.amount_spent
            rec.payee_name=rec.imprest_retirement_id.retirement_applicant.name


class ImprestRetirementProjectLines(models.Model):
    _name = 'imprest.retirement.project.lines'
    _description = 'Imprest Retirement Project Lines'

    name = fields.Char(string='Item Description')
    project_codes_ids = fields.Many2one('imprest.retirement', string='Imprest Application')
    imprest_application_project = fields.Many2one('imprest.retirement', string='Imprest Application')
    project_ids = fields.Many2one('project.project', string='Project Name')
    project_manager = fields.Many2one(related='project_ids.user_id', string='Project Manager')
    project_code = fields.Char(related='project_ids.pcode', string='Project Code')
    # project_line = fields.Many2one('imprest.project', string='Cost Lines')
    project_funder = fields.Char(related='project_ids.funder', readonly=True, string='Project Funder')

    # i remove it
    # project_drl = fields.Char('DRL')
    # i remove it


    project_percentage = fields.Float(required=True, string='% Contribution', default=0.0)
    manager_confirmed = fields.Boolean(compute='compute_confirmed', track_visibility='onchange')
    current_user = fields.Integer(string='Active User', track_visibility='onchange',
                                  default=lambda self: self.env.user.id, compute='_compute_user_id')
    project_manager_id = fields.Integer(string='Active Project User', track_visibility='onchange',
                                        default=lambda self: self.project_manager.id,
                                        compute='_compute_project_user_id')
    project_amount = fields.Float(string='Amount')




    def _compute_user_id(self):
        for rec in self:
            rec.current_user = self.env.user.id

    def _compute_project_user_id(self):
        for rec in self:
            rec.project_manager_id = rec.project_manager.id

    def compute_confirmed(self):
        for rec in self:
            rec.manager_confirmed = False
            if rec.project_manager.id == self.env.uid:
                rec.manager_confirmed = True
            else:
                rec.manager_confirmed = False








# New drl
class ImprestRetirementProjectDrls(models.Model):
    _name = 'imprest.retirement.project.drl'
    _description = 'Imprest Retirement Project Drl'

    drl_rel = fields.Many2one('imprest.retirement',string='Drl_rel')
    drl_code = fields.Many2one('imprest.project',string='DRL CODE')
    totalDrl=fields.Float(string="Total Drl Cost  Cost" ,store=True)
     # domain = "[('project_id.user_id', '=', 'self.env.uid')]"
    drl_percent = fields.Float(string='DRL Percent(%)')
    drl_amount = fields.Float(string='Amount')
    show_drl=fields.Boolean(default=True)

    # benjamin deus


    # @api.depends('show_drl','drl_code')
    # def check_user_drl(self):
    #     for vvv in self:
    #         refT=vvv.drl_rel.imprest_application_project_line_ids.project_ids
    #         sort_drls = []
    #         for rr in refT:
    #             if vvv.env.uid==rr.user_id.id:
    #                 return True
    #             else:
    #                 return False


# i commented this

    # @api.onchange('drl_code','drl_rel','drl_percent')
    # @api.depends('drl_code','drl_rel','drl_percent')
    # def _dem_data(self):
    #     for red in self:
    #         if red.show_drl==False:
    #             raise UserError("You can not add drl to this project")
    #         else:
    #             refT=red.drl_rel.imprest_application_project_line_ids.project_ids
    #             sort_drls = []
    #             for rr in refT:
    #                 if red.env.uid==rr.user_id.id:
    #                     sort_drls.append(rr.id)
    #                 else:
    #                     sort_drls=sort_drls
    #
    #             dast={}
    #             if sort_drls:
    #                 dast['domain'] = {'drl_code': [('project_id', 'in', sort_drls)]}
    #
    #                 return dast












