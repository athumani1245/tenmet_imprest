from odoo import models, fields, api, _
from odoo.exceptions import UserError

# new reason class for the line managers rejection reasons for imprest lines
class ManagerReason(models.TransientModel):

    _name = 'manager.reason'
    _description = 'Reason Wizard'
    _inherit = 'mail.thread'

    reason = fields.Char(
        string='Reason',
        required=True
    )

    def submit_reason_ochu(self):
        imprest_obj = self.env['imprest.application.lines']
        active_ids = self.env.context.get('active_ids', [])
        imprest_id = imprest_obj.sudo().browse(active_ids)
        template_id = self.env.ref('tenmet_imprest.email_template_mst_reject').id
        template = self.env['mail.template'].browse(template_id)
        template.email_from = self.env.user.email_formatted
        # template.email_to = imprest_id.applicant_id.email_formatted or imprest_id.applicant_id.user_id.login
        template.email_to = imprest_id.imprest_application_id.applicant_id.user_id.login
        
        if imprest_id.imprest_application_id.state == 'fleet_manager':
            imprest_id.imprest_application_id.message_post(body='Reject Reason : ' + self.reason)
            imprest_id.unlink()
        template.send_mail(imprest_id.imprest_application_id.id, force_send=True)
            
    
        




class ReasonReason(models.TransientModel):

    _name = 'reason.reason'
    _description = 'Reason Wizard'

    reason = fields.Char(
        string='Reason',
    )
    def reject(self):
        imprest_obj = self.env['imprest.application']
        active_ids = self.env.context.get('active_ids', [])
        imprest_id = imprest_obj.sudo().browse(active_ids)
        template_id = self.env.ref('tenmet_imprest.email_template_mst_reject').id
        template = self.env['mail.template'].browse(template_id)
        template.email_from = self.env.user.email_formatted
        # template.email_to = imprest_id.applicant_id.email_formatted or imprest_id.applicant_id.user_id.login
        template.email_to = imprest_id.applicant_id.user_id.login
        

        if imprest_id.state == 'finance_lead':
            if imprest_id.is_second_finacial_verify:
                imprest_id.write({'state': 'verify'})
                for i in imprest_id.imprest_application_project_line_drl:
                        
                        for j in i.drl_code:
                            j.amount = j.amount + i.drl_amount
                            # ben added this?
                            
                            self.env['drl.journal'].create({
                                'drl_rec': j.name,
                                'update_date': fields.Datetime.now(),
                                'vals': j.amount,
                                'imprest': self.id,
                                'drl_id': j.id,})
                        
                imprest_id.message_post(body='Reject Reason : ' + self.reason)
            elif imprest_id.is_third_finacial_verify:
                for i in imprest_id.imprest_application_project_line_drl:
                        
                        for j in i.drl_code:
                            j.amount = j.amount + i.drl_amount
                            # ben added this?
                            
                            self.env['drl.journal'].create({
                                'drl_rec': j.name,
                                'update_date': fields.Datetime.now(),
                                'vals': j.amount,
                                'imprest': self.id,
                                'drl_id': j.id,})
                imprest_id.write({'state': 'verify'})
                imprest_id.message_post(body='Reject Reason : ' + self.reason)
            elif imprest_id.is_fourth_finacial_verify:
                for i in imprest_id.imprest_application_project_line_drl:
                        
                        for j in i.drl_code:
                            j.amount = j.amount + i.drl_amount
                            # ben added this?
                            
                            self.env['drl.journal'].create({
                                'drl_rec': j.name,
                                'update_date': fields.Datetime.now(),
                                'vals': j.amount,
                                'imprest': self.id,
                                'drl_id': j.id,})
                imprest_id.write({'state': 'verify'})
                imprest_id.message_post(body='Reject Reason : ' + self.reason)
            else:
                raise UserError(
                    'Only Financial Lead with Respective Limit can  Reject this request')

        if imprest_id.state == 'finance_director':
            if imprest_id.is_third_finacial_verify:
                for i in imprest_id.imprest_application_project_line_drl:
                        
                        for j in i.drl_code:
                            j.amount = j.amount + i.drl_amount
                            # ben added this?
                            
                            self.env['drl.journal'].create({
                                'drl_rec': j.name,
                                'update_date': fields.Datetime.now(),
                                'vals': j.amount,
                                'imprest': self.id,
                                'drl_id': j.id,})
                imprest_id.write({'state': 'finance_lead'})
                imprest_id.message_post(body='Reject Reason : ' + self.reason)
            elif imprest_id.is_fourth_finacial_verify:
                imprest_id.write({'state': 'finance_lead'})
                imprest_id.message_post(body='Reject Reason : ' + self.reason)
            else:
                raise UserError(
                    'Only Financial Director with Respective Limit can  Reject this request')

        if imprest_id.state == 'country_director':
            if imprest_id.is_fourth_finacial_verify:
                imprest_id.write({'state': 'country_director'})
                imprest_id.message_post(body='Reject Reason : ' + self.reason)
            else:
                raise UserError('Only Country Director can Reject')

        if imprest_id.state == 'fleet_manager':
            if self.env.user.id != imprest_id.authorizer_id.id:
                raise UserError(
                    'Only %s can Authorize or Reject this Application!' % imprest_id.authorizer_id.name)
            imprest_id.write({'state': 'rejected'})
            imprest_id.message_post(body='Reject Reason : ' + self.reason)



        if imprest_id.state == 'submitted':
            if self.env.user.id != imprest_id.fleet_id.id:
                raise UserError(
                    'Only %s can Authorize or Reject this Application!' % imprest_id.fleet_id.name)
            
            imprest_id.write({'state': 'rejected'})
            imprest_id.message_post(body='Reject Reason : ' + self.reason)

        if imprest_id.state == 'authorized':
            if self.env.user.id not in imprest_id.verify_id.ids:
                err_namez = []
                for ax in imprest_id.verify_id:
                    print(ax.name)
                    err_namez.append(ax.name)
                raise UserError('Only %s can Reject Application!' % err_namez)
            imprest_id.write({'state': 'rejected'})
            
            imprest_id.message_post(body='Reject Reason : ' + self.reason)





        if imprest_id.state == 'certified':
            if self.env.user.id not in imprest_id.approver_id.ids:
                err_namez = []
                for ax in imprest_id.approver_id:
                    print(ax.name)
                    err_namez.append(ax.name)
                raise UserError('Only %s can Reject Application!' % err_namez)
            imprest_id.write({'state': 'rejected'})
            imprest_id.message_post(body='Reject Reason : ' + self.reason)



        if imprest_id.state == 'approved':
            if self.env.user.id not in imprest_id.pm_approver_id.ids:
                err_namez = []
                for ax in imprest_id.approver_id:
                    print(ax.name)
                    err_namez.append(ax.name)
                raise UserError('Only %s can Reject Application!' % err_namez)
            imprest_id.write({'state': 'authorised'})
            imprest_id.message_post(body='Reject Reason : ' + self.reason)


        if imprest_id.state == 'post' or imprest_id.state =='posted' or imprest_id.state =='account1' or imprest_id.state =='account2' or imprest_id.state =='country_director' or imprest_id.state == 'finance_director' or imprest_id.state =='finance_lead':
        # if imprest_id.state in ('post','posted','account1','account2','country_director', 'finance_director', 'finance_lead'):

            imprest_id.state = 'verify'
            
            imprest_id.message_post(body='Reject Reason : ' + self.reason)



        # if imprest_id.state in ['certified', 'authorized', 'submitted', 'approved','post','posted']:
        #     imprest_id.state = 'rejected'
        #     imprest_id.message_post(body='Reject Reason : ' + self.reason)

        template.send_mail(imprest_id.id, force_send=True)


    def rejectRet(self):
        imprest_obj = self.env['imprest.retirement']
        active_ids = self.env.context.get('active_ids', [])
        imprest_id = imprest_obj.sudo().browse(active_ids)
        template_id = self.env.ref('tenmet_imprest.email_template_mst_reject_retirement').id
        template = self.env['mail.template'].browse(template_id)
        template.email_from = self.env.user.email_formatted
        # template.email_to = imprest_id.applicant_id.email_formatted or imprest_id.applicant_id.user_id.login
        template.email_to = imprest_id.retirement_applicant.user_id.login

        if imprest_id.state == 'submitted':
            if self.env.user.id != imprest_id.authorizer_id.id:
                raise UserError(
                    'Only %s can Authorize or Reject this Application!' % imprest_id.authorizer_id.name)
            imprest_id.write({'state': 'pending'})
            imprest_id.message_post(body='Reject Reason : ' + self.reason)

        if imprest_id.state == 'authorized':
            if self.env.user.id not in imprest_id.certifier_id.ids:
                err_namez = []
                for ax in imprest_id.certifier_id:
                    print(ax.name)
                    err_namez.append(ax.name)
                raise UserError('Only %s can Reject Application!' % err_namez)
            imprest_id.write({'state': 'pending'})
            imprest_id.message_post(body='Reject Reason : ' + self.reason)





        if imprest_id.state == 'certified':
            if self.env.user.id != imprest_id.account1_id.id:
                raise UserError(
                    'Only %s can Authorize or Reject this Application!' % imprest_id.account1_id.name)
            imprest_id.write({'state': 'pending'})
            imprest_id.message_post(body='Reject Reason : ' + self.reason)



        if imprest_id.state == 'verify':
            if self.env.user.id != imprest_id.account2_id.id:
                raise UserError(
                    'Only %s can Authorize or Reject this Application!' % imprest_id.account2_id.name)
            
            
            imprest_id.write({'state': 'pending'})
            
            imprest_id.message_post(body='Reject Reason : ' + self.reason)



        template.send_mail(imprest_id.id, force_send=True)
    
        