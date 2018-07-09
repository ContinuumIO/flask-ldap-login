from setuptools import setup, find_packages


setup(
    name='flask-ldap-login',
    version='0.3.4',
    author='Continuum Analytics',
    author_email='dev@continuum.io',
    url='https://github.com/ContinuumIO/flask-ldap-login',
    packages=find_packages(),

    include_package_data=True,
    zip_safe=False,

    install_requires=['flask',
                      'flask-wtf',
                      'python-ldap'
                      ],

    entry_points={
        'console_scripts': [
            'flask-ldap-login-check = flask_ldap_login.check:main',
        ],
    },

)
