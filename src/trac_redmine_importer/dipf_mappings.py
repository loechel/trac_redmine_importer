from collections import namedtuple
from trac_redmine_importer.utils import Attachement
from trac_redmine_importer.utils import Category
from trac_redmine_importer.utils import Milestone
from trac_redmine_importer.utils import Priority
from trac_redmine_importer.utils import Status
from trac_redmine_importer.utils import Tracker
from trac_redmine_importer.utils import User

import datetime

# Mappings for DIPF Project
trackers =  { # Mapping of Tracker (Trac-Type to Redmine Tracker)
    'task':            Tracker(id=4, name='Task'),
    'defect':          Tracker(id=1, name='Bug'),
    'enhancement':     Tracker(id=2, name='Feature'),
    'feature-request': Tracker(id=2, name='Feature'),
    'question':        Tracker(id=3, name='Support'),
}

priorities = {
    'trivial':  Priority(id=1, name='Low'),
    'minor':    Priority(id=1, name='Low'),
    'normal':   Priority(id=2, name='Normal'),
    'critical': Priority(id=4, name='Urgent'),
    'blocker':  Priority(id=5, name='Immediate'),
}

milestones = {
    'BBF-Webseite':                     Milestone(id=74,  name='BBF-Webseite',                     date=datetime.date(2011, 4, 11),  description=''),
    'BBF-Webseite 2':                   Milestone(id=84,  name='BBF-Webseite 2',                   date=datetime.date(2012, 12, 12), description=''),
    'BBF-Webseite 3':                   Milestone(id=91,  name='BBF-Webseite 3',                   date=datetime.date(2013, 8, 6),   description=''),
    'BBF-Webseite 4':                   Milestone(id=95,  name='BBF-Webseite 4',                   date=None,                        description=''),
    'DIPF-Intranet 1 (Festpreis)':      Milestone(id=68,  name='DIPF-Intranet 1 (Festpreis)',      date=datetime.date(2010, 9, 23),  description=''),
    'DIPF-Intranet 1 (stundenbasiert)': Milestone(id=102, name='DIPF-Intranet 1 (stundenbasiert)', date=datetime.date(2010, 9, 23),  description=''),
    'DIPF-Intranet 2':                  Milestone(id=90,  name='DIPF-Intranet 2',                  date=datetime.date(2013, 8, 6),   description=''),
    'DIPF-Intranet 3':                  Milestone(id=96,  name='DIPF-Intranet 3',                  date=None,                        description=''),
    'Kompetenzmodelle':                 Milestone(id=78,  name='Kompetenzmodelle',                 date=datetime.date(2012, 3, 18),  description=''),
    'Plone4-Migration':                 Milestone(id=81,  name='Plone4-Migration',                 date=datetime.date(2012, 10, 23), description=''),
    'Relaunch www.dipf.de':             Milestone(id=89,  name='Relaunch www.dipf.de',             date=datetime.date(2013, 8, 6),   description=''),
    'Relaunch www.dipf.de 2':           Milestone(id=97,  name='Relaunch www.dipf.de 2',           date=None,                        description=''),
    'Suport für dipf 7':                Milestone(id=83,  name='Support für dipf 7',               date=datetime.date(2012, 12, 12), description=''),
    'Support für dipf 7':               Milestone(id=83,  name='Support für dipf 7',               date=datetime.date(2012, 12, 12), description=''),
    'Support für dipf':                 Milestone(id=98,  name='Support für dipf',                 date=None,                        description=''),
    'Support für dipf 3':               Milestone(id=72,  name='Support für dipf 3',               date=datetime.date(2010, 12, 19), description='Supportleistungen ab 23.09.2010 plus einiger in diesen Milestone herübergezogene Tickets'),
    'Support für dipf 4':               Milestone(id=73,  name='Support für dipf 4',               date=datetime.date(2011, 4, 11),  description=''),
    'Support für dipf 5':               Milestone(id=76,  name='Support für dipf 5',               date=datetime.date(2011, 12, 21), description='Abgerechtnet am 21.12.2011 mit Rechnung DIPF-04-2011 '),
    'Support für dipf 6':               Milestone(id=79,  name='Support für dipf 6',               date=datetime.date(2012, 7, 20),  description=''),
    'Support für dipf 8':               Milestone(id=88,  name='Support für dipf 8',               date=datetime.date(2013, 8, 6),   description=''),
    'Support für dipf.de 1':            Milestone(id=67,  name='Support für dipf.de 1',            date=datetime.date(2010, 4, 20),  description='Ziel ist es die momentane Sammelinstanz in 5 einzelne Instanzen mit eigenen buildouts aufzuteilen und damit Administrierbarkeit zu erreichen. '),
    'Support für dipf.de 2':            Milestone(id=69,  name='Support für dipf.de 2',            date=datetime.date(2010, 9, 23),  description='Ziel ist:\n* Dokumentation\n* Optimierung der Performance\n* Umzug auf ein neues sicheres Hostsystem\n'),
    'gebf':                             Milestone(id=92,  name='gebf',                             date=datetime.date(2013, 8, 6),   description=''),
    'gebf 2':                           Milestone(id=99,  name='gebf 2',                           date=None,                        description=''),
    'idea-frankfurt':                   Milestone(id=71,  name='idea-frankfurt',                   date=datetime.date(2010, 12, 18), description=''),
    'idea-frankfurt 2':                 Milestone(id=75,  name='idea-frankfurt 2',                 date=datetime.date(2011, 6, 14),  description='Abgerechnet mir Rechnung IDEA-01-2011'),
    'idea-frankfurt 3':                 Milestone(id=100, name='idea-frankfurt 3',                 date=None,                        description='Sachen für IDeA, die noch nicht bezahlt sind'),
    'idea-frankfurt intranet':          Milestone(id=77,  name='idea-frankfurt intranet',          date=datetime.date(2011, 12, 29), description="Alle Tickets, die für die SIG's verwendet werden und über die schon bezahlte Rechnung IDEA-02-2011 (44 Stunden) abgerechnet werden."),
    'idea-frankfurt supportguthaben':   Milestone(id=85,  name='idea-frankfurt supportguthaben',   date=datetime.date(2013, 7, 31),  description='In diesen Milestone werden alle Leistungen gebucht, für die das Guthaben über 112 Stunden Support für IDeA aufgewendet wird. Diese 112 Stunden sind mit der Rechnung vom 14.06.2011 schon bezahlt.'),
    'idea-relaunch':                    Milestone(id=86,  name='idea-relaunch',                    date=datetime.date(2013, 7, 31),  description=''),
    'idea-relaunch phase2':             Milestone(id=87,  name='idea-relaunch phase2',             date=datetime.date(2013, 8, 6),   description=''),
    'intranet-relaunch':                Milestone(id=94,  name='intranet-relaunch',                date=datetime.date(2014, 1, 30),  description=''),
    'kompetenzmodelle 2':               Milestone(id=80,  name='kompetenzmodelle 2',               date=datetime.date(2012, 10, 23), description=''),
    'kompetenzmodelle 3':               Milestone(id=93,  name='kompetenzmodelle 3',               date=datetime.date(2013, 8, 6),   description=''),
    'kompetenzmodelle4':                Milestone(id=101, name='kompetenzmodelle4',                date=None,                        description=''),
    'pinnwand':                         Milestone(id=82,  name='pinnwand',                         date=datetime.date(2012, 12, 12), description=''),
    'zzz_for_testing_purposes':         Milestone(id=70,  name='zzz_for_testing_purposes',         date=datetime.date(2010, 9, 23),  description='')
}

status_solutions = {
    'new-None':          Status(id=1, name='New'),
    'new---':            Status(id=1, name='New'),
    'accepted-None':     Status(id=2, name='In Progress'),
    'accepted---':       Status(id=2, name='In Progress'),
    'assigned-None':     Status(id=4, name='Feedback'),
    'assigned---':       Status(id=4, name='Feedback'),
    'assigned-':         Status(id=4, name='Feedback'),
    'reopened-':         Status(id=4, name='Feedback'),
    'closed-None':       Status(id=5, name='Done'),
    'closed-fixed':      Status(id=5, name='Done'),
    'closed-wontfix':    Status(id=6, name='Rejected'),
    'closed-invalid':    Status(id=6, name='Rejected'),
    'closed-duplicate':  Status(id=6, name='Rejected'),
    'closed-worksforme': Status(id=6, name='Rejected'),
}

users = {
   'pbauer':    User(id=3,  name='Philip Bauer', login='pbauer'),
   'cfl':       User(id=47, name='dipf dummy', login='dipf_dummy'),
   'cschumann': User(id=47, name='dipf dummy', login='dipf_dummy'),
   'dipfit':    User(id=45, name='dipfit dipfit', login='dipfit'),
   'eschrepf':  User(id=46, name='Eva Schrepf', login='eschrepf'),
   'mbleicher': User(id=47, name='dipf dummy', login='dipf_dummy'),
   'mwuensch':  User(id=47, name='dipf dummy', login='dipf_dummy'),
   'pgerken':   User(id=19, name='Patrick Gerken', login='gerken@starzel.de'),
   'scramme':   User(id=48, name='Stefan Cramme', login='scramme'),
   'sliebmann': User(id=49, name='Sabine Liebmann', login='sliebmann'),
   'slindner':  User(id=1,  name='Steffen Lindner', login='slindner'),
   'somebody':  User(id=47, name='dipf dummy', login='dipf_dummy'),
   'sroth':     User(id=47, name='dipf dummy', login='dipf_dummy'),
   'sschmuck':  User(id=50, name='Steffen Schmuck-Soldan', login='sschmuck'),
   'tbreede':   User(id=51, name='Tom Breede', login='tbreede'),
   'tedelhoff': User(id=52, name='Theresa Edelhoff', login='tedelhoff'),
   'uschmitt':  User(id=41, name='Ursula Schmitt', login='uschmitt'),
   'vdietrich': User(id=47, name='dipf dummy', login='dipf_dummy'),
   # None --> Kein Nutzer zugewiesen
}

categories = {
    'LDAP':               Category(id=17, name='LDAP'),
    'Plone-Anpassungen':  Category(id=18, name='Plone-Anpassungen'),
    'Projekt-Management': Category(id=19, name='Projekt-Management'),
    'Rechte':             Category(id=20, name='Rechte'),
    'buildout':           Category(id=21, name='buildout'),
    'hosting':            Category(id=22, name='hosting'),
    'sonstiges':          Category(id=23, name='sonstiges'),
    'visual design':      Category(id=24, name='visual design'),
    'web-server':         Category(id=25, name='web-server')
}
