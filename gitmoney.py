from __future__ import division
import os
from flask import Flask, request, render_template, jsonify
import subprocess
import logging
import json
from sendmail import notify
from os.path import join
from base64 import b64decode
import re

app = Flask(__name__)
app.config['DEBUG'] = True

def extract_meta(file_name, dir_name):
    json_data_file = open(join(dir_name, file_name))
    json_data = json.loads(json_data_file.read())
    json_data_file.close()
    if "summary" not in json_data: json_data["summary"] = {}
    return json_data

def writeback_meta(dir_name, file_name, meta):
    new_json_file = open(join(dir_name, file_name), "w")
    new_json_file.write("%s" % meta)
    new_json_file.close()

@app.route('/')
def gitmoney():
    subprocess.call(["./git_pull.sh", "git_reader"])
    json_data = extract_meta("README.md", "git_reader")
    return render_template('index.html', candidates = json_data["summary"].keys(),
                           cur_head = json_data["summary"])

@app.route('/new_transaction', methods=["POST"])
def new_transaction():
    val_s = request.json["transaction"]["amount"]
    att_a = request.json["transaction"]["attendees"]
    pdb_a = request.json["transaction"]["paidby"]
    smy_s = request.json["summary"]
    print request.json
    subprocess.call(["./git_pull.sh", "git_reader"])
    print "here"
    if ("data" in request.json):
        data = request.json["data"]
        del request.json["data"]
        json_data = extract_meta("README.md", "git_reader")
        pattern = re.compile(r'^data:image/(png|jpeg);base64,(.*)$')
        match = pattern.match(data)
        filename = json_data["watermark"]
        file_data = b64decode(match.group(2))
        with open(filename, 'wb') as f:
            f.write(file_data)
    print "here2"
    value = 0
    try:
        value = round(eval(val_s), 2)
    except:
        return json.dumps({"error":"true", "msg":"wrong value"})
    request.json["transaction"]["amount"] = value
    if not (len(att_a) and len(pdb_a)):
        return json.dumps({"error":"true", "msg":"empty people"})
    msg_s = json.dumps(request.json, indent=4, sort_keys=True)
    msg_a = msg_s.split()
    msg_a[0:2] = [msg_a[0] + msg_a[1]]
    msg_s = "\n".join(msg_a)
    writeback_meta("git_reader", "COMMIT_MSG",
                   msg_s)
    subprocess.call(["./git_pull.sh", "git_reader"])
    subprocess.call(["./git_commit_and_push.sh", "git_reader", "COMMIT_MSG"])
    return json.dumps({"error":"false"})

def calculate_transaction(transaction):
    if len(transaction["paidby"]) == 0: return {}
    if len(transaction["attendees"]) == 0: return {}
    ret = {}
    for p in transaction["paidby"]:
        ret[p] = 0
    for a in transaction["attendees"]:
        ret[a] = 0
    contribe = round(transaction["amount"] / len(transaction["paidby"]), 2)
    owe = round(transaction["amount"] / len(transaction["attendees"]), 2)
    for p in transaction["paidby"]:
        ret[p] += contribe
    for a in transaction["attendees"]:
        ret[a] -= owe
    return ret

def apply_delta(summary, delta):
    # init
    for p in delta:
        if p not in summary:
            summary[p] = 0
        summary[p] = round( summary[p] + delta[p] , 2)
        if abs(summary[p]) <= 0.2:
            del summary[p]

@app.route('/post_receive_hook', methods=['GET', 'POST'])
def post_receive_hook():
    payload = json.loads(request.form['payload'])
    ##print "msg got :%s" % payload["commits"][0]["message"]
    # Reject forced push
    print "post receive hook triggerred!!"
    if payload["forced"]:
        return "skip"
    msg = json.loads(payload["commits"][0]["message"].replace("\n", " "))
    id = payload["head_commit"]["id"]
    transaction = msg["transaction"]
    delta = calculate_transaction(transaction)
    subprocess.call(["./git_pull.sh", "git_reader"])
    json_data = extract_meta("README.md", "git_reader")
    apply_delta(json_data["summary"], delta)
    old_watermark = json_data["watermark"]
    json_data["watermark"] = id
    writeback_meta("git_reader", "README.md", json.dumps(json_data, indent=4))
    subprocess.call(["./amend_and_push.sh", "git_reader"])

    notify(json_data["summary"],
           msg["summary"],
           transaction["attendees"],
           transaction["paidby"],
           transaction["amount"],
           old_watermark
    )
    return "ok"

def main():
    subprocess.call("./setup_git.sh",)

main()
# json_data = extract_meta("README.md", "git_reader")
# delta = calculate_transaction({ "attendees" : ["a", "b", "c"],
#                               "paidby" : ["d"],
#                               "amount" : 100, } )
# apply_delta(json_data["summary"], delta)
# print json_data
