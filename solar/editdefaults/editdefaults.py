# -*- coding: utf-8 -*-
"""
Created on Sat Apr 23 18:44:29 2022

Web Interface zur Einstellung der Parameter

@author: annet
"""

__version__ = '0.0.4'

import json
import socket
import os
from flask import Flask, render_template, request, url_for, flash, redirect
from pathlib import Path

seckey = os.urandom(24).hex()


class Defaults():
    '''Class reading, saving and manipulating defaults'''
    v_sep = '.'
    path = '../definitions'
    data = None

    def __init__(self, defaults='newdefaults.json',
                 edits='editdefaults.json', path=None):
        if path is not None:
            self.path = path
        self.fname = Path(self.path, defaults)
        self.fnameedit = Path(self.path, edits)
        self.data = self._read(self.fname)
        editdata = self._read(self.fnameedit)
        self.edit_value = {k: v[1] for k, v in editdata.items()}
        self.edit_texts = {k: v[0] for k, v in editdata.items()}

    def __repr__(self):
        return json.dumps(self.data, indent=4)

    def _read(self, path):
        '''Read defaults from json file'''
        with open(path) as file:
            data = json.load(file)
        data = self._cvt2int(data)
        return data

    @staticmethod
    def _cvt2int(values: dict):
        """Convert values in dict to int"""
        for key, value in values.items():
            try:
                values[key] = int(values[key])
            except (ValueError, TypeError):
                pass
        return values

    def write(self, path):
        '''Write defaults to formatted json file'''
        if self.data is None:
            return
        try:
            self.data = self._inc_version()
        except AttributeError:
            pass
        self.data = self._cvt2int(self.data)
        try:
            with open(path, 'w') as file:
                file.write(json.dumps(self.data, indent=4))
        except Exception as err:
            print(f'Could not write defaults due to: {str(err)!r}')
        else:
            print(f'Successfully wrote to: {self.fname!r}')

    def _inc_version(self, data=None):
        '''Increment version number before writing to file'''
        if data is None:
            data = self.data
        try:
            version = self.data['__version__'].split(self.v_sep)
            version[-1] = str(int(version[-1]) + 1)
            self.data['__version__'] = self.v_sep.join(version)
        except ValueError as err:
            print(err)
        return data

    def labels(self):
        '''Return dict with labels'''
        label_list = list()
        for key in self.edit_texts.keys():
            # print(f'{key:20s}: '
            #       f'{self.edit_texts[key].format(self.edit_value[key])!r:50s}'
            #       f'  -  {self.edit_value[key]!r}')
            text = self.edit_texts[key].format(float(self.data[key]))
            label_list.append([key,
                               text.replace(',', "'"),
                               self.data[key]])
        return label_list


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


app = Flask(__name__)
app.config['SECRET_KEY'] = seckey


@app.route('/', methods=('GET', 'POST'))
def home():
    defaults = Defaults()
    self = defaults
    saved = ''
    print('Method:', request.method)
    if request.method == 'POST':
        newdata = dict(request.form)
        print(newdata['button'])
        if newdata['button'] == 'reset':
            newdata.update(self.edit_value)
            newdata['__version__'] = '0.1.0'
        del newdata['button']
        keys = list(newdata.keys())
        results = [str(newdata[key]) == str(self.data[key])
                   for key in keys]
        changedkeys = [keys[i] for i in range(len(results)) if not results[i]]
        changed = [f'{key}: {self.data[key]!r} -> {newdata[key]!r}'
                   for key in changedkeys]
        print(str(changed).center(80, '-'))
        if not all(results):
            for key in newdata.keys():
                print(f'{key:25s} - {str(defaults.data[key]):>19s}'
                      f' => {str(newdata[key]):>19s}')
            self.data.update(newdata)
            self.write(self.fname)
            saved = 'new defaults saved in version' \
                    f' {self.data["__version__"]}'
    version = self.data['__version__']
    labels = self.labels()
    return render_template('home.html',
                           name='test',
                           saved=saved,
                           labels=labels,
                           version=version)


if __name__ == '__main__':
    hostip = get_ip()
    port = '8888'
    print(f'connect to {hostip}:{port}')
    # app.run(host=hostip, port=port, ssl_context='adhoc', debug=False)
    app.run(host=hostip, port=port, debug=False)
    # app.run()
    if False:  # for debugging
        defaults = Defaults(defaults='test.json')
        self = defaults
        print('Neuer Start\n', defaults)
