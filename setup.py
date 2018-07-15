from setuptools import setup, find_packages


setup(
    name='Starlit',
    version='0.1.dev',
    description='A lightweight, modular, and extensible content management system.',
    license='MIT',
    author='Musharraf Omer',
    author_email='ibnomer2011@hotmail.com',
    packages=find_packages(),
    platforms='any',
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'flask.commands': [
            'starlit-project=starlit.main:create_project'
        ],
    },
    install_requires=[
      'Flask',
      'Flask-Admin',
      'Flask-BabelEx',
      'Flask-Cors',
      'Flask-Login',
      'Flask-Mail',
      'flask-marshmallow',
      'Flask-Migrate',
      'Flask-Permissions',
      'Flask-Principal',
      'Flask-RESTful',
      'Flask-Security',
      'Flask-SQLAlchemy',
      'Flask-WTF',
      'inflect',
      'marshmallow',
      'marshmallow-sqlalchemy',
      'Pillow',
      'six',
      'speaklater',
      'SQLAlchemy-Utils',
      'unicode-slugify',
      'WTForms-Components',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)