from jinja import Environment

env = Environment()

scribe_already_set = env.from_string("Scribe is already set")
field_set_to = env.from_string("{{field}} set to: {{value}}")
position_set_to = env.from_string("{{position}} is: {{name}}")
only_scribe_can = env.from_string("Only the scribe can {{action}}. If you haven't, set a scribe")
no_topic_for_minute = env.from_string("Before submiting a minute you must submit a topic")
no_minute_to_continue = env.from_string("Before continuing a minute you must submit one")
minutes_ended = env.from_string("Minutes ended")
