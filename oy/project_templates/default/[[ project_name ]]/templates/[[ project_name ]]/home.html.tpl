{% extends "richtext_page/page.html" %}

{% block extra_css %}
  <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='css/[[ project_name ]].css') }}">
{% endblock %}

{% block page_body %}
  {{  super() }}
{% endblock %}