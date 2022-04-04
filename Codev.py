import random
import sys
import os
import os.path
import requests
import platform
import shutil
import time
import subprocess
import queue
import threading
import psutil

CONFIG_FILE = "Config.txt"
VERIFIED_FILE = "Verified.txt"

def getVersion():
	return "1.0.2"

def isVersionAtLeast(ver):
	def Convert(verTXT):
		verVEC = verTXT.split(".")
		for i in range(len(verVEC)):
			verVEC[i] = int(verVEC[i])
		return verVEC
	myVer = Convert(getVersion())
	srvVer = Convert(ver)
	return myVer >= srvVer

def printWait():
	print("----------------------")
	input("Press ENTER to continue...")

class repository(object):
	target = None
	hws = None

	def __init__(self, target):
		self.target = target

	def find(self, hid):
		for hw in self.hws:
			if hw.hid == hid:
				return hw

	@staticmethod
	def add(hid):
		hwfolder = REPOSITORY_FOLDER + "/" + CONFIG_FILE
		if isFile(hwfolder):
			hwdata = readFile(hwfolder)
		else:
			hwdata = ""
		if hwdata != "":
			hwdata += " "
		hwdata += hid
		writeFile(hwfolder, hwdata)

	@staticmethod
	def remove(hid):
		hwfolder = REPOSITORY_FOLDER + "/" + CONFIG_FILE
		if isFile(hwfolder):
			chwdata = readFile(hwfolder)
		else:
			chwdata = ""
		hwdata = ""
		for hw in split(chwdata, " "):
			if hw != hid:
				if hwdata != "":
					hwdata += " "
				hwdata += hw
		writeFile(hwfolder, hwdata)

	def load(self):
		if self.target == "local":
			hwfolder = REPOSITORY_FOLDER + "/" + CONFIG_FILE
			if isFile(hwfolder):
				hwdata = readFile(hwfolder)
			else:
				hwdata = ""
			lrep = None
		else:
			lrep = repository("local")
			lrep.load()
			hwfolder = SERVER_URL + "/" + CONFIG_FILE
			hwdata = getURL(hwfolder)
		self.hws = []
		lsthid = split(hwdata, " ")
		hcont = 1
		for hid in lsthid:
			if self.target != "local":
				print("Retrieving homework data {0}/{1}...".format(hcont, len(lsthid)))
			loadhw = (self.target == "local") or lrep.find(hid) == None
			if loadhw:
				hw = homework(hid)
				hw.load(self.target)
				self.hws.append(hw)
			hcont += 1


class homework(object):
	hid = None
	description = None
	exs = None
	status = None

	def __init__(self, hid):
		self.hid = hid

	def find(self, eid):
		for ex in self.exs:
			if ex.eid == eid:
				return ex

	def load(self, target):
		if target == "local":
			hwfolder = REPOSITORY_FOLDER + "/" + self.hid + "/" + CONFIG_FILE
			hwdata = readFile(hwfolder)
		else:
			hwfolder = SERVER_URL + "/" + self.hid + "/" + CONFIG_FILE
			hwdata = getURL(hwfolder)
		hwdata = split(hwdata, "\n")
		self.description = hwdata[0]
		self.exs = []
		cokay = 0
		lsteid = split(hwdata[1], " ")
		econt = 1
		for eid in lsteid:
			if target != "local":
				print("Retrieving exercise data {0}/{1}...".format(econt, len(lsteid)))
			ex = exercise(eid, self.hid)
			ex.load(target)
			if ex.status == "OK":
				cokay += 1
			self.exs.append(ex)
			econt += 1
		if target == "local":
			self.status = "{0}/{1}".format(cokay, len(self.exs))
		else:
			self.status = "{0}".format(len(self.exs))


class exercise(object):
	hid = None
	eid = None
	title = None
	timelimit = None
	description = None
	status = None

	def __init__(self, eid, hid):
		self.eid = eid
		self.hid = hid

	def load(self, target):
		if target == "local":
			exfolder = REPOSITORY_FOLDER + "/" + self.hid + "/" + self.eid
			exdata = readFile(exfolder + "/" + CONFIG_FILE)
		else:
			exfolder = SERVER_URL + "/" + self.hid + "/" + self.eid
			exdata = getURL(exfolder + "/" + CONFIG_FILE)
		exdata = split(exdata, "\n")
		self.title = exdata[0]
		self.timelimit = float(exdata[1])
		desc = ""
		for t in exdata[2:]:
			if desc != "":
				desc += "\n"
			desc += t
		self.description = desc
		if target == "local":
			self.status = "OK" if isFile(exfolder + "/" + VERIFIED_FILE) else "Pending"


def split(txt, sep):
	r = []
	for v in txt.split(sep):
		v = v.strip()
		if v != '':
			r.append(v)
	return r


def isDir(obj):
	obj = OSPath(obj)
	return os.path.isdir(obj)


def isFile(obj):
	obj = OSPath(obj)
	return os.path.isfile(obj)


def OSPath(path):
	if path[0] == ".":
		path = os.path.dirname(os.path.realpath(__file__)) + path[1:]
	return path if platform.system() != "Windows" else path.replace("/", "\\")


