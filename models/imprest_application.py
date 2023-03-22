# -*- coding: utf-8 -*-
from email.policy import default

from odoo import models, fields, api
from datetime import datetime,timedelta
from odoo.exceptions import UserError
import json



class ImprestApplication(models.Model):
    _name = 'imprest.application'
    _description = 'Imprest Application'
    _order = 'name desc'
    _inherit = 'mail.thread'

    def _active_budget(self):
        return self.env['crossovered.budget'].search([('state', 'in', ('confirm', 'validate'))], limit=1).id

    name = fields.Char(string='Imprest Application', copy=False, default=lambda self: ('New'), readonly=True)
    retirement_ref=fields.Many2one('imprest.retirement',string='Retirement Reference#')
    application_type=fields.Selection([
        ('imprest','IMPREST APPLICATION'),
        ('adhoc', 'ADHOC APPLICATION'),
        ('claim', 'CLAIM APPLICATION')

    ], track_visibility='onchange',string='Choose Application Type',default='imprest',required=True)
    applicant_id = fields.Many2one('hr.employee', string='Applicant', required=True)
    imprest_application_project_line_ids = fields.One2many('imprest.application.project.lines',
                                                      'imprest_application_project', string='Project',
                                                           track_visibility='onchange')
    @api.depends('applicant_id')
    def _message_to_retire(self):
        for datx in self:
            checkz=datx.env['imprest.retirement'].search_count([('retirement_applicant','=',self.applicant_id.id),('state','in',['draft','submitted','authorized','certified','rejected'])])
            if checkz >0:
                datx.message_to_retire="You need to retire first before creating new application"
            else:
                datx.message_to_retire=""



    message_to_retire= fields.Text(compute='_message_to_retire')
    imprest_application_project_line_drl = fields.One2many('imprest.application.project.drl',
                                                           'drl_rel', string='Drl', track_visibility='onchange')
    purpose = fields.Text(string='Purpose', required=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.today())
    dateStart = fields.Date(string='Activity Start Date', required=True)
    dateEnd = fields.Date(string='Activity End Date', required=True)
    dateDue = fields.Date(string='Due Date', default=fields.Date.today(),
                          help='Due date will apper after 5 days after financial approval',compute='_compute_due_activitydate')
    
    # adding 15 days to due date to limitthe retirement proccess/ 2nd phase changes ben
    @api.depends('dateEnd')
    @api.onchange('dateEnd')
    def _compute_due_activitydate(self):
        for rec in self:
            if rec.dateEnd:
                rec.dateDue=rec.dateEnd + timedelta(days=15)
            else:
                rec.dateDue=fields.Date.today()
                
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    imprest_application_line_ids = fields.One2many('imprest.application.lines', 'imprest_application_id', track_visibility='onchange')
    drl_percent_total = fields.Float(compute='_compute_drl_perctage_total1', store=True,default=0.0,
                                     string='Total Drl %')
    project_parcentage_total = fields.Float(compute='_compute_project_perctage_total', store=True,
                                            string='Total Parcentage')

    #for drl on change


    grand_total = fields.Float(compute='_compute_grand_total', store=True, string='Total')
    state = fields.Selection([
        ('draft', "Draft"),
        ('submitted', "Submitted"),
        ('training', "Training"),
        ('fleet_manager', "Fleet Approved"),
        ('authorized', "Authorized"),
        ('certified', "Certified"),
        ('approved', "Approved"),
        ('assign_project_codes', "PM's Verified"),
        ('verify', "F.O Verified"),
        ('account1', "Accountant1 Reviewed"),
        ('account2', "Accountant2 Approved"),
        ('finance_lead', "Finance Lead Approved"),
        ('finance_director', "Finance Director Approved"),
        ('country_director', "Country Director Approved"),
        ('post', "Posted"),
        ('posted', "Paid"),
        ('retired', "Retirement Initiated"),
        ('completed','Completed'),
        ('rejected', "Rejected")], default='draft', track_visibility='onchange')
    imprest_activity = fields.Selection([
        ('single_project', "Funded by single project"),
        ('multiple_project', "Funded by multiple project")], track_visibility='onchange')
    def reminder(self):
        template_id = self.env.ref(
            'tenmet_imprest.email_template_mst_imprest_global').id
        template = self.env['mail.template'].browse(template_id)
        template.email_from = self.applicant_id.work_email or self.env.user.email_formatted
        if self.state == 'submitted':
            template.email_to = self.authorizer_id.login
            template.send_mail(self.id, force_send=True)

        # Benjamin Added This Starts
        if self.state == 'fleet_manager':
            template.email_to = self.fleet_id.login
            template.send_mail(self.id, force_send=True)
        # Benjamin Added This ENDs

        if self.state == 'authorized':
            for send_email in self.certifier_id.ids:
                # for send_email in ['bdeus@supercom.co.tz','info@supercom.co.tz']:
                zzz = self.env['res.users'].search([('id', '=', send_email)], limit=1)
                template.email_to = zzz.login
                template.send_mail(self.id, force_send=True)
        if self.state == 'certified':
            for send_email in self.approver_id.ids:
                # for send_email in ['bdeus@supercom.co.tz','info@supercom.co.tz']:
                zzz = self.env['res.users'].search([('id', '=', send_email)], limit=1)
                template.email_to = zzz.login
                template.send_mail(self.id, force_send=True)
        if self.state == 'approved':
            for send_email in self.pm_approver_id.ids:
                # for send_email in ['bdeus@supercom.co.tz','info@supercom.co.tz']:
                zzz = self.env['res.users'].search([('id', '=', send_email)], limit=1)
                template.email_to = zzz.login
                template.send_mail(self.id, force_send=True)
        if self.state == 'assign_project_codes':
            template.email_to = self.verify_id.login
            template.send_mail(self.id, force_send=True)
        if self.state == 'verify':
            template.email_to = self.finance_lead_id.login
            template.send_mail(self.id, force_send=True)
        if self.state == 'finance_lead':
            template.email_to = self.finance_director_id.login
            template.send_mail(self.id, force_send=True)
        if self.state == 'finance_director':
            template.email_to = self.country_dir_id.login
            template.send_mail(self.id, force_send=True)
        if self.state == 'country_director':
            template.email_to = self.post_id.login
            template.send_mail(self.id, force_send=True)
        if self.state == 'post':
            template.email_to = self.paid_id.login
            template.send_mail(self.id, force_send=True)

    #this method is for get the subtotal of employee
    def get_employee_qty(self):
        vals = {}
        for rec in self.imprest_application_line_ids:
            if rec.employee_id.id in vals:
                vals[rec.employee_id.id] += rec.line_total
            else:
                vals.update({rec.employee_id.id: rec.line_total})
        return vals

    @api.onchange('imprest_application_line_ids')
    def _default_approve_limit(self):
        res = self.env['res.users']
        # user_id=-1
        # result = -1
        # for record in self:
        #     users_list = self.env['imprest.limit'].search([('initial_amount', '<', self.grand_total),('final_amount', '>', self.grand_total)]).user_id
        #     print(users_list,self.approver_id)
        #     for items in users_list:
        #         if items:
        #             user_id=items.id
        #             print("approve presents",user_id)
        #         break
        # if user_id!=-1:
        #     result = res.search([('id','=',user_id)])
        return res



    @api.model
    # @api.onchange('fleet_id')
    def default_get(self, fields):
        res = super(ImprestApplication, self).default_get(fields)
        res['applicant_id'] = self.env.user.employee_id.id
        res['verify_id'] = 736
        res['paid_id'] = 420
        res['post_id'] = 420
        res['country_dir_id'] = 430
        res['fleet_id'] = 553
        res['finance_lead_id'] = 425
        res['finance_director_id'] = 428


        # This is intended to return name DAVID FEO for as fiance review and Augusta as for post and pay
        return res

    @api.onchange('imprest_application_line_ids')
    def _default_line_manager(self):
        rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

        for user in rec:
            if user:
                self.authorizer_id = user.parent_id.id
            else:
                self.authorizer_id = False
                # raise ValidationError("Please Set Line Manager of Applicant ")
                raise UserError("Please Set Line Manager of Applicant ")

    is_first_finacial_verify = fields.Boolean(string='first finacial verify', compute='_is_first_finacial_verify',
                                              default=False)
    is_second_finacial_verify = fields.Boolean(string='second finacial verify', compute='_is_second_finacial_verify',
                                               default=False)
    is_third_finacial_verify = fields.Boolean(string='third finacial verify', compute='_is_third_finacial_verify',
                                              default=False)
    is_fourth_finacial_verify = fields.Boolean(string='fourth finacial verify', compute='_is_fourth_finacial_verify',
                                               default=False)
    imprest_type = fields.Selection([('group', 'Group'), ('individual', 'Individual')], default='group')
    current_X_user = fields.Many2one('res.users', string='Current Userx',store=False)
    current_user = fields.Many2one('res.users', 'Current User',compute='_compute_user_id',store=True)
    @api.depends('current_X_user')
    @api.onchange('current_X_user')
    def _compute_user_id(self):
        for rec in self:
            print(f"log in user {rec.current_X_user}")
            return rec.current_X_user



    fleet_id=fields.Many2one('res.users', string='Fleet Manager')
    @api.onchange('fleet_id')
    def _get_many2one_field223(self):
        class_obj =self.env['res.users'].search([])
        teacher_list22 = []
        
        for data22 in class_obj:
            if data22.has_group('tenmet_imprest.group_imprest_fleet'):
                teacher_list22.append(data22.id)
        res223 = {}
        res223['domain'] = {'fleet_id': [('id', 'in', teacher_list22)]}
        return res223

    authorizer_id = fields.Many2one('res.users', string='To Authorise', required=True, store=True)
    authorizer_id_domain = fields.Char(string='Domain to Authorise', compute='_compute_authorizer_id_domain')

    compute = fields.Many2many('res.users' , 'certifer_user_rel','certifer_id','user_id',string='Certifiers',compute='_check_certification_limit')
    compute_pms = fields.Many2many('res.users' , 'pms_user_rel','pm_approvers_id','user_id',string='pms approval',compute='_select_default_pms_to_assign_drl')

    pm_approver_id = fields.Many2many('res.users' , 'pm_users_rel','pm_approvers_id','user_id',string='PM to Assig DRL',domain=lambda self: self.compute_pms)
    
    certifier_id = fields.Many2many('res.users' , 'certifer_users_rel','certifers_id','user_id',string='Certifiers',domain=lambda self: self.compute)
    compute_approvers = fields.Many2many('res.users' , 'approver_user_rel','approver_id','user_id',string='Approvers',compute='_check_approve_limit')
    approver_id = fields.Many2many('res.users' , 'approver_users_rel','approver_id','user_id',string='Approvers',domain=lambda self: self.compute_approvers)
    is_authorizer = fields.Boolean(string='Is Authorizer', compute='_is_authorizer', default=False)
    is_approver = fields.Boolean(string='Is Approver', compute='_is_approver', default=False)



