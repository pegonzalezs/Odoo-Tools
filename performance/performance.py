#!/usr/bin/env python
# b-*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Pedro Gonzalez (pegonzalezs@gmail.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import erppeek
import argparse
import sys
import csv
import time
import os
# Find the best implementation available on this platform
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
import base64

import xlsxwriter
import collections
from threading import Thread

SERVER = 'http://your.server.com:8069'
DATABASE = 'database_name'

class Performance(object):
    def __init__(self, sysArgs):
        self.options = self.parse_args(sysArgs)
        self.users = self.read_users()
        self.measures = {}

    def parse_args(self, args):
        """
        Create the args Parser
        :return: list of arguments
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-i', '--inputfile', default='users_input.csv',
            help='CSV file with first column login, second column password'
        )
        parser.add_argument(
            '-m', '--multithread', default=False, action='store_true',
            help='Execute Multithreading. Each user in test in a different thread'
        )
        parser.add_argument(
            '-s', '--save', default=False, action='store_true',
            help='Save current results in history folder'
        )

        return parser.parse_args(args)

    def read_users(self):
        """
        Read a CSV file with first column login, second column password
        :return: {
                    'login1': 'password1,
                    'login2': 'password2',
                    .....
                  }
        """
        users = {}
        if not self.options.inputfile:
            print 'No File with users info found'
            sys.exit()

        with open(self.options.inputfile, 'rb') as f:
            content = csv.reader(f)
            for row_data in content:
                users.setdefault(row_data[0], row_data[1])
        return users

    def do_operations(self, login, password):

        client = erppeek.Client(SERVER, DATABASE, login, password)

        # Do some operations
        t0 = time.time()
        partner_obj = client.model('res.partner')
        partner_ids = partner_obj.search([], limit=80)
        partner_obj.read(partner_ids, ['first_name'])
        self.measures.setdefault(login, "{:.2f}".format(time.time() - t0))
        print "{} => {:.2f}(s)".format(login, time.time() - t0)
        return

    def run(self):
        """
        Connecting each user to ERP and do the operations to be measured.
        :return:
        """
        t_start = time.time()
        for login, password in self.users.iteritems():
            if self.options.multithread:
                #thread.start_new_thread(self.do_operations, ())
                Thread(target=self.do_operations, args=(login, password)).start()
            else:
                self.do_operations(login, password)
        self.measures.setdefault('TOTAL', time.time() - t_start)
        print "Execution time => {}".format(time.time() - t_start)
        return


    def get_file_path(self):
        """
        Return the output excel file depending on the parameter --save
        :return: file_name including current path
        """
        file_name = 'output.xlsx'
        if self.options.save:
            if not os.path.exists("history"):
                try:
                    os.mkdir("history")
                except Exception:
                    pass
            file_name = os.path.join(os.getcwd(), 'history', 'output_{}.xlsx'.format(time.strftime("%d%m%Y-%H%M%S")))
        return file_name

    def write_output(self):
        """
        Save in Excel a sorted collection of Users / Execution time
        :return:
        """
        od = collections.OrderedDict(sorted(self.measures.items()))
        with open(self.get_file_path(), "w+") as fh:
            workbook = xlsxwriter.Workbook(fh)
            bold = workbook.add_format({'bold': True})
            worksheet1 = workbook.add_worksheet()
            worksheet1.write('A1', 'USERS', bold)
            worksheet1.write('A2', 'TIME(s)', bold)
            worksheet1.write_row(0, 1, od.keys(), bold)
            worksheet1.write_row(1, 1, od.values())
            workbook.close()
        return

if __name__ == '__main__':
    performance = Performance(sys.argv[1:])
    performance.run()
    performance.write_output()