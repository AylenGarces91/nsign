from odoo import fields, models
from odoo.tools import ormcache


class VatNumberXlsx(models.AbstractModel):
    _inherit = 'report.l10n_es_vat_book.l10n_es_vat_book_xlsx'

    def fill_received_row_data(
        self, sheet, row, line, tax_line, with_total, draft_export
    ):
        """ Fill received data """
        date_invoice = line.move_id.date
        # We don't want to fail on empty records, like in the case of PoS
        # cash sales, which dont't have a partner. Just return empty values.
        # Country code will be "ES", as the operations will be made in Spain
        # in all cases.
        country_code, identifier_type, vat_number = (
            line.partner_id._parse_aeat_vat_info() if line.partner_id.id is not False else ("ES", "", "")
        )
        sheet.write("A" + str(row), self.format_boe_date(line.invoice_date))
        if date_invoice and date_invoice != line.invoice_date:
            sheet.write("B" + str(row), self.format_boe_date(date_invoice))
        sheet.write("C" + str(row), line.external_ref and line.external_ref[:40] or "")
        sheet.write("D" + str(row), "")
        sheet.write("E" + str(row), line.ref[:20])
        sheet.write("F" + str(row), "")
        sheet.write("G" + str(row), identifier_type)
        if country_code != "ES":
            sheet.write("H" + str(row), country_code)
        sheet.write("I" + str(row), vat_number)
        sheet.write("J" + str(row), line.partner_id.name[:40])
        # TODO: Substitute Invoice
        # sheet.write('K' + str(row),
        #             line.invoice_id.refund_invoice_id.number or '')
        sheet.write("L" + str(row), "")  # Operation Key
        if with_total:
            sheet.write("M" + str(row), line.total_amount)
        sheet.write("N" + str(row), tax_line.base_amount)
        sheet.write("O" + str(row), tax_line.tax_id.amount)
        sheet.write("P" + str(row), tax_line.tax_amount)
        if tax_line.tax_id not in self._get_undeductible_taxes(line.vat_book_id):
            sheet.write("Q" + str(row), tax_line.tax_amount)
        if tax_line.special_tax_id:
            map_vals = line.vat_book_id.get_special_taxes_dic()[
                tax_line.special_tax_id.id
            ]
            sheet.write(
                map_vals["fee_type_xlsx_column"] + str(row),
                tax_line.special_tax_id.amount,
            )
            sheet.write(
                map_vals["fee_amount_xlsx_column"] + str(row),
                tax_line.special_tax_amount,
            )
        if draft_export:
            last_column = sheet.dim_colmax
            num_row = row - 1
            sheet.write(num_row, last_column, tax_line.tax_id.name)