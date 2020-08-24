#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging

from SteamClient import SteamClient

username = ''
password = ''
secrets = {'shared_secret': '',
    'serial_number': '',
    'revocation_code': '',
    'uri': '',
    'server_time': '',
    'account_name': '',
    'token_gid': '',
    'identity_secret': '',
    'secret_1': '',
    'status': 1
}
deviceId = 'android:'

steam = SteamClient(username, password, secrets, deviceId)

from telegram.ext import Updater, CommandHandler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

def online(bot, update):
    update.message.reply_text('机器人处于在线状态。')

def check_card(bot, update, args):
    if len(args) == 0:
        update.message.reply_text('必须要有一个参数！')
        return
    if len(args) != 1:
        update.message.reply_text('参数只能有一个！')
        return
    results = steam.validateWalletCode(args[0])
    if results['success'] == 21:
        msg = '卡被别人兑换过了'
    elif results['detail'] == 0:
        msg = '卡可用\n面额: %s' % (results['formattedcodeamount'])
        update.message.reply_text(msg)
        return
    elif results['detail'] == 9:
        msg = '卡已经被这个账号兑换过了'
    elif results['detail'] == 14:
        msg = '卡号不存在'
    elif results['detail'] == 15:
        msg = '卡被别人兑换过了'
    else:
        msg = '未知错误'
    update.message.reply_text(msg + '\n' + json.dumps(results))
    
def redeem_card(bot, update, args):
    if len(args) == 0:
        update.message.reply_text('必须要有一个参数！')
        return
    if len(args) != 1:
        update.message.reply_text('参数只能有一个！')
        return
    results = steam.validateWalletCode(args[0])
    if results['success'] == 21:
        results = steam.validateWalletCode(args[0])
    if results['success'] != 1:
        return check_card(bot, update, args)
    if results['detail'] != 0:
        return check_card(bot, update, args)
    redeem_results = steam.redeemWalletCode(args[0])
    msg = '兑换结果\n%s' % (json.dumps(redeem_results))
    update.message.reply_text(msg)

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your token and private key
    updater = Updater('')

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('online', online))
    dp.add_handler(CommandHandler('check', check_card, pass_args=True))
    dp.add_handler(CommandHandler('redeem', redeem_card, pass_args=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()