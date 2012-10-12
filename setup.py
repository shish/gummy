import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'pyramid_jinja2',
    'zope.sqlalchemy',
    'waitress',
    'dulwich',
    ]

setup(name='gummy',
      version='0.0',
      description='gummy',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Shish',
      author_email='shish+gummy@shishnet.org',
      url='http://code.shishnet.org/gummy',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='gummy',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = gummy:main
      [console_scripts]
      initialize_gummy_db = gummy.scripts.initializedb:main
      """,
      )

