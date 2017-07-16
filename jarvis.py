from os import environ, path
from subprocess import Popen

from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *

import time

import pyaudio	

import pyttsx3 as sp

from queue import Queue
from threading import Thread

def init_worker():
	global q
	q = Queue()

	t = Thread(target = worker)
	t.daemon = True
	t.start()

def worker():
	global q
	engine = sp.init()
	engine.setProperty('rate', 120)
	engine.setProperty('volume', 0.6)
	engine.setProperty('voice', 0)

	while True:
		speech = q.get()
		engine.say(speech)
		engine.runAndWait()
		q.task_done()

def say(speech):
	print(speech)
	q.put(speech)

#---------------------------------
init_worker()

say('initializing')

MODELDIR = "C:\Python34\Lib\site-packages\pocketsphinx\model"
DATADIR = "C:\Python34\Lib\site-packages\pocketsphinx\data"

#decoder for speech recog
config = Decoder.default_config()
config.set_string('-hmm', path.join(MODELDIR, 'alt-en-us'))
config.set_string('-lm', path.join(MODELDIR, 'en-us.lm.bin'))
config.set_string('-dict', path.join(MODELDIR, 'cmudict-0.7b.dict'))
decoder = Decoder(config)
decoder.set_kws('keyword', 'C:\Python34\Lib\site-packages\pocketsphinx\model\keyword.list')
decoder.set_search('keyword')

#setting up decoder for grammar
#grammar = Decoder(config)

#audio stream from mic
stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
stream.start_stream()

decoder.start_utt()

global p

while True:
	buf = stream.read(1024)
	decoder.process_raw(buf, False, False)
	hypothesis = decoder.hyp()
	if hypothesis is not None:
		print(hypothesis.hypstr)
		print(hypothesis.best_score)
		if hypothesis.hypstr == 'QUIT':
			say('Ending my own life')
			q.join()
			exit(0)
		elif hypothesis.hypstr == 'LISTEN':
			say('Yes?')
			print('Waiting for grammar')
			currTime = time.time()

		
		elif hypothesis.hypstr == 'HIT ME':
			say('opening notepad')
			p = Popen(['notepad'])
		elif hypothesis.hypstr == 'KILL':
			if p is not None:
				say('Give me your clothes')
				p.terminate()
		decoder.end_utt()
		decoder.start_utt()

say('shutting down')

time.sleep(4)
quit(0)