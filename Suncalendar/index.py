#!/usr/bin/env python 

# -*- coding: iso-8859-1 -*-

"""A quick redirect."""

def Suncalendar(req):
	_redirect(req, '..')

index = Suncalendar

def cal(req):
	_redirect(req, '../cal'+(req.args and '?' or '')+req.args)

def _redirect(req, loc):
	"""A hack to redirect calendars installed under a previous version."""
	req.status = 301;
	req.content_type = 'text/plain';
	req.headers_out['Location'] = loc;
	req.write("Moved permanently");
