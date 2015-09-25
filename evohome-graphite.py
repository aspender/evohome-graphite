import sys
import optparse
import graphitesend
from evohomeclient2 import EvohomeClient

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding("utf-8")

cmdline = optparse.OptionParser(usage="usage: %prog [options]",
    description="Retrieves temperature data from an Evohome System and logs to graphite")

cmdline.add_option('--userid', '-u',
                    help='the Evohome userid',
                    default=None,
                    type='string',
                    dest='userid')

cmdline.add_option('--password', '-p',
                    help='the Evohome password',
                    default=None,
                    type='string',
                    dest='password')

cmdline.add_option('--graphite-host', '-s',
                    help='the Graphite instance host',
                    default="localhost",
                    type='string',
                    dest='graphitehost')

cmdline.add_option('--graphite-port', '-c',
                    help='the Graphite Carbon plaintext instance port',
                    default=2003,
                    type='int',
                    dest='graphiteport')

options, arguments = cmdline.parse_args()

if not options.userid:
	cmdline.error("Evohome userid must be specified")

if not options.password:
	cmdline.error("Evohome password must be specified")

client = EvohomeClient(options.userid, options.password)

locationid = client.installation_info[0]['locationInfo']['locationId']

graphitesend.init(prefix='evohome', graphite_server=options.graphitehost, graphite_port=options.graphiteport,system_name=locationid,lowercase_metric_names=True)

metrics = {}
for device in client.temperatures():
	if device['thermostat'] is 'DOMESTIC_HOT_WATER':
		metrics["water.temp"] = device['temp']
	else:
		metrics["heating.{0}.setpoint".format(device['name'])] = device['setpoint']
		metrics["heating.{0}.temp".format(device['name'])] = device['temp']
graphitesend.send_dict(metrics)