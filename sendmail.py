import sendgrid
import os
from flask import render_template
import sys
import re
import json
reload(sys)
sys.setdefaultencoding('utf8')
s = sendgrid.Sendgrid(os.getenv("SENDGRID_USERNAME", 'app11487356@heroku.com'),
                      os.getenv("SENDGRID_PASSWORD", 'fn99lro1'),
                      secure=True)

def notify(head, summary, attendees, paidby, amount, watermark):
    recipients = filter(lambda email: re.match(r"[^@]+@[^@]+\.[^@]+", email),
                        set(attendees).union(set(paidby)))
    if not recipients: return
    title = "[GitMoney] New transaction from gitmoney!"
    sender = "nov503@gmail.com"
    content = "(To add more transactions, visit gitmoney.herokuapp.com): \r\n"
    content += "You have a new transaction from gitmoney, here is the summary:\r\n"
    content += "%s \r\n" % summary
    content += "attendees: %s \r\n" % ", ".join(attendees)
    content += "paidby: %s \r\n" % ", ".join(paidby)
    content += "amount: %s \r\n" % str(amount)
    content += "\r\n\r\n\r\n"
    content += "current credit is:\r\n"
    for p in head:
        content += "%s : %s\r\n" % (p, str(head[p]))
    content += "\r\n\r\n"
    content = content.encode('utf-8')
    print title
    message = sendgrid.Message(sender, title, content)
    for r in recipients:
        message.add_to(r)
    message.add_header("charset", "utf-8")
    path_to_file = os.path.join(os.getcwd(), watermark)
    if os.path.exists(path_to_file):
        message.add_attachment("proof.png", path_to_file)
    s.web.send(message)
# if __name__ == "__main__":
#     notify(["nov503@gmail.com", "axia@macalester.edu"], {"axia@macalester.edu":1, "nov503@gmail.com":-1}, "lunch",
#            ["nov503@gmail.com", "axia@macalester.edu"], ["nov503@gmail.com"],
#            1.00)
