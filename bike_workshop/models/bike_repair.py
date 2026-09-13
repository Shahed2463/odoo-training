from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from .constants import BIKE_TYPE_SELECTION


class BikeRepair(models.Model):
    _name = "bike.repair"
    _inherit = ["bike.service.mixin"]
    _description = "Bike Repair Job"
    
    name = fields.Char(
        string="Repair Reference",
        required=True,
        readonly=True,
        copy=False,
        default="New",
    )

    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        required=True,
        ondelete="restrict",
    )

    bike_source = fields.Selection(
        [
            ("workshop", "Workshop Bike"),
            ("external", "External Bike"),
        ],
        string="Bike Source",
        required=True,
        default="workshop",
    )

    workshop_bike_id = fields.Many2one(
        "bike.workshop",
        string="Workshop Bike",
        ondelete="restrict",
    )

    external_bike_reference = fields.Char(
        string="External Bike Reference / Description",
    )

    external_brand = fields.Char(
        string="External Bike Brand",
    )

    external_bike_type = fields.Selection(
        selection=BIKE_TYPE_SELECTION,
        string="External Bike Type",
    )

    reported_issue = fields.Text(
        string="Reported Issue",
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        required=True,
        copy=False,
    )

    part_line_ids = fields.One2many(
        "bike.repair.part.line",
        "repair_id",
        string="Spare Parts",
    )

    total_parts_cost = fields.Float(
        string="Total Parts Cost",
        compute="_compute_total_parts_cost",
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        sequence = self.env["ir.sequence"]

        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    sequence.next_by_code("bike.repair") or "New"
                )

        return super().create(vals_list)

    @api.depends("part_line_ids.subtotal")
    def _compute_total_parts_cost(self):
        for repair in self:
            repair.total_parts_cost = sum(
                repair.part_line_ids.mapped("subtotal")
            )

    @api.onchange("bike_source")
    def _onchange_bike_source(self):
        for repair in self:
            if repair.bike_source == "workshop":
                repair.external_bike_reference = False
                repair.external_brand = False
                repair.external_bike_type = False
            else:
                repair.workshop_bike_id = False

    @api.constrains(
        "bike_source",
        "workshop_bike_id",
        "external_bike_reference",
        "external_brand",
        "external_bike_type",
    )
    def _check_bike_information(self):
        for repair in self:
            if repair.bike_source == "workshop":
                if not repair.workshop_bike_id:
                    raise ValidationError(
                        _(
                            "A workshop bike must be selected for a "
                            "workshop repair."
                        )
                    )

            elif repair.bike_source == "external":
                missing_fields = []

                if not repair.external_bike_reference:
                    missing_fields.append(
                        _("External Bike Reference / Description")
                    )

                if not repair.external_brand:
                    missing_fields.append(_("External Bike Brand"))

                if not repair.external_bike_type:
                    missing_fields.append(_("External Bike Type"))

                if missing_fields:
                    raise ValidationError(
                        _("Please complete: %s")
                        % ", ".join(missing_fields)
                    )

    @api.constrains("total_parts_cost")
    def _check_total_parts_cost(self):
        for repair in self:
            if repair.total_parts_cost < 0:
                raise ValidationError(
                    _("Total parts cost cannot be negative.")
                )

    def _check_can_start(self):
        self.ensure_one()

        if self.state != "draft":
            raise UserError(
                _("Only a Draft repair can move to In Progress.")
            )

        missing_fields = []

        if not self.customer_id:
            missing_fields.append(_("Customer"))

        if not self.reported_issue:
            missing_fields.append(_("Reported Issue"))

        if not self.assigned_mechanic:
            missing_fields.append(_("Assigned Mechanic"))

        if self.bike_source == "workshop":
            if not self.workshop_bike_id:
                missing_fields.append(_("Workshop Bike"))
        else:
            if not self.external_bike_reference:
                missing_fields.append(
                    _("External Bike Reference / Description")
                )

            if not self.external_brand:
                missing_fields.append(_("External Bike Brand"))

            if not self.external_bike_type:
                missing_fields.append(_("External Bike Type"))

        if missing_fields:
            raise UserError(
                _("Please complete the following fields: %s")
                % ", ".join(missing_fields)
            )

    def action_start(self):
        for repair in self:
            repair._check_can_start()

        for repair in self:
            repair.state = "in_progress"

        return True

    def action_complete(self):
        for repair in self:
            if repair.state != "in_progress":
                raise UserError(
                    _(
                        "Only an In Progress repair can be completed."
                    )
                )

            if not repair.service_notes:
                raise UserError(
                    _("Service notes are required before completion.")
                )

            if not repair.last_service_date:
                raise UserError(
                    _("A service date is required before completion.")
                )

        for repair in self:
            repair.state = "completed"

        return True

    def action_cancel(self):
        for repair in self:
            if repair.state not in ("draft", "in_progress"):
                raise UserError(
                    _(
                        "Only Draft or In Progress repairs can be "
                        "cancelled."
                    )
                )

        for repair in self:
            repair.state = "cancelled"

        return True

    @api.constrains("state", "service_notes", "last_service_date")
    def _check_completed_repair(self):
        for repair in self.filtered(
            lambda record: record.state == "completed"
        ):
            if not repair.service_notes:
                raise ValidationError(
                    _("A completed repair must have service notes.")
                )

            if not repair.last_service_date:
                raise ValidationError(
                    _("A completed repair must have a service date.")
                )