# phase 2 ben impliments
    group_authorize = fields.Many2many('res.users' , 'group_authorize_rel','group_authorize_id','user_id',string='Group Authorize')   


    # @api.depends('applicant_id')
    # @api.onchange('imprest_application_line_ids')
    def _check_certification_group_limit_ben(self):
        for rec in self:
            if rec.imprest_type == 'group' and rec.imprest_application_line_ids:
                data_users = self.env['imprest.application.lines'].search([('imprest_application_id', '=', rec.id)])
                dataxx=[]
                
                for xyz in data_users:
                    dataxx.append(xyz.employee_id.parent_id.user_id.id)
                
                # .user_id
                print(dataxx)
                
                rec.group_authorize = dataxx 

            else:
                rec.group_authorize = [rec.authorizer_id.id]
                # data_users = self.env['certify.limit'].search([('name', '=', 'pl')]).user_id
                # rec.group_authorize = data_users and data_users.ids or False



    authorized_by = fields.Many2many('hr.employee', string='Authorized By')
    # certified_by = fields.Many2one('res.users', string='Certified By')
    # approved_by = fields.Many2one('res.users', string='Approved By')


    authorizer_by = fields.Many2one('res.users',string='Authorized By')
    certifier_by = fields.Many2one('res.users',string='Certified By')
    approver_by = fields.Many2one('res.users', string='Approved By')
    fleetmanager_authorise_by = fields.Many2one( 'res.users',string='Fleet Authoriser')
    pm_approve_by = fields.Many2one( 'res.users',string='Certified By')



    fo_verfy_by = fields.Many2one('res.users',string='Approved By')
    account1_review_by = fields.Many2one('res.users',string='Authorized By')
    account2_approve_by = fields.Many2one('res.users',string='Certified By')
    finance_lead_approved_by = fields.Many2one('res.users',string='Approved By')
    finance_dr_approved_by = fields.Many2one('res.users',string='Authorized By')
    posted_by = fields.Many2one('res.users',string='Certified By')
    paid_by = fields.Many2one('res.users',string='Approved By')
    country_director_by = fields.Many2one('res.users',string='Approved By')

    date_authorized = fields.Datetime(string='Date Authorized')
    date_certified = fields.Datetime(string='Date Certified')
    date_approved = fields.Datetime(string='Date Approved')
    created_by_id = fields.Many2one('hr.employee', readonly=True, string='Created by',
                                    default=lambda self: self.env['hr.employee'].search(
                                        [('user_id', '=', self.env.uid)], limit=1))

    imprest_account_id = fields.Many2one('account.account', string='Imprest Account')
    bank_account_id = fields.Many2one('account.account', string='Bank Account')

    

    verify_id = fields.Many2one('res.users', string='Verify', readonly=True)
    drl_to_display=fields.Float(compute="_drl_to_store_compute",default=0.0,store=False,string='Total Drl amount:')


   
  


    country_dir_id = fields.Many2one(
        'res.users',
        string='Country Director',
    )
    retired_id = fields.Many2one(
        'res.users',
        string='Retired',
    )

    nonmst_id= fields.One2many(
        'nonmst.staff',
        'imprest_id2',
        string='Non MST STAFFS',
    )

    general_ids = fields.One2many(
        'general.advance',
        'imprest_id',
        string='General',
    )

    general_total = fields.Float(
        string='General Total', compute='_compute_general_total'
    )
    non_mst_total = fields.Float(
        string='Non MST STAFFS Total', compute='_compute_nonmst_total'
    )
    url = fields.Char(
        string='URL', compute='compute_url'
    )

    imprest_total = fields.Float(
        string='Imprest Total', compute='_compute_imprest_total'
    )

    @api.depends('nonmst_id','imprest_application_project_line_ids')
    def _compute_nonmst_total(self):
        for items in self:
            total_amount = 0.0
            for line in items.nonmst_id:
                total_amount += line.sub_total
            items.non_mst_total = total_amount




    post_id = fields.Many2one('res.users',string='Post By')
    paid_id = fields.Many2one('res.users',string='Pay By')
    finance_lead_id = fields.Many2one('res.users',string='Finance Lead')
    finance_director_id = fields.Many2one('res.users',string='Finance Director')

    account1_id = fields.Many2one('res.users',string='Account1')
    account2_id = fields.Many2one('res.users',string='Account2')



    @api.onchange('post_id','paid_id')
    def _get_many2one_field(self):
        class_objs =self.env['res.users'].search([])
        teacher_lists = []
        for datas in class_objs:
            if datas.has_group('tenmet_imprest.group_imprest_paypost'):
                teacher_lists.append(datas.id)

        res = {}
        res['domain'] = {'post_id': [('id', 'in', teacher_lists)],'paid_id': [('id', 'in', teacher_lists)]}

        return res






    @api.onchange('verify_id')
    def _get_many2one_field_verify22(self):
        class_obj =self.env['res.users'].search([])
        teacher_list22 = []
        
        for data22 in class_obj:
            if data22.has_group('tenmet_imprest.group_imprest_accountant'):
                teacher_list22.append(data22.id)

        res222 = {}
        res222['domain'] = {'verify_id': [('id', 'in', teacher_list22)]}
        return res222

    @api.onchange('finance_lead_id')
    def _get_many2one_field_finance_lead(self):
        class_obj =self.env['res.users'].search([])
        finance_lead_list = []
        for datad in class_obj:
            if datad.has_group('tenmet_imprest.group_imprest_lead'):
                finance_lead_list.append(datad.id)

        resd = {}
        resd['domain'] = {'finance_lead_id': [('id', 'in', finance_lead_list)]}
        return resd


    @api.onchange('finance_director_id')
    def _get_many2one_field_finance_director(self):
        class_obj =self.env['res.users'].search([])
        finance_director_list = []
        for data_fd in class_obj:
            if data_fd.has_group('tenmet_imprest.group_imprest_director'):
                finance_director_list.append(data_fd.id)

        res_d = {}
        res_d['domain'] = {'finance_director_id': [('id', 'in', finance_director_list)]}
        return res_d

    @api.onchange('account2_id')
    def _get_many2one_field_accountant1and2(self):
        class_obj =self.env['res.users'].search([])
        accountant1and2 = []
        for accountant1and2_data in class_obj:
            if accountant1and2_data.has_group('tenmet_imprest.group_imprest_project_accountant'):
                accountant1and2.append(accountant1and2_data.id)

        res12 = {}
        res12['domain'] = {'account2_id': [('id', 'in', accountant1and2)]}
        return res12

    @api.onchange('account1_id')
    def _get_many2one_field_accountant(self):
        class_obj =self.env['res.users'].search([])
        accountant= []
        for accountant_data in class_obj:
            if accountant_data.has_group('tenmet_imprest.group_imprest_project_accountant'):
                accountant.append(accountant_data.id)

        res123 = {}
        res123['domain'] = {'account1_id': [('id', 'in', accountant)]}
        return res123






