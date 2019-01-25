#!/usr/bin/env python

import etesync as api
import zmq
import json
import logging
import vobject
from datetime import datetime, timedelta
import re
from time import sleep
from dateutil.tz import tzlocal
from sys import exit


class EtesyncInterface:
    def __init__(self, email, userPassword, remoteUrl, uid, authToken,
                 port, logfile, listen=True):
        r""" Constructor

        Parameters
        ----------
        email : etesync username(email)
        userPassword : etesync encryption password
        remoteUrl : url of etesync server
        uid : uid of calendar (currently only one calendar is supported)
        authToken : authentication token for etesync server
        port : port on which to open zmq socket (if listen=True)
        logfile : logfile to write error messages (if listen=True)
        listen : whether to open zmq socket and listen on it
        """
        self.email = email
        self.userPassword = userPassword
        self.remoteUrl = remoteUrl
        self.uid = uid
        self.authToken = authToken
        self.port = port
        self.logfile = logfile
        self.logger()
        self.download()
        if listen:
            self.bind_socket()
            self.listen()

    def create_event(self, event_string):
        r"""Create event and sync calendar

        Parameters
        ----------
        event_string : iCalendar file as a string
        (calendar containing one event to be added)

        Returns
        -------
        List [True, 'Event Created'] serialized as a json string
        which can be sent over the zmq socket.
        Exceptions are handled in the function listen()
        """
        ev = api.Event.create(self.journal.collection, event_string)
        ev.save()
        self.sync()
        return json.dumps([True, 'Event Created'])

    def edit_event(self, event_string):
        r"""Edit event and sync calendar

        Parameters
        ----------
        event_string : iCalendar file as a string
        (calendar containing one event to be updated)

        Returns
        -------
        List [True, 'Event Changed'] serialized as a json string
        which can be sent over the zmq socket
        Exceptions are handled in the function listen()
        """
        uid = vobject.readOne(event_string).vevent.uid.value
        ev_for_change = self.calendar.get(uid)
        ev_for_change.content = event_string
        ev_for_change.save()
        self.sync()
        return json.dumps([True, 'Event Changed'])

    def delete_event(self, uid):
        r"""Delete event and sync calendar

        Parameters
        ----------
        uid : uid of event to be deleted

        Returns
        -------
        List [True, 'Event Deleted'] serialized as a json string
        which can be sent over the zmq socket
        Exceptions are handled in the function listen()
        """
        ev_for_deletion = self.calendar.get(uid)
        ev_for_deletion.delete()
        self.sync()
        return json.dumps([True, 'Event Deleted'])

    @staticmethod
    def to_datetime(d):
        r"""Convert date or datetime to timezone aware datetime

        Parameters
        ----------
        d : date or datetime (may or not be timezone aware)

        Returns
        -------
        timezone aware datetime converted to local timezone
        """
        def localize_datetime(dt):
            if dt.tzinfo is None:
                return dt.replace(tzinfo=tzlocal())
            else:
                return dt.astimezone(tzlocal())
        if isinstance(d, datetime):
            return localize_datetime(d)
        else:
            return localize_datetime(datetime.combine(
                d, datetime.min.time()))

    def event_match(self, event, start=None, end=None,
                    pattern=None, field='summary', ignore_case=True):
        r"""Check whether an event matches search criteria

        Parameters
        ----------
        event : event (vobject) to be checked
        start : starting date (datetime object) for date searches
        end : ending date (datetime object) for date searches
        pattern : regex pattern for text based searches
        field : field to be searched for text based searches
        ignore_case : do case insensitive matching (defaults to True)

        Returns
        -------
        True if the event matches:
        a) the text based search (if pattern is not None)
        AND
        a) the date based search (unless both start & end are None)
        """
        if 'dtend' in event.contents.keys():
            event_end = self.to_datetime(event.dtend.value)
        else:
            event_end = self.to_datetime(event.dtstart.value
                                         + event.duration.value)
        event_start = self.to_datetime(event.dtstart.value)
        date_in_range = not ((start and event_end < start) or
                             (end and event_start > end))
        flags = re.I if ignore_case else 0
        pat_match = (not pattern) or (
            re.search(pattern, getattr(event, field).value,
                      flags=flags) is not None)
        return date_in_range and pat_match

    def search(self, json_string):
        r"""Retrieve events matching (text and/or date based) search criteria

        Parameters
        ----------
        json_string : dict with following fields (serialized as a json string)

        start : starting date (ISO format) for date searches (defaults to None)
        end : ending date (ISO format) for date searches (defaults to None)
        pattern : regex pattern for text based searches  (defaults to None)
        field : field to be searched for text based searches
                (defaults to 'summary")
        ignore_case : do case insensitive matching (defaults to True)
        Returns
        -------
        iCalendar file containing matching events serialized as a json string
        which can be sent over the zmq socket
        Exceptions are handled in the function listen()
        TODO
        ----
        Allow the regex match to be case insensitive
        """
        def get_params(key, default, to_datetime=False):
            r"""Look up key in parameters dict and return value
            Default value is used if key not found
            Value converted to datetime object if required

            Parameters
            ----------
            key : key to be searched in parameters dict
            default : value to be returned if key not found
            to_datetime : if True convert value to datetime object

            Returns
            -------
            (Converted) value
            """
            if key in parameters.keys():
                if to_datetime:
                    return datetime.fromisoformat(parameters[key])
                else:
                    return parameters[key]
            else:
                return default
        parameters = json.loads(json_string)
        field = get_params('field', 'summary')
        start = get_params('start', None, True)
        end = get_params('end', None, True)
        pattern = get_params('pattern', None)
        ignore_case = get_params('ignore_case', True)
        newcal = vobject.iCalendar()
        for ev in self.events:
            if self.event_match(ev, start=start, end=end,
                                pattern=pattern, field=field,
                                ignore_case=ignore_case):
                newcal.add(ev)
        return json.dumps([True, newcal.serialize()])

    def recent(self, json_string):
        r"""Retrieves recent activity in the journal (add/change/delete)

        Parameters
        ----------
        json_string : dict with one field (serialized as a json string)
        ndays: int number of days of activity to be returned

        Returns
        -------
        iCalendar file containing added/changed/deleted events serialized
        as a json string which can be sent over the zmq socket.
        The events have a custom field X-ACTION set to add/change/delete
        Exceptions are handled in the function listen()
        """
        ndays = json.loads(json_string)['ndays']
        cutoff = self.to_datetime(datetime.today()) - timedelta(days=ndays)
        recent_cal = vobject.iCalendar()
        for e in self.journal.list():
            action = json.loads(e.content)['action']
            cal = vobject.readOne(json.loads(e.content)['content'])
            for ev in cal.vevent_list:
                if('dtstamp' in ev.contents.keys() and
                   self.to_datetime(ev.dtstamp.value) > cutoff):
                    ev.add('X-ACTION').value = action
                    recent_cal.add(ev)
        return json.dumps([True, recent_cal.serialize()])

    def download(self):
        r"""Download calendar from etesync server

        Returns
        -------
        Does not return anything, but stores the following:
        journal: the journal for the chosen calendar
        calendar: the collection for the chosen calendar
        events: list of vobject vevents (all events in calendar)
        """
        self.etesync = api.EteSync(self.email, self.authToken,
                                   remote=self.remoteUrl)
        self.etesync.derive_key(self.userPassword)
        self.etesync.sync()
        self.journal = self.etesync.get(self.uid)
        self.calendar = self.journal.collection
        self.events = [vobject.readOne(E.content).vevent
                       for E in self.calendar.list()]

    def sync(self):
        r"""Sync with server and rebuild vevent list
        """
        self.etesync.sync()
        self.events = [vobject.readOne(E.content).vevent
                       for E in self.calendar.list()]

    def bind_socket(self):
        r"""Create a ZMQ context and socket and bind to a
        port on localhost
        """
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://127.0.0.1:%s" % self.port)

    def logger(self):
        r"""Set up a basic logfile
        Required since this is intended to run as a daemon
        """
        logging.basicConfig(filename=self.logfile,
                            format='%(asctime)s %(message)s',
                            level=logging.INFO)
        logging.info("Etesync Server Started")

    def listen(self):
        r"""Listen and process client requests
        Client requests come on the zmq socket as a list [command, parameters]
        serialized as a json string. Depending on the command, parameters may
        be a simple string (e.g. uid) or a iCalendar file as a string
        or a dict serialized as json string.
        Depending on the command, the request is passed on to the appropriate
        command and the return value from that function is sent back to the
        client as a reply.
        Exceptions are handled by enclosing the entire request handling in
        a try block. This ensures that this server does not abort because of
        a faulty client request. The exception is serialized and sent back to
        the client
        The reply to the client is a list [status, message] serialized as a
        json string. The status (True/False) tells the client whether the
        command succeeded. The message has further details. In case of failure,
        the message includes the exception as a string.
        """
        while True:
            try:
                message = self.socket.recv_string()
                try:
                    command, parameters = json.loads(message)
                    logging.info("Received %s request:\n %s",
                                 command, parameters)
                    if command == 'add':
                        reply = self.create_event(parameters)
                    elif command == 'edit':
                        reply = self.edit_event(parameters)
                    elif command == 'delete':
                        reply = self.delete_event(parameters)
                    elif command == 'sync':
                        self.sync()
                        reply = json.dumps([True, 'Calendar Synced'])
                    elif command == 'search':
                        reply = self.search(parameters)
                    elif command == 'quit':
                        logging.info("Quitting ...")
                        reply = json.dumps([True, "Quitting"])
                        self.socket.send_string(reply)
                        exit(0)
                    elif command == 'recent':
                        reply = self.recent(parameters)
                    else:
                        reply = json.dumps([False, "Invalid Command"])
                except Exception as inst:
                    # We log the exception and also
                    # send it to the client as a string
                    logging.error('EXCEPTION: ' + str(inst))
                    reply = json.dumps([False, str(inst)])
                self.socket.send_string(reply)
                logging.info("Sent Reply:\n %s ...", reply[:45])
            except Exception as inst:
                # The inner try block captures all exceptions raised
                # during the processing. The only exceptions handled
                # here are in the receive/send operations on the socket
                # Only thing that can be done is to log the exception
                logging.error(str(inst))
            sleep(1)


def main(email, userPassword, remoteUrl, uid, authToken, port, logfile):
    r"""Create an instance of the EtesyncInterface and start listening

    Parameters
    ----------
    email : etesync email address
    userPassword : etesync encryption password
    remoteUrl : url of etesync server
    uid : uid of calendar (currently only one calendar is supported)
    authToken : authentication token for etesync server
    port : port on which to open zmq socket
    logfile : logfile to write error messages
    """
    EtesyncInterface(email, userPassword, remoteUrl, uid,
                     authToken, port, logfile)


# if __name__ == '__main__':
#     # Use terminal or configuration file or keyring
#     # to read username(email), password, url, calendar uid,
#     # authentication token, port and logfile
#     # Call main() with these values and maybe daemonize
