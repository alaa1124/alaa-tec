{
    'name':'Ownership Contract Adjustment',
    'version': '17.0.0.0',
    'category':'Real Estate',
    'sequence':14,
    'summary':'',
    'description':""" 
      """,
    'author':'Marwa Abouzaid',
    'depends':['base','itsys_real_estate'],
    'data':[
        'views/ownership_contract.xml'
    ],

    'installable':True,
    'auto_install':False,
    'application':False,
    'qweb': ['static/src/xml/*.xml'],
}
