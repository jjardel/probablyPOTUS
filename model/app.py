from model.src import Listener, AuthHandler
from tweepy import Stream

auth_handler = AuthHandler()

listener = Listener()
stream = Stream(auth=auth_handler.auth, listener=listener)
stream.filter(follow=['25073877'], async=True)

print("listening...")