import sys, os, time, datetime, signal
import argparse, logging
import ConfigParser
import requests
from provplan_email_lib import *

parser = argparse.ArgumentParser(description='Ping urls and evaluate return status')
#parser.add_argument('-f', action="store", dest="url_file", type=str, help="Path to url config file")
parser.add_argument('-t', action="store", dest="time", type=int,  help='Time between pings')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
lfh = logging.FileHandler(filename='var/log/pinger.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s')
lfh.setFormatter(formatter)
logger.addHandler(lfh)

# get urls from conf
urlconfig = ConfigParser.SafeConfigParser()
urlconfig.read('urls.conf')


mailer = Emailer(config_file='email.conf')
admins = mailer.config.get('emails','to')


def make_message(url, status_code):
    mssg = 'URL {0} Responded with {1}'.format(url, status_code)
    return mssg

def notify(url, status_code):
    # send notification to admins
    logger.error(make_message(url, status_code))
    # send email to admins
    mailer.send_email(to_addresses=admins, subject='%s Response from Pinger' % url, body=make_message(url, status_code), from_address='do-not-reply@provplan.org')

def ping(url):
    r = requests.get(url)
    if r.status_code != 200:
        notify(url, r.status_code)
    else:
        logger.info(make_message(url, r.status_code))

def signal_handler(signal, frame):
    print '...Exiting...'
    logger.info('Stopping Ping Process')
    mailer.disconnect()
    sys.exit(0)

def run():
    # register signal
    signal.signal(signal.SIGINT, signal_handler)
    args = parser.parse_args()

    logger.info('Starting Ping Process')

    while True:
        for section in urlconfig.sections():
            url = urlconfig.get(section,'url')
            ping(url)

        time.sleep(args.time)

if __name__ == '__main__':
    run()


