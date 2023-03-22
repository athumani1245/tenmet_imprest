from odoo import models, api, fields, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, Warning
import base64
import io
import datetime

class PlaneXls(models.AbstractModel):
    _name = 'report.tenmet_imprest.report_plane_xls'
    _inherit = 'report.report_xlsx.abstract'
    

    def generate_xlsx_report(self, workbook, data,lines):
        
        # print ("==========================payslip_ids",self, workbook, data, lines)
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
        worksheet.merge_range(2, 1, 2, 2, "AIRLINE REPORT", bold_center)
       

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
                'A5', "Fleet Imprest Number:" or '', bold_left)
        worksheet.write(
                'B5', lines.imprest_ref_id.name  or '', bold_leftx)
        worksheet.write(
                'A6', "Applicant Name:"  or '', bold_left)

        worksheet.write(
                'B6', lines.imprest_ref_id.applicant_id.name  or '', bold_leftx)

        worksheet.write(
                'A7', "Application Date:" or '', bold_left)
        worksheet.write(
                'B7', lines.date.strftime("%d-%m-%Y")  or '', bold_leftx)
        worksheet.write(
                'A8', "Total Fleet Amount:" or '', bold_left)
        worksheet.write(
                'B8', lines.fleet_total  or '', bold_leftx)

    
        bold_center = workbook.add_format(
            {'size': 10,
             'align': 'center',
             'bold': False, 'font_name': 'Times New Roman'})
        worksheet.write(
                'A11', "SR/NO." or '', bold_center)
        worksheet.write(
                'B11', "EMPLOYEE NAME" or '', bold_center)
        worksheet.write(
                'C11', "FROM " or '', bold_center)
        worksheet.write(
                'D11', "TO" or '', bold_center)
        worksheet.write(
                'E11', "PLANE" or '', bold_center)
        worksheet.write(
                'F11', "DEPARTURE DATE" or '', bold_center)
        worksheet.write(
                'G11', "COST" or '', bold_center)
  
        sr_no = 0
        row = 11
        grand_total = sum(lines.fleet_line.mapped('fleet_cost'))
         

           
        for line_rec in lines.fleet_line:
            name_ = line_rec.applicant.name
            from_ = line_rec.fleet_from
            to_ = line_rec.fleet_to
            plane_ = line_rec.fleet_category
            date_ = line_rec.dep_date.strftime("%d-%m-%Y")
            cost_ = line_rec.fleet_cost

            sr_no += 1
            worksheet.write(
                row, 0,  sr_no or '', bold_leftx)
            worksheet.write(
                row, 1, name_ or '', bold_leftx)
            worksheet.write(
                row, 2, from_ or '', bold_leftx)
            worksheet.write(
                row, 3, to_, bold_leftx)
            worksheet.write(
                row, 4, plane_, bold_leftx)
            worksheet.write(
                row, 5, date_, bold_leftx)
            worksheet.write(
                 row, 6, cost_, bold_leftx)

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