from odoo import models


class Invoice(models.Model):
    _inherit = "account.invoice"

    def generate_self_invoice(self):
        res = super(Invoice, self).generate_self_invoice()
        rc_type = self.fiscal_position_id.rc_type_id
        if rc_type.fiscal_document_type_id:
            self.rc_self_invoice_id.fiscal_document_type_id =\
                rc_type.fiscal_document_type_id.id
        return res