def mv(src, dst):
	if isFile(src) or isDir(src):
		shutil.copy(OSPath(src), OSPath(dst))
		rm(src)

def cp(src, dst):
	if isFile(src) or isDir(src):
		shutil.copy(OSPath(src), OSPath(dst))

def rm(obj):
	if isFile(obj):
		obj = OSPath(obj)
		os.remove(obj)
	elif isDir(obj):
		obj = OSPath(obj)
		shutil.rmtree(obj)

def mkdir(folder):
	folder = OSPath(folder)
	if not isDir(folder):
		os.mkdir(folder)


def readFile(filename):
	filename = OSPath(filename)
	f = open(filename, "r", encoding="utf-8")
	strRead = f.read()
	f.close()
	return strRead


def writeFile(filename, content):
	filename = OSPath(filename)
	f = open(filename, "w", encoding="utf-8")
	f.write(content)
	f.close()

def kill(pid):
	p = psutil.Process(pid)
	for sp in p.children(recursive=True):
		sp.kill()
	p.kill()

def checkConnection(printWarning=False):
	try:
		servurl = "{0}/{1}".format(SERVER_URL, CONFIG_FILE)
		return getURL(servurl) != ""
	except:
		if printWarning:
			print("Connection to the server seems to be down...")
			printWait()
		return False

def downloadFile(url, filename):
	filename = OSPath(filename)
	r = requests.get(url, allow_redirects=True)
	if r.status_code == 200:
		f = open(filename, 'wb')
		f.write(r.content)
		f.close()
		return True
	else:
		return False

def getURL(url):
	r = requests.get(url, allow_redirects=True)
	if r.status_code == 200:
		s = r.content.decode("utf-8").strip('\n')
		if s == "404: Not Found":
			s = ""
		return s
	else:
		return ""

def readConfigFile(filename):
	params = {}
	for l in split(readFile(filename), "\n"):
		ld = split(l, "=")
		keyw = ld[0].strip()
		keyv = ld[1].strip()
		params[keyw] = keyv
	return params

def getRandomWord():
	p = 0
	def getPart(ncon):
		c = 'bcdfghjlmnpqrstvxz'; v = 'aeiou'
		p = ''
		for _ in range(ncon):
			p += c[random.randint(0,len(c)-1)]
		return  p + v[random.randint(0,len(v)-1)]
	w = getPart(1) + getPart(2) + getPart(2)
	while random.randint(1,100) <= p:
		w += getPart(2)
	return w

def printFormatted(text, cols):
	for l in text.split('\n'):
		i = 0
		l += ' '
		while i < len(l):
			e = l[:min(len(l),i+cols)].rfind(' ')
			print(l[i:e])
			i = e + 1
		print()

def getDisclaimer():
	text = "ATENÇÃO!! Aviso de isenção de responsabilidade:\n" +\
			"Antes de continuar, é muito importante ter tentado pensar em diversas soluções antes de ver uma.\n" +\
			"A razão é que o seu cérebro é muito bom em esquecer algo que tenha vindo de maneira fácil. Se não conseguir encontrar uma solução, mesmo tendo empregado certo tempo, isto não caracteriza de forma nenhuma um desperdício de seu tempo, mas um investimento: saiba que, quando tomar conhecimento da solução, seu cérebro fará o trabalho necessário para gravar a maior parte do conhecimento que lhe faltou para chegar àquela solução, justamente por reconhecer o quanto aquele assunto lhe é importante. E não adianta afirmar para si próprio o quanto para você é importante aquela solução, se não gastar tempo com ela: seu cérebro acredita em suas ações, não em suas intenções.\n" +\
			"Como mentor de seu aprendizado, sinto-me obrigado a lhe lembrar disso. Se continuar, você confirma que assume os riscos daqui em diante."
	keypwd = getRandomWord()
	esp = 0; i = 0
	while True:
		j = text.find(' ', i)
		if j >= 0:
			esp += 1; i = j+1
		else:
			break
	cesp = random.randint(1,esp)
	i = -1
	for j in range(cesp):
		i = text.find(' ', i+1)
	text = text[:i] + ' ' + keypwd + text[i:]
	printFormatted(text, 80)
	print("---")
	print("There is a random generated word which does not belong to the text.")
	pwd = input("Which is it? ")
	if pwd != keypwd:
		print("Wrong word!")
		printWait()
		return False
	else:
		return True

def printHeader():
	os.system("clear" if platform.system() != "Windows" else "cls")
	print()
	print(r"       ██████╗ ██████╗ ██████╗ ███████╗██╗   ██╗ ")
	print(r"      ██╔════╝██╔═══██╗██╔══██╗██╔════╝██║   ██║ ")
	print(r"      ██║     ██║   ██║██║  ██║█████╗  ██║   ██║ ")
	print(r"      ██║     ██║   ██║██║  ██║██╔══╝  ╚██╗ ██╔╝ ")
	print(r"      ╚██████╗╚██████╔╝██████╔╝███████╗ ╚████╔╝  ")
	print(r"       ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝  ╚═══╝   ")
	print()
	print(r"   CODEV : a CODE Validator for programming learners ")
	print(r"                     version {0}".format(getVersion()))
	print()