# ben add this FLEET concept start here
    is_training=fields.Selection([('yes','Yes'),('no','No')],string='Do you want Training?',help='Choose if you want training',default='no',required=True)
    is_fleet=fields.Selection([('yes','Yes'),('no','No')],string='Do you want Fleet?',help='Choose if you have means of transport',default='no',required=True)
    imprest_fleet=fields.Selection([('car','Car'),('plane','Plane'),('boat','Boat')],string='Fleet',help='Means of transport',default='plane')
    imprest_driver=fields.Many2one('hr.employee',string='Choose Driver',domain="[('job_title', '=', 'Support Office Drivers')]")
   
    imprest_millage=fields.Float(string='Approximeted distance in KM\'s')
    
    
    
    # second phase ben
    show_tab_project=fields.Boolean(string="showing tabs",default=False,compute='compute_showing_project_selection_tab')
     # to reset values
    @api.depends('current_user')
    def compute_showing_project_selection_tab(self):
        for rec in self:
            # rec.manager_confirmed = False
            if rec.authorizer_id.id == self.env.uid and rec.state not in ['draft']:
                rec.show_tab_project = True
                print(rec.authorizer_id.name)
            else:
                rec.show_tab_project = False
                # print(rec.authorizer_id.name + "False")
                # print(self.env.user.employee_id.name)
    
    # second phase ben
    

# ben add this FLEET concept ends here

    @api.depends('imprest_application_line_ids', 'imprest_application_line_ids.line_total')
    def _compute_imprest_total(self):
        for items in self:
            total_amount = 0.0
            for line in items.imprest_application_line_ids:
                total_amount += line.line_total
            items.imprest_total = total_amount



    def compute_url(self):
        url = ''
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        for rec in self:
            base_url += '/web#id=%d&view_type=form&model=%s' % (
                rec.id, self._name)
            rec.url = base_url

    @api.depends('general_ids','imprest_application_project_line_ids')
    def _compute_general_total(self):
        for items in self:
            total_amount = 0.0
            for line in items.general_ids:
                total_amount += line.sub_total
            items.general_total = total_amount
            fleet = self.env['imprest.fleet.application'].search([('imprest_ref_id','=',self.id)])
            if fleet:
                items.general_total = total_amount + fleet.fleet_total


