#!/usr/bin/env python
# b-*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Pedro Gonzalez Universitäre Fernstudien (http://www.fernuni.ch)
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
import re
# Find the best implementation available on this platform
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

import xlsxwriter
import collections
import threading
import ConfigParser

class Performance(object):
    def __init__(self, sysArgs):
        # Parse arguments
        self.options = self.parse_args(sysArgs)
        # Get the connection/operations to execute from config file
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(open(self.options.config))
        # Get the users login, password info
        self.users = self.read_users()
        self.operations = self.read_operations()
        self.measures = {}

    def parse_args(self, args):
        """
        Create the args Parser
        :return: list of arguments
        """
        parser = argparse.ArgumentParser()

        parser.add_argument(
            '-m', '--multithread', default=False, action='store_true',
            help='Execute Multithreading. Each user in test in a different thread'
        )

        parser.add_argument(
            '-s', '--save', default=False, action='store_true',
            help='Save current results in history folder'
        )

        parser.add_argument(
            '-c', '--config', default='operations.ini',
            help='Configuration file including information object, method, arguments, groups'
        )
        return parser.parse_args(args)

    def read_operations(self):
        """
        Read all the operation sections and save them in a dictionary
        :return:
        """
        result = {}
        for section in self.config.sections():
            tmp = {}
            if 'operation' not in section:
                continue
            for (k, v) in self.config.items(section):
                tmp.setdefault(k, v)
            result.setdefault(section, tmp)
        od = collections.OrderedDict(sorted(result.items()))
        return od

    def read_users(self):
        """
        Read section users in config file and import the login=password operators
        :return: {
                    'login1': 'password1,
                    'login2': 'password2',
                    .....
                  }
        """
        users = {}
        if not self.config.items('users'):
            print 'No User credentials found on config file'
            sys.exit()

        for (k, v) in self.config.items('users'):
            users.setdefault(k, v)
        return users

    def replace_args(self, args):
        """
        For each occurrence of operation* in the config parameters replace it by the result of that operation
        :param args:
        """
        args_replaced = args
        matches = re.findall("operation[0-9]+", args)
        for match in matches:
            result = str(self.operations[match]['result'])
            args_replaced = re.sub('operation[0-9]+', result, args)
        return args_replaced

    def user_belongs_group(self, client, login, operation):
        """
        Allow/reject user operation
        :param operation: dictionary with the operation information
        :return: True if user allowed, False otherwise
        """
        # Get user object
        user_obj = client.model('res.users')
        group_obj = client.model('res.groups')
        user_id = user_obj.search([('login', '=', login)])
        user = user_obj.browse(user_id)
        user_group_ids = [x.id for x in user.groups_id]
        user_group_ids = user_group_ids and user_group_ids[0]

        for group in operation.get('groups').split(','):
            group_ids = group_obj.search([('name', '=', group)])
            for group_id in group_ids:
                if group_id in user_group_ids:
                    return True
        return False

    def do_operations(self, login, password):
        # Connection per user
        client = erppeek.Client(
            self.config.get('connection', 'host'),
            self.config.get('connection', 'db'),
            login,
            password
        )
        # Execute operations
        t0 = time.time()
        for name, operation in self.operations.iteritems():
            if not self.user_belongs_group(client, login, operation):
                continue
            object = self if operation.get('model', False) == "self" else client.model(operation.get('model', False))
            method = operation.get('method', False)
            args = eval('tuple({})'.format(self.replace_args(operation.get('args', None))))
            if hasattr(object, method):
                result = getattr(
                    object,
                    method
                )(*args)
                operation.setdefault('result', result)

        self.measures.setdefault(login, "{:.2f}".format(time.time() - t0))
        print "{} => {:.2f}(s)".format(login, time.time() - t0)
        return

    def my_super_long_function(self):
        print "My Super Long Function"
        return True

    def run(self):
        """
        Connecting each user to ERP and execute the operations to be measured
        :return:
        """
        t_start = time.time()
        for login, password in self.users.iteritems():
            if self.options.multithread:
                threading.Thread(target=self.do_operations, args=(login, password)).start()
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