def getFirstLines(text, n):
	i = -1
	for j in range(n):
		i = text.find('\n', i+1)
		if i == -1:
			i = len(text)
			break
	if i == -1:
		i = 0
	return text[:i]

def bytesDecode(arrbytes):
	while True:
		try:
			s = arrbytes.decode("utf-8")
			break
		except UnicodeDecodeError as e:
			p = e.start
			arrbytes = arrbytes[:p] + arrbytes[p+1:]
		except:
			return ""
	return getFirstLines(s, 50000)

def run(cmd, params=None, inputfile="", timelimit=None):
	if params==None:
		params = []
	cmd = OSPath(cmd)
	fullcmd = [cmd] + params
	if inputfile == "":
		infileObj = None
	else:
		infileObj = open(OSPath(inputfile), "r", encoding="utf-8")
	try:
		p = subprocess.run(fullcmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=infileObj, timeout=timelimit)
		r = bytesDecode(p.stdout)
		rerr = bytesDecode(p.stderr)
		if rerr != "":
			if r != "":
				r += '\n'
			r += rerr
	except KeyboardInterrupt:
		r = "\nCodev has forced the process to stop."
	except subprocess.TimeoutExpired as e:
		r = bytesDecode(e.stdout)
		r += "\n---\nTime limit has been reached. Codev has forced the process to stop.".format(timelimit)
	return r


def output_reader(outpipe, errpipe, queue):
	try:
		for lout in outpipe:
			lout = lout.rstrip('\n')
			queue.put(lout)
		for lerr in errpipe:
			lerr = lerr.rstrip('\n')
			queue.put(lerr)
		queue.put(None)
	except:
		queue.put(None)

def runAsync(cmd, params=None, inputfile="", outputfile="", timelimit=None):
	if params==None:
		params = []
	cmd = OSPath(cmd)
	fullcmd = [cmd] + params
	if inputfile == "":
		fin = None
	else:
		fin = open(OSPath(inputfile), "r", encoding="utf-8")

	outputs = []
	def addOutput(line):
		print(line)
		outputs.append(line)

	elapsedtime = 0
	realelapsedtime = 0
	userealtime = True
	try:
		p = subprocess.Popen(fullcmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=fin, bufsize=0,
							 universal_newlines=True)
		q = queue.Queue()
		t = threading.Thread(target=output_reader, args=[p.stdout, p.stderr, q])
		t.daemon = True
		t.start()
		starttime = time.time()
		realstarttime = starttime
		countingtime = False
		while True:
			elapsed = realelapsedtime if userealtime else elapsedtime
			if timelimit != None and (elapsed > timelimit):
				addOutput("Time limit has been reached. Codev has forced the process to stop.")
				kill(p.pid)
				break
			else:
				try:
					instanttime = time.time()
					realelapsedtime = instanttime - realstarttime
					if countingtime:
						elapsedtime += (instanttime - starttime)
						starttime = instanttime

					lout = q.get(timeout=0.1)
					if lout == None:
						break
					else:
						if lout == "CODEV_PREPARE_EXEC":
							userealtime = False
						elif lout == "CODEV_BEGIN_EXEC":
							userealtime = False
							countingtime = True
							starttime = time.time()
						elif lout == "CODEV_END_EXEC":
							countingtime = False
							elapsedtime += (time.time() - starttime)
							starttime = time.time()
						else:
							addOutput(lout)
				except queue.Empty:
					continue
				except:
					break

	except KeyboardInterrupt:
		addOutput("Codev has forced the process to stop.")

	finally:
		if outputfile != "":
			writeFile(outputfile, '\n'.join(outputs))
		elapsed = realelapsedtime if userealtime else elapsedtime
		return elapsed, outputs

def removeCodev(text):
	token = r"// codevremove"
	i = text.find(token)
	while i >= 0:
		j = text.find(token, i+1)
		ej = text.find("\n", j)
		ei = text[:i].rfind("\n")
		text = text[:ei+1] + text[ej+1:]
		i = text.find(token)
	token = r"// codev"
	i = text.find(token)
	while i >= 0:
		j = text.find(token, i+1)
		ej = text.find("\n", j)
		text = text[:i] + r"/* insert your code here */" + text[ej:]
		i = text.find(token)
	return text

def removeCodevComments(text):
	tokens = [r"// codevremove", r"// codev"]
	for token in tokens:
		i = text.find(token)
		while i >= 0:
			ej = text.find("\n", i)
			ei = text[:i].rfind("\n")
			text = text[:ei+1] + text[ej+1:]
			i = text.find(token)
	return text

def ParseParams(text):
	return text.split(",")

def EditCode(eid, hid):
	path = "{0}/{1}/{2}/Code.cpp".format(REPOSITORY_FOLDER, hid, eid)
	path = OSPath(path)
	cmd = ParseParams(EDITOR_CMD.replace("<CODE_FILE>", path))
	run(cmd[0], cmd[1:])

