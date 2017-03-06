from collections import namedtuple

Attachement = namedtuple('Attachement', ['path', 'filename'])
Category = namedtuple('Category', ['id', 'name'])
Milestone = namedtuple('Milestone', ['id', 'name', 'date', 'description'])
Priority = namedtuple('Priority', ['id', 'name'])
Status = namedtuple('Status', ['id', 'name'])
Tracker = namedtuple('Tracker', ['id', 'name'])
User = namedtuple('User', ['id', 'name', 'login'])
