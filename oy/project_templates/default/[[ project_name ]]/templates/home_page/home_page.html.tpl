{% extends "oy/contrib/bs4/page/base.html" %}

{% block extra_css %}
  <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='css/[[ project_name ]].css') }}">
{% endblock %}

{% block page_body %}
  {{  super() }}
{% endblock %}