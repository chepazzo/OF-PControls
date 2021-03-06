#/usr/bin/env python
# -*- coding: utf-8 -*-

## Add or save rule to ruleset via POST to /saverule:
## curl -i -H "Content-Type: application/json" -X POST -d '{"mac":"192.168.0.134","dow":"0,1,2,3,4","time_start":"18:00","time_end:"23:59","domain":"youtube.com","action":"block"}' http://localhost:5000/saverule

import logging
log = logging.getLogger('dnspc.server')

from flask import Flask, render_template, request
app = Flask(__name__)

import dnspc
from dnsconf import settings
from utils import net
import os
from flask import request
from flask import jsonify
import json
from pprint import pprint as pp

PC = dnspc.ParentalControls()

## Pages

@app.route('/')
def top():
    return render_template('index.html')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/onboard')
def onboard():
    '''/onboard is a page to allow a user to set a hostname, etc for a given device'''
    return render_template('onboard.html')

@app.route('/pcapp.js')
def pcappjs():
    ip = request.remote_addr
    mac = net.get_mac_addr(ip)
    hostname = net.get_hostname(ip)
    main = render_template('pcapp.js')
    rules = render_template('RuleCtrl.js')
    hosts = render_template('HostCtrl.js',
        ip=ip,mac=mac,hostname=hostname)
    check = render_template('checklist-model.js')
    return main+rules+hosts+check

#@app.route('/PCCtrl.js')
#def pcctrljs():
#    return render_template('PCCtrl.js')

#@app.route('/HostCtrl.js')
#def hostctrljs():
#    ip = request.remote_addr
#    mac = net.get_mac_addr(ip)
#    hostname = net.get_hostname(ip)
#    temp = render_template('HostCtrl.js',
#        ip=ip,mac=mac,hostname=hostname)
#    return temp

## API

@app.route('/saverule', methods = ['POST'])
def saverule():
    rule = PC.save_rule(**request.json)
    return jsonify(succ(value=rule._serialize()))

@app.route('/delrule', methods = ['POST'])
def delrule():
    args = request.json
    uid = args['uid']
    res = PC.del_rule(uid)
    if res == False:
        ret = fail('Unable to delete rule {}'.format(uid))
    else:
        ret = succ(value=uid)
    return jsonify(ret)

@app.route('/get/rules')
def get_rules():
    rules = PC.get_rules()
    retval = [s._serialize() for s in PC.rules]
    return jsonify(succ(value=retval))

@app.route('/savehost', methods = ['POST'])
def savehost():
    host = PC.save_host(**request.json)
    return jsonify(succ(value=host._serialize()))

@app.route('/delhost', methods = ['POST'])
def delhost():
    args = request.json
    uid = args['uid']
    res = PC.del_host(uid)
    if res == False:
        ret = fail('Unable to delete host {}'.format(uid))
    else:
        ret = succ(value=uid)
    return jsonify(ret)

@app.route('/get/hosts')
def get_hosts():
    hosts = PC.get_hosts()
    retval = [s._serialize() for s in PC.hosts]
    return jsonify(succ(value=retval))

## start/stop

@app.route('/start')
def start():
    PC.start()
    return "dnspc Started!"

@app.route('/stop')
def stop():
    PC.stop()
    return "dnspc Stopped!"

@app.route('/setloglevel', methods = ['POST'])
def setloglevel():
    args = request.json
    newlevel = args['ll'].upper()
    rootlog = logging.getLogger('dnspc')
    oldlevel = logging.getLevelName(rootlog.level)
    log.info('Changing log level from [{}] to [{}]'.format(oldlevel,newlevel))
    rootlog.setLevel(getattr(logging,newlevel))
    return jsonify(succ(value=newlevel))

def succ(field='data',value=''):
    ''' {'stat':'ok', 'data':{} '''
    return {'stat':'ok',field:value}

def fail(msg='',code=0):
    ''' {'stat':'fail', 'err':{'msg':'', 'code':0}} '''
    err = {'msg':msg,'code':code}
    return {'stat':'fail','err':err}

if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-i",default='/etc/dnspc.conf',help="Specify config file")
    parser.add_argument('--debug', action='store_true', default=False,help="Enable debug mode")
    args = parser.parse_args()

    if args.debug is True:
        log( "Flask DEBUG" )
    else:
        log( "Flask Production" )

    log( "About to start PC" )
    PC.stop()
    PC.start()

    log( "About to start flask" )
    app.run(host='0.0.0.0',debug = args.debug)
    ## Nothing else gets executed here
