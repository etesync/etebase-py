#!/usr/bin/env python

import etesync as api


class EtesyncCRUD:
    def __init__(self, email, userPassword, remoteUrl, uid, authToken,
                 cipher_key=None):
        r"""Initialize EtesyncInterface

        Parameters
        ----------
        email : etesync username(email)
        userPassword : etesync encryption password
        remoteUrl : url of etesync server
        uid : uid of calendar
        authToken : authentication token for etesync server
        """
        self.etesync = api.EteSync(email, authToken, remote=remoteUrl)
        if cipher_key:
            self.etesync.cipher_key = cipher_key
        else:
            self.etesync.derive_key(userPassword)
        self.journal = self.etesync.get(uid)
        self.calendar = self.journal.collection
        self.error = None

    def create_event(self, event):
        r"""Create event

        Parameters
        ----------
        event : iCalendar file as a string
        (calendar containing one event to be added)

        Returns
        -------
        True if event created
        False otherwise (Error is stored in self.error)
        """
        try:
            ev = api.Event.create(self.journal.collection, event)
            ev.save()
            return True
        except Exception as inst:
            self.error = inst
            return False

    def update_event(self, event, uid):
        r"""Edit event

        Parameters
        ----------
        event : iCalendar file as a string
        (calendar containing one event to be updated)
        uid : uid of event to be updated

        Returns
        -------
        True if event updated
        False otherwise (Error is stored in self.error)
        """
        try:
            ev_for_change = self.calendar.get(uid)
            ev_for_change.content = event
            ev_for_change.save()
            return True
        except Exception as inst:
            self.error = inst
            return False

    def retrieve_event(self, uid):
        r"""Retrieve event by uid

        Parameters
        ----------
        uid : uid of event to be retrieved

        Returns
        -------
        On success returns iCalendar file (as a string)
        Otherwise returns None (Error is stored in self.error)
        """
        try:
            return self.calendar.get(uid).content
        except Exception as inst:
            self.error = inst
            return None

    def all_events(self):
        r"""Retrieve all events in calendar


        Returns
        -------
        On success returns list of iCalendar files (as strings)
        Otherwise returns None (Error is stored in self.error)
        """
        try:
            return [E.content for E in self.calendar.list()]
        except Exception as inst:
            self.error = inst
            return None

    def delete_event(self, uid):
        r"""Delete event and sync calendar

        Parameters
        ----------
        uid : uid of event to be deleted

        Returns
        -------
        True if event deleted
        False otherwise (Error is stored in self.error)
        """
        try:
            ev_for_deletion = self.calendar.get(uid)
            ev_for_deletion.delete()
            return True
        except Exception as inst:
            self.error = inst
            return False

    def sync(self):
        r"""Sync with server
        """
        try:
            self.etesync.sync()
            return True
        except Exception as inst:
            self.error = inst
            return False
