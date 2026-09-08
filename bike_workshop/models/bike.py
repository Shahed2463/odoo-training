from odoo import models, fields

class BikeWorkshop(models.Model):
    _name = 'bike.workshop'
    _description = 'Bike Workshop'

    name = fields.Char(string='Bike Name / Code', required=True)
    brand = fields.Char(string='Brand', required=True)
    bike_type = fields.Selection([
        ('road', 'Road'),
        ('mountain', 'Mountain'),
        ('city', 'City'),
        ('electric', 'Electric')
    ], string='Bike Type', default='city', required=True)
    purchase_date = fields.Date(string='Purchase Date')
    last_maintenance_date = fields.Date(string='Last Maintenance Date')
    daily_rental_price = fields.Float(string='Daily Rental Price')
    wheel_size = fields.Float(string='Wheel Size (inches)')