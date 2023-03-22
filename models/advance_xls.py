from odoo import models, api, fields, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, Warning
import base64
import io

class AdvanceXls(models.AbstractModel):
    _name = 'report.tenmet_imprest.report_advance_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        
        print ("==========================payslip_ids",self, workbook, data, lines)
        worksheet = workbook.add_worksheet('Sheet 1')
        header1 = workbook.add_format(
            {'bold': True, 'font_name': 'Times New Roman',
             'size': 14, 'align': 'center',
             'font': 'height 180',
             }
        )
        header1.set_fg_color('#808080')
        content = workbook.add_format(
            {'size': 10,
             'align': 'left', 'font_name': 'Times New Roman'})
        bold_left = workbook.add_format(
            {'size': 10,
             'align': 'left',
             'bold': True, 'font_name': 'Times New Roman'})
        bold_right = workbook.add_format(
            {'size': 12,
             'align': 'right',
             'bold': True, 'font_name': 'Times New Roman'})
        bold_center = workbook.add_format(
            {'size': 10,
             'align': 'center',
             'bold': True, 'font_name': 'Times New Roman'})
        
        worksheet.merge_range(1, 1, 1, 2, "MARIE STOPES TANZANIA", bold_center)
        worksheet.merge_range(2, 1, 2, 2, "ADVANCE / IMPREST APPLICATION", bold_center)
       

        worksheet.set_column(0, 0, 18)
        worksheet.set_column(1, 1, 20)
        worksheet.set_column(6, 6, 20)
        worksheet.set_column(2, 2, 20)

        worksheet.set_column(3, 3, 5)
        worksheet.set_column(4, 4, 7)
        worksheet.set_column(5, 5, 10)
        worksheet.set_column(6, 6, 12)
        worksheet.set_column(7, 7, 12)

        bold_leftx = workbook.add_format(
            {'size': 9,
             'align': 'left',
             'bold': False, 'font_name': 'Times New Roman'})

        worksheet.write(
                'A5', "Application Number:" or '', bold_left)
        worksheet.write(
                'B5', lines.name  or '', bold_leftx)
        worksheet.write(
                'A6', "Applicant Name:"  or '', bold_left)

        worksheet.write(
                'B6', lines.applicant_id.name  or '', bold_leftx)

        worksheet.write(
                'A7', "Application Date:" or '', bold_left)
        worksheet.write(
                'B7', lines.date  or '', bold_leftx)
        worksheet.write(
                'A8', "Ammount Requested:" or '', bold_left)
        worksheet.write(
                'B8', lines.grand_total  or '', bold_leftx)
        worksheet.write(
                'A9', "Application Purposes:" or '', bold_left)
        worksheet.write(
                'B9', lines.purpose  or '', bold_leftx)

    
        bold_center = workbook.add_format(
            {'size': 10,
             'align': 'center',
             'bold': False, 'font_name': 'Times New Roman'})
        worksheet.write(
                'A11', "SR/NO." or '', bold_center)
        worksheet.write(
                'B11', "EMPLOYEE NAME" or '', bold_center)
        worksheet.write(
                'C11', "DESCRIPTION " or '', bold_center)
        worksheet.write(
                'D11', "UNIT." or '', bold_center)
        worksheet.write(
                'E11', "QUANTITY" or '', bold_center)
        worksheet.write(
                'F11', "UNITY PRICE" or '', bold_center)
        worksheet.write(
                'G11', "LINE TOTAL" or '', bold_center)
  
        sr_no = 0
        row = 11
        grand_total = lines.grand_total

        print(f'{len(lines.imprest_application_line_ids)}....................')
         

           
        for line_rec in lines.imprest_application_line_ids:
            e_name = line_rec.employee_id.name
            desc = line_rec.name
            price = line_rec.unit_price
            unit_ = line_rec.product_uom_id.name
            qty = line_rec.quantity
            total = line_rec.line_total

            sr_no += 1
            worksheet.write(
                row, 0,  sr_no or '', bold_leftx)
            worksheet.write(
                row, 1, e_name or '', bold_leftx)
            worksheet.write(
                row, 2, desc or '', bold_leftx)
            worksheet.write(
                row, 3, unit_, bold_leftx)
            worksheet.write(
                row, 4, qty, bold_leftx)
            worksheet.write(
                row, 5, price, bold_leftx)
            worksheet.write(
                 row, 6, total, bold_leftx)

            row += 1
           
        
       

        # worksheet.merge_range(row, 0, row, 7, "" or 0.0 , content)

        # worksheet.write(
        #             row, 0, "General Advances", content)
        
        worksheet.write(
                row, 0,  'TOTAL', bold_left)
        worksheet.write(
            row, 1, '', content)
        worksheet.write(
            row, 2, '', content)
        worksheet.write(
            row, 3, '', content)
        worksheet.write(
            row, 4, ' ',  content)
        worksheet.write(
            row, 5, '', content)
        worksheet.write(
            row, 6, grand_total, bold_left)
        row+=1
        workbook.close()


    # 