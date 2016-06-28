# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko.conf import settings
from pyoko.lib.utils import get_object_from_path
from zengine.messaging.model import Channel, Attachment
from zengine.views.base import BaseView

UserModel = get_object_from_path(settings.USER_MODEL)


def create_message(current):
    """
    Creates a message for the given channel.

    .. code-block:: python

        # request:
        {
            'view':'_zops_create_message',
            'message': {
                'channel': "code_name of the channel",
                'receiver': key, " of receiver. Should be set only for direct messages",
                'title': "Title of the message. Can be blank.",
                'body': "Message body.",
                'type': zengine.messaging.model.MSG_TYPES,
                'attachments': [{
                    'description': "Can be blank.",
                    'name': "File name with extension.",
                    'content': "base64 encoded file content"
                    }]}
        # response:
        {
            'msg_key': key,  # of the just created message object,
        }

    """
    msg = current.input['message']
    ch = Channel.objects.get(msg['channel'])
    msg_obj = ch.add_message(body=msg['body'], typ=msg['typ'], sender=current.user,
                             title=msg['title'], receiver=msg['receiver'] or None)
    if 'attachment' in msg:
        for atch in msg['attachments']:
            # TODO: Attachment type detection
            typ = current._dedect_file_type(atch['name'], atch['content'])
            Attachment(channel=ch, msg=msg_obj, name=atch['name'], file=atch['content'],
                       description=atch['description'], typ=typ).save()


def _dedect_file_type(name, content):
    # FIXME: Implement attachment type detection
    return 1  # Return as Document for now


def show_channel(current):
    """
    Initial display of channel content.
    Returns channel description, members, no of members, last 20 messages etc.


    .. code-block:: python

        #  request:
            {
                'view':'_zops_show_public_channel',
                'channel_key': key,
            }

        #  response:
            {
                'channel_key': key,
                'description': string,
                'no_of_members': int,
                'member_list': [
                    {'name': string,
                     'is_online': bool,
                     'avatar_url': string,
                    }],
                'last_messages': [
                    {'content': string,
                     'title': string,
                     'channel_key': key,
                     'sender_name': string,
                     'sender_key': key,
                     'type': int,
                     'key': key,
                     'actions':[('name_string', 'cmd_string'),]
                    }
                ]
            }
    """
    ch_key = current.input['channel_key']
    ch = Channel.objects.get(ch_key)
    current.output = {'channel_key': ch_key,
                      'description': ch.description,
                      'no_of_members': len(ch.subscriber_set),
                      'member_list': [{'name': sb.user.full_name,
                                       'is_online': sb.user.is_online(),
                                       'avatar_url': sb.user.get_avatar_url()
                                       } for sb in ch.subscriber_set],
                      'last_messages': [msg.serialize_for(current.user)
                                        for msg in ch.get_last_messages()]
                      }

def mark_offline_user(current):
    current.user.is_online(False)

def list_channels(current):
    return [
        {'name': sbs.channel.name,
         'key': sbs.channel.key,
         'unread': sbs.unread_count()} for sbs in
        current.user.subscriptions]


def create_public_channel(current):
    pass


def create_direct_channel(current):
    """
    Create a One-To-One channel for current user and selected user.

    """
    pass


def create_broadcast_channel(current):
    """
    Create a One-To-One channel for current user and selected user.

    """
    pass


def find_message(current):
    pass


def delete_message(current):
    pass


def edit_message(current):
    pass
