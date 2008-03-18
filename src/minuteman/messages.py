from jinja import Environment

env = Environment()

scribe_already_set = env.from_string("Scribe is already set")
field_set_to = env.from_string("{{field}} set to: {{value}}")
position_set_to = env.from_string("{{position}} is: {{name}}")
only_scribe_can = env.from_string("Only the scribe can {{action}}. If you haven't, set a scribe")
no_topic_for_minute = env.from_string("Before submiting a minute you must submit a topic")
no_minute_to_continue = env.from_string("Before continuing a minute you must submit one")
minutes_ended = env.from_string("Minutes ended")
error_deleting = env.from_string("Error deleting minutes with id {{id}}")
minutes_deleted = env.from_string("Minutes with id {{id}} deleted")
select_minutes_to_remove = env.from_string("Select minutes to delete")
available_minutes_are = env.from_string("Available minutes are")
show_available_minutes = env.from_string("""\
{% for minutes in minutes_list %}
Title: {{minutes.title}}
Chair: {{minutes.chair}}
Scribe: {{minutes.scribe}}
Date: {{minutes.date}}

{% else %}
No minutes available
{% endfor %}

""")
show_minutes = env.from_string("""\
Title: {{minutes.title}}
Chair: {{minutes.chair}}
Scribe: {{minutes.scribe}}
Date: {{minutes.date}}
Participants: {% for person in minutes.participants %}{{person.name}}, {% endfor %}
{% for topic in minutes.topics %}
{{topic.title}}
{{topic.statements|join('\n')}}

{% else %}
No minutes
{% endfor %}
""")