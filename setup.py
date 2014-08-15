from setuptools import setup, find_packages


setup(
    name='flask-ldap-login',
    version='0.1',
    author='Continuum Analitics',
    author_email='srossross@gmail.com',
    url='https://github.com/srossross/flask-ldap-login',
    packages=find_packages(),

    include_package_data=True,
    zip_safe=False,

    entry_points={
        'console_scripts': [
            'flask-ldap-login-check = flask_ldap_login.check:main',
        ],
    },

)
