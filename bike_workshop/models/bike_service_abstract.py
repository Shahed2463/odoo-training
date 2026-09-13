from odoo import models, fields

class BikeRepair(models.Model):
    _name = 'bike.repair'
    _description = 'Bike Repair'

    # الحقول الخاصة بالصيانة هنا مباشرة

    mechanic_id = fields.Many2one('res.users', string='Assigned Mechanic', tracking=True)
    last_service_date = fields.Date(string='Last Service Date', tracking=True)
    service_notes = fields.Text(string='Service Notes', tracking=True)