def OpenFigure(fig, eid, hid):
	path = "{0}/{1}/{2}/Figure{3}.pdf".format(REPOSITORY_FOLDER, hid, eid, fig)
	path = OSPath(path)
	cmd = ParseParams(PDF_READER.replace("<PDF_FILE>", path))
	run(cmd[0],cmd[1:])

def VerifyCode(eid, hid):
	rep = repository("local")
	rep.load()
	hw = rep.find(hid)
	ex = hw.find(eid)

	exeFile = "{0}/{1}/{2}/Code.exe".format(REPOSITORY_FOLDER, hid, eid)
	code = "{0}/{1}/{2}/Code.cpp".format(REPOSITORY_FOLDER, hid, eid)
	solutionTXT = "{0}/{1}/{2}/Solution.txt".format(REPOSITORY_FOLDER, hid, eid)
	inputTXT = "{0}/{1}/{2}/Input.txt".format(REPOSITORY_FOLDER, hid, eid)
	outputTXT = "{0}/{1}/{2}/Output.txt".format(REPOSITORY_FOLDER, hid, eid)
	diffTXT = "{0}/{1}/{2}/Diff.txt".format(REPOSITORY_FOLDER, hid, eid)
	verifiedTXT = "{0}/{1}/{2}/{3}".format(REPOSITORY_FOLDER, hid, eid, VERIFIED_FILE)

	rm(exeFile)
	rm(verifiedTXT)
	rm(outputTXT)
	rm(diffTXT)

	print("Running my solution:")
	print("----------------------")
	print("Starting compilation...")
	compCmd = ParseParams(COMPILER_CMD.replace("<EXE_FILE>", OSPath(exeFile)).replace("<CODE_FILE>", OSPath(code)))
	print(run(compCmd[0],compCmd[1:]))
	print("Compilation done.")
	print("---")
	if isFile(exeFile):
		print("Running executable file... (type Ctrl+C to stop the execution)")
		starttime = time.time()
		#output = run(exeFile, inputfile=inputTXT, timelimit=(EXE_TIMELIMIT_FACTOR * ex.timelimit))
		#print(output)
		(algElapsedTime, outputs) = runAsync(exeFile, inputfile=inputTXT, outputfile=outputTXT, timelimit=(EXE_TIMELIMIT_FACTOR * ex.timelimit))
		realElapsedTime = time.time() - starttime
		print("Execution done in {:.1f} sec. (Total time: {:.1f} sec)".format(algElapsedTime, realElapsedTime))
		print("----------------------")
		difflastline = ""
		if len(outputs)>0:
			print("Comparing results:")
			print("----------------------")
			diffCmd = ParseParams(DIFF_CMD.replace("<FILE1>", OSPath(outputTXT)).replace("<FILE2>", OSPath(solutionTXT)))
			diffout = run(diffCmd[0], diffCmd[1:])
			diffout = diffout.strip().strip('\n')
			difflastline = diffout.split('\n')[-1]
			print(diffout)
			writeFile(diffTXT, diffout)
			print("----------------------")
	else:
		outputs = []; difflastline = ""; algElapsedTime = 0

	verOkay = True
	if len(outputs)>0 and difflastline == DIFF_NO_TEXT:
		print("Correctness: Checked!")
	else:
		print("Correctness: Failed...")
		verOkay = False
	if algElapsedTime <= ex.timelimit:
		print("Time Complexity: Checked!")
	else:
		print("Time Complexity: Failed...")
		verOkay = False
	if verOkay:
		writeFile(verifiedTXT, "Okay")
		print("Veredict: Correct!")
	else:
		print("Veredict: Wrong Answer...")
	printWait()

def RunCode(eid, hid):

	exeFile = "{0}/{1}/{2}/Code.exe".format(REPOSITORY_FOLDER, hid, eid)
	code = "{0}/{1}/{2}/Code.cpp".format(REPOSITORY_FOLDER, hid, eid)

	print("Running my solution:")
	print("----------------------")
	print("Starting compilation...")
	compCmd = ParseParams(COMPILER_CMD.replace("<EXE_FILE>", OSPath(exeFile)).replace("<CODE_FILE>", OSPath(code)))
	print(run(compCmd[0],compCmd[1:]))
	print("Compilation done.")
	print("---")
	print("Running executable file...")
	print("(type the input; use {0} to indicate that there is no more input data)".format("Ctrl+D" if platform.system() != "Windows" else "Ctrl+D or Ctrl+Z"))
	print("(type Ctrl+C to stop the execution)")
	output = run(exeFile)
	#for lout in runAsync(exeFile):
	#	print(lout)
	print("\n---")
	#print("Execution done.")
	print("Execution done. Output:")
	print(output)
	printWait()

def ShowInput(eid, hid):
	path = "{0}/{1}/{2}/Input.txt".format(REPOSITORY_FOLDER, hid, eid)
	print("Below, you find the input data that Codev will give")
	print("to your program during the validation process. Be aware")
	print("that some (or even all) input data may be produced")
	print("directly from the code. So, check the code out too.")
	print("----------------------")
	print(readFile(path))
	printWait()

