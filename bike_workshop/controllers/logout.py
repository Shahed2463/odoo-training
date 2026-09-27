from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.session import Session


class BikeWorkshopSession(Session):

    @http.route(
        '/web/session/logout',
        type='http',
        auth='none',
        readonly=True,
    )
    def logout(self, redirect='/odoo'):
        lang = request.session.context.get('lang')

        request.session.logout(keep_db=True)

        if lang:
            redirect = f'/web/login?lang={lang}'

        return request.redirect(redirect, 303)
