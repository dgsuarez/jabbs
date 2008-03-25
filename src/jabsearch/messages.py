search_result = """\
{% for r in results %}
{{r.title}}: {{r.url}}
{% else %}
No results found
{% endfor %}
"""