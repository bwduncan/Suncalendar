#!/usr/bin/env python

# -*- coding: iso-8859-1 -*-

"""A mod_python script to output ICS calendar files of sunrise and sunset times
at a given lat/long.

Note: The Sun.py library used seems to follow the long/lat convention, which is
different from the more-commonly used lat/long convention. We attempt to use
lat/long where possible."""

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

    def __init__(self, lat, lon, date, days, type="sunRiseSet"):
        from Sun import Sun
        f = getattr(Sun, type, Sun.sunRiseSet)
        self.utc = vobject.icalendar.utc
        self.v = v = vobject.iCalendar()
        self.lat = lat
        self.lon = lon
        self.d = date
        if f is Sun.sunRiseSet:
            name = "Sunrise and Sunset times for %fN, %fW"
        elif f is Sun.civilTwilight:
            name = "Civil dawn and dusk times for %fN, %fW"
        elif f is Sun.nauticalTwilight:
            name = "Nautical dawn and dusk times for %fN, %fW"
        elif f is Sun.astronomicalTwilight:
            name = "Astronomical dawn and dusk times for %fN, %fW"
        else:
            name = "Times for %fN, %fW" # but it will error anyway.
        v.add('x-wr-calname').value = name % (lat, lon)
        v.add('prodid').value = "-//Bruce Duncan//Sunriseset Calendar 1.1//EN"
        v.add('description').value = "Show the sunrise and sunset times for " \
            + "a given location for one year from the current date."
        for date in range(days):
            rise, set = f(self.d.year, self.d.month, self.d.day,
                          lon, lat) # lat/long reversed.
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
                int(t), int(min), int(sec), tzinfo=self.utc)
        stamp.value = datetime.utcnow()
        start.value = datetime(self.d.year, self.d.month, self.d.day,
                int(t), int(min), int(sec), tzinfo=self.utc)
        uid.value = str(calendar.timegm(start.value.timetuple())) \
                + "-1@suncalendar"
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
    document.getElementById('link').href = 'cal?lat=' +
        document.getElementById('lat').value + '&long=' +
        document.getElementById('long').value + '&type=' +
        document.getElementById('type').value;
    document.getElementById('link').innerHTML = 'iCalendar for ' +
        document.getElementById('type').value + ' for ' +
        document.getElementById('lat').value + 'N, ' +
        document.getElementById('long').value + 'W';
    document.getElementById('linkContainer').style.display = 'block';
    return false
}
/* ]]> */
</script>
</head>
<body style="text-align: justify">
<div style="float: right; width=500px; text-align:right; margin: 1em;
    font-size: small">
<img src="/~bduncan/sunset.jpeg"
    alt="Sunset at Oca&ntilde;a, Spain" style="width:495px" /><br />
<p>Sunset taken at Oca&ntilde;a, Spain by Amy Barsby, 2006.
<a rel="license" href="http://creativecommons.org/licenses/by/2.0/uk/">
<img alt="Creative Commons License" style="border-width:0"
    src="http://i.creativecommons.org/l/by/2.0/uk/80x15.png" /></a><br />
</p>
</div>
<h1>Sunset/Sunrise iCalendar</h1>
<p>Enter your lat/long to get an iCal file for one year, from last month, of
sunrise and sunset times. You may change the parameters to show the times for
civil/nautical/astonomical twilight. You should also be able to import the
calendar dynamically into something like
<a href="http://www.google.com/calendar">Google Calendar</a>. No account is
made of altitude. The default location is pretty close to my flat in
Edinburgh.</p>
<form action="cal" method="get">
<p style="margin-left: 2em">
<label for="lat">Latitude (decimal degrees, negative is South):</label>
<input type="text" name="lat" id="lat" value="55.932756" /><br />
<label for="long">Longitutde (decimal degrees, negative is West):</label>
<input type="text" name="long" id="long" value="-3.177664" /><br />
<label for="type">Type</label>
<select name="type" id="type">
<option value="sunRiseSet">Sunrise/sunset</option>
<option value="civilTwilight">Civil dawn/dusk</option>
<option value="nauticalTwilight">Nautical dawn/dusk</option>
<option value="astronomicalTwilight">Astronomical dawn/dusk</option>
</select><br />
<input type="submit" value="Download .ics" />
<input type="submit" name="URL" value="Show Link"
    onclick="return showLink()" />
