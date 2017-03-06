# -*- coding: utf-8 -*-

import click

from trac_redmine_importer.load_trac_data import load_data
from trac_redmine_importer.write_redmine_data import main as write_data

def main():
    #load_data()
    write_data()

if __name__ == "__main__":
    main()
