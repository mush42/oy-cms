#!/bin/sh
pybabel extract -F babel.ini -k _gettext -k _ngettext -k lazy_gettext -o oycms.pot --project Oy CMS ../oy
pybabel compile -f -D oy -d ../oy/translations/

# docs
cd ..
make gettext
cp build/locale/*.pot babel/
sphinx-intl update -p build/locale/ -d oy/translations/
