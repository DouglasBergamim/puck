"""What the agent calls through the puck CLI while it works."""

# Commands an agent may run without asking each time. Left out on purpose:
# `task check` and `learn check`, which run commands a model wrote into a
# file, and everything that changes Puck itself: setup, skills, build, run.
AGENT_COMMANDS = (
    "puck status", "puck lint",
    "puck task start", "puck task list", "puck task show", "puck task step", "puck task close",
    "puck note", "puck scratch",
    "puck topic", "puck sources",
    "puck learn status", "puck learn next", "puck learn record", "puck learn open", "puck learn roadmap",
)
