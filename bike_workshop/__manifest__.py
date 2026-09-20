{
    'name': 'Rami\'s Bike Workshop',
    'version': '19.0.2.0.0',
    'summary': 'Manage bikes, rentals, repairs, and spare parts',
    'category': 'Sales/Rental',
    'author': 'Shahed Alawneh',
    'license': 'LGPL-3',

    'depends': [
        'base',
        'contacts',
        'product',
        'stock',
        'portal',
    ],

    'data': [
    'security/bike_security.xml',
    'security/ir.model.access.csv',

    'data/bike_sequence.xml',
    'data/dashboard_data.xml',
    'reports/rental_agreement_report.xml',


    'views/login_templates.xml',
    'views/bike_views.xml',
    'views/bike_rental_views.xml',
    'views/bike_rental_analysis_views.xml',
    'views/bike_repair_views.xml',
    'views/res_partner_views.xml',
    'views/product_views.xml',
    'views/res_users_views.xml',
    'views/dashboard_views.xml',
    'views/portal_templates.xml',

],
    'assets': {
    'web.assets_backend': [
        'bike_workshop/static/src/css/bike_workshop.css',
        'bike_workshop/static/src/js/bike_workshop_branding.js',
        'bike_workshop/static/src/img/rami_bike_workshop_logo.png',
    ],
},

    'installable': True,
    'application': True,
    'auto_install': False,
}