def DelConfirmHW(hid):
	path = "{0}/{1}".format(REPOSITORY_FOLDER, hid)
	rm(path)
	repository.remove(hid)

def DelConfirmCode(eid, hid):
	path = "{0}/{1}/{2}/Code.cpp".format(REPOSITORY_FOLDER, hid, eid)
	rm(path)
	path = "{0}/{1}/{2}/KeyCode.cpp".format(REPOSITORY_FOLDER, hid, eid)
	rm(path)

def DownloadHW(hid, creating):
	if not checkConnection(True):
		return
	hwurl = "{0}/{1}".format(SERVER_URL, hid)
	hwfolder = "{0}/{1}".format(REPOSITORY_FOLDER, hid)
	if creating:
		print("Recreating local folders...")
		rm(hwfolder)
		mkdir(hwfolder)
	f = CONFIG_FILE
	c = getURL(hwurl + "/" + f)
	writeFile(hwfolder + "/" + f, c)
	exLst = split(split(c, "\n")[1], " ")
	econt = 1
	for eid in exLst:
		print("Retrieving exercise data {0}/{1}...".format(econt, len(exLst)))
		exurl = hwurl + "/" + eid
		exfolder = hwfolder + "/" + eid
		createEx = not isDir(exfolder)
		if createEx:
			mkdir(exfolder)
		filesOverwrite = [CONFIG_FILE, "Solution.txt", "Input.txt"]
		filesKeepOriginal = ["Code.cpp"]
		filesRem = [VERIFIED_FILE]

		def DownloadSeqFiles(basename, extension):
			i = 1
			f = "{0}{1}.{2}".format(basename, i, extension)
			while isFile(exfolder + "/" + f):
				rm(exfolder + "/" + f)
				i = i + 1
				f = "{0}{1}.{2}".format(basename, i, extension)
			i = 1
			f = "{0}{1}.{2}".format(basename, i, extension)
			while downloadFile(exurl + "/" + f, exfolder + "/" + f):
				i = i + 1
				f = "{0}{1}.{2}".format(basename, i, extension)

		for f in filesOverwrite:
			writeFile(exfolder + "/" + f, getURL(exurl + "/" + f))
		for f in filesKeepOriginal:
			fn = exfolder + "/" + f
			if not isFile(fn):
				writeFile(fn, removeCodev(clear(getURL(exurl + "/" + f))))
		for f in filesRem:
			rm(exfolder + "/" + f)
		DownloadSeqFiles('Figure', 'pdf')
		DownloadSeqFiles('Bib', 'h')
		DownloadSeqFiles('Hint', 'txt')

		econt += 1

	if creating:
		repository.add(hid)

def UpdateHW(hid):
	DownloadHW(hid, False)

def GenMenuReadHW(eid, hid):
	rep = repository("local")
	rep.load()
	hw = rep.find(hid)
	ex = hw.find(eid)
	Opt = []
	Opt.append("Homework: {0}".format(hw.description))
	Opt.append(None)
	Opt.append("Exercise  : {0}".format(ex.title))
	Opt.append("Time Limit: {0} secs.".format(ex.timelimit))
	Opt.append("Status    : {0}".format(ex.status))
	Opt.append(None)
	Opt.append(ex.description)
	exfolder = REPOSITORY_FOLDER + "/" + hid + "/" + eid
	if isFile(exfolder + "/" + "Figure1.pdf"):
		Opt.append(None)
		i = 1
		while isFile(exfolder + "/" + "Figure{0}.pdf".format(i)):
			Opt.append(["f{0}".format(i), "Show Figure {0}".format(i), ["openFig", i, eid, hid]])
			i = i+1
	Opt.append(None)
	Opt.append(["1", "Edit Code", ["editCode", eid, hid]])
	Opt.append(["2", "Run Code", ["runCode", eid, hid]])
	Opt.append(["3", "Validate Code", ["verifyCode", eid, hid]])
	Opt.append(None)
	hwurl = "{0}/{1}".format(SERVER_URL, hid)
	exfolder = "{0}/{1}/{2}".format(REPOSITORY_FOLDER, hid, eid)
	Opt.append(["i", "Show Input", ["showInput", eid, hid]])
	Opt.append(None)
	if isFile(exfolder + "/" + "Hint1.txt"):
		Opt.append(["h1", "Get a Hint", ["seeBasicHint", eid, hid]])
	if isFile(exfolder + "/" + "Hint2.txt"):
		Opt.append(["h2", "Get a Spoiler Hint", ["seeSpoilerHint", eid, hid]])
	if isFile(exfolder + "/" + "KeyCode.cpp") or (checkConnection() and getURL(hwurl + "/Pass.txt") != ""):
		Opt.append(["s", "See a Solution", ["editKeyCode", eid, hid]])
	Opt.append(None)
	Opt.append(["d", "Delete Code", ["delCode", eid, hid]])
	Opt.append(None)
	Opt.append(["b", "Go Back", ["openHW", hid]])
	return Opt


