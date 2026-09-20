from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class BikeRental(models.Model):
    _name = "bike.rental"
    _description = "Bike Rental"
    _rec_name = "name"
    _order = "start_date desc, id desc"

    name = fields.Char(
        string="Rental Reference",
        required=True,
        readonly=True,
        copy=False,
        default="New",
    )

    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        required=True,
    )

    bike_id = fields.Many2one(
        "bike.workshop",
        string="Bike",
        required=True,
        ondelete="restrict",
    )
    
    bike_type = fields.Selection(
        related="bike_id.bike_type",
        string="Bike Type",
        store=True,
        readonly=True,
    )

    start_date = fields.Date(
        string="Rental Start Date",
        required=True,
        default=fields.Date.context_today,
    )

    expected_return_date = fields.Date(
        string="Expected Return Date",
        required=True,
    )

    actual_return_date = fields.Date(
        string="Actual Return Date",
        readonly=True,
    )

    daily_rental_price = fields.Float(
        string="Daily Rental Price",
        default=0.0,
    )


    duration_days = fields.Integer(
        string="Rental Duration (Days)",
        compute="_compute_rental_values",
        store=True,
        aggregator="avg",
    )


    total_amount = fields.Float(
        string="Total Rental Amount",
        compute="_compute_rental_values",
        store=True,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("returned", "Returned"),
        ],
        string="Status",
        default="draft",
        required=True,
        copy=False,
    )

    return_performance = fields.Selection(
        [
            ("on_time", "On Time"),
            ("late", "Late"),
            ("pending", "Pending"),
        ],
        string="Return Performance",
        compute="_compute_return_performance",
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        sequence = self.env["ir.sequence"]

        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    sequence.next_by_code("bike.rental") or "New"
                )

            bike_id = vals.get("bike_id")

            if bike_id and "daily_rental_price" not in vals:
                bike = self.env["bike.workshop"].browse(bike_id)
                vals["daily_rental_price"] = bike.daily_rental_price

        return super().create(vals_list)

    @api.depends(
        "start_date",
        "expected_return_date",
        "daily_rental_price",
    )
    def _compute_rental_values(self):
        for rental in self:
            if rental.start_date and rental.expected_return_date:
                rental.duration_days = (
                    rental.expected_return_date - rental.start_date
                ).days
            else:
                rental.duration_days = 0

            rental.total_amount = (
                rental.duration_days * rental.daily_rental_price
            )

    @api.depends(
        "state",
        "expected_return_date",
        "actual_return_date",
    )
    def _compute_return_performance(self):
        for rental in self:
            if not rental.actual_return_date:
                rental.return_performance = "pending"
            elif rental.actual_return_date <= rental.expected_return_date:
                rental.return_performance = "on_time"
            else:
                rental.return_performance = "late"

    @api.onchange("bike_id")
    def _onchange_bike_id(self):
        for rental in self:
            if rental.bike_id:
                rental.daily_rental_price = (
                    rental.bike_id.daily_rental_price
                )
            else:
                rental.daily_rental_price = 0.0

    @api.onchange("start_date", "expected_return_date")
    def _onchange_rental_dates(self):
        for rental in self:
            if (
                rental.start_date
                and rental.expected_return_date
                and rental.expected_return_date <= rental.start_date
            ):
                return {
                    "warning": {
                        "title": _("Invalid Rental Dates"),
                        "message": _(
                            "The expected return date must be strictly "
                            "after the rental start date."
                        ),
                    }
                }

        return {}

    @api.constrains("start_date", "expected_return_date")
    def _check_rental_dates(self):
        for rental in self:
            if (
                rental.start_date
                and rental.expected_return_date
                and rental.expected_return_date <= rental.start_date
            ):
                raise ValidationError(
                    _(
                        "The expected return date must be strictly "
                        "after the rental start date."
                    )
                )

    @api.constrains(
        "daily_rental_price",
        "duration_days",
        "total_amount",
    )
    def _check_non_negative_values(self):
        for rental in self:
            if rental.daily_rental_price < 0:
                raise ValidationError(
                    _("Daily rental price cannot be negative.")
                )

            if rental.duration_days <= 0:
                raise ValidationError(
                    _("Rental duration must be greater than zero.")
                )

            if rental.total_amount < 0:
                raise ValidationError(
                    _("Total rental amount cannot be negative.")
                )

    def _get_conflicting_rental(self):
        self.ensure_one()

        return self.env["bike.rental"].search(
            [
                ("id", "!=", self.id),
                ("bike_id", "=", self.bike_id.id),
                ("state", "=", "confirmed"),
                ("start_date", "<=", self.expected_return_date),
                ("expected_return_date", ">=", self.start_date),
            ],
            limit=1,
        )

    def _check_can_confirm(self):
        self.ensure_one()

        if self.state != "draft":
            raise UserError(
                _(
                    "Only a Draft rental can be confirmed. "
                    "The current rental is already %s."
                )
                % dict(self._fields["state"].selection).get(
                    self.state,
                    self.state,
                )
            )

        if not self.bike_id:
            raise UserError(_("Please select a bike."))

        if (
            not self.start_date
            or not self.expected_return_date
            or self.expected_return_date <= self.start_date
        ):
            raise UserError(
                _(
                    "The expected return date must be strictly "
                    "after the rental start date."
                )
            )

        if self.duration_days <= 0:
            raise UserError(
                _("Rental duration must be greater than zero.")
            )

        conflicting_rental = self._get_conflicting_rental()

        if conflicting_rental:
            raise UserError(
                _(
                    "This bike is already booked during the selected "
                    "period by rental %s."
                )
                % conflicting_rental.name
            )

        repair_in_progress = self.env["bike.repair"].search(
            [
                ("workshop_bike_id", "=", self.bike_id.id),
                ("state", "=", "in_progress"),
            ],
            limit=1,
        )

        if repair_in_progress:
            raise UserError(
                _(
                    "This bike cannot be rented because it has a repair "
                    "job currently In Progress: %s."
                )
                % repair_in_progress.name
            )

    @api.constrains(
        "bike_id",
        "start_date",
        "expected_return_date",
        "state",
    )
    def _check_confirmed_rental_conflict(self):
        for rental in self.filtered(
            lambda record: record.state == "confirmed"
        ):
            conflict = rental._get_conflicting_rental()

            if conflict:
                raise ValidationError(
                    _(
                        "Rental %s overlaps with confirmed rental %s "
                        "for the same bike."
                    )
                    % (rental.name, conflict.name)
                )

    @api.constrains("bike_id", "state")
    def _check_repair_conflict(self):
        for rental in self.filtered(
            lambda record: record.state == "confirmed"
        ):
            repair_in_progress = self.env["bike.repair"].search(
                [
                    ("workshop_bike_id", "=", rental.bike_id.id),
                    ("state", "=", "in_progress"),
                ],
                limit=1,
            )

            if repair_in_progress:
                raise ValidationError(
                    _(
                        "A bike with an In Progress repair cannot be "
                        "confirmed for a rental."
                    )
                )

    def action_confirm(self):
        for rental in self:
            rental._check_can_confirm()

        for rental in self:
            rental.state = "confirmed"

        return True

    def action_return(self):
        for rental in self:
            if rental.state != "confirmed":
                raise UserError(
                    _("Only a Confirmed rental can be returned.")
                )

        for rental in self:
            rental.write(
                {
                    "state": "returned",
                    "actual_return_date": fields.Date.context_today(
                        rental
                    ),
                }
            )

        return True
