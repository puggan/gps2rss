#!/usr/bin/python
# -*- coding: UTF-8 -*-

import datetime
import gps
import math
import sys

files = set()
options = set()
keywords = {}

for arg in sys.argv[1:]:
	if arg.startswith("--"):
		arg = arg[2:]
		if "=" in arg:
			key, value = arg.split("=", 1)
			keywords[key] = value
		else:
			options.add(arg)
	else:
		files.add(arg)

gps_server = {
	"host": "127.0.0.1",
	"port": "2947"
}

if "host" in keywords:
	gps_server["host"] = keywords["host"]
elif "ip" in keywords:
	gps_server["host"] = keywords["ip"]

if "port" in keywords:
	gps_server["port"] = keywords["port"]

# Tellus radie: 40 Mm = 360° => 50m = 0.00045°
# 360° * 50m / 40 000 000m
if "mindiff" in keywords:
	min_diff = 360 * float(keywords["mindiff"]) / 40000000
else:
	min_diff = 0.00045

if "template" in keywords:
	template = keywords["template"]
else:
	template = "georss_template.xml"

if "outfile" in keywords:
	outfile = keywords["outfile"]
	template_data = open(template, 'r').read()
else:
	outfile = "";

last_lat = 0.00
last_lon = 0.00

positions = ""

session = gps.gps(**gps_server)

session.stream(2)

for report in session:
	try:
		diff_lat = report.lat - last_lat
		diff_lon = report.lon - last_lon
		diff = diff_lat * diff_lat + diff_lon * diff_lon * math.fabs(math.cos(report.lat))
		if diff >= min_diff:
			new_pos = "%(lat)s %(lon)s " % report
			last_lat = report.lat
			last_lon = report.lon
			print new_pos
			positions += new_pos
			if outfile:
				georss = template_data % {"position": positions, "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S") + "Z"}
				open(outfile, 'w').write(georss)
	except AttributeError:
		pass
	except KeyError:
		pass
del session