def GenMenuOpenHW(hid):
	rep = repository("local")
	rep.load()
	hw = rep.find(hid)
	i = 1
	Opt = []
	Opt.append("Homework: {0}".format(hw.description))
	Opt.append(None)
	for ex in hw.exs:
		Opt.append([str(i), ex.title + " (" + ex.status + ")", ["readHW", ex.eid, hid]])
		i += 1
	Opt.append(None)
	Opt.append(["u", "Update Homework", ["updHW", hid]])
	Opt.append(["d", "Delete Homework", ["delHW", hid]])
	Opt.append(None)
	Opt.append(["b", "Go Back", ["hwList"]])
	return Opt


def GenMenuNewHW():
	connec = checkConnection()

	rep = repository("remote")
	if connec:
		rep.load()

	Opt = []
	i = 1
	Opt.append("New Homeworks:")
	Opt.append(None)
	if connec and len(rep.hws) == 0:
		Opt.append("(no new homeworks have been found)")
	elif not connec:
		Opt.append("(connection to the server seems to be down...)")
	else:
		for hw in rep.hws:
			Opt.append([str(i), hw.description + " (" + hw.status + ")", ["downloadHW", hw.hid]])
			i += 1
	Opt.append(None)
	Opt.append(["b", "Go Back", ["hwList"]])
	return Opt


def GenMenuDelHW(hid):
	rep = repository("local")
	rep.load()
	hw = rep.find(hid)
	Opt = []
	Opt.append("Homework: {0}".format(hw.description))
	Opt.append(None)
	Opt.append("Are you sure you want to delete ALL saved data for this homework (including the code file)?")
	Opt.append(None)
	Opt.append(["yes", "Yes", ["delConfirmHW", hid]])
	Opt.append(["n", "No", ["openHW", hid]])
	return Opt

def GenMenuDelCode(eid, hid):
	rep = repository("local")
	rep.load()
	hw = rep.find(hid)
	ex = hw.find(eid)
	Opt = []
	Opt.append("Homework: {0}".format(hw.description))
	Opt.append(None)
	Opt.append("Exercise: {0}".format(ex.title))
	Opt.append(None)
	Opt.append("Are you sure you want to delete its associated code?")
	Opt.append(None)
	Opt.append(["yes", "Yes", ["delConfirmCode", eid, hid]])
	Opt.append(["n", "No", ["readHW", eid, hid]])
	return Opt

def SeeBasicHint(eid, hid):
	path = "{0}/{1}/{2}/Hint1.txt".format(REPOSITORY_FOLDER, hid, eid)
	print()
	print(readFile(path))
	printWait()

def SeeSpoilerHint(eid, hid):
	path = "{0}/{1}/{2}/Hint2.txt".format(REPOSITORY_FOLDER, hid, eid)
	print()
	text = clear(readFile(path))
	if getDisclaimer():
		print()
		print(text)
		printWait()

def EditKeyCode(eid, hid):
	path = "{0}/{1}/{2}/KeyCode.cpp".format(REPOSITORY_FOLDER, hid, eid)

	if not isFile(path):
		Pwd = input("Please, enter the password: ")
		hwurl = "{0}/{1}".format(SERVER_URL, hid)
		sPwd = clear(getURL(hwurl + "/" + "Pass.txt"))
		if sPwd == "" or Pwd != sPwd:
			print("This given password for this homework does not match.")
			printWait()
		else:
			exurl = hwurl + "/" + eid
			f = "Code.cpp"
			writeFile(path, removeCodevComments(clear(getURL(exurl + "/" + f))))

	if isFile(path):
		path = OSPath(path)
		cmd = ParseParams(EDITOR_CMD.replace("<CODE_FILE>", path))
		run(cmd[0], cmd[1:])

def GenMenuHWList():
	rep = repository("local")
	rep.load()

	Opt = []
	i = 1
	Opt.append("Downloaded Homeworks:")
	Opt.append(None)
	if len(rep.hws) == 0:
		Opt.append("(no homework has been downloaded yet)")
	else:
		for hw in rep.hws:
			Opt.append([str(i), hw.description + " (" + hw.status + ")", ["openHW", hw.hid]])
			i += 1
	Opt.append(None)
	Opt.append(["n", "Download New Homework", ["newHW"]])
	Opt.append(None)
	if UPDATE_SOFTWARE == "1":
		Opt.append(["u", "Update Codev Software", ["updSoft"]])
	Opt.append(["s", "Settings", ["settings"]])
	Opt.append(["a", "About", ["about"]])
	Opt.append(["q", "Quit", ["quit"]])
	return Opt


def DisplayMenu(Opt):
	while True:
		printHeader()
		menu = {}
		margin = " ║ "
		for item in Opt:
			if item == None:
				print(margin)
			elif isinstance(item, str):
				for txt in item.split("\n"):
					print(margin + txt)
			else:
				print(margin + "[{0}] {1}".format(item[0], item[1]))
				menu[item[0].upper()] = item[2]
		print()
		x = input("Option: ").upper()
		if x in menu:
			return menu[x]