# i comment this due to some issues ben dev

    # @api.onchange('project_parcentage_total', 'imprest_application_project_line_ids')
    # @api.depends('project_parcentage_total', 'imprest_application_project_line_ids')
    # def check_project_parcentage_total1(self):
    #     if self.project_parcentage_total:
    #         if self.project_parcentage_total > 100:
                # if self.project_parcentage_total > 100 or self.project_parcentage_total < 100:
                # raise UserError(
                #     "The project parcent exceed's 100%")

    @api.onchange('drl_percent_total', 'imprest_application_project_line_drl')
    @api.depends('drl_percent_total', 'imprest_application_project_line_drl')
    def check_project_parcentage_total2(self):
        if self.drl_percent_total:
            if self.imprest_application_project_line_drl  and self.imprest_activity=='single_project':
                amountza=0
                for amnt in self.imprest_application_project_line_drl:
                    amountza+=amnt.drl_amount
                if amountza > self.grand_total:
                    raise UserError('Can not exeed grand total amount')
            if self.imprest_application_project_line_drl and self.imprest_activity!='single_project':
                amountza=0
                for amnt in self.imprest_application_project_line_drl:
                    amountza+=amnt.drl_amount
                if round(amountza,1) > round(self.grand_total,1):
                    raise UserError('Can not exeed grand total amount')

    @api.onchange('applicant_id','drl_percent_total', 'imprest_application_project_line_drl')
    @api.depends('applicant_id','drl_percent_total', 'imprest_application_project_line_drl')
    def _drl_to_store_compute(self):
        for recv in self:
            amountza=0
            for amnt in self.imprest_application_project_line_drl:
                amountza+=amnt.drl_amount
            self.drl_to_display=amountza




    @api.onchange('imprest_application_project_line_ids.project_percentage','project_parcentage_total', 'imprest_application_project_line_ids')
    @api.depends('imprest_application_project_line_ids.project_percentage','project_parcentage_total', 'imprest_application_project_line_ids')
    def _calc_amount(self):
        for benz in self.imprest_application_project_line_ids:
            if benz.project_percentage:
                tot=benz.project_percentage/100 * self.grand_total
                benz.write({'project_amount': tot})





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
# generate  randomly codes
    @api.model
    def create(self, vals):
        if 'name' not in vals or vals['name'] == ('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('imprest.application') or ('New')
            return super(ImprestApplication, self).create(vals)

    @api.depends('imprest_total', 'general_total','non_mst_total')
    @api.onchange('imprest_total','general_total','non_mst_total')
    def _compute_grand_total(self):
        for items in self:
            items.grand_total = items.imprest_total + items.general_total + items.non_mst_total

    @api.depends('imprest_application_project_line_ids')
    def _compute_project_perctage_total(self):
        for items in self:
            total_parcentage = 0.0
            for line in items.imprest_application_project_line_ids:
                total_parcentage += line.project_percentage
            items.project_parcentage_total = total_parcentage
            
            if items.project_parcentage_total > 100:
                raise UserError("Contribution percentage can't exceed 100")


# for Drl Computations

    @api.depends('imprest_application_project_line_drl')
    def _compute_drl_perctage_total1(self):
        for items in self:
            total_parcentage = 0.0
            for line in items.imprest_application_project_line_drl:
                total_parcentage += line.drl_percent
            items.drl_percent_total = total_parcentage


    @api.onchange('drl_percent_total', 'imprest_application_project_line_drl')
    @api.depends('drl_percent_total', 'imprest_application_project_line_drl')
    def check_project_parcentage_total2(self):
        if self.drl_percent_total:
            if self.imprest_application_project_line_drl  and self.imprest_activity=='single_project':
                amountza=0
                for amnt in self.imprest_application_project_line_drl:
                    amountza+=amnt.drl_amount
                if round(amountza,1) > round(self.grand_total,1):
                    raise UserError('Can not exeed grand total amount')
            if self.imprest_application_project_line_drl and self.imprest_activity!='single_project':
                amountza=0
                for amnt in self.imprest_application_project_line_drl:
                    amountza+=amnt.drl_amount
                if round(amountza,1) > round(self.grand_total,1):
                    raise UserError('Can not exeed grand total amount')



    def unlink(self):
        if self.state not in ('draft','submitted'):
            raise UserError("You can not delete this record")

    @api.depends('imprest_application_line_ids', 'applicant_id')
    def _compute_authorizer_id_domain(self):
        self.authorizer_id_domain
        result = []

        for rec in self:
            users_list = self.env['imprest.limit'].search(
                [('initial_amount', '<', rec.grand_total), ('final_amount', '>', rec.grand_total)]).user_id
            manager_list = self.env['hr.employee'].search([('id', '=', rec.applicant_id.id)], limit=1).parent_id.user_id
            rec.authorizer_id = manager_list

            for line in rec.imprest_application_project_line_ids:
                project_manager = line.project_manager
                # rec.certifier_id=project_manager
                # rec.approver_id=project_manager

    @api.depends('applicant_id')
    @api.onchange('imprest_activity')
    def _check_certification_limit(self):
        for rec in self:
            if rec.imprest_activity == 'single_project' and rec.grand_total <= 5000000:
                rec.compute = False
                data_users = self.env['certify.limit'].search([('name', '=', 'pm')]).user_id
                rec.compute = data_users and data_users.ids or False

            else:
                rec.compute = False
                data_users = self.env['certify.limit'].search([('name', '=', 'pl')]).user_id
                rec.compute = data_users and data_users.ids or False


    @api.depends('applicant_id')
    @api.onchange('imprest_activity')
    def _select_default_pms_to_assign_drl(self):
        for rec in self:
            rec.compute_pms = False
            data_users_pms = self.env['project.project'].search([('status', '=', 'active')]).user_id
            rec.compute_pms = data_users_pms and data_users_pms.ids or False



    @api.depends('applicant_id')
    @api.onchange('approver_id')
    def _check_approve_limit(self):
        for rec in self:

            rec.compute_approvers = False
            data_users_approver = self.env['imprest.limit'].search([('initial_amount', '<=', rec.grand_total), ('final_amount', '>=', rec.grand_total)]).user_id
            rec.compute_approvers = data_users_approver and data_users_approver.ids or False





    @api.depends('imprest_application_line_ids')
    def _is_first_finacial_verify(self):
        for items in self:
            check = -1
            users_list = self.env['imprest.financial.limit'].search(
                [('name', '=', "1-5M"), ('initial_amount', '<=', items.grand_total),
                 ('threashold_amount', '>', items.grand_total)]).user_id
            for record in users_list:
                if record.id == self.env.uid:
                    check = record.id

            if check != -1:
                items.is_first_finacial_verify = True
            else:
                items.is_first_finacial_verify = False

    @api.depends('imprest_application_line_ids')
    def _is_second_finacial_verify(self):
        for items in self:
            check = -1
            users_list = self.env['imprest.financial.limit'].search(
                [('name', '=', "5-12M"), ('initial_amount', '<=', items.grand_total),
                 ('threashold_amount', '>', items.grand_total)]).user_id

            for record in users_list:
                if record.id == self.env.uid:
                    check = record.id

            if check != -1:
                print('@2'*100)
                items.is_second_finacial_verify = True
            else:
                print('#1' * 100)
                items.is_second_finacial_verify = False

    @api.depends('imprest_application_line_ids')
    def _is_third_finacial_verify(self):
        for items in self:
            check = -1
            users_list = self.env['imprest.financial.limit'].search(
                [('name', '=', "12-25M"), ('initial_amount', '<=', items.grand_total),
                 ('threashold_amount', '>', items.grand_total)]).user_id

            for record in users_list:
                if record.id == self.env.uid:
                    check = record.id
            if check != -1:
                print('@'*100)
                items.is_third_finacial_verify = True
            else:
                print('#' * 100)
                items.is_third_finacial_verify = False

    @api.depends('imprest_application_line_ids')
    def _is_fourth_finacial_verify(self):
        for items in self:
            check = -1
            users_list = self.env['imprest.financial.limit'].search(
                [('name', '=', "25M and above"), ('initial_amount', '<=', items.grand_total),
                 ('threashold_amount', '>', items.grand_total)]).user_id
            for record in users_list:
                if record.id == self.env.uid:
                    check = record.id

            if check != -1:
                items.is_fourth_finacial_verify = True
            else:
                items.is_fourth_finacial_verify = False


    def view_imprest_posting(self):
        return {
            'name': 'Imprest Posting',
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

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_fleet(self):
        if self.env.user.id != self.fleet_id.id:
            raise UserError(
                'Only %s can Review or Reject this Application!' % self.fleet_id.name)
        else:
            self.write({'state': 'fleet_manager','fleetmanager_authorise_by': self.fleet_id.id})



    def action_pay_review(self):
        users_list = self.env['imprest.financial.limit'].search(
            [('name', '=', "1-5M"), ('initial_amount', '<', self.grand_total),
            ('threashold_amount', '>', self.grand_total)]).user_id

        if users_list:

            template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest_global').id
            template = self.env['mail.template'].browse(template_id)
            template.email_from = self.applicant_id.work_email or self.env.user.email_formatted
            template.email_to = self.account2_id.login
            template.send_mail(self.id, force_send=True)
            self.write({'state': 'account1','account1_review_by': self.account1_id.id})
        else:

            template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest_finance_lead').id
            template = self.env['mail.template'].browse(template_id)
            template.email_from = self.applicant_id.work_email or self.env.user.email_formatted
            template.email_to = self.finance_lead_id.login
            template.send_mail(self.id, force_send=True)
            self.write({'state': 'account2','account1_review_by': self.account1_id.id})

    # def action_pm_verify(self):
    #     self.write({'state': 'assign_project_codes'})

    def action_pm_verify(self):
        check=False
        if not self.imprest_application_project_line_drl:
            raise UserError(
                'Provide at least one DRL please!!')

        if self.drl_percent_total < 100:
            raise UserError('You can not proceed the application without complete on project DRL 100%.')
        if self.imprest_application_project_line_drl:
            amountza=0
            for amnt in self.imprest_application_project_line_drl:
                amountza+=amnt.drl_amount
            if round(amountza,1) != round(self.grand_total,1):
                raise UserError('Can not proceed to next stage untill all required PMs fill their contributions')


        if self.env.user.id not in self.pm_approver_id.ids:
            namz12=[]
            for namz in self.pm_approver_id:
                namz12.append(namz.name)

            raise UserError(
                'Only %s can Authorize or Reject this Application!' % namz12)

        else:
            for rec in self.imprest_application_project_line_drl:
                if not rec.drl_code:
                    raise UserError('You can not proceed the application without project DRL.')
                else:
                    pass

            if self.pm_approver_id.ids:
                certifierss = self.pm_approver_id.ids
                template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest_global').id
                template = self.env['mail.template'].browse(template_id)
                for send_email in self.pm_approver_id.ids:
                # for send_email in ['bdeus@supercom.co.tz','info@supercom.co.tz']:
                    zzz=self.env['res.users'].search([('id', '=', send_email)], limit=1)
                    if zzz:
                        template.email_to = zzz.login
                        self.name_email=zzz.name
                        template.send_mail(self.id, force_send=True)
                    else:
                        pass
                self.write({'state': 'assign_project_codes'})



    def reject(self):
        wizard_form = self.env.ref(
            'tenmet_imprest.view_reason_wizard', False).id
        return {
            'name': 'Reject Reason',
            'view_mode': 'form',
            'view_id': wizard_form,
            'view_type': 'form',
            'res_model': 'reason.reason',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def action_fn_verify(self):
        # to limit the requestor untill finishes the retiremens
        checkz=self.env['imprest.retirement'].search_count([('retirement_applicant','=',self.applicant_id.id),('state','in',['draft','submitted','authorized','certified','rejected'])])
        if checkz > 0:
            raise UserError('This request can not be authorized untill the requestor finishes the retirements')
        if self.env.user.id != self.verify_id.id:
            raise UserError(
                'Only %s can Review or Reject this Application!' % self.verify_id.name)

        fo = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

        if self.env.user.id != self.verify_id.id:
            raise UserError('Only %s can Verify or Reject this Application!' % self.fo.name)

        else:

            if self.grand_total >= 12000000:

                template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest_finance_lead').id
                template = self.env['mail.template'].browse(template_id)
                template.email_from = self.applicant_id.work_email or self.env.user.email_formatted
                template.email_to = self.finance_lead_id.login
                template.send_mail(self.id, force_send=True)
                self.write({'state': 'account2'})

            else:

                template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest_global').id
                template = self.env['mail.template'].browse(template_id)
                template.email_from = self.applicant_id.work_email or self.env.user.email_formatted
                template.email_to = self.account1_id.login
                template.send_mail(self.id, force_send=True)
                self.write({'state': 'verify'})



    def action_first_finacial_review(self):
        if self.is_first_finacial_verify:

            template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest_global').id
            template = self.env['mail.template'].browse(template_id)
            template.email_from = self.applicant_id.work_email or self.env.user.email_formatted
            template.email_to = self.account2_id.login
            template.send_mail(self.id, force_send=True)
            self.write({'state': 'post','account2_approve_by': self.account2_id.id})
        else:
            raise UserError('Only User with Respective Limit Can Review this Advance')

    def action_first_finacial_review(self):
        if self.is_first_finacial_verify:

            template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest_global').id
            template = self.env['mail.template'].browse(template_id)
            template.email_from = self.applicant_id.work_email or self.env.user.email_formatted
            template.email_to = self.post_id.login
            template.send_mail(self.id, force_send=True)
            self.write({'state': 'post'})



        else:
            raise UserError('Only User with Respective Limit Can Approve / Reject this Advance')


    def action_finance_lead_approve(self):
        if self.is_second_finacial_verify:
            print('*'*100)
            template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest_global').id
            template = self.env['mail.template'].browse(template_id)
            template.email_from = self.applicant_id.work_email or self.env.user.email_formatted
            template.email_to = self.post_id.login
            template.send_mail(self.id, force_send=True)
            self.write({'state': 'post'})


        elif self.is_third_finacial_verify:

            template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest_global').id
            template = self.env['mail.template'].browse(template_id)
            template.email_from = self.applicant_id.work_email or self.env.user.email_formatted
            template.email_to = self.finance_director_id.login
            template.send_mail(self.id, force_send=True)
            self.write({'state': 'finance_lead'})

        elif self.is_fourth_finacial_verify:
            template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest_global').id
            template = self.env['mail.template'].browse(template_id)
            template.email_from = self.applicant_id.work_email or self.env.user.email_formatted
            template.email_to = self.country_dir_id.login
            template.send_mail(self.id, force_send=True)
            self.write({'state': 'country_director'})
        else:
            raise UserError('Only Finance Lead with Respective Limit can  Approve / Reject this request')


    def action_finance_director_approve(self):
        if self.is_third_finacial_verify:
            template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest_global').id
            template = self.env['mail.template'].browse(template_id)
            template.email_from = self.applicant_id.work_email or self.env.user.email_formatted
            template.email_to = self.post_id.login
            template.send_mail(self.id, force_send=True)
            self.write({'state': 'post'})


        elif self.is_fourth_finacial_verify:


            template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest_global').id
            template = self.env['mail.template'].browse(template_id)
            template.email_from = self.applicant_id.work_email or self.env.user.email_formatted
            template.email_to = self.country_dir_id.login
            template.send_mail(self.id, force_send=True)
            self.write({'state': 'country_director'})



        else:
            raise UserError('Only Finance Director with Respective Limit can  Verify this request')

# showing the tab on the screen
#    @api.depends('imprest_application_line_ids')

    # ,compute='compute_showing_project_selection_tab'
    # @api.onchange('state')
    # @api.depends('state')

                
                






    def action_country_director_approve(self):
        self.write({'state': 'post'})

    def action_finance_lead_reject(self):
        if self.is_second_finacial_verify:
            self.write({'state': 'rejected'})
        elif self.is_third_finacial_verify:
            self.write({'state': 'rejected'})
        elif self.is_fourth_finacial_verify:
            self.write({'state': 'rejected'})
        else:
            raise UserError('Only Financial Lead with Respective Limit can  Reject this request')

    def action_finance_director_reject(self):
        if self.is_third_finacial_verify:
            self.write({'state': 'rejected'})
        elif self.is_fourth_finacial_verify:
            self.write({'state': 'rejected'})
        else:
            raise UserError('Only Financial Director with Respective Limit can  Reject this request')

    def action_first_finacial_reject(self):
        if self.is_third_finacial_verify:
            self.write({'state': 'rejected'})
        elif self.is_fourth_finacial_verify:
            self.write({'state': 'rejected'})
        else:
            raise UserError('Only Candidate with Respective Limit can  Reject this request')

    def action_country_director_reject(self):
        if self.is_fourth_finacial_verify:
            self.write({'state': 'rejected'})
        else:
            raise UserError('Only Country Director can Reject')

    def action_post(self):
        if self.is_fourth_finacial_verify:
            self.write({'state': 'post'})
        else:
            raise UserError('Only Country Director with Respective Limit can  Reject this request')

    def action_pay(self):
        
       
        # for line in self.imprest_application_project_line_drl_ids
        self.write({'state': 'posted'})
        self.generate_fleet_application()
        
    def action_training(self):
        if self.is_fleet == 'no':
            self._check_certification_group_limit_ben() 
            template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest').id
            template = self.env['mail.template'].browse(template_id)
            template.send_mail(self.id, force_send=True)
            self.write({'state': 'fleet_manager'})
            

        # if self.is_fleet == 'yes':

        else:
            if not applications.fleet_id:

                raise UserError('Include name of Fleet Manager to Approve the Application')
            self._check_certification_group_limit_ben()
            template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest').id
            template = self.env['mail.template'].browse(template_id)
            template.send_mail(self.id, force_send=True)
            self.write({'state': 'training'})



    def action_submitted(self):

        for applications in self:

            if not applications.imprest_application_line_ids:
                raise UserError('Imprest details are missing. Please fill the details before submitting!')
            if not applications.authorizer_id:
                raise UserError('Include name of Person to authorize the Application')
            
            if self.is_training == 'no':
                self._check_certification_group_limit_ben() 
                template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest').id
                template = self.env['mail.template'].browse(template_id)
                template.send_mail(self.id, force_send=True)
                self.write({'state': 'training'})
                
            else:
                self._check_certification_group_limit_ben()
                template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest').id
                template = self.env['mail.template'].browse(template_id)
                template.send_mail(self.id, force_send=True)
                self.write({'state': 'submitted'})

                # field to be used in email template

    name_email=fields.Char(string="Name to display on email")
                # field to be used in email template

    def action_authorized(self):

        
        # if not self.approver_id:
            
        if not self.finance_lead_id:
            raise UserError('Include name of Finance Lead to Approve the Application')

        if not self.finance_director_id:
                raise UserError('Include name of Finance Director to Approve the Application')


        authorizer = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if self.env.user.id != self.authorizer_id.id:
            raise UserError('Only %s can Authorize or Reject this Application!' % self.authorizer_id.name)

        # checking projects
        if not self.imprest_application_project_line_ids:
            raise UserError('Add at least One Project')
        
        # checking projects percentages
        if self.project_parcentage_total<100:
            raise UserError('Project Contribution Must be 100%')
        
        # checkingbother members if they are authirized
        count=0
        for dataz in self.imprest_application_line_ids:
            if dataz.lead_state not in ['approved']:
                count+=1
                
        if count > 0:
            raise UserError("There is still unapproved applicant by one of the line Managers")
        
        # reducing drl amounts from the imprest lines that their lead states are rejected
        
        

                
            
        # checking drl amounts
        if self.imprest_application_project_line_drl:
            amountza=0
            for amnt in self.imprest_application_project_line_drl:
                amountza+=amnt.drl_amount
            if amountza > self.grand_total:
                raise UserError('Can not exeed grand total amount')
            elif amountza < self.grand_total:
                raise UserError('You can not proceed due to issuficient amount')
            else:
                pass
        

 
        for rec in self:

            if rec.imprest_activity == 'single_project' and rec.grand_total <= 5000000:
                if not rec.imprest_application_project_line_drl:
                    raise UserError('You can not proceed the application without project DRL.')
                elif rec.drl_percent_total<100:
                    raise UserError('You can not proceed the application without project less 100% DRL.')
        for x in self:        

            for i in x.imprest_application_project_line_drl:
                
                for j in i.drl_code:
                    
                    if j.amount < i.drl_amount:
                        raise UserError('insufficient amount in some of drl code(s)')
                    else:
                        j.amount = j.amount - i.drl_amount
                        # ben added this?
                        
                        self.env['drl.journal'].create({
                            'drl_rec': j.name,
                            'update_date': fields.Datetime.now(),
                            'vals': j.amount,
                            'imprest': self.id,
                            'drl_id': j.id,})
                        
                        
                        
                        


        template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest_global2').id
        template = self.env['mail.template'].browse(template_id)
 
        for send_email in self.certifier_id.ids:
        # for send_email in ['bdeus@supercom.co.tz','info@supercom.co.tz']:
            zzz=self.env['res.users'].search([('id', '=', send_email)], limit=1)
            template.email_to = zzz.login
            self.name_email=zzz.name
            template.send_mail(self.id, force_send=True)


        self.write({'state': 'authorized'})
        self.date_authorized = fields.Datetime.now()



     
    def action_certified(self):
        if self.env.user.id not in self.certifier_id.ids:
            err_namez = []
            for ax in self.certifier_id:
                err_namez.append(ax.name)

            raise UserError('Only %s can Certify or Reject this Application!' %err_namez)
        if not self.imprest_application_project_line_ids:
            raise UserError('Add at least One Project')
        if self.project_parcentage_total<100:
            raise UserError('Project Contribution Must be 100%')
        if self.imprest_application_project_line_drl:
            amountza=0
            for amnt in self.imprest_application_project_line_drl:
                amountza+=amnt.drl_amount
            if amountza > self.grand_total:
                raise UserError('Can not exeed grand total amount')
            elif amountza < self.grand_total:
                raise UserError('You can not proceed due to issuficient amount')
            else:
                pass


        for rec in self:

            if rec.imprest_activity == 'single_project' and rec.grand_total <= 5000000:
                if not rec.imprest_application_project_line_drl:
                    raise UserError('You can not proceed the application without project DRL.')
                elif rec.drl_percent_total<100:
                    raise UserError('You can not proceed the application without project less 100% DRL.')
                # elif rec.drl_percent_total>100:
                #     raise UserError('You can not proceed the application without project greater 100% DRL.')

                else:
                    if rec.certifier_id:
                        certifierss = rec.certifier_id.ids
                        template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest_global').id
                        template = self.env['mail.template'].browse(template_id)
                        for send_email in self.verify_id.ids:
                            zzz=self.env['res.users'].search([('id', '=', send_email)], limit=1)
                            template.email_to = zzz.login
                            self.name_email=zzz.name
                            template.send_mail(self.id, force_send=True)
                        self.write({'state': 'assign_project_codes'})

                    else:
                        raise UserError('No Certifiers found')


            else:

                certifier = rec.certifier_id.ids
                template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest_global2').id
                template = self.env['mail.template'].browse(template_id)
                for send_email in self.approver_id.ids:
                    zzz=self.env['res.users'].search([('id', '=', send_email)], limit=1)
                    template.email_to = zzz.login
                    self.name_email=zzz.name
                    template.send_mail(self.id, force_send=True)
                self.write({'state': 'certified'})
                self.date_certified = fields.Datetime.now()

    def action_approved(self):

        approver =  self.approver_id.ids
        # approver = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if self.env.user.id not in self.approver_id.ids:
            err_namez = []
            for ax in self.approver_id:
                err_namez.append(ax.name)
            raise UserError('Only %s can Approve or Reject this Application!' %err_namez)
        self.write({'state': 'approved'})
        self.date_approved = fields.Datetime.now()
    
    
    def action_fleet_application(self):
        fleet_obj = self.env['imprest.fleet.application']
        for rec in self:
            fleet_applicant_id = rec.applicant_id.id
            if rec.fleet_lines_ids:
                fleet_lines = []
                for ss in record.fleet_lines_ids:
                    fleet_lines.append(
                            (0, 0, {'applicant': ss.applicant, 'fleet_from': ss.fleet_from, 'fleet_to': ss.fleet_to
                                , 'dep_date': ss.dep_date, 'ret_date': ss.ret_date, 'time':ss.fleet_time, 'fleet_category':ss.fleet_category, 'fleet_cost':ss.fleet_cost or False}))
                
                vals = {
                    'fleet_applicant': record.applicant_id.name,
                    'fleet_applicant_id': record.applicant_id.id,
                    'fleet_purpose': record.purpose,
                    'imprest_ref': record.name,
                    'imprest_ref_id': record.id,
                    'currency_used':record.currency_id.name,
                    'authorizer_id': record.authorizer_id.id,
                    'certifier_id': record.certifier_id.ids,
                    'approver_id': record.approver_id.ids,
                    'fleet_lines_ids': fleet_lines,
                    # 'amount_advanced': sum + sum1 + sum2, we remove general total
                    }
                fleet_application = fleet_obj.create(vals)
                template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest_global').id
                template = self.env['mail.template'].browse(template_id)
                template.email_from = record.paid_id.work_email or self.env.user.email_formatted
                template.email_to = record.applicant_id.work_email
                template.send_mail(self.id, force_send=True)
            self.write({'state': 'submitted'})
                
                
    
    

# Ben Dev Added This
    def action_retired(self):
        if self.imprest_type=='group' and self.application_type=='imprest':
            linezDr = []
            linez = []
            retirement_lines = []
            retirement_lines2 = []
            sum2 = 0
            sum1 = 0
            sum = 0
            linezMst = []
            generalMst = []
            retirement_obj = self.env['imprest.retirement']
            for record in self:
                retirement_applicant_id = record.applicant_id
                if record.imprest_application_project_line_ids:
                    # retirement lines
                    linez=[]
                    for gg in record.imprest_application_project_line_ids:
                        linez.append((0,0,{'name':gg.name,'project_ids':gg.project_ids.id,
                                          'project_manager':gg.project_manager.id,'project_code':gg.project_code or False,'project_funder':gg.project_funder,'project_percentage':gg.project_percentage,
                                          'manager_confirmed':gg.manager_confirmed,'current_user':gg.current_user,'project_manager_id':gg.project_manager_id,'project_amount':gg.project_amount}))

                if record.nonmst_id:
                    # retirement lines
                    sum2=0
                    linezMst=[]
                    for kk in record.nonmst_id:
                        sum2+=kk.sub_total
                        linezMst.append((0,0,{'item_description':kk.item_description,'obligated_budget':kk.sub_total,'amount_spent':kk.sub_total}))

                if record.general_ids:
                    # retirement lines
                    generalMst=[]
                    sum1=0
                    for zz in record.general_ids:
                        sum1 += zz.sub_total
                        generalMst.append((0,0,{'item_description':zz.item_description,'obligated_budget':zz.sub_total,'amount_spent':zz.sub_total}))



                if record.imprest_application_project_line_drl:
                    linezDr=[]
                    for ss in record.imprest_application_project_line_drl:
                        print(ss.drl_code)
                        linezDr.append((0,0,{'totalDrl':ss.totalDrl,'drl_percent':ss.drl_percent,'drl_amount':ss.drl_amount
                                             ,'show_drl':True,'drl_code':ss.drl_code.id or False}))
                    print(linezDr)


                if record.imprest_application_line_ids:
                    retirement_lines = []
                    retirement_lines2 = []
                    sum=0
                    for items23 in record.imprest_application_line_ids:
                        retirement_lines2.append(items23.employee_id.id)
                    print(retirement_lines2)
                    # to remove duplicated from list
                    nodub_list = list(set(retirement_lines2))
                    print(nodub_list)

                            # for application were the requestor is not the part of the imprest
                    if record.applicant_id.id not in nodub_list and (linezMst or generalMst):
                        vals = {
                            'retirement_applicant_id': record.applicant_id.name,
                            'retirement_applicant': record.applicant_id.id,
                            'retirement_purpose': record.purpose,
                            'imprest_ref': record.name,
                            'imprest_ref_id': record.id,
                            'account1_id': record.verify_id.id,
                            'created_by_id': record.applicant_id.id,
                            'account2_id': record.account2_id.id,
                            'currency_used': record.currency_id.name,
                            'imprest_activity': record.imprest_activity,
                            'authorizer_id': record.authorizer_id.id,
                            'certifier_id': record.certifier_id.ids,
                            'approver_id': record.approver_id.ids,
                            'imprest_application_project_line_ids': linez,
                            'imprest_application_project_line_drl': linezDr,
                            'amount_advanced': sum + sum2,
                            # 'amount_advanced': sum + sum1 + sum2, we remove general toatal
                            'imprest_retirement_line_ids': retirement_lines,
                            'nonmst_id': linezMst or False,
                            'linezMst': generalMst or False,
                            'general_total': sum1 or 0.0,
                            'non_mst_total': sum2 or 0.0,
                        }
                        print(f'this is the vibez {vals}_____________________________________')
                        retirement = retirement_obj.create(vals)
                        template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest_global').id
                        template = self.env['mail.template'].browse(template_id)
                        template.email_from = record.paid_id.work_email or self.env.user.email_formatted
                        template.email_to = record.applicant_id.work_email
                        template.send_mail(self.id, force_send=True)

                    for ccc in nodub_list:
                        data11=[]
                        sum = 0
                        for rec1 in record.imprest_application_line_ids:
                            if rec1.employee_id.id==ccc:

                                for x in rec1:
                                    sum+=x.line_total
                                    data11.append((0,0,{'name': x.name or False,'unit':x.product_uom_id.id, 'obligated_budget': x.line_total,'amount_spent': x.line_total,'payee_name': retirement_applicant_id.name}))
                            else:
                                pass
                        vals = {
                                'retirement_applicant_id': x.employee_id.name,
                                'retirement_applicant': x.employee_id.id,
                                'retirement_purpose': record.purpose,
                                'account1_id':record.verify_id.id,
                                'account2_id':record.account2_id.id,
                                'imprest_ref': record.name,
                                'imprest_ref_id': record.id,
                                'created_by_id': x.employee_id.id,
                                'currency_used': record.currency_id.name,
                                'imprest_activity':record.imprest_activity,
                                'authorizer_id':record.authorizer_id.id,
                                'certifier_id':record.certifier_id.ids,
                                'approver_id':record.approver_id.ids,
                                'imprest_application_project_line_drl':linezDr,
                                'amount_advanced':sum,
                                'imprest_retirement_line_ids': data11 or False,
                                'imprest_application_project_line_ids':linez,
                                'nonmst_id':linezMst or False,
                                'linezMst':generalMst or False,
                                'general_total':sum1 or 0.0,
                                'non_mst_total':sum2 or 0.0,
                          }
                        retirement = retirement_obj.create(vals)
                        template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest_global').id
                        template = self.env['mail.template'].browse(template_id)
                        template.email_from = record.paid_id.work_email or self.env.user.email_formatted
                        template.email_to = rec1.employee_id.work_email
                        template.send_mail(self.id, force_send=True)
            self.write({'state': 'retired'})

        elif self.imprest_type=='individual' and self.application_type=='imprest':
             linezDr = []
             linez = []
             retirement_lines = []
             retirement_lines2 = []
             sum2 = 0
             sum1 = 0
             sum = 0
             linezMst = []
             generalMst = []
             retirement_obj = self.env['imprest.retirement']
             for record in self:
                 retirement_applicant_id = record.applicant_id

                 if record.imprest_application_project_line_ids:
                     linez = []
                     for gg in record.imprest_application_project_line_ids:
                         linez.append((0, 0, {'name': gg.name, 'project_ids': gg.project_ids.id,
                                              'project_manager': gg.project_manager.id,
                                              'project_code': gg.project_code or False, 'project_funder': gg.project_funder,
                                              'project_percentage': gg.project_percentage,
                                              'manager_confirmed': gg.manager_confirmed, 'current_user': gg.current_user,
                                              'project_manager_id': gg.project_manager_id,
                                              'project_amount': gg.project_amount}))

                 if record.nonmst_id:   
                     # retirement lines
                     sum2 = 0
                     linezMst = []
                     for kk in record.nonmst_id:
                         sum2 += kk.sub_total
                         linezMst.append((0, 0,
                                          {'item_description': kk.item_description, 'obligated_budget': kk.sub_total,
                                           'amount_spent': kk.sub_total}))

                 if record.general_ids:
                     # retirement lines
                     generalMst = []
                     sum1 = 0
                     for zz in record.general_ids:
                         sum1 += zz.sub_total
                         generalMst.append((0, 0,
                                            {'item_description': zz.item_description, 'obligated_budget': zz.sub_total,
                                             'amount_spent': zz.sub_total}))

                 if record.imprest_application_project_line_drl:
                     linezDr = []
                     for ss in record.imprest_application_project_line_drl:
                         print(ss.drl_code)
                         linezDr.append(
                             (0, 0, {'totalDrl': ss.totalDrl, 'drl_percent': ss.drl_percent, 'drl_amount': ss.drl_amount
                                 , 'show_drl': True, 'drl_code': ss.drl_code.id or False}))
                     print(linezDr)
                 if record.imprest_application_line_ids:
                     retirement_lines = []
                     sum=0
                     for x in record.imprest_application_line_ids:
                         sum += x.line_total
                         retirement_lines.append((0, 0, {'name': x.name ,'unit':x.product_uom_id.id, 'obligated_budget': x.line_total,'amount_spent': x.line_total,'payee_name': retirement_applicant_id.name}))
                     vals = {
                             'retirement_applicant_id': record.applicant_id.name,
                             'retirement_applicant': record.applicant_id.id,
                             'retirement_purpose': record.purpose,
                             'imprest_ref': record.name,
                             'imprest_ref_id': record.id,
                             'account1_id': record.verify_id.id,
                             'created_by_id': record.applicant_id.id,
                             'account2_id': record.account2_id.id,
                             'currency_used':record.currency_id.name,
                             'imprest_activity': record.imprest_activity,
                             'authorizer_id': record.authorizer_id.id,
                             'certifier_id': record.certifier_id.ids,
                             'approver_id': record.approver_id.ids,
                             'imprest_application_project_line_ids': linez,
                             'imprest_application_project_line_drl': linezDr,
                             'amount_advanced':sum + sum2,
                             # 'amount_advanced': sum + sum1 + sum2, we remove general total
                             'imprest_retirement_line_ids': retirement_lines,
                             'nonmst_id': linezMst or False,
                             'linezMst': generalMst or False,
                             'general_total': sum1 or 0.0,
                             'non_mst_total': sum2 or 0.0,
                     }
                     retirement = retirement_obj.create(vals)
                     template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest_global').id
                     template = self.env['mail.template'].browse(template_id)
                     template.email_from = record.paid_id.work_email or self.env.user.email_formatted
                     template.email_to = record.applicant_id.work_email
                     template.send_mail(self.id, force_send=True)
             self.write({'state': 'retired'})

        elif self.application_type != 'imprest':
            #emailto be sent to a user for alet on finishing
            self.write({'state': 'completed'})

    # Ben Dev Added This

    def action_reset_to_posted(self):
        self.write({'state': 'posted'})
        
        
        
# ben added this on second phase
    def generate_fleet_application(self):
        fleet_tbl=self.env['imprest.fleet.application']
        # fleet_line_tbl=self.env['fleet.lines.application']\\\\\
        fleet_lines=[]
        vals={}
        for rec in self:
            if rec.is_fleet == 'yes' and rec.imprest_fleet == 'plane' and rec.fleet_lines_ids:
                for lines in rec.fleet_lines_ids:
                    fleet_lines.append((0,0,{'applicant':lines.applicant.id,'fleet_from':lines.fleet_from,'fleet_to':lines.fleet_to,'fleet_to':lines.fleet_to,'fleet_time':lines.fleet_time,
                                             'fleet_cost':lines.fleet_cost,'dep_date':lines.dep_date,'ret_date':lines.ret_date,
                                             'fleet_category':lines.fleet_category}))
                valz={
                    'fleet_applicant':rec.applicant_id.id,
                    'imprest_ref_id':rec.id,
                    'date':rec.date,
                    'fleet_lines_ids':fleet_lines or False,
                }
                print(valz)
                fleet_tbl.create(valz)
        
        
        
        
# ben added second phase for fleet management lines
    fleet_lines_ids = fields.One2many('imprest.application.fleet.lines',
                                                           'fleet_rel', string='Fleet Lines', track_visibility='onchange')

# athumani changes
class DrlJournal(models.Model):
    _name = 'drl.journal'
    _description = 'Drl Journal' 
    _rec_name = 'imprest'
    
    drl_rec = fields.Char(string='DRL REC')
    drl_code = fields.Char(string='DRL Code')
    update_date = fields.Datetime(required=True, string='Update Date')
    vals = fields.Text(required=True)
    imprest = fields.Many2one('imprest.application',string='Imprest')
    

class DrlsImprests(models.Model):
    _name = 'drls.imprests'
    _description = 'many to many drl relationships with imprests'
    
    
    drl = fields.One2many('drl.journal','drl_rec',string='DRL Transaction')
    name = fields.Char(string='Name')

from .choices import MIKOA, PLANES

class ImplestFleetLines(models.Model):
    _name='imprest.application.fleet.lines'
    _description="Imprest application fleet lines"

    fleet_rel = fields.Many2one('imprest.application')
    applicant = fields.Many2one('hr.employee',string="Applicant", domain=lambda self: self._filter_names())
    fleet_from = fields.Selection(MIKOA, string = 'From')
    fleet_to = fields.Selection(MIKOA, string= "To")
    fleet_time = fields.Selection([('day','DAY'),('night', 'NIGHT')], string='Time')
    fleet_cost = fields.Float(string='Approximated Trip Cost')
    dep_date = fields.Date(string='Departure Date')
    ret_date = fields.Date(string='Return Date')
    fleet_category = fields.Char(string='Fleet Mode')
    
    
    def _filter_names(self):
        users = []
        for rec in self.fleet_rel:
            xyz = rec.employee_id.id
            users.append(xyz)
        return users
    
    
    
# class ImprestFLeet(models.Model):
#     _name  = "imprest.fleet"
#     _description = "Imprest Fleet"
    
#     state = fields.Selection([('submit','Submitted'),('certified','Certified'),('approved','Aproved'),('reject','Reject')], string='Status', default='draft')
#     application_fleet_line_ids = fields.One2many('imprest.application.fleet.lines','fleet_id',string='Fleet Lines')
#     
#     imprest = fields.One2many('extension.imprest.application','fleet_id',string='Imprest')



class ImprestApplicationLines(models.Model):
    _name = 'imprest.application.lines'
    _description = 'Imprest Applcation Lines'
    _rec_name = 'imprest_application_id'
    
    
    imprest_application_id = fields.Many2one('imprest.application', string='Imprest Application')
    employee_id = fields.Many2one('hr.employee', string='Emplyee Name')
    name = fields.Char(string='Item Description')
    product_uom_id = fields.Many2one('uom.uom', string='Unit',default=lambda self:self.env['uom.uom'].search([('name', '=', 'Units')], limit=1).id)
    quantity = fields.Float(string='Quantity', default=1.0)
    unit_price = fields.Float(string='Unit Price', default=0.0)
    line_total = fields.Float(string='Line Total',stored=True)
    manager=fields.Many2one(string='Line Manager',related='employee_id.parent_id')
    lead_state=fields.Selection([('pending','pending'),('approved','approved')]
                               ,string="Project Lead Status",default='pending', track_visibility='onchange')
    
    state=fields.Selection([
        ('draft', "Draft"),
        ('submitted', "Submitted"),
        ('fleet_manager', "Fleet Approved"),
        ('authorized', "Authorized"),
        ('certified', "Certified"),
        ('approved', "Approved"),
        ('assign_project_codes', "PM's Verified"),
        ('verify', "F.O Verified"),
        ('account1', "Accountant1 Reviewed"),
        ('account2', "Accountant2 Approved"),
        ('finance_lead', "Finance Lead Approved"),
        ('finance_director', "Finance Director Approved"),
        ('country_director', "Country Director Approved"),
        ('post', "Posted"),
        ('posted', "Paid"),
        ('retired', "Retirement Initiated"),
        ('completed','Completed'),
        ('rejected', "Rejected")],string="state",related='imprest_application_id.state')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")



# computed field to show button
    btn_is_showing=fields.Boolean(string="Button",default=False,)
    # compute="_btn_compute_showing_line"
    @api.depends('imprest_application_id','manager')
    def _btn_compute_showing_line(self):
        for rec in self:        
            if self.employee_id and self.env.user.employee_id.id == self.manager.id and imprest_application_id.state not in ['draft']:
                self.btn_is_showing=True
            else:
                self.btn_is_showing=False   
            
    
    # btn_is_showing=fields.Boolean(string="Button is showing",default=False, compute="_btn_compute_showing_line")


    @api.onchange('quantity', 'unit_price')
    def _onchange_unit_price(self):
        for rec in self:
            rec.line_total = rec.quantity * rec.unit_price
            
            
# we introduced this for approving members for a group roject snd phase
    def approve_member(self):
        # print(str(self.env.user.employee_id.name) + " dhghjgdfhdfg" + str(self.manager.id))
        if self.env.user.employee_id.id == self.manager.id:
            data=self.env['imprest.application.lines'].search([('id','=',self.id)])
            print(data)
            data.write({'lead_state':'approved'})
            # for dataz in data:
            #     if dataz.id == self.id:
            #         dataz.write({'lead_state':'approved'}) 
            #         print("b"*2000)
                    
            #     else:
            #         print("1"*2000)
            # self.write({'lead_state':'approved'}) 
            print(self.line_total)
            # raise UserError("yes") 
        else:
            raise UserError("You are not His/Her Line Manager")
        # for rec in self:
        # print(self.env.uid + "dhghjgdfhdfg")
        
        
# we introduced this for approving members for a group roject snd phase
    def group_reject_member(self):
        
        if self.env.user.employee_id.id == self.manager.id:
            action = {
                'name': 'Line Manager Reason',
                'type': 'ir.actions.act_window',
                'res_model': 'manager.reason',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
                'context': {'applicant_imprest_application_line_id': self.id}
            }
            return action

        else:
            raise UserError("Denied! You are not His/Her Line Manager")
        
        # for rec in self:
        # print(self.env.uid + "dhghjgdfhdfg")
    


class ImprestApplicationProjectLines(models.Model):
    _name = 'imprest.application.project.lines'
    _description = 'Imprest Applcation Project Lines'

    name = fields.Char(string='Item Description')
    project_codes_ids = fields.Many2one('imprest.application', string='Imprest Application')
    imprest_application_project = fields.Many2one('imprest.application', string='Imprest Application')
    project_ids = fields.Many2one('project.project', string='Project Name')
    project_manager = fields.Many2one(related='project_ids.user_id', string='Project Manager')
    project_code = fields.Char(related='project_ids.pcode', string='Project Code')
    # project_line = fields.Many2one('imprest.project', string='Cost Lines')
    project_funder = fields.Char(related='project_ids.funder', readonly=True, string='Project Funder')
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
            
            
    # we have changed this for line manager        

    def compute_confirmed(self):
        for rec in self:
            rec.manager_confirmed = False
            if rec.project_codes_ids.authorizer_id.id == self.env.user.employee_id.id:
                rec.manager_confirmed = True
            else:
                rec.manager_confirmed = False
                
#    first before second phase             
    # def compute_confirmed(self):
    #     for rec in self:
    #         rec.manager_confirmed = False
    #         if rec.project_manager.id == self.env.uid:
    #             rec.manager_confirmed = True
    #         else:
    #             rec.manager_confirmed = False



class ImprestApplicationProjectDrls(models.Model):
    _name = 'imprest.application.project.drl'
    _description = 'Imprest Applcation Project Drl'

    drl_rel = fields.Many2one('imprest.application',string='Drl_rel')
    drl_code = fields.Many2one('imprest.project',string='DRL CODE')
    totalDrl=fields.Float(string="Total Drl Cost  Cost" ,store=True,compute='_dem_date_amount')
    drl_percent = fields.Float(string='DRL Percent(%)')
    drl_amount = fields.Float(string='Amount',store=True,compute='_get_comp_drlparcent')
    show_drl=fields.Boolean(store=False)



    @api.depends('drl_percent','drl_code')
    def _get_comp_drlparcent(self):
        for dex in self:
            dex.drl_amount=(dex.drl_percent *dex.totalDrl)/100




    @api.onchange('drl_code')
    def _dem_data(self):
        for red in self:
            refT=red.drl_rel.imprest_application_project_line_ids.project_ids
            my_drlz=[]
            for rr in refT:
                dast = {}
                if red.env.uid==red.drl_rel.authorizer_id.id:
                    my_drlz.append(rr.id)
            if not my_drlz:
                raise UserError("You can not add drl to this project")
            else:
                dast={}
                if my_drlz:
                    dast['domain'] = {'drl_code': [('project_id', 'in', my_drlz)]}
                    return dast

    @api.depends('drl_code')
    def _dem_date_amount(self):
        for dataz in self:
            if dataz.drl_code:
               current_drl=dataz.drl_code.project_id
               for dx in dataz.drl_rel.imprest_application_project_line_ids:
                   if dx.project_ids ==current_drl:
                       dataz.totalDrl= dx.project_amount






class ProjectProject(models.Model):
    _inherit = 'project.project'

    funder = fields.Char('Project Funder',required=True)
    budget = fields.Float('Project Budget')
    total_drls = fields.Float('Total amount', compute='get_drl_totals')
    # project_code=fields.One2many('')
    drl_relation = fields.One2many('imprest.project', 'project_id')
    pcode = fields.Char('Project Code',required=True)
    status = fields.Selection([
        ('active', "active"),
        ('inactive', "Inactive")], default="active", help="Technical field for UX purpose.")
    
    @api.onchange('drl_relation.amount')
    @api.depends('drl_relation.amount')
    def get_drl_totals(self):
        for rec in self:
            for drl in rec.drl_relation:
                if rec.total_drls > rec.budget:
                    raise UserError("Total DRLs cannot be greater than the project budget")
                else: 
                    rec.total_drls += drl.amount
                


# new for imprest extension now not used
class ImprestApplicationExtension(models.Model):
    _name = 'extension.imprest.application'
    _description = 'Imprest Application Extension'
    _inherit = 'mail.thread'

    name=fields.Many2one('imprest.application',required=True,string='Imprest REF #',store=True)
    applicant_id = fields.Many2one('hr.employee', string='Applicant', required=True,default=lambda self:self.name.applicant_id)
    date=fields.Date(string="Imprest Application Date",compute='set_date',store=True)
    dateStart=fields.Date(string="Activity Start Date",compute='set_dateStart',store=True)
    dateEnd=fields.Date(string="Activity End Date",store=True,compute='set_dateEnd')
    imprest_type=fields.Selection([('group', 'Group'), ('individual', 'Individual')],string="Imprest Type",store=True,compute='set_imprestType')
    state = fields.Selection([
        ('draft', "Draft"),
        ('submited', "Submited"),
        ('authorized', "Authorized"),
        ('certified', "Certified"),
        ('approved', "Approved"),
        ('rejected', "Rejected"),
    ], default='draft', track_visibility='onchange',store=True)
    purpose=fields.Text(string="Purporse",store=True)
    dateCreate=fields.Date(string="Application Date",default=fields.Date.today(),store=True)
    dateExt=fields.Date(string="Date Extend",store=True)
    created_by_id = fields.Many2one('hr.employee', readonly=True, string='Created by',
                                    default=lambda self: self.env['hr.employee'].search(
                                        [('user_id', '=', self.env.uid)], limit=1),store=True)
    current_user = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.user.id,store=True)
    is_submited=fields.Boolean(default=False)
    is_authorized=fields.Boolean(default=False)
    is_certified=fields.Boolean(default=False)
    is_approved=fields.Boolean(default=False)
    is_rejected=fields.Boolean(default=False)

    # ben modifies
    authorizer_id = fields.Many2one('res.users', string='To Authorise ')
    # certifier_id = fields.Many2one('res.users', string='To Certify (Project Manager)')
    certifier_id = fields.Many2many('res.users','ref_idayo', string='To Certify ')
    approver_id = fields.Many2many('res.users','ref_idayo12', string='To Approve ')
   

    # ben modifies

    @api.onchange('name')
    @api.depends('name')
    def set_domain_for_teacher(self):
        cc=self.env['hr.employee'].search([('user_id', '=', self.env.uid)],limit=1).id
        class_obj = self.env['imprest.application'].search([('created_by_id', '=', cc)])
        print(class_obj)
        teacher_list =[]
        for data in class_obj:
              teacher_list.append(data.id)

        res = {}
        res['domain'] = {'name': [('id', 'in', teacher_list)]}
        return res





    @api.onchange('name')
    @api.depends('name')
    def set_valuez(self):
        self.date=self.name.date
        self.dateStart=self.name.dateStart
        self.dateEnd=self.name.dateEnd
        self.imprest_type=self.name.imprest_type
        self.purpose=self.name.purpose
        self.authorizer_id=self.name.authorizer_id
        self.certifier_id=self.name.certifier_id.ids
        self.approver_id=self.name.approver_id.ids

    @api.depends('name')
    def set_date(self):
        self.date=self.name.date

    @api.depends('name')
    def set_dateStart(self):
        self.dateStart=self.name.dateStart

    @api.depends('name')
    def set_dateEnd(self):
        self.dateEnd=self.name.dateEnd

    @api.depends('name')
    def set_imprestType(self):
        self.imprest_type=self.name.imprest_type

    @api.depends('name')
    def set_authorizer_id(self):
        self.authorizer_id=self.name.authorizer_id
    
    @api.depends('name')
    def set_certifier_id(self):
        self.certifier_id=self.name.certifier_id

    @api.depends('name')
    def set_approver_id(self):
        self.approver_id=self.name.approver_id



    benja=fields.Integer(string="for Testing")

    def action_submitted(self):

        for applications in self:
            if not applications.authorizer_id:
                raise UserError('Include name of Person to authorize the Application')
            else:
                # template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest').id
                # template = self.env['mail.template'].browse(template_id)
                # template.send_mail(self.id, force_send=True)
                self.write({'state': 'submited','is_submited':True})

    


      

    def action_certified(self):
        if self.env.user.id not in self.certifier_id.ids:
            err_namez = []
            for ax in self.certifier_id.ids:
                err_namez.append(ax.name)
            raise UserError('Only %s can Certify or Reject this Application!' %err_namez.name)
        else:
            self.write(
                {'state': 'certified', 'is_certified':True})

            # template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest_authorized').id
            # template = self.env['mail.template'].browse(template_id)
            # template.send_mail(self.id, force_send=True)

    def action_approved(self):
        if self.env.user.id != self.approver_id.id:
            raise UserError('Only %s can Approve or Reject this Application!' % self.approver_id.name)
        else:
            self.write(
                {'state': 'approved', 'is_approved':True})
            #
            # template_id = self.env.ref('tenmet_imprest.email_template_mst_imprest_authorized').id
            # template = self.env['mail.template'].browse(template_id)
            # template.send_mail(self.id, force_send=True)

    def reject(self):
        wizard_form = self.env.ref(
            'tenmet_imprest.view_reason_wizard', False).id
        return {
            'name': 'Reject Reason',
            'view_mode': 'form',
            'view_id': wizard_form,
            'view_type': 'form',
            'res_model': 'reason.reason',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def action_draft(self):
        self.write({'state': 'draft'})

    def unlink(self):
        if self.state not in ('draft','submited'):
            raise UserError("You can not delete this record")

    # benjamin Add this
    def reminder(self):
        template_id = self.env.ref(
            'tenmet_imprest.email_template_mst_imprest_global').id
        template = self.env['mail.template'].browse(template_id)
        template.email_from = self.applicant_id.work_email or self.env.user.email_formatted
        if self.state == 'submited':
            template.email_to = self.authorizer_id.login
            template.send_mail(self.id, force_send=True)

        if self.state == 'authorized':
            for ax in self.certifier_id.ids:
                template.email_to = self.ax.login
                template.send_mail(self.id, force_send=True)
        if self.state == 'certified':
            for ax in self.approver_id.ids:
                template.email_to = self.ax.login
                template.send_mail(self.id, force_send=True)
        if self.state == 'approved':
            pass
            # template.email_to = self.pm_approver_id.login
            # template.send_mail(self.id, force_send=True)
# last stage



