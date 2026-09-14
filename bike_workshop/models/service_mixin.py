nano ~/odoo-dev/clean_bike_project/bike_workshop/models/service_mixin.pyfrom odoo import fields, models


class BikeServiceMixin(models.AbstractModel):
    _name = "bike.service.mixin"
    _description = "Shared Bike Service Information"

    assigned_mechanic = fields.Many2one(
        "res.users",
        string="Assigned Mechanic",
        domain="[('is_mechanic', '=', True)]",
    )
    last_service_date = fields.Date(
        string="Last Service Date",
    )

    service_notes = fields.Text(
        string="Service Notes",
    )
