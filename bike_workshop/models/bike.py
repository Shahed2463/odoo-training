from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .constants import BIKE_TYPE_SELECTION


class BikeWorkshop(models.Model):
    _name = "bike.workshop"
    _inherit = ["bike.service.mixin"]
    _description = "Bike Workshop Bike"

    name = fields.Char(
        string="Bike Name / Code",
        required=True,
    )

    brand = fields.Char(
        string="Brand",
        required=True,
    )

    bike_type = fields.Selection(
        selection=BIKE_TYPE_SELECTION,
        string="Bike Type",
        required=True,
        default="city",
    )

    purchase_date = fields.Date(
        string="Purchase Date",
    )

    last_maintenance_date = fields.Date(
        string="Last Maintenance Date",
    )

    daily_rental_price = fields.Float(
        string="Daily Rental Price",
        default=0.0,
    )

    wheel_size = fields.Float(
        string="Wheel Size (inches)",
        default=0.0,
    )

    rental_ids = fields.One2many(
        "bike.rental",
        "bike_id",
        string="Rentals",
    )

    rental_count = fields.Integer(
        string="Rental Count",
        compute="_compute_rental_count",
    )

    repair_ids = fields.One2many(
        "bike.repair",
        "workshop_bike_id",
        string="Repair Jobs",
    )

    repair_count = fields.Integer(
        string="Repair Count",
        compute="_compute_repair_count",
    )

    _bike_name_unique = models.Constraint(
        "unique(name)",
        "The bike name/code must be unique.",
    )

    @api.depends("rental_ids")
    def _compute_rental_count(self):
        for bike in self:
            bike.rental_count = len(bike.rental_ids)

    @api.depends("repair_ids")
    def _compute_repair_count(self):
        for bike in self:
            bike.repair_count = len(bike.repair_ids)

    @api.constrains("daily_rental_price", "wheel_size")
    def _check_non_negative_values(self):
        for bike in self:
            if bike.daily_rental_price < 0:
                raise ValidationError(
                    "Daily rental price cannot be negative."
                )

            if bike.wheel_size < 0:
                raise ValidationError(
                    "Wheel size cannot be negative."
                )

    def action_view_rentals(self):
        self.ensure_one()

        action = self.env.ref(
            "bike_workshop.action_bike_rental"
        ).read()[0]

        action["domain"] = [
            ("bike_id", "=", self.id),
        ]

        action["context"] = {
            "default_bike_id": self.id,
        }

        return action

    def action_new_rental(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "New Rental",
            "res_model": "bike.rental",
            "view_mode": "form",
            "target": "current",
            "context": {
                "default_bike_id": self.id,
            },
        }