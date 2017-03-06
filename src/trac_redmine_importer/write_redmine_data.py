from collections import namedtuple
from redmine import Redmine
from redmine.exceptions import ForbiddenError
from redmine.exceptions import ImpersonateError
from redmine.exceptions import ServerError

import csv
import datetime
import html2text
import io
import logging
import os
import requests
import pickle
import sys
import traceback

from trac_redmine_importer.log import logger
from trac_redmine_importer.log import report_logger

from trac_redmine_importer.utils import Attachement
from trac_redmine_importer.utils import Category
from trac_redmine_importer.utils import Milestone
from trac_redmine_importer.utils import Priority
from trac_redmine_importer.utils import Status
from trac_redmine_importer.utils import Tracker
from trac_redmine_importer.utils import User

from trac_redmine_importer.dipf_mappings import categories
from trac_redmine_importer.dipf_mappings import milestones
from trac_redmine_importer.dipf_mappings import priorities
from trac_redmine_importer.dipf_mappings import status_solutions
from trac_redmine_importer.dipf_mappings import trackers
from trac_redmine_importer.dipf_mappings import users


# Redmine Settings
redmine_api_url = "https://redmine/"
redmine_project_id = ''

redmine_key = ""


def load_trac_data(name='data.pickle'):
    trac_data = dict()
    with open(name, 'rb') as data_file:
        trac_data = pickle.load(data_file)
    return trac_data


MapData = namedtuple('MapData', ['assigned_to', 'version', 'ccs', 'category', 'attachments'])
def map_data(ticket_data):
    assigned_to = None
    if ticket_data['assigned_to']:
        assigned_to = users.get(ticket_data['assigned_to']).id
    logger.debug('Assigned To: %s', assigned_to)

    version = None
    if ticket_data['version'] is not None:
        version_name = ticket_data['version'].strip()
        version_mapping = milestones.get(version_name)
        if version_mapping:
            version = version_mapping.id
        else:
            version = ''
            print('Could not find version: "' + version + '"')
    logger.debug('Version: %s', version)

    ccs = set()
    cc = ticket_data.get('watchers').split(',')
    for user in cc:
        if '@' in user:
            user = user[:-2]
        user = user.strip()
        if users.get(user):
            ccs.add(users.get(user).id)
    ccs = list(ccs)
    logger.debug('Watchers: %s', ', '.join([str(cc) for cc in ccs]))

    category = None
    if ticket_data['category']:
        category = categories.get(ticket_data['category']).id
    logger.debug('Category: %s', category)

    attachments = []
    if ticket_data['attachments']:
        attachments = [{'path': elem.path, 'filename': elem.filename} for elem in ticket_data['attachments']]
    logger.debug('Attachments: %s', ', '.join([at.get('filename') for at in attachments]))

    return MapData(assigned_to=assigned_to, version=version, ccs=ccs, category=category, attachments=attachments)


def reset_redmine_ids(trac_data):
    logger.info('Prevent multiple Creation of tickets, by linking both')
    for index in trac_data:
        ticket_data = trac_data[index]
        if ticket_data.get('redmine_id'):
            del ticket_data['redmine_id']

    redmine = Redmine(
        redmine_api_url,
        key=redmine_key
    )
    issues = redmine.issue.filter(project_id=redmine_project_id, status_id='*')
    for issue in issues:
        # try to not duplicate import Issues
        trac_id = issue.custom_fields[0].value
        if trac_id:
            trac_data[trac_id]['redmine_id'] = issue.id


def write_ticket_data(trac_data, error_list=[]):
    logger.info('Write Ticket Data to Redmine')
    for index in trac_data.keys():
        ticket_data = trac_data[index]
        user = ticket_data['reporter']
        logger.debug('try to impersonate as %s --> %s', user, users.get(user).login)
        redmine = Redmine(
            redmine_api_url,
            key=redmine_key,
            impersonate=users.get(user).login
        )

        if ticket_data.get('redmine_id'):
            logger.debug('Ticket : %s already exists.', index)
        else:
            logger.info('Processing Ticket %s', index)

            assigned_to, version, ccs, category, attachments = map_data(ticket_data)

            try:
                issue = redmine.issue.create(
                    project_id=redmine_project_id,
                    subject=ticket_data['title'],
                    tracker_id=trackers.get(ticket_data['type']).id,
                    description=ticket_data['description_markdown'],
                    status_id=status_solutions.get(ticket_data['status-solution']).id,
                    priority_id=priorities.get(ticket_data['priority']).id,
                    fixed_version_id=version,
                    category_id=category,
                    assigned_to_id=assigned_to,
                    watcher_user_ids=ccs,
                    start_data=ticket_data['start_date'],
                    #due_date=ticket_data['due_date'],
                    estimated_hours=ticket_data['estimatedhours'],
                    custom_fields=[
                        {'id': 1, 'value': int(ticket_data['id'])},
                        {'id': 3, 'value': 'trac_id_' + str(ticket_data['id']) + 'E'},
                    ],
                    uploads=attachments
                )
                ticket_data['redmine_id'] = issue.id
            except Exception as e:
                logger.error(e)
                error_list.append({'type': 'not created',
                                   'ticket': 'https://dev.starzel.de/dipf/ticket/' + index,
                                   'index': index,
                                  })

def failsafe_write_ticket_data(trac_data, error_list, error_set=dict()):
    for elem in error_list:
        index = elem['index']
        issue = None
        ticket_data = trac_data[index]
        user = ticket_data['reporter']
        redmine = Redmine(
            redmine_api_url,
            key=redmine_key,
            impersonate=users.get(user).login
        )

        if ticket_data.get('redmine_id'):
            logger.debug('Ticket : %s already exists.', index)
            issue = redmine.issue.get(ticket_data.get('redmine_id'))
        else:
            logger.info('Processing Ticket %s', index)

            assigned_to, version, ccs, category, attachments = map_data(ticket_data)

            try:
                issue = redmine.issue.create(
                    project_id=redmine_project_id,
                    subject=ticket_data['title'],
                    tracker_id=trackers.get(ticket_data['type']).id,
                    status_id=status_solutions.get(ticket_data['status-solution']).id,
                    priority_id=priorities.get(ticket_data['priority']).id,
                    fixed_version_id=version,
                    category_id=category,
                    assigned_to_id=assigned_to,
                    start_data=ticket_data['start_date'],
                    watcher_user_ids=ccs,
                    custom_fields=[
                        {'id': 1, 'value': int(ticket_data['id'])},
                        {'id': 3, 'value': 'trac_id_' + str(ticket_data['id']) + 'E'},
                    ],
                    estimated_hours=ticket_data['estimatedhours'],
                    uploads=attachments
                )
                ticket_data['redmine_id'] = issue.id

            except Exception as e:
                logger.error(e)
                error_set[index] = {
                    'type': 'not created',
                    'ticket': 'https://dev.starzel.de/dipf/ticket/' + index,
                    'index': index,
                }
                continue
        try:
            issue.description=ticket_data['description_raw']
            issue.save()
        except Exception as e:
            logger.error(e)
            error_set[index] = {
                    'type': 'decription_not_written',
                    'ticket': 'https://dev.starzel.de/dipf/ticket/' + index,
                    'index': index,
                    'redmine_ticket_id': issue.id
                }

def write_report_ticket_import(errors=dict()):
    not_created_error = []
    description_error = []
    for key, entry in errors.items():
        if entry['type'] == 'not created':
            not_created_error.append('* ' + str(entry['ticket']))
        elif entry['type'] == 'decription_not_written':
            description_error.append('* #' + str(entry['redmine_ticket_id']) + ' ' + str(entry['ticket']))
    with open ('report.md', 'a') as reportfile:
        print('## Tickets die nicht angelegt werden konnten:\n', file=reportfile)
        print('Anzahl: ' + str(len(not_created_error)) + '\n\n', file=reportfile)
        print('\n'.join(not_created_error), file=reportfile)

        print('\n\n## Ticket bei denen die Beschreibung einen Fehler verursacht hat:\n', file=reportfile)
        print('Die Tickets wurden ohne Beschreibung angelegt.\n', file=reportfile)
        print('Anzahl: ' + str(len(description_error)) + '\n\n', file=reportfile)
        print('\n'.join(description_error), file=reportfile)

def write_changes_to_tickets(trac_data, errors=[]):
    logger.info('Write Changelog Data to Redmine')
    for index in trac_data.keys():
        logger.info('Processing Ticket %s', index)
        ticket_data = trac_data[index]
        if ticket_data.get('redmine_id'):
            changes = ticket_data['changes']
            redmine = Redmine(
                redmine_api_url,
                key=redmine_key,
            )
            redmine_issue = redmine.issue.get(ticket_data['redmine_id'], include="journals")
            for elem in redmine_issue.journals:
                logger.debug('Journal Entry %s already exists', elem.id)

            for change in changes:
                logger.debug('Change: \n%s', change)
                comment = change['comment'].strip()
                hours = 0.0
                if len(comment) > 1024:
                    errors.append({'type': 'comment_to_long', 'ticket':'https://dev.starzel.de/dipf/ticket/' + index + '#' + str(change.get('trac_change_id'))})
                    continue
                if change.get('hours'):
                    hours=change.get('hours')
                    if hours < 0.0:
                        errors.append({'type': 'negative_hours', 'ticket':'https://dev.starzel.de/dipf/ticket/' + index + '#' + str(change.get('trac_change_id')), 'hours': hours})
                        hours = 0.0
                if change['type'] == 'time_entry' and change.get('time_entry_id') is None:
                    user = change['user']
                    if user in users.keys():
                        try:
                            redmine = Redmine(
                                redmine_api_url,
                                key=redmine_key,
                                impersonate=user
                            )
                            time_entry = redmine.time_entry.create(
                                issue_id=ticket_data['redmine_id'],
                                hours=hours,
                                spent_on=change.get('timestamp'),
                                activity_id=9, # Development
                                comments=comment)
                            change['time_entry_id'] = time_entry.id
                        except ImpersonateError as e:
                            try:
                                redmine = Redmine(
                                    redmine_api_url,
                                    key=redmine_key,
                                )
                                time_entry = redmine.time_entry.create(
                                    issue_id=ticket_data['redmine_id'],
                                    hours=hours,
                                    spent_on=change.get('timestamp'),
                                    activity_id=9, # Development
                                    comments=comment)
                                change['time_entry_id'] = time_entry.id
                            except:
                                errors.append({'type': 'unkown', 'ticket':'https://dev.starzel.de/dipf/ticket/' + index + '#' + str(change.get('trac_change_id'))})
                        except:
                            errors.append({'type': 'unkown', 'ticket':'https://dev.starzel.de/dipf/ticket/' + index + '#' + str(change.get('trac_change_id'))})


                elif change['type'] == 'comment_entry' and change.get('journal_entry_id') is None:
                    user = change['user']
                    if user in users.keys() and comment:
                        note=user + ':\n\n' + comment
                        try:
                            redmine = Redmine(
                                redmine_api_url,
                                key=redmine_key,
                                impersonate=user
                            )
                            if redmine.issue.update(ticket_data['redmine_id'], notes=note):
                                issue = redmine.issue.get(ticket_data['redmine_id'], include='journal')
                                journal_id = issue.journals[issue.journals.total_count -1].id
                                change['journal_entry_id'] = journal_id
                        except ImpersonateError:
                            try:
                                redmine = Redmine(
                                    redmine_api_url,
                                    key=redmine_key,
                                )
                                if redmine.issue.update(ticket_data['redmine_id'], notes=note):
                                    issue = redmine.issue.get(ticket_data['redmine_id'], include='journal')
                                    journal_id = issue.journals[issue.journals.total_count -1].id
                                    change['journal_entry_id'] = journal_id
                            except:
                                errors.append({'type': 'unkown', 'ticket':'https://dev.starzel.de/dipf/ticket/' + index + '#' + str(change.get('trac_change_id'))})
                        except:
                            errors.append({'type': 'unkown', 'ticket':'https://dev.starzel.de/dipf/ticket/' + index + '#' + str(change.get('trac_change_id'))})
                else:
                    logger.info('Change alreadey exists: https://dev.starzel.de/dipf/ticket/' + str(index) + '#' + str(change.get('trac_change_id')))


def write_report_changes(errors=[]):
    comment_error = []
    time_error = []
    unknow_error = []
    for entry in errors:
        if entry['type'] == 'negative_hours':
            time_error.append('* ' + str(entry['ticket']) + ' - hours: ' + str(entry['hours']) )
        elif entry['type'] == 'comment_to_long':
            comment_error.append('* ' + entry['ticket'])
        elif entry['type'] == 'unkown':
            unknow_error.append('* ' + entry['ticket'])


    with open ('report.md', 'a') as reportfile:

        print('### Negative Zeitbuchung:\n\n'+ '\n'.join(time_error), file=reportfile)
        print('\n\n### Kommentar zu lang:\n\n'+ '\n'.join(comment_error), file=reportfile)
        print('\n\n### Unbekannter Fehler:\n\n'+ '\n'.join(unknow_error), file=reportfile)

def verify(trac_data):
    redmine = Redmine(
        redmine_api_url,
        key=redmine_key,
    )
    issues = redmine.issue.filter(project_id=redmine_project_id, status_id='*')

    verify_errors = []
    for issue in issues:
        trac_id = issue.custom_fields[0].value
        if trac_id != '':
            trac_ticket_data = trac_data[trac_id]
            if issue.id != trac_ticket_data['redmine_id']:
                verify_errors.append('Issue: ' + str(issue.id) + ' mapping not correct')
            if issue.subject != trac_ticket_data['title']:
                verify_errors.append('Issue: ' + str(issue.id) + ' Subject not correct')
            if issue.description != trac_ticket_data['description_markdown']:
                verify_errors.append('Issue: ' + str(issue.id) + ' Description not correct')

    with open ('verification.log', 'w') as reportfile:
        print(verify_errors, file=reportfile)

def write_trac_data(trac_data):
    with open('processed_data.pickle', 'wb') as data_file:
        pickle.dump(trac_data, data_file)

def main():

    #trac_data = load_trac_data(name='processed_data.pickle')
    trac_data = load_trac_data()
    reset_redmine_ids(trac_data)

    ticket_error_list = []
    repeat_errors = dict()
    change_error_list = []

    try:
        # Write Ticket Data
        write_ticket_data(trac_data, ticket_error_list)
        failsafe_write_ticket_data(trac_data, ticket_error_list, error_set=repeat_errors)

    except:
        pass

    write_report_ticket_import(errors=repeat_errors)

    try:
        # Write Changelog
        write_changes_to_tickets(trac_data, errors=change_error_list)
    except:
        pass

    write_report_changes(errors=change_error_list)

    # Verify Datas
    verify(trac_data)
    # Write Data back if they should be reprocessed
    write_trac_data(trac_data)

if __name__ == "__main__":
    # execute only if run as a script
    main()
