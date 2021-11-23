from odoo import models, api


class Order(models.Model):
    _inherit = "pos.order"

    @api.model
    def create_from_ui(self, orders):
        order_ids = super(Order, self).create_from_ui(orders)
        for order in self.browse(order_ids):
            if (
                order.invoice_id and
                order.invoice_id.state in ("open", "in_payment", "paid")
            ):
                wizard = self.env["wizard.export.fatturapa"].with_context(
                    active_id=order.invoice_id.id, active_ids=order.invoice_id.ids,
                    active_model="account.invoice"
                ).create({})
                wizard.exportFatturaPA()
                order.invoice_id.fatturapa_attachment_out_id.send_via_pec()
        return order_ids
