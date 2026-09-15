from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal


class BikeWorkshopCustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)

        Rental = request.env["bike.rental"]
        partner = request.env.user.partner_id

        values["bike_rental_count"] = Rental.search_count(
            [
                ("customer_id", "=", partner.id),
            ]
        )

        return values

    @http.route(
        ["/my/rentals", "/my/rentals/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_rentals(self, page=1, **kw):
        values = self._prepare_portal_layout_values()

        partner = request.env.user.partner_id
        Rental = request.env["bike.rental"]

        rentals = Rental.search(
            [
                ("customer_id", "=", partner.id),
            ],
            order="start_date desc, id desc",
        )

        values.update(
            {
                "rentals": rentals,
                "page_name": "rental",
                "default_url": "/my/rentals",
            }
        )

        return request.render(
            "bike_workshop.portal_my_rentals",
            values,
        )

    @http.route(
        "/my/rentals/<int:rental_id>",
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_rental(self, rental_id, **kw):
        partner = request.env.user.partner_id

        rental = request.env["bike.rental"].search(
            [
                ("id", "=", rental_id),
                ("customer_id", "=", partner.id),
            ],
            limit=1,
        )

        if not rental:
            return request.not_found()

        values = self._prepare_portal_layout_values()

        values.update(
            {
                "rental": rental,
                "page_name": "rental",
            }
        )

        return request.render(
            "bike_workshop.portal_my_rental",
            values,
        )