</p>
</form>
<p style="display:none; border: dashed 2px red; padding: 5px; margin-left: 2em"
    id="linkContainer">
<a href="cal" id="link">This iCalendar link does not work without javascript
yet...</a></p>
<p>This application was written in <a href="http://www.python.org/">python</a>
by Bruce Duncan in 2008.
It uses the public domain <a href="Sunsource">Sun.py</a> and the
<a href="http://www.apache.org/licenses/LICENSE-1.1">Apache licensed</a>
<a href="http://vobject.skyhouseconsulting.com/">vobject</a> python class (I
used the <a href="http://packages.debian.org/vobject">Debian package</a> for
development).
The <a href="source">source</a> is available under the GPL version 2.
When I wrote this, I was (and still am) working for the
<a href="http://www.see.ed.ac.uk/">University of Edinburgh School of
Engineering<span style="text-decoration: line-through"> and
Electronics</span></a>, but I wrote it in my own time.
I used <a href="http://www.vim.org/">Vim</a>.</p>
<h2>Changes</h2>
<p><b>2009-03-31</b></p>
<p>Times are now output in UTC. This should allow clients to adjust to the
local timezone, especially for DST!</p>
<p><b>2009-12-08</b></p>
<p>Big code cleanup. Fix a presentation bug (&quot;E&quot; instead of
&quot;N&quot;).</p>
<p><b>2009-12-08</b></p>
<p>Add twilight options. Remove promise to store locations. Calendars start
from one month ago.</p>
<p style="text-align: right"><i>Bruce Duncan, &copy; 2008</i>
<a href="http://validator.w3.org/check?uri=referer">
<img src="http://www.w3.org/Icons/valid-xhtml10-blue"
    alt="Valid XHTML 1.0 Strict" style="border:none" /></a>
</p>
</body>
</html>
"""
    req.headers_out['Content-Length'] = str(len(s))
    return s


def cal(req, lat=None, long=None, type=None):
    """Use the Suncal class to output a calendar for one year from the current
    date."""
    if lat is None or long is None:
        req.status = 302
        req.content_type = 'text/plain'
        req.headers_out['Location'] = '.'
        req.write('Found')
    if type is None:
        type = "sunRiseSet"
    req.content_type = "text/calendar"
    d = datetime.datetime.today()
    req.headers_out['Content-Disposition'] = \
        'filename="sun_%s_%s_%s-%02f-%02f.ics"' % (d.year, d.month, d.day,
        lat, long)
    k = Suncal(float(long), float(lat), # lat/long reversed
        d - timedelta(days=30), 365, type)
    s = k.ical()
    req.headers_out['Content-Length'] = str(len(s))
    req.write(s)


def Sunsource(req):
    """Distribute the Sun module."""
    req.content_type = "application/x-python"
    req.headers_out['Content-Disposition'] = 'filename="Sun.py"'
    f = open("/home/bduncan/WWW/Suncalendar/Sun.py")
    req.write(f.read())
    f.close()


def source(req):
    """Deliver the source. Self-replicating code!"""
    req.content_type = "application/x-python"
    req.headers_out['Content-Disposition'] = 'filename="Suncalendar.py"'
    f = open("/home/bduncan/WWW/Suncalendar/index.py")
    req.write(f.read())
    f.close()


def Suncalendar(req):
    """A hack to redirect calendars installed under a previous version."""
    req.status = 301
    req.content_type = 'text/plain'
    req.headers_out['Location'] = '../Suncalendar'
    req.write("Moved permanently")


if __name__ == "__main__":
    d = datetime.today()
    k = Suncal(-3.177664, 55.932756, d-timedelta(days=30), 365)
    print k.ical()
