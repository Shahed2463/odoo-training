from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_spare_part = fields.Boolean(
        string="Is Spare Part",
        help="Allow this product to be used in bike repair jobs.",
    )
    