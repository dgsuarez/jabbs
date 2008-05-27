started_minutes = "Started minutes"
started_managing = "Started managing minutes"
scribe_already_set = "Scribe is already set"
field_set_to = "{{field}} set to: {{value}}"
position_set_to = "{{position}} is: {{name}}"
only_scribe_can = "Only the scribe can {{action}}. If you haven't, set a scribe"
no_topic_for_minute = "Before submiting a minute you must submit a topic"
no_minute_to_continue = "Before continuing a minute you must submit one"
minutes_ended = "Minutes ended"
error_deleting = "Error deleting minutes with id {{id}}"
minutes_deleted = "Minutes with id {{id}} deleted"
select_minutes_to_remove = "Select minutes to delete"
available_minutes_are = "Select one of the available minutes"
show_available_minutes = """\
Available minutes are:
{% for minutes in minutes_list %}
Title: {{minutes.title}}
Chair: {{minutes.chair}}
Scribe: {{minutes.scribe}}
Date: {{minutes.date}}

{% else %}
No minutes available
{% endfor %}

"""
show_minutes = """\
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
"""

help_minuteman ="""\
To become scribe -> I'm the scribe
To set the title -> Title: title
To set the chair -> Chair: chair
To add a topic -> Topic: title
To add a statement -> To be minuted: author: title
To continue a statement -> ... statement
To close the minutes -> End minutes
To manage minutes -> Start a conversation just with me
"""

help_manager = """\
To show all minutes -> Show minutes
To show just one minute -> Select minutes
To delete one minute -> Remove minutes
To start minutes -> Enter a room chat i'm into
"""

default_manager = """\
The command you just introduced is invalid. To see a list of available commands type "help"
"""
