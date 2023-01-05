import json
import time

import requests

from pytesseract import pytesseract
from PIL import ImageGrab

from typing import Union

THRESHOLDS = {}
cfg = {}


def send_msg(content: str, webhook: str) -> None:
    """
    Sends message to a webhook
    :param content: Content of message to send
    :param webhook: Url of webhook
    :return: None
    """
    data = {"content": content}
    requests.post(webhook, json=data).raise_for_status()


def get_queue_information() -> Union[int, None]:
    """
    :return: number of players ahead of you, None if error reading.
    """
    bb = (1500, 960, 1820, 1000)

    im = ImageGrab.grab(bb)
    queue_data = pytesseract.image_to_string(im).split(" ")

    ahead = queue_data[0]
    if not ahead.isnumeric() and "next" in [x.lower() for x in queue_data]:
        return 0
    if ahead.isnumeric():
        return int(ahead)
    return None


def load_cfg() -> None:
    """
    Loads configuration file.
    :return: None
    """
    with open("settings.json", 'r') as f:
        data = json.load(f)
        next_msg = data.get("next")
        user_to_mention = data.get("user_to_mention_id")
        webhook_url = data.get('webhook')

        cfg['next_msg'] = next_msg
        cfg['user_to_mention'] = user_to_mention
        cfg['webhook'] = webhook_url
        for threshold, msg in data.get("thresholds").items():
            THRESHOLDS[int(threshold)] = {"msg": msg, "triggered": False}


def read_notify() -> bool:
    """
    Loop to check how many players are ahead of you, check thresholds, notify when needed
    :return: True if done, False if not
    """
    players_ahead = get_queue_information()
    if not players_ahead:
        print("Err")
        return False
    for threshold in THRESHOLDS:
        if THRESHOLDS[threshold].get('triggered'):
            continue
        if players_ahead == 0:
            send_msg(f"<@{cfg['user_to_mention']}> {cfg['next_msg']}", webhook=cfg['webhook'])
            return True
        if players_ahead <= threshold:
            print(THRESHOLDS[threshold]['msg'])
            send_msg(f"<@{cfg['user_to_mention']}> {THRESHOLDS[threshold]['msg']}", webhook=cfg['webhook'])
            THRESHOLDS[threshold]['triggered'] = True


if __name__ == '__main__':
    load_cfg()
    while True:
        if read_notify():
            print("Done!")
            break
        time.sleep(1)