def GenMenuAbout():
	Opt = []
	Opt.append("Author: Fabiano Oliveira")
	Opt.append("Email : fabiano.oliveira@ime.uerj.br")
	Opt.append(None)
	Opt.append("What do you think of this tool?")
	Opt.append(None)
	Opt.append(["1", "Awesome", ["hwList"]])
	Opt.append(["2", "Really great", ["hwList"]])
	Opt.append(["3", "Terrific", ["hwList"]])
	return Opt

def GenMenuSettings():
	Opt = []
	Opt.append("Settings must be adjusted in the file Settings.txt")
	Opt.append("located in the Codev folder. Settings that can be adjusted:")
	Opt.append(None)
	Opt.append(r"EDITOR_CMD = <value>")
	Opt.append(r"<value> should be a valid command line for opening")
	Opt.append(r"the code editor; the substring of value named <CODE_FILE>")
	Opt.append(r"will be replaced with the code filename.")
	Opt.append(r"If a space between arguments does not work well, try replacing")
	Opt.append(r"with a comma (,) those spaces that delimit arguments.")
	Opt.append(None)
	Opt.append(r"COMPILER_CMD = <value>")
	Opt.append(r"<value> should be a valid command line for compiling")
	Opt.append(r"the code; the substring <CODE_FILE> will be replaced with")
	Opt.append(r"the code filename, and <EXE_FILE> with the executable file")
	Opt.append(r"to be created.")
	Opt.append(r"If a space between arguments does not work well, try replacing")
	Opt.append(r"with a comma (,) those spaces that delimit arguments.")
	Opt.append(None)
	Opt.append(r"UPDATE_SOFTWARE = 0/1")
	Opt.append(r"0 for hiding the option for downloading new versions of Codev.")
	Opt.append(None)
	Opt.append(r"SERVER_URL = <value>")
	Opt.append(r"Codev repository server URL.")
	Opt.append(None)
	Opt.append(r"REPOSITORY_FOLDER = <value>")
	Opt.append(r"Codev local repository; all the files are located there.")
	Opt.append(None)
	Opt.append(r"DIFF_CMD = <value>")
	Opt.append(r"<value> should be a valid command line for executing a")
	Opt.append(r"file comparison tool; the substrings <FILE1> and <FILE2>")
	Opt.append(r"will be replaced with the two files to be compared.")
	Opt.append(r"If a space between arguments does not work well, try replacing")
	Opt.append(r"with a comma (,) those spaces that delimit arguments.")
	Opt.append(None)
	Opt.append(r"PDF_READER = <value>")
	Opt.append(r"<value> should be a valid command line for executing a")
	Opt.append(r"pdf reader tool; the substrings <PDF_FILE>")
	Opt.append(r"will be replaced with the filename to be opened.")
	Opt.append(r"If a space between arguments does not work well, try replacing")
	Opt.append(r"with a comma (,) those spaces that delimit arguments.")
	Opt.append(None)
	Opt.append(["b", "Go Back", ["hwList"]])
	return Opt

def UpdateSoftware():
	if checkConnection(True) and UPDATE_SOFTWARE == "1":
		hwurl = SERVER_URL
		hwfolder = os.getcwd()
		files = ["Codev.py", "Installation.txt", "Settings.txt.Linux", "Settings.txt.Windows"]
		for f in files:
			writeFile(hwfolder + "/" + f, getURL(hwurl + "/" + f))
		print()
		print("You must restart in order to run the new version.")
		print("If anything goes wrong with the new version, try reading the")
		print("updated Installation.txt file and compare the updated Settings.txt.Linux")
		print("(or Settings.txt.Windows) to your Settings.txt to see whether there are")
		print("new or modified settings required in this new version.")
		printWait()

def obscure(text):
	r = ""
	li = 32; ls = 127; t = ls - li + 1; s = 40
	for i in range(len(text)):
		c = text[i]
		if li <= ord(c) <= ls:
			r += chr((ord(c) - li + s) % t + li)
		else:
			r += c
	return r


def clear(text):
	r = ""
	li = 32; ls = 127; t = ls - li + 1; s = 40
	for i in range(len(text)):
		c = text[i]
		if li <= ord(c) <= ls:
			r += chr((ord(c) - li - s) % t + li)
		else:
			r += c
	return r


