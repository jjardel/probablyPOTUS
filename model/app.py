from model.src import Listener, AuthHandler
from tweepy import Stream
from lib.utils.lw import get_header, get_root_logger


if __name__ == '__main__':

    lg = get_root_logger()
    get_header(lg, 'Opening stream to listen for Trump-like tweets.')
    auth_handler = AuthHandler()

    listener = Listener()
    stream = Stream(auth=auth_handler.auth, listener=listener)
    stream.filter(follow=['25073877'], async=True)

    lg.info('listening...')