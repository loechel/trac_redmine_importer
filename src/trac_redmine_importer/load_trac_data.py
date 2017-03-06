from bs4 import BeautifulSoup
from collections import namedtuple

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

# Trac Settings
trac_url = "https://trac/"
trac_project = ""

trac_user = ""
trac_password = ""

def load_data():
    # html 2 Markdown Handler
    h = html2text.HTML2Text()
    h.ignore_links = False

    trac_data = dict()

    payload = {
        'format': 'csv',
        'max': 10000,
        'col': ['id',
                'type',
                'summary',
                'status',
                'solution',
                'reporter',
                'owner',
                'cc',
                'priority',
                'milestone',
                'component',
                'resolution',
                'time',
                'changetime',
                'estimatedhours',
                'billable',
                'totalhours',
                'keywords',
               ],
        'order': 'id',
    }

    # First Run: Process Base Data from CSV Query
    logger.info('Process Base Data from CSV Query')
    base_data_request = requests.get(trac_url + trac_project + '/query', auth=(trac_user, trac_password), params=payload)
    if base_data_request.status_code == 200 and base_data_request.headers['content-type'] == 'text/csv;charset=utf-8':
        csv_data = io.StringIO(base_data_request.text)
        csv_reader = csv.DictReader(csv_data)
        for row in csv_reader:
            ticket_data = dict()
            ticket_data['id'] = row['id']
            logger.debug('Process Ticket: %s', ticket_data['id'])
            ticket_data['type'] = row['type']
            ticket_data['title'] = row['summary']
            ticket_data['status-solution'] = row['status'] + '-' + row['resolution']
            ticket_data['reporter'] = row['reporter']
            ticket_data['assigned_to'] = row['owner']
            ticket_data['watchers'] = row['cc']
            ticket_data['priority'] = row['priority']
            ticket_data['version'] = row['milestone']
            ticket_data['category'] = row['component']
            if row['time']:
                ticket_data['start_date'] = datetime.datetime.strptime(row['time'][0:19], '%Y-%m-%d %H:%M:%S').date()
            if row['changetime']:
                ticket_data['due_date'] = datetime.datetime.strptime(row['changetime'][0:19], '%Y-%m-%d %H:%M:%S').date()
            ticket_data['estimatedhours'] = row['estimatedhours']
            ticket_data['billable'] = row['billable']
            ticket_data['totalhours'] = row['totalhours']
            ticket_data['keywords'] = row['keywords']

            trac_data[ticket_data['id']] = ticket_data

    # First Run: Process Advanced Data sets via HTML Scrapping
    logger.info('Process Advanced Data (Attachments, Changelog, Time Booking)')
    for index in trac_data.keys():
        logger.debug('Process Ticket: %s', ticket_data['id'])
        ticket_data = trac_data[index]
        r = requests.get(trac_url + trac_project + '/ticket/' + str(index), auth=(trac_user, trac_password), params={'format': 'csv'})
        if r.status_code == 200 and r.headers['content-type'] == 'text/csv;charset=utf-8':
            csv_data = io.StringIO(r.text)
            csv_reader = csv.DictReader(csv_data)
            for row in csv_reader:
                ticket_data['description_raw'] = row['description']
        r = requests.get(trac_url + trac_project + '/ticket/' + str(index), auth=(trac_user, trac_password))
        if r.status_code == 200 and r.headers['content-type'] == 'text/html;charset=utf-8':
            soup = BeautifulSoup(r.text, 'html.parser')
            # Get Description
            desc_part = soup.find(id='ticket').find('div', {'class': 'description'}).find('div', {'class': 'searchable'})
            ticket_data['description_html'] = str(desc_part)
            ticket_data['description_markdown'] = h.handle(str(desc_part))
            # Get Attachements
            attachements = soup.find('div' , {'id': 'attachments'}).find_all('dt')
            ticket_data['attachments'] = []
            for attachment in attachements:
                try:
                    os.stat('transfer-files/' + str(index))
                except:
                    os.mkdir('transfer-files/' + str(index))
                title = attachment.a.text
                file = attachment.find('a', {'class': 'trac-rawlink'})
                with open('transfer-files/' + index + '/' + title, 'wb') as handle:
                    file_r = requests.get(trac_url + file.get('href'), auth=(trac_user, trac_password))
                    if file_r.ok:
                        for chunk in file_r.iter_content(chunk_size=1024):
                            if chunk:
                                handle.write(chunk)
                ticket_data['attachments'].append(Attachement(filename=title, path='transfer-files/' + index + '/' + title))
            # Changelog --> Comments and hours
            if soup.find(id='changelog'):
                changes = soup.find(id='changelog').find_all('div', {'class': 'change'})
                ticket_data['changes'] = []
                for change in changes:
                    change_id = 0
                    change_id_elem = change.find('span', {'class': 'cnum'})
                    if change_id_elem:
                        change_id = int(change_id_elem.attrs['id'][8:])
                    raw_timestamp = change.find('a', {'class': 'timeline'})
                    user = raw_timestamp.next_sibling[8:].strip()
                    raw_timestamp = raw_timestamp.get('title')[0:10]
                    timestamp = datetime.datetime.strptime(raw_timestamp, '%Y-%m-%d').date()
                    changelog = change.find('ul', {'class': 'changes'})
                    ttype = 'comment'
                    if changelog:
                        for elem in changelog.find_all('li'):
                            if elem.strong.text == "Add Hours to Ticket":
                                if len(elem.find_all('em')) == 2:
                                    hours = float(elem.find_all('em')[1].text)
                                    ttype = 'TimeEntry'
                    comment_raw = change.find('div', {'class': 'comment'})
                    comment_html = str(comment_raw)
                    comment_markdown = str(h.handle(str(comment_raw))).strip()
                    if ttype == 'TimeEntry':
                        ticket_data['changes'].append({'type': 'time_entry',
                                                       'trac_change_id': change_id,
                                                       'user': user,
                                                       'hours': hours,
                                                       'timestamp': timestamp,
                                                       'comment': comment_markdown})
                    else:
                        ticket_data['changes'].append({'type': 'comment_entry',
                                                       'trac_change_id': change_id,
                                                       'user': user,
                                                       'timestamp': timestamp,
                                                       'comment': comment_markdown})

    with open('data.pickle', 'wb') as data_file:
        pickle.dump(trac_data, data_file)
