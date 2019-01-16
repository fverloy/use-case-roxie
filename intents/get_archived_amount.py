"""Return amount of data archived."""
import json
import math
import os
import ssl
import urllib2

CLUSTER_IP = os.environ['CLUSTER_IP']
AUTH_TOKEN = os.environ['AUTH_TOKEN']

''' Sample Utterances
How much data has been archived
Give me details of archival storage
What is the amount of archived data
'''

LEX_RESULT = {
    'dialogAction': {
        'type': 'Close',
        'fulfillmentState': 'Fulfilled',
        'message': {
            'contentType': 'PlainText',
            # 'content': '%s' <--- This is filled in the end
        }
    }
}

TB = math.pow(10, 12)
GB = math.pow(10, 9)
MB = math.pow(10, 6)
PRECISION = 1


def human_readable_size(bytes):
    tb = None
    gb = None
    mb = None
    bytes = int(bytes)
    tb = round(bytes / TB, PRECISION)
    if not tb:
        gb = round(bytes / GB, PRECISION)
    if not tb and not gb:
        mb = round(bytes / MB, PRECISION)

    output = None
    if tb:
        output = '%s Terabytes' % tb
    if gb:
        output = '%s Gigabytes' % gb
    if mb:
        output = '%s Megabytes' % mb
    if not output:
        output = '%s Bytes' % bytes

    return output


def lambda_handler(event, context):
    del event
    del context

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    req = urllib2.Request(
        ('https://%s/api/internal/stats/cloud_storage/physical' %
         CLUSTER_IP),
        None
    )
    req.add_header('Authorization', 'Bearer %s' % AUTH_TOKEN)

    handler = urllib2.HTTPSHandler(context=ssl_context)
    opener = urllib2.build_opener(handler)
    resp = json.load(opener.open(req))
    print('REST API call response: %s' % resp)
    """ Sample response:
    {u'lastUpdateTime': u'2019-01-16T00:09:57.371Z',
     u'name': u'PhysicalCloudStorage', u'value': u'3482213220',
     u'frequencyInMin': 30}
    """

    if 'value' not in resp:
        output = (
            'I am sorry, amount of data archived is not available')
    else:
        output = 'Archived amount is %s' % human_readable_size(resp['value'])

    LEX_RESULT['dialogAction']['message']['content'] = output
    print('Response to Lex: %s' % LEX_RESULT)
    return LEX_RESULT

if __name__ == '__main__':
    lambda_handler(None, None)
