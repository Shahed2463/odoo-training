from odoo import fields, models


class BikeWorkshopDashboard(models.Model):
    _name = "bike.workshop.dashboard"
    _description = "Bike Workshop Operations Dashboard"

    name = fields.Char(
        string="Dashboard",
        default="Workshop Operations",
        translate=True,
    )

    active_rentals_today = fields.Integer(
        string="Active Rentals Today",
        compute="_compute_dashboard_counts",
    )

    returns_due_today = fields.Integer(
        string="Returns Due Today",
        compute="_compute_dashboard_counts",
    )

    repairs_in_progress = fields.Integer(
        string="Repairs In Progress",
        compute="_compute_dashboard_counts",
    )

    def _compute_dashboard_counts(self):
        today = fields.Date.context_today(self)

        Rental = self.env["bike.rental"]
        Repair = self.env["bike.repair"]

        active_rentals_domain = [
            ("state", "=", "confirmed"),
            ("start_date", "<=", today),
            ("expected_return_date", ">=", today),
        ]

        returns_due_domain = [
            ("state", "=", "confirmed"),
            ("expected_return_date", "=", today),
        ]

        repairs_in_progress_domain = [
            ("state", "=", "in_progress"),
        ]

        active_rentals_count = Rental.search_count(
            active_rentals_domain
        )

        returns_due_count = Rental.search_count(
            returns_due_domain
        )

        repairs_in_progress_count = Repair.search_count(
            repairs_in_progress_domain
        )

        for dashboard in self:
            dashboard.active_rentals_today = active_rentals_count
            dashboard.returns_due_today = returns_due_count
            dashboard.repairs_in_progress = repairs_in_progress_count

    def action_open_active_rentals(self):
        today = fields.Date.context_today(self)

        return {
            "type": "ir.actions.act_window",
            "name": "Active Rentals Today",
            "res_model": "bike.rental",
            "view_mode": "list",
            "views": [
                (
                    self.env.ref(
                        "bike_workshop.view_bike_rental_dashboard_list"
                    ).id,
                    "list",
                ),
            ],
            "domain": [
                ("state", "=", "confirmed"),
                ("start_date", "<=", today),
                ("expected_return_date", ">=", today),
            ],
            "create": False,
            "edit": False,
            "delete": False,
        }

    def action_open_returns_due_today(self):
        today = fields.Date.context_today(self)

        return {
            "type": "ir.actions.act_window",
            "name": "Returns Due Today",
            "res_model": "bike.rental",
            "view_mode": "list",
            "views": [
                (
                    self.env.ref(
                        "bike_workshop.view_bike_rental_dashboard_list"
                    ).id,
                    "list",
                ),
            ],
            "domain": [
                ("state", "=", "confirmed"),
                ("expected_return_date", "=", today),
            ],
            "create": False,
            "edit": False,
            "delete": False,
        }

    def action_open_repairs_in_progress(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Repairs In Progress",
            "res_model": "bike.repair",
            "view_mode": "list",
            "views": [
                (
                    self.env.ref(
                        "bike_workshop.view_bike_repair_dashboard_list"
                    ).id,
                    "list",
                ),
            ],
            "domain": [
                ("state", "=", "in_progress"),
            ],
            "create": False,
            "edit": False,
            "delete": False,
        }
