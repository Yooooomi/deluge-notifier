/**
 * Script: myplugin.js
 *     The client-side javascript code for the MyPlugin plugin.
 *
 * Copyright:
 *     (C) Your Name 2023 <yourname@example.com>
 *
 *     This file is part of MyPlugin and is licensed under GNU GPL 3.0, or
 *     later, with the additional special exception to link portions of this
 *     program with the OpenSSL library. See LICENSE for more details.
 */

MyPluginPlugin = Ext.extend(Deluge.Plugin, {
    constructor: function(config) {
        config = Ext.apply({
            name: 'MyPlugin'
        }, config);
        MyPluginPlugin.superclass.constructor.call(this, config);
    },

    onDisable: function() {
        deluge.preferences.removePage(this.prefsPage);
    },

    onEnable: function() {
        this.prefsPage = deluge.preferences.addPage(
            new Deluge.ux.preferences.MyPluginPage());
    }
});
new MyPluginPlugin();