def GenMenu():
	cmd = "hwList"
	chosen = None
	while cmd != "quit":
		if cmd == "hwList":
			chosen = DisplayMenu(GenMenuHWList())
		elif cmd == "newHW":
			chosen = DisplayMenu(GenMenuNewHW())
		elif cmd == "downloadHW":
			DownloadHW(chosen[1], True)
			chosen = ["hwList"]
		elif cmd == "openHW":
			chosen = DisplayMenu(GenMenuOpenHW(chosen[1]))
		elif cmd == "readHW":
			chosen = DisplayMenu(GenMenuReadHW(chosen[1], chosen[2]))
		elif cmd == "delHW":
			chosen = DisplayMenu(GenMenuDelHW(chosen[1]))
		elif cmd == "updHW":
			DownloadHW(chosen[1], False)
			chosen = ["openHW", chosen[1]]
		elif cmd == "delConfirmHW":
			DelConfirmHW(chosen[1])
			chosen = ["hwList"]
		elif cmd == "editCode":
			EditCode(chosen[1], chosen[2])
			chosen = ["readHW", chosen[1], chosen[2]]
		elif cmd == "runCode":
			RunCode(chosen[1], chosen[2])
			chosen = ["readHW", chosen[1], chosen[2]]
		elif cmd == "verifyCode":
			VerifyCode(chosen[1], chosen[2])
			chosen = ["readHW", chosen[1], chosen[2]]
		elif cmd == "showInput":
			ShowInput(chosen[1], chosen[2])
			chosen = ["readHW", chosen[1], chosen[2]]
		elif cmd == "delCode":
			chosen = DisplayMenu(GenMenuDelCode(chosen[1], chosen[2]))
		elif cmd == "editKeyCode":
			EditKeyCode(chosen[1], chosen[2])
			chosen = ["readHW", chosen[1], chosen[2]]
		elif cmd == "seeBasicHint":
			SeeBasicHint(chosen[1], chosen[2])
			chosen = ["readHW", chosen[1], chosen[2]]
		elif cmd == "seeSpoilerHint":
			SeeSpoilerHint(chosen[1], chosen[2])
			chosen = ["readHW", chosen[1], chosen[2]]
		elif cmd == "delConfirmCode":
				DelConfirmCode(chosen[1], chosen[2])
				chosen = ["readHW", chosen[1], chosen[2]]
		elif cmd == "about":
			chosen = DisplayMenu(GenMenuAbout())
		elif cmd == "updSoft":
			UpdateSoftware()
			chosen = ["hwList"]
		elif cmd == "settings":
			chosen = DisplayMenu(GenMenuSettings())
		elif cmd == "openFig":
			OpenFigure(chosen[1], chosen[2], chosen[3])
			chosen = ["readHW", chosen[2], chosen[3]]
		cmd = chosen[0]

if not isFile("./Settings.txt"):
	osstr = "Windows" if platform.system() == "Windows" else "Linux"
	if isFile("./Settings.txt." + osstr):
		cp("./Settings.txt." + osstr, "./Settings.txt")
	else:
		print("Codev did not find the file Settings.txt")
		exit(0)

cfg = readConfigFile("./Settings.txt")

REPOSITORY_FOLDER = cfg.get("REPOSITORY_FOLDER", "./repository")
if OSPath(REPOSITORY_FOLDER).find(" ") >= 0:
	print("ATTENTION: The path of the repository folder has")
	print("blank spaces: '{0}'".format(OSPath(REPOSITORY_FOLDER)))
	print("Since Codev has to call external programs passing files")
	print("in this folder as arguments, it is highly recommended")
	print("setting a respository folder with no blank spaces to")
	print("avoid integration issues. Change it in Settings.txt")
	print("or reinstall Codev in another folder.")
	print("(Continue as is only if you are sure the settings of")
	print("external programs can manage paths with blank spaces.)")
	printWait()

if not isDir(REPOSITORY_FOLDER):
	mkdir(REPOSITORY_FOLDER)

SERVER_URL = cfg["SERVER_URL"]
EDITOR_CMD = cfg["EDITOR_CMD"]
COMPILER_CMD = cfg["COMPILER_CMD"]
DIFF_CMD = cfg["DIFF_CMD"]
DIFF_NO_TEXT = cfg.get("DIFF_NO_TEXT", "")
UPDATE_SOFTWARE = cfg.get("UPDATE_SOFTWARE", "1")
PDF_READER = cfg.get("PDF_READER", "<PDF_FILE>")
EXE_TIMELIMIT_FACTOR = int(cfg.get("EXE_TIMELIMIT_FACTOR", "3"))

if checkConnection():
	minver = getURL(SERVER_URL + "/" + "MinVersion.txt")
	if minver != "" and not isVersionAtLeast(minver):
		print("ATTENTION: Your Codev client software may not work with")
		print("the current server version. It is highly recommended")
		print("updating Codev before continuing.")
		printWait()

if len(sys.argv) > 1:
		if sys.argv[1] == "upload":
			hid = sys.argv[2]; eid = sys.argv[3]
			exfolder = "{0}/{1}/{2}".format(REPOSITORY_FOLDER, hid, eid)
			for f in ["Code.cpp","Hint2.txt"]:
				keyf = "Key" + f
				if isFile(exfolder + "/" + keyf):
					writeFile(exfolder + "/" + f, obscure(readFile(exfolder + "/" + keyf)))
				else:
					print(keyf + " not found.")
		elif sys.argv[1] == "pass":
			hid = sys.argv[2]
			hwfolder = "{0}/{1}".format(REPOSITORY_FOLDER, hid)
			if isFile(hwfolder + "/KeyPass.txt"):
				writeFile(hwfolder + "/Pass.txt", obscure(readFile(hwfolder + "/KeyPass.txt")))
			else:
				print("KeyPass.txt not found.")
		else:
			print("Codev could not recognize the given parameters.")
else:

	GenMenu()
