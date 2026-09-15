from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class BikeRepairPartLine(models.Model):
    _name = "bike.repair.part.line"
    _description = "Bike Repair Spare Part Line"

    repair_id = fields.Many2one(
        "bike.repair",
        string="Repair Job",
        required=True,
        ondelete="cascade",
    )

    product_id = fields.Many2one(
        "product.product",
        string="Spare Part Product",
        required=True,
        ondelete="restrict",
        domain=[("product_tmpl_id.is_spare_part", "=", True)],
    )

    quantity = fields.Float(
        string="Quantity",
        required=True,
        default=1.0,
    )

    unit_price = fields.Float(
        string="Unit Price",
        required=True,
        default=0.0,
    )

    subtotal = fields.Float(
        string="Subtotal",
        compute="_compute_subtotal",
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if (
                vals.get("product_id")
                and "unit_price" not in vals
            ):
                product = self.env["product.product"].browse(
                    vals["product_id"]
                )
                vals["unit_price"] = product.lst_price

        return super().create(vals_list)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for line in self:
            if line.product_id:
                line.unit_price = line.product_id.lst_price
            else:
                line.unit_price = 0.0

    @api.depends("quantity", "unit_price")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price

    @api.constrains("product_id")
    def _check_spare_part_product(self):
        for line in self:
            if (
                line.product_id
                and not line.product_id.product_tmpl_id.is_spare_part
            ):
                raise ValidationError(
                    _(
                        "Only products marked as spare parts can be "
                        "used in a repair."
                    )
                )

    @api.constrains("quantity", "unit_price", "subtotal")
    def _check_non_negative_values(self):
        for line in self:
            if line.quantity < 0:
                raise ValidationError(
                    _("Part quantity cannot be negative.")
                )

            if line.unit_price < 0:
                raise ValidationError(
                    _("Part unit price cannot be negative.")
                )

            if line.subtotal < 0:
                raise ValidationError(
                    _("Part subtotal cannot be negative.")
                )