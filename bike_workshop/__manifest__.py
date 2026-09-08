{
    'name': "Rami's Bike Workshop",
    'version': '19.0.1.0.0',
    'summary': 'Manage bike rentals and workshop fleet',
    'category': 'Sales/Rental',
    'author': 'Shahed Alawneh',
    'license': 'LGPL-3',  
    'depends': ['base'],
    'data': [
        'security/bike_security.xml',
        'security/ir.model.access.csv',
        'views/bike_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'version': '19.0.1.0.1',
    
}