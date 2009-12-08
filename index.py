#!/usr/bin/env python 

# -*- coding: iso-8859-1 -*-

"""A mod_python script to output ICS calendar files of sunrise and sunset times
at a given lat/long."""

import vobject
from datetime import datetime, timedelta, tzinfo
import calendar

#class UTC(tzinfo):
#    def __init__(self):
#        self.ZERO = timedelta(0)
#    def utcoffset(self, dt):
#        return self.ZERO
#    def dst(self, dt):
#        return self.ZERO
#    def tzname(self, dt):
#        return "UTC"

class Suncal:
    """Wrapper class for the Sun class. One useful method which returns a
       string representation of the ICS."""
    def __init__(self, lon, lat, year, month, day, days):
        import Sun
        self.utc = vobject.icalendar.utc
        self.v = v = vobject.iCalendar()
        self.lon = lon
        self.lat = lat
        self.d = datetime(year, month, day)
        j = Sun.Sun()
        v.add('x-wr-calname').value = "Sunrise and Sunset times for %fW, %fN" % (lon, lat)
        v.add('prodid').value = "-//Bruce Duncan//Sunriseset Calendar 1.1//EN"
        v.add('description').value = "Show the sunrise and sunset times for a given location for one year from the current date."
        for date in range(days):
            rise, set = j.sunRiseSet(self.d.year, self.d.month, self.d.day, lon, lat)
            self.__addPoint(v, rise, 'Sunrise')
            self.__addPoint(v, set, 'Sunset')
            self.d += timedelta(1)
    def __addPoint(self, v, t, summary):
        ev = v.add('vevent')
        ev.add('summary').value = summary
        uid = ev.add('uid')
        start = ev.add('dtstart')
        stamp = ev.add('dtstamp')
        end = ev.add('dtend')
        geo = ev.add('geo')
        min = 60 * (t - int(t))
        sec = 60 * (min - int(min))
        end.value = datetime(self.d.year, self.d.month, self.d.day, 
                int(t), int(min), int(sec), tzinfo = self.utc) + timedelta(seconds=1)
        stamp.value = datetime.utcnow()
        start.value = datetime(self.d.year, self.d.month, self.d.day, 
                int(t), int(min), int(sec), tzinfo = self.utc)
        uid.value = str(calendar.timegm(start.value.timetuple())) + "-1@suncalendar"
        geo.value = "%f;%f" % (self.lat, self.lon)

    def ical(self):
        return self.v.serialize().replace("\r\n", "\n").strip()

def index(req):
    """Serve the static index page."""
    req.content_type = "application/xhtml+xml"
    s = """\
<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
<meta http-equiv="Content-Style-Type" content="text/css" />
<meta http-equiv="Content-Script-Type" content="text/javascript" />
<title>iCal sunrise and sunset</title>
<script type="text/javascript">
/* <![CDATA[ */
function showLink() {
    document.getElementById('link').href = 'cal?long=' +
        document.getElementById('long').value + '&lat=' +
        document.getElementById('lat').value;
    document.getElementById('link').innerHTML = 'iCalendar for ' +
        document.getElementById('long').value + 'W, ' +
        document.getElementById('lat').value + 'E';
    document.getElementById('linkContainer').style.display = 'block';
    return false
}
/* ]]> */
</script>
</head>
<body style="text-align: justify">
<div style="float: right; width=500px; text-align:right; margin: 1em; font-size: small">
<img src="/~bduncan/sunset.jpeg"
    alt="Sunset at Oca&ntilde;a, Spain" style="width:495px" /><br />
<p>Sunset taken at Oca&ntilde;a, Spain by Amy Barsby, 2006.
<a rel="license" href="http://creativecommons.org/licenses/by/2.0/uk/">
<img alt="Creative Commons License" style="border-width:0"
    src="http://i.creativecommons.org/l/by/2.0/uk/80x15.png" /></a><br />
</p>
</div>
<h1>Sunset/Sunrise iCalendar</h1>
<p>Enter your lat/long to get an iCal file for one year, from today, of sunrise
and sunset times. You should also be able to import the calendar dynamically
into something like <a href="http://www.google.com/calendar">Google
Calendar</a>. No account is made of altitude. The default location is pretty
close to my flat in Edinburgh. In future versions, I hope to be able to store
named locations for people to choose from a list.</p>
<form action="cal" method="get">
<p style="margin-left: 2em">
<label for="long">Longitutde (decimal degrees, negative is West):</label>
<input type="text" name="long" id="long" value="-3.177664" /><br />
<label for="lat">Latitude (decimal degrees, negative is South):</label>
<input type="text" name="lat" id="lat" value="55.932756" />
<input type="submit" value="Download .ics" />
<input type="submit" name="URL" value="Show Link" onclick="return showLink()" />
</p>
</form>
<p style="display:none; border: dashed 2px red; padding: 5px; margin-left: 2em" id="linkContainer">
<a href="cal" id="link">This iCalendar link does not work without javascript yet...</a></p>
<p>This application was written in <a href="http://www.python.org/">python</a> by Bruce Duncan in 2008.
It uses the public domain <a href="Sunsource">Sun.py</a> and the <a href="http://www.apache.org/licenses/LICENSE-1.1">Apache licensed</a> <a href="http://vobject.skyhouseconsulting.com/">vobject</a> python class (I used the <a href="http://packages.debian.org/vobject">Debian package</a> for development).
The <a href="source">source</a> is available under the GPL version 2.
When I wrote this, I was (and still am) working for the <a href="http://www.see.ed.ac.uk/">University of Edinburgh School of Engineering<span style="text-decoration: line-through"> and Electronics</span></a>, but I wrote it in my own time.
I used <a href="http://www.vim.org/">Vim</a>.</p>
<h2>Changes</h2>
<p><b>2009-03-31</b></p>
<p>Times are now output in UTC. This should allow clients to adjust to the local timezone, especially for DST!</p>
<p style="text-align: right"><i>Bruce Duncan, &copy; 2008</i>
<a href="http://validator.w3.org/check?uri=referer">
<img src="http://www.w3.org/Icons/valid-xhtml10-blue" alt="Valid XHTML 1.0 Strict" style="border:none" /></a>
</p>
</body>
</html>
"""
    req.headers_out['Content-Length'] = str(len(s))
    return s

def cal(req, long=None, lat=None):
    """Use the Suncal class to output a calendar for one year from the current date."""
    if long is None or lat is None:
        req.status = 302
        req.content_type = 'text/plain'
        req.headers_out['Location'] = '.'
        req.write('Found')
    from datetime import datetime
    req.content_type = "text/calendar"
    d = datetime.today()
    req.headers_out['Content-Disposition'] = 'filename="sun_%s_%s_%s-%02d-%02d.ics"' % (long, lat, d.year, d.month, d.day)
    k = Suncal(float(long), float(lat), d.year, d.month, d.day, 365)
    s = k.ical()
    req.headers_out['Content-Length'] = str(len(s))
    req.write(s)

def Sunsource(req):
    """Distribute the Sun module."""
    req.content_type="application/x-python"
    req.headers_out['Content-Disposition'] = 'filename="Sun.py"'
    f = open("/home/bduncan/WWW/Suncalendar/Sun.py")
    req.write(f.read())
    f.close()

def source(req):
    """Deliver the source. Self-replicating code!"""
    req.content_type="application/x-python"
    req.headers_out['Content-Disposition'] = 'filename="Suncalendar.py"'
    f = open("/home/bduncan/WWW/Suncalendar/index.py")
    req.write(f.read())
    f.close()

def Suncalendar(req):
    """A hack to redirect calendars installed under a previous version."""
    req.status = 301;
    req.content_type = 'text/plain';
    req.headers_out['Location'] = '../Suncalendar';
    req.write("Moved permanently");

if __name__ == "__main__":
    from datetime import datetime
    d = datetime.today()
    k = Suncal(-3.177664, 55.932756, d.year, d.month, d.day, 365)
    print k.ical()
