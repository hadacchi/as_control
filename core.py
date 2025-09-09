import logging
import toml
from .airstation import AirStationWebsite

'''
ap.py is a plugin to control device MAC address authentication on AirStation.

This plugin needs hadacchi/as_control.

Usage:
    @BOTNAME ap SUBCOMMAND [OPTION]

Example:
    @BOTNAME ap devices
'''

logger = logging.getLogger(__name__)

SUBCOMMANDS = ['devices', 'del', 'add', 'delmac', 'addmac']
CONFIG_FILE = 'ap_config.toml'

def run_internal(attrs, bot_client, channel_id):
    '''
    @BOTNAME ap
        devices           登録済デバイスのMACアドレスのリストを取得
        del DEVNAME       デバイスリストのうち削除するデバイスを指定
        add DEVNAME       デバイスリストのうち追加するデバイスを指定
        delmac MACADDR    削除するデバイスのMACアドレスを直接指定
        addmac MACADDR    追加するデバイスのMACアドレスを直接指定
    '''

    logger.info(f'ap runs: {attrs}')

    if attrs is None:
        logger.error('This plugin requires SUBCOMMAND.')
        bot_client.chat_postMessage(channel=channel_id, text=msgs.error())
        return False

    #say(msgs.confirm())

    # サブコマンドで振り分け
    subcommand = attrs[0]

    if subcommand not in SUBCOMMANDS:
        logger.error('Invalid subcommand: ' + subcommand)
        bot_client.chat_postMessage(channel=channel_id, text=msgs.error())
        return False

    if subcommand == 'devices':
        # デバイスリストを返却する処理
        ASsite = AirStationWebsite(CONFIG_FILE)
        try:
            devices = ASsite.get_registered_devices()
            bot_client.chat_postMessage(channel=channel_id, text=str(devices))
        except Exception as e:
            bot_client.chat_postMessage(channel=channel_id, text=str(e))
            logger.error(str(e))
        ASsite.exit()
    elif subcommand == 'delmac':
        # del macaddr
        ASsite = AirStationWebsite(CONFIG_FILE)
        try:
            if ASsite.del_mac_addr(attrs[1]):
                bot_client.chat_postMessage(channel=channel_id, text=msgs.finish())
            else:
                bot_client.chat_postMessage(channel=channel_id, text=msgs.error())
                logger.error('del_mac_addr returns False')
        except Exception as e:
            bot_client.chat_postMessage(channel=channel_id, text=str(e))
            logger.error(str(e))
        ASsite.exit()
    elif subcommand == 'addmac':
        # add macaddr
        ASsite = AirStationWebsite(CONFIG_FILE)
        try:
            if ASsite.add_mac_addr(attrs[1]):
                bot_client.chat_postMessage(channel=channel_id, text=msgs.finish())
            else:
                bot_client.chat_postMessage(channel=channel_id, text=msgs.error())
                logger.error('add_mac_addr returns False')
        except Exception as e:
            bot_client.chat_postMessage(channel=channel_id, text=str(e))
            logger.error(str(e))
        ASsite.exit()
    elif match.find('del') >= 0:
        # del device
        ASsite = AirStationWebsite(CONFIG_FILE)
        try:
            if ASsite.del_device(' '.join(attrs[1:])):
                bot_client.chat_postMessage(channel=channel_id, text=msgs.finish())
            else:
                bot_client.chat_postMessage(channel=channel_id, text=msgs.error())
                logger.error('del_device returns False')
        except Exception as e:
            bot_client.chat_postMessage(channel=channel_id, text=str(e))
            logger.error(str(e))
        ASsite.exit()
    elif match.find('add') >= 0:
        # add device
        ASsite = AirStationWebsite(CONFIG_FILE)
        try:
            if ASsite.add_device(' '.join(attrs[1:])):
                bot_client.chat_postMessage(channel=channel_id, text=msgs.finish())
            else:
                bot_client.chat_postMessage(channel=channel_id, text=msgs.error())
                logger.error('add_device returns False')
        except Exception as e:
            bot_client.chat_postMessage(channel=channel_id, text=str(e))
            logger.error(str(e))
        ASsite.exit()
    return True