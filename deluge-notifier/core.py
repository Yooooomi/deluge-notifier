# -*- coding: utf-8 -*-
# Copyright (C) 2023 Your Name <yourname@example.com>
#
# Basic plugin template created by the Deluge Team.
#
# This file is part of MyPlugin and is licensed under GNU GPL 3.0, or later,
# with the additional special exception to link portions of this program with
# the OpenSSL library. See LICENSE for more details.
from __future__ import unicode_literals

import logging
import requests

import deluge.configmanager
import deluge.component
from deluge.core.rpcserver import RPCServer
from deluge.core.torrentmanager import TorrentManager
from deluge.core.eventmanager import EventManager
from deluge.core.torrent import Torrent
from deluge.core.rpcserver import export
from deluge.plugins.pluginbase import CorePluginBase

log = logging.getLogger(__name__)

DEFAULT_PREFS = {
    'notification_server_endpoint': '',
    'torrent_id_to_username': {}
}


class Core(CorePluginBase):
    def enable(self):
        log.debug('Enabling')
        self.config = deluge.configmanager.ConfigManager(
            'deluge-notifier.conf', DEFAULT_PREFS)

        rpcServer: RPCServer = deluge.component.get('RPCServer')
        rpcServer.register_object(self)

        event_manager: EventManager = deluge.component.get('EventManager')
        event_manager.register_event_handler('TorrentFinishedEvent', self.on_torrent_finish)

        event_manager: EventManager = deluge.component.get('EventManager')
        event_manager.register_event_handler('TorrentRemovedEvent', self.on_torrent_removed)

    def disable(self):
        log.debug('Disabling')

        event_manager: EventManager = deluge.component.get('EventManager')
        event_manager.deregister_event_handler('TorrentFinishedEvent', self.on_torrent_finish)

        event_manager: EventManager = deluge.component.get('EventManager')
        event_manager.deregister_event_handler('TorrentRemovedEvent', self.on_torrent_removed)

        rpcServer: RPCServer = deluge.component.get('RPCServer')
        rpcServer.deregister_object(self)

    def notify(self, username: str, torrent_id: str):
        torrent: Torrent = deluge.component.get('TorrentManager')[torrent_id]
        params = {"username": username, "title": f"Le fichier {torrent.get_name()} est téléchargé", "content": "Il devrait être disponible"}
        requests.post("https://notification.yooooomi.com/notify", params=params)

    def on_torrent_finish(self, torrent_id: str):
        torrent: Torrent = deluge.component.get('TorrentManager')[torrent_id]
        log.info(f"Torrent {torrent.torrent_id} has finished, sending notifications")
        if torrent_id not in self.config['torrent_id_to_username']:
            return
        found_username = self.config['torrent_id_to_username'][torrent_id]
        log.info(f"Found username {found_username}, sending notification")
        self.notify(torrent_id)

    def on_torrent_removed(self, torrent_id: str):
        if torrent_id not in self.config['torrent_id_to_username']:
            return
        del(self.config['torrent_id_to_username'][torrent_id])

    @export
    def add_torrent_with_username(self, username: str, add_options):
        filepath = add_options["path"]
        options = add_options["options"]
        
        torrent_manager: TorrentManager = deluge.component.get('TorrentManager')
        torrent_info = torrent_manager.get_torrent_info_from_file(filepath)
        added_torrent_id = torrent_manager.add(torrent_info=torrent_info, options=options)
        
        self.config['torrent_id_to_username'][added_torrent_id] = username

    @export
    def set_config(self, config):
        """Sets the config dictionary"""
        for key in config:
            self.config[key] = config[key]
        self.config.save()

    @export
    def get_config(self):
        """Returns the config dictionary"""
        return self.config.config
