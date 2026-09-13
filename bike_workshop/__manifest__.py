{
    'name': "Rami's Bike Workshop",
    'version': '19.0.1.0.0',
    'summary': 'Manage bike rentals and workshop fleet',
    'category': 'Sales/Rental',
    'author': 'Shahed Alawneh',
    'license': 'LGPL-3',  
    'depends': [
    'base',
    'contacts',
    'product',
    ],
    'data': [
        'security/bike_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/bike_rental_views.xml',  
        'views/bike_menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'version': '19.0.1.0.1',
    
}
