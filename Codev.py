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
from colorama import Fore, Style
from colorama import init as colorama_init
from progress.bar import FillingSquaresBar

CONFIG_FILE = "Config.txt"
VERIFIED_FILE = "Verified.txt"

def getVersion():
	return "1.3"

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
	selectColor("CYAN")
	print(color("----------------------"))
	input(color("Press ") + color("ENTER", "LIGHTYELLOW_EX") + color(" to continue..."))

def selectColor(color):
	global SELECTED_COLOR
	SELECTED_COLOR = color

def selectOutputColor(colorname):
	if colorname == None:
		print(Style.RESET_ALL, end='')
	else:
		print(colorama_colors[colorname], end='')

def color(text, colorname=None):
	if MONOCHROMATIC == 1:
		c = ""
	elif colorname==None:
		c = colorama_colors[SELECTED_COLOR]
	else:
		c = colorama_colors[colorname]
	return c + text + Style.RESET_ALL

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
				if hw.load(self.target):
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
		self.exs = []
		if target == "local":
			hwfolder = REPOSITORY_FOLDER + "/" + self.hid + "/" + CONFIG_FILE
			if isFile(hwfolder):
				hwdata = readFile(hwfolder)
			else:
				return False
		else:
			hwfolder = SERVER_URL + "/" + self.hid + "/" + CONFIG_FILE
			hwdata = getURL(hwfolder)
		hwdata = split(hwdata, "\n")
		self.description = hwdata[0]
		cokay = 0
		lsteid = split(hwdata[1], " ")
		econt = 1
		b = None
		if target != "local":
			b = getProgressBar("Retrieving exercise data... ", len(lsteid))
		for eid in lsteid:
			if b != None:
				b.next()
			ex = exercise(eid, self.hid)
			if ex.load(target):
				if ex.status == "OK":
					cokay += 1
				self.exs.append(ex)
			econt += 1
		if b != None:
			b.finish()

		if target == "local":
			self.status = "{0}/{1}".format(cokay, len(self.exs))
		else:
			self.status = "{0}".format(len(self.exs))
		return True

	def cstatus(self):
		s = split(self.status, "/")
		if len(s) == 1:
			return color(self.status, "LIGHTYELLOW_EX")
		else:
			return color(self.status, "GREEN" if s[0] == s[1] else "YELLOW")


class exercise(object):
	hid = None
	eid = None
	title = None
	timelimit = None
	description = None
	status = None
	language = None

	def __init__(self, eid, hid):
		self.eid = eid
		self.hid = hid

	@staticmethod
	def getLanguage(eid):
		return "C++" if int(eid) < 100 else "Python"

	def cstatus(self):
		if self.status == "OK":
			return color(self.status, "GREEN")
		else:
			return color(self.status, "YELLOW")

	def load(self, target):
		if target == "local":
			exfolder = REPOSITORY_FOLDER + "/" + self.hid + "/" + self.eid
			if isFile(exfolder + "/" + CONFIG_FILE):
				exdata = readFile(exfolder + "/" + CONFIG_FILE)
			else:
				return False
		else:
			exfolder = SERVER_URL + "/" + self.hid + "/" + self.eid
			exdata = getURL(exfolder + "/" + CONFIG_FILE)
		exdata = exdata.split("\n")
		self.title = exdata[0]
		self.timelimit = float(exdata[1])
		desc = ""
		for t in exdata[2:]:
			if desc != "":
				desc += "\n"
			desc += t
		self.description = desc
		self.language = exercise.getLanguage(self.eid)
		if target == "local":
			self.status = "OK" if isFile(exfolder + "/" + VERIFIED_FILE) else "Pending"
		return True

def split(txt, sep):
	r = []
	for v in txt.split(sep):
		v = v.strip()
		if v != '':
			r.append(v)
	return r

def SplitEscaped(text, sep):
	if text == "":
		return []
	parts = text.split(sep)
	i = 0
	r = []
	newPart = True
	while i<len(parts):
		if i==0 or parts[i] != '':
			if newPart:
				r.append(parts[i])
			else:
				r[-1] += parts[i]
				newPart = True
		else:
			q = 1
			while i+1<len(parts) and parts[i+1]=='':
				q += 1
				i += 1
			f = 0 if i+1<len(parts) else 1
			r[-1] += sep*((q+(1-f))//2)
			newPart = ((q+f)%2 == 0)
		i += 1
	if parts[-1] == '' and newPart:
		r.append('')
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
			print("Connection to the server could not be established...")
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
		return p + v[random.randint(0,len(v)-1)]
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
	selectColor("LIGHTBLACK_EX")
	print(color(r"       ██████╗ ██████╗ ██████╗ ███████╗██╗   ██╗ "))
	print(color(r"      ██╔════╝██╔═══██╗██╔══██╗██╔════╝██║   ██║ "))
	print(color(r"      ██║     ██║   ██║██║  ██║█████╗  ██║   ██║ "))
	print(color(r"      ██║     ██║   ██║██║  ██║██╔══╝  ╚██╗ ██╔╝ "))
	print(color(r"      ╚██████╗╚██████╔╝██████╔╝███████╗ ╚████╔╝  "))
	print(color(r"       ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝  ╚═══╝   "))
	print()
	selectColor("WHITE")
	print(color(r"   CODEV : a CODE Validator for programming learners "))
	print(color(r"                     version {0}".format(getVersion())))
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

def runAsync(cmd, params=None, inputfile="", outputfile="", solutionfile="", debugfile="", mapinoutfile="", timelimit=None):
	if params==None:
		params = []
	cmd = OSPath(cmd)
	fullcmd = [cmd] + params
	if inputfile == "":
		fin = None; inputs = None
	else:
		fin = open(OSPath(inputfile), "r", encoding="utf-8")
		inputs = readFile(inputfile).split("\n\n")

	outputs = []
	solutions = None; b = None
	errors = []  #[(input, output, solution),...]

	if solutionfile != "":
		solutions = readFile(solutionfile).split("\n")
		b = getProgressBar("Validating: ", len(solutions))

	def addOutput(line, isSolution=True):
		if not isSolution or b == None:
			print(color("[{0}]".format(line), "LIGHTYELLOW_EX"))
		else:
			r = b.index < len(solutions) and line == solutions[b.index]
			if not r:
				if b.index < len(inputs):
					if mapinoutfile == "" or not isFile(mapinoutfile):
						inputinfo = inputs[b.index]
					else:
						inputinfo = '\n'.join(inputs[:b.index+1])
				else:
					inputinfo = ""
				if b.index >= len(solutions):
					solutioninfo = ""
				else:
					solutioninfo = solutions[b.index]
				errors.append((inputinfo, line, solutioninfo))

			if not r and debugfile != "" and not isFile(debugfile):
				writeFile(debugfile + "Input.txt", errors[0][0])
				writeFile(debugfile + "Solution.txt", errors[0][2])
			b.next()
		outputs.append(line)

	elapsedtime = 0
	realelapsedtime = 0
	userealtime = True
	try:
		if platform.system() != "Windows":
			fullcmd = ' '.join(fullcmd)
		p = subprocess.Popen(fullcmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=fin, bufsize=0,
							 universal_newlines=True)
		q = queue.Queue()
		t = threading.Thread(target=output_reader, args=[p.stdout, p.stderr, q])
		t.daemon = True
		t.start()
		starttime = time.time()
		realstarttime = starttime
		countingtime = False
		printingDebug = False
		while True:
			elapsed = realelapsedtime if userealtime else elapsedtime
			if timelimit != None and (elapsed > timelimit):
				addOutput("Time limit has been reached. Codev has forced the process to stop.", False)
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
						elif lout == "CODEV_DEBUG":
							printingDebug = not printingDebug
						else:
							addOutput(lout, not printingDebug)

				except queue.Empty:
					continue
				except:
					break

	except KeyboardInterrupt:
		addOutput("Codev has forced the process to stop.", False)

	finally:
		if outputfile != "":
			writeFile(outputfile, '\n'.join(outputs))
		elapsed = realelapsedtime if userealtime else elapsedtime
		if b != None:
			for i in range(b.index, b.max):
				addOutput("")
			b.finish()

		return elapsed, outputs, errors

def removeCodev(language, text):

	ctag = r"//" if language == "C++" else r"#"

	if language == "C++":
		insertCode = r"/* insert your code here */"
	else:
		insertCode = r"# insert your code here"

	token = ctag + " codevremove"
	i = text.find(token)
	while i >= 0:
		j = text.find(token, i+1)
		ej = text.find("\n", j)
		ei = text[:i].rfind("\n")
		text = text[:ei+1] + text[ej+1:]
		i = text.find(token)
	token = ctag + " codev"
	i = text.find(token)
	while i >= 0:
		j = text.find(token, i+1)
		ej = text.find("\n", j)
		if ej == -1:
			ej = len(text)
		text = text[:i] + insertCode + text[ej:]
		i = text.find(token)
	return text

def removeCodevComments(language, text):
	ctag = r"//" if language == "C++" else r"#"

	tokens = [ctag + " codevremove", ctag + " codev"]
	for token in tokens:
		i = text.find(token)
		while i >= 0:
			ej = text.find("\n", i)
			if ej==-1:
				ej = len(text)
			ei = text[:i].rfind("\n")
			text = text[:ei+1] + text[ej+1:]
			i = text.find(token)
	return text

def ParseParams(text):
	return SplitEscaped(text, ",")

def EditCode(eid, hid):
	rep = repository("local")
	rep.load()
	hw = rep.find(hid)
	ex = hw.find(eid)

	codeExt = "cpp" if ex.language == "C++" else "py"
	code = "{0}/{1}/{2}/Code.{3}".format(REPOSITORY_FOLDER, hid, eid, codeExt)
	path = OSPath(code)
	cmd = ParseParams(getLanguageSetting(ex.language, "EDITOR_CMD").replace("<CODE_FILE>", path))
	run(cmd[0], cmd[1:])

def ShowTextFile(filename):
	path = filename
	path = OSPath(path)
	cmd = ParseParams(getLanguageSetting("TEXT", "EDITOR_CMD").replace("<CODE_FILE>", path))
	run(cmd[0], cmd[1:])

def OpenFigure(fig, eid, hid):
	path = "{0}/{1}/{2}/Figure{3}.pdf".format(REPOSITORY_FOLDER, hid, eid, fig)
	path = OSPath(path)
	cmd = ParseParams(PDF_READER.replace("<PDF_FILE>", path))
	run(cmd[0],cmd[1:])

def LineDiff(text, compareTo, maxwidth=30):
	i = 0
	while i < len(compareTo) and i < len(text) and text[i] == compareTo[i]:
		i += 1
	if i == len(text) and i == len(compareTo):
		i = 0
	i = max(0, min(i + 4, len(text) - 1) - maxwidth + 1)
	f1 = min(i + maxwidth - 1, len(text) - 1)
	f2 = min(i + maxwidth - 1, len(compareTo) - 1)

	cs1 = ''; cs2 = ''
	if i > 0:
		cs1 += '(+{0}) ...'.format(i)
		cs2 += '(+{0}) ...'.format(i)
	j = i
	while j - i + 1 <= maxwidth and j <= f1 and j <= f2:
		if text[j] == compareTo[j]:
			cs1 += text[j]
			cs2 += compareTo[j]
		else:
			cs1 += color(text[j], "YELLOW")
			cs2 += color(compareTo[j], "YELLOW")
		j += 1
	e1 = j
	while e1 <= f1:
		cs1 += color(text[e1], "YELLOW")
		e1 += 1
	if e1 < len(text):
		cs1 += '... (+{0})'.format(len(text) - e1)
	e2 = j
	while e2 <= f2:
		cs2 += color(compareTo[e2], "YELLOW")
		e2 += 1
	if e2 < len(compareTo):
		cs2 += '... (+{0})'.format(len(compareTo) - e2)

	return cs1, cs2

def VerifyCode(eid, hid):
	rep = repository("local")
	rep.load()
	hw = rep.find(hid)
	ex = hw.find(eid)

	codeExt = "cpp" if ex.language == "C++" else "py"
	exeExt = "exe" if ex.language == "C++" else "py"

	code = "{0}/{1}/{2}/Code.{3}".format(REPOSITORY_FOLDER, hid, eid, codeExt)
	exeFile = "{0}/{1}/{2}/Code.{3}".format(REPOSITORY_FOLDER, hid, eid, exeExt)

	solutionTXT = "{0}/{1}/{2}/Solution.txt".format(REPOSITORY_FOLDER, hid, eid)
	inputTXT = "{0}/{1}/{2}/Input.txt".format(REPOSITORY_FOLDER, hid, eid)
	outputTXT = "{0}/{1}/{2}/Output.txt".format(REPOSITORY_FOLDER, hid, eid)
	verifiedTXT = "{0}/{1}/{2}/{3}".format(REPOSITORY_FOLDER, hid, eid, VERIFIED_FILE)
	mapinoutTXT = "{0}/{1}/{2}/{3}".format(REPOSITORY_FOLDER, hid, eid, "MapInOut.txt")
	debugTXT = "{0}/{1}/{2}/{3}".format(REPOSITORY_FOLDER, hid, eid, "Debug")

	if exeFile != code:
		rm(exeFile)

	rm(verifiedTXT)
	rm(outputTXT)
	rm(debugTXT + "Input.txt")
	rm(debugTXT + "Solution.txt")

	selectColor("CYAN")
	print(color("Running my solution:"))
	print(color("----------------------"))
	if exeFile != code:
		print(color("Starting compilation..."))
		compCmd = ParseParams(getLanguageSetting(ex.language, "COMPILER_CMD").replace("<EXE_FILE>", OSPath(exeFile)).replace("<CODE_FILE>", OSPath(code)))
		print(color(run(compCmd[0],compCmd[1:]), "LIGHTYELLOW_EX"))
		print(color("Compilation done."))
		print(color("----------------------"))
	if isFile(exeFile):
		print(color("Running executable file... (type ") + color("Ctrl+C", "LIGHTYELLOW_EX") + color(" to stop the execution)"))
		if exeFile != code:
			exeCmd = [exeFile]
		else:
			exeCmd = ParseParams(getLanguageSetting(ex.language, "COMPILER_CMD").replace("<CODE_FILE>", OSPath(code)))
		starttime = time.time()
		(algElapsedTime, outputs, errors) = runAsync(exeCmd[0], params=exeCmd[1:], inputfile=inputTXT, outputfile=outputTXT, solutionfile=solutionTXT, debugfile=debugTXT, mapinoutfile=mapinoutTXT, timelimit=(EXE_TIMELIMIT_FACTOR * ex.timelimit))
		realElapsedTime = time.time() - starttime
		print(color("Execution done in ") +\
			  color("{:.1f} sec.".format(algElapsedTime), "LIGHTYELLOW_EX") +\
			  color(" (Total time: {:.1f} sec)".format(realElapsedTime)))
		print(color("----------------------"))

		if len(errors)>0:
			print(color("The following differences have been found:"))
			print(color("----------------------"))
			for (inputinfo, outputinfo, solutioninfo) in errors:
				(outdiff, soldiff) = LineDiff(outputinfo, solutioninfo)
				(inputinfo, inputinfo) = LineDiff(inputinfo, inputinfo)
				print(color("Input:"))
				print(inputinfo)
				print(color("Output:"))
				print(outdiff)
				print(color("Solution:"))
				print(soldiff)
				print(color("----------------------"))

		else:
			print(color("No differences have been found."))
			print(color("----------------------"))
	else:
		outputs = []; algElapsedTime = 0
		errors = ["Compilation error."]

	verOkay = True
	if len(outputs)>0 and len(errors) == 0:
		print(color("Correctness:") + " " + color("Checked!", "GREEN"))
	else:
		print(color("Correctness:") + " " + color("Failed...", "YELLOW"))
		verOkay = False
	if algElapsedTime <= ex.timelimit:
		print(color("Time Complexity:") + " " + color("Checked!", "GREEN"))
	else:
		print(color("Time Complexity:") + " " + color("Failed...", "YELLOW"))
		verOkay = False
	if verOkay:
		writeFile(verifiedTXT, "Okay")
		print(color("Veredict:", "LIGHTYELLOW_EX") + " " + color("Correct!", "GREEN"))
	else:
		print(color("Veredict:", "LIGHTYELLOW_EX") + " " + color("Wrong Answer...", "YELLOW"))
	printWait()

def DebugCode(eid, hid):
	rep = repository("local")
	rep.load()
	hw = rep.find(hid)
	ex = hw.find(eid)

	codeExt = "cpp" if ex.language == "C++" else "py"
	exeExt = "exe" if ex.language == "C++" else "py"

	code = "{0}/{1}/{2}/Code.{3}".format(REPOSITORY_FOLDER, hid, eid, codeExt)
	exeFile = "{0}/{1}/{2}/Code.{3}".format(REPOSITORY_FOLDER, hid, eid, exeExt)

	debugTXT = "{0}/{1}/{2}/{3}".format(REPOSITORY_FOLDER, hid, eid, "Debug")

	if exeFile != code:
		rm(exeFile)

	selectColor("CYAN")
	print(color("Running my solution") + " " + color("(using the first wrong answer as input, in DEBUG mode)", "LIGHTYELLOW_EX") + color(":"))
	print(color("----------------------"))
	if exeFile != code:
		print(color("Starting compilation..."))
		compCmd = ParseParams(getLanguageSetting(ex.language, "COMPILER_CMD").replace("<EXE_FILE>", OSPath(exeFile)).replace("<CODE_FILE>", OSPath(code)))
		print(color(run(compCmd[0],compCmd[1:]), "LIGHTYELLOW_EX"))
		print(color("Compilation done."))
		print(color("----------------------"))
	if isFile(exeFile):
		print(color("Running executable file... (type ") + color("Ctrl+C", "LIGHTYELLOW_EX") + color(" to stop the execution)"))
		if exeFile != code:
			exeCmd = [exeFile]
		else:
			exeCmd = ParseParams(getLanguageSetting(ex.language, "COMPILER_CMD").replace("<CODE_FILE>", OSPath(code)))
		exeCmd.append("DEBUG")
		starttime = time.time()
		(algElapsedTime, outputs, errors) = runAsync(exeCmd[0], params=exeCmd[1:], inputfile=debugTXT+"Input.txt", solutionfile=debugTXT+"Solution.txt", timelimit=(EXE_TIMELIMIT_FACTOR * ex.timelimit))
		realElapsedTime = time.time() - starttime
		print(color("Execution done in ") +\
			  color("{:.1f} sec.".format(algElapsedTime), "LIGHTYELLOW_EX") +\
			  color(" (Total time: {:.1f} sec)".format(realElapsedTime)))
		print(color("----------------------"))

		if len(errors)>0:
			print(color("The following differences have been found:"))
			print(color("----------------------"))
			for (inputinfo, outputinfo, solutioninfo) in errors:
				(outdiff, soldiff) = LineDiff(outputinfo, solutioninfo)
				(inputinfo, inputinfo) = LineDiff(inputinfo, inputinfo)
				print(color("Input:"))
				print(inputinfo)
				print(color("Output:"))
				print(outdiff)
				print(color("Solution:"))
				print(soldiff)
				print(color("----------------------"))

		else:
			print(color("No differences have been found."))
			print(color("----------------------"))

	printWait()

def RunCode(eid, hid):
	rep = repository("local")
	rep.load()
	hw = rep.find(hid)
	ex = hw.find(eid)

	exeExt = "exe" if ex.language == "C++" else "py"
	codeExt = "cpp" if ex.language == "C++" else "py"

	exeFile = "{0}/{1}/{2}/Code.{3}".format(REPOSITORY_FOLDER, hid, eid, exeExt)
	code = "{0}/{1}/{2}/Code.{3}".format(REPOSITORY_FOLDER, hid, eid, codeExt)

	if exeFile != code:
		rm(exeFile)

	selectColor("CYAN")
	print(color("Running my solution:"))
	print(color("----------------------"))
	if exeFile != code:
		print(color("Starting compilation..."))
		compCmd = ParseParams(getLanguageSetting(ex.language, "COMPILER_CMD").replace("<EXE_FILE>", OSPath(exeFile)).replace("<CODE_FILE>", OSPath(code)))
		print(color(run(compCmd[0],compCmd[1:]), "LIGHTYELLOW_EX"))
		print(color("Compilation done."))
		print(color("----------------------"))
	if isFile(exeFile):
		print(color("Running the program..."))
		print(color("(type the input; use ") +\
			  color("Ctrl+D" if platform.system() != "Windows" else "Ctrl+D or Ctrl+Z", "LIGHTYELLOW_EX") +\
			  color(" to indicate that there is no more input data)"))
		print(color("(type ") + color("Ctrl+C", "LIGHTYELLOW_EX") + color(" to stop the execution)"))
		if exeFile != code:
			exeCmd = [exeFile]
		else:
			exeCmd = ParseParams(getLanguageSetting(ex.language, "COMPILER_CMD").replace("<CODE_FILE>", OSPath(code)))
		output = run(exeCmd[0], exeCmd[1:])
		print()
		print(color("----------------------"))
		print(color("Execution done. Output:"))
		print(output)

	printWait()

def ShowInput(eid, hid):
	path = "{0}/{1}/{2}/Input.txt".format(REPOSITORY_FOLDER, hid, eid)
	selectColor("CYAN")
	print(color("Below, you find the input data that Codev will give"))
	print(color("to your program during the validation process. Be aware"))
	print(color("that some (or even all) input data may be produced"))
	print(color("directly from the code. So, check the code out too."))
	print(color("----------------------"))
	print(readFile(path))
	printWait()

def DelConfirmHW(hid):
	path = "{0}/{1}".format(REPOSITORY_FOLDER, hid)
	rm(path)
	repository.remove(hid)

def DelConfirmCode(eid, hid):
	rep = repository("local")
	rep.load()
	hw = rep.find(hid)
	ex = hw.find(eid)

	codeExt = "cpp" if ex.language == "C++" else "py"
	code = "{0}/{1}/{2}/Code.{3}".format(REPOSITORY_FOLDER, hid, eid, codeExt)
	rm(code)
	code = "{0}/{1}/{2}/KeyCode.{3}".format(REPOSITORY_FOLDER, hid, eid, codeExt)
	rm(code)

def getProgressBar(text, count):
	b = FillingSquaresBar(text + ' ', fill='█', suffix='%(percent).0f%% (%(eta)ds)', max=count)
	return b

def DownloadHW(hid, creating, onlyNew):
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
	b = getProgressBar("Retrieving exercise data... ", len(exLst))
	for eid in exLst:
		language = exercise.getLanguage(eid)

		exurl = hwurl + "/" + eid
		exfolder = hwfolder + "/" + eid
		createEx = not isDir(exfolder)

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

		if not onlyNew or createEx:
			if createEx:
				mkdir(exfolder)
			filesOverwrite = [CONFIG_FILE, "Solution.txt", "Input.txt", "MapInOut.txt"]
			if language == "C++":
				filesKeepOriginal = ["Code.cpp"]
			else:
				filesKeepOriginal = ["Code.py"]
			filesRem = [VERIFIED_FILE]

			for f in filesOverwrite:
				rm(exfolder + "/" + f)
				c = getURL(exurl + "/" + f)
				if c != "":
					writeFile(exfolder + "/" + f, c)
			for f in filesKeepOriginal:
				fn = exfolder + "/" + f
				if not isFile(fn):
					writeFile(fn, removeCodev(language, clear(getURL(exurl + "/" + f))))
			for f in filesRem:
				rm(exfolder + "/" + f)
			DownloadSeqFiles('Figure', 'pdf')
			if language == "C++":
				DownloadSeqFiles('Bib', 'h')
			else:
				DownloadSeqFiles('Bib', 'py')
			DownloadSeqFiles('Hint', 'txt')

		econt += 1
		b.next()
	b.finish()

	if creating:
		repository.add(hid)

def GenMenuReadHW(eid, hid):
	rep = repository("local")
	rep.load()
	hw = rep.find(hid)
	ex = hw.find(eid)
	Opt = []
	selectColor("CYAN")
	Opt.append(color("Homework: ") + color("{0}".format(hw.description), "LIGHTCYAN_EX"))
	Opt.append(None)
	Opt.append(color("Exercise  : ") + "{0}".format(ex.title))
	Opt.append(color("ID        : ") + "{0}".format(ex.eid))
	Opt.append(color("Time Limit: ") + "{0} secs.".format(ex.timelimit))
	Opt.append(color("Status    : ") + "{0}".format(ex.cstatus()))
	Opt.append(color("Language  : ") + "{0}".format(ex.language))
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
	selectColor("YELLOW")
	Opt.append(["1", color("Edit Code"), ["editCode", eid, hid]])
	Opt.append(["2", color("Run Code"), ["runCode", eid, hid]])
	Opt.append(["3", color("Validate Code"), ["verifyCode", eid, hid]])
	if isFile(exfolder + "/" + "DebugInput.txt"):
		Opt.append(["4", color("Debug Code"), ["debugCode", eid, hid]])
	Opt.append(None)
	hwurl = "{0}/{1}".format(SERVER_URL, hid)
	exfolder = "{0}/{1}/{2}".format(REPOSITORY_FOLDER, hid, eid)
	selectColor("LIGHTBLUE_EX")
	Opt.append(["i", color("Show Input"), ["showInput", eid, hid]])
	if isFile(exfolder + "/" + "Hint1.txt"):
		Opt.append(["h1", color("Get a Hint"), ["seeBasicHint", eid, hid]])
	if isFile(exfolder + "/" + "Hint2.txt"):
		Opt.append(["h2", color("Get a Spoiler Hint"), ["seeSpoilerHint", eid, hid]])
	if isFile(exfolder + "/" + "KeyCode.cpp") or (checkConnection() and getURL(hwurl + "/Pass.txt") != ""):
		Opt.append(["s", color("See a Solution"), ["editKeyCode", eid, hid]])
	selectColor("CYAN")
	Opt.append(None)
	Opt.append(["d", color("Delete Code"), ["delCode", eid, hid]])
	Opt.append(None)
	Opt.append(["b", color("Go Back"), ["openHW", hid]])
	return Opt


def GenMenuOpenHW(hid):
	rep = repository("local")
	rep.load()
	hw = rep.find(hid)
	i = 1
	Opt = []
	selectColor("CYAN")
	Opt.append(color("Homework: ") + color("{0}".format(hw.description), "LIGHTCYAN_EX"))
	Opt.append(None)
	for ex in hw.exs:
		Opt.append([str(i), ex.title + " (" + ex.cstatus() + ")", ["readHW", ex.eid, hid]])
		i += 1
	Opt.append(None)
	downcolor = "YELLOW" if isThereNewEx(hid) else "CYAN"
	Opt.append(["n", color("Download New Exercises", downcolor), ["addnewHW", hid]])
	Opt.append(["u", color("Update Homework"), ["updHW", hid]])
	Opt.append(["d", color("Delete Homework"), ["delHW", hid]])
	Opt.append(None)
	Opt.append(["b", color("Go Back"), ["hwList"]])
	return Opt


def GenMenuNewHW():
	connec = checkConnection()

	rep = repository("remote")
	if connec:
		rep.load()

	Opt = []
	i = 1
	Opt.append(color("New Homeworks:", "CYAN"))
	Opt.append(None)
	if connec and len(rep.hws) == 0:
		Opt.append("(no new homeworks have been found)")
	elif not connec:
		Opt.append("(connection to the server seems to be down...)")
	else:
		for hw in rep.hws:
			Opt.append([str(i), hw.description + " (" + hw.cstatus() + ")", ["downloadHW", hw.hid]])
			i += 1
	Opt.append(None)
	Opt.append(["b", "Go Back", ["hwList"]])
	return Opt


def GenMenuDelHW(hid):
	rep = repository("local")
	rep.load()
	hw = rep.find(hid)
	Opt = []
	selectColor("CYAN")
	Opt.append(color("Homework: ") + color("{0}".format(hw.description), "LIGHTCYAN_EX"))
	Opt.append(None)
	selectColor("YELLOW")
	Opt.append(color("Are you sure you want to delete ALL saved data for this homework,"))
	Opt.append(color("including the code files?"))
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
	selectColor("CYAN")
	Opt.append(color("Homework:") + " " + color("{0}".format(hw.description), "LIGHTCYAN_EX"))
	Opt.append(None)
	Opt.append(color("Exercise:") + " " + ex.title)
	Opt.append(None)
	Opt.append(color("Are you sure you want to delete its associated code?", "YELLOW"))
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
	rep = repository("local")
	rep.load()
	hw = rep.find(hid)
	ex = hw.find(eid)

	codeExt = "cpp" if ex.language == "C++" else "py"
	keycode = "{0}/{1}/{2}/KeyCode.{3}".format(REPOSITORY_FOLDER, hid, eid, codeExt)

	if not isFile(keycode):
		Pwd = input("Please, enter the password: ")
		hwurl = "{0}/{1}".format(SERVER_URL, hid)
		sPwd = clear(getURL(hwurl + "/" + "Pass.txt"))
		if sPwd == "" or Pwd != sPwd:
			print("This given password for this homework does not match.")
			printWait()
		else:
			exurl = hwurl + "/" + eid
			f = "Code." + codeExt
			writeFile(keycode, removeCodevComments(ex.language, clear(getURL(exurl + "/" + f))))

	if isFile(keycode):
		path = OSPath(keycode)
		cmd = ParseParams(getLanguageSetting(ex.language, "EDITOR_CMD").replace("<CODE_FILE>", path))
		run(cmd[0], cmd[1:])

def isThereNewHW():
	if checkConnection():
		hwurl = "{0}".format(SERVER_URL)
		hwfolder = "{0}".format(REPOSITORY_FOLDER)
		f = CONFIG_FILE
		if isFile(hwfolder + "/" + f):
			cr = getURL(hwurl + "/" + f); lr = split(cr, " ")
			cl = readFile(hwfolder + "/" + f); ll = split(cl, " ")
			for hid in lr:
				if not hid in ll:
					return True
		else:
			return True
	return False

def isThereNewEx(hid):
	if checkConnection():
		hwurl = "{0}/{1}".format(SERVER_URL, hid)
		hwfolder = "{0}/{1}".format(REPOSITORY_FOLDER, hid)
		f = CONFIG_FILE
		cr = getURL(hwurl + "/" + f)
		cl = readFile(hwfolder + "/" + f)
		lr = split(split(cr, "\n")[1], " ")
		ll = split(split(cl, "\n")[1], " ")
		for eid in lr:
			if not eid in ll:
				return True
		return False
	return False

def GenMenuHWList():
	rep = repository("local")
	rep.load()

	Opt = []
	i = 1
	Opt.append(color("Downloaded Homeworks:", "CYAN"))
	Opt.append(None)
	if len(rep.hws) == 0:
		Opt.append("(no homework has been downloaded yet)")
	else:
		for hw in rep.hws:
			Opt.append([str(i), hw.description + " (" + hw.cstatus() + ")", ["openHW", hw.hid]])
			i += 1
	Opt.append(None)
	selectColor("CYAN")
	downcolor = "YELLOW" if isThereNewHW() else "CYAN"
	Opt.append(["n", color("Download New Homework", downcolor), ["newHW"]])
	Opt.append(None)
	if UPDATE_SOFTWARE == "1":
		Opt.append(["u", color("Update Codev Software"), ["updSoft"]])
	Opt.append(["s", color("Settings"), ["settings"]])
	Opt.append(["a", color("About"), ["about"]])
	Opt.append(["q", color("Quit"), ["quit"]])
	return Opt


def DisplayMenu(Opt):
	while True:
		printHeader()
		menu = {}
		margin = color(" ║ ", "CYAN")  #LIGHTBLACK_EX
		for item in Opt:
			if item == None:
				print(margin)
			elif isinstance(item, str):
				for txt in item.split("\n"):
					print(margin + txt)
			else:
				print(margin + color("[", "CYAN") + color(item[0], "LIGHTCYAN_EX") + color("]", "CYAN") + " " + item[1])
				menu[item[0].upper()] = item[2]
		print()
		x = input("Option: ").upper()
		if x in menu:
			return menu[x]

def GenMenuAbout():
	Opt = []
	Opt.append(color("Author:", "CYAN") + " " + color("Fabiano Oliveira", "YELLOW"))
	Opt.append(color("Email :", "CYAN") + " " + color("fabiano.oliveira@ime.uerj.br", "YELLOW"))
	Opt.append(None)
	Opt.append("What do you think of this tool?")
	Opt.append(None)
	Opt.append(["1", "Awesome", ["hwList"]])
	Opt.append(["2", "Really great", ["hwList"]])
	Opt.append(["3", "Terrific", ["hwList"]])
	return Opt

def GenMenuSettings():
	selectColor("YELLOW")
	Opt = []
	Opt.append("Settings must be adjusted in the file Settings.txt")
	Opt.append("located in the Codev folder. Settings that can be adjusted:")
	Opt.append(None)
	Opt.append(color(r"EDITOR_CMD = <value>"))
	Opt.append(color(r"EDITOR_CMD_<LANGUAGE> = <value>"))
	Opt.append(r"<value> should be a valid command line for opening")
	Opt.append(r"the code editor; the substring of value named <CODE_FILE>")
	Opt.append(r"will be replaced with the code filename.")
	Opt.append(r"This parameter can be personalized to each <LANGUAGE> (C++/PYTHON/TEXT).")
	Opt.append(r"If a space between arguments does not work well, try replacing")
	Opt.append(r"with a comma (,) those spaces that delimit arguments.")
	Opt.append(None)
	Opt.append(color(r"COMPILER_CMD = <value>"))
	Opt.append(color(r"COMPILER_CMD_<LANGUAGE> = <value>"))
	Opt.append(r"<value> should be a valid command line for compiling")
	Opt.append(r"the code; the substring <CODE_FILE> will be replaced with")
	Opt.append(r"the code filename, and <EXE_FILE> with the executable file")
	Opt.append(r"to be created.")
	Opt.append(r"This parameter can be personalized to each <LANGUAGE> (C++/PYTHON).")
	Opt.append(r"If a space between arguments does not work well, try replacing")
	Opt.append(r"with a comma (,) those spaces that delimit arguments.")
	Opt.append(None)
	Opt.append(color(r"UPDATE_SOFTWARE = 0/1"))
	Opt.append(r"0 for hiding the option for downloading new versions of Codev.")
	Opt.append(None)
	Opt.append(color(r"SERVER_URL = <value>"))
	Opt.append(r"Codev repository server URL.")
	Opt.append(None)
	Opt.append(color(r"REPOSITORY_FOLDER = <value>"))
	Opt.append(r"Codev local repository; all the files are located there.")
	Opt.append(None)
	Opt.append(color(r"PDF_READER = <value>"))
	Opt.append(r"<value> should be a valid command line for executing a")
	Opt.append(r"pdf reader tool; the substrings <PDF_FILE>")
	Opt.append(r"will be replaced with the filename to be opened.")
	Opt.append(r"If a space between arguments does not work well, try replacing")
	Opt.append(r"with a comma (,) those spaces that delimit arguments.")
	Opt.append(None)
	Opt.append(color(r"EXE_TIMELIMIT_FACTOR = <value>"))
	Opt.append(r"During a programa validation, Codev will allow a program run longer")
	Opt.append(r"than the time limit to assess its correctness. If this execution time")
	Opt.append(r"reaches a threshold, Codev will interrupt the execution. The total time")
	Opt.append(r"Codev allows is given by the exercise time limit multiplied by <value>.")
	Opt.append(None)
	Opt.append(color(r"MONOCHROMATIC = 0/1"))
	Opt.append(r"Use MONOCHROMATIC = 1 to use Codev without multiple colors.")
	Opt.append(None)
	Opt.append(["b", "Go Back", ["hwList"]])

	ShowTextFile("./Settings.txt")
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
			DownloadHW(chosen[1], True, True)
			chosen = ["hwList"]
		elif cmd == "openHW":
			chosen = DisplayMenu(GenMenuOpenHW(chosen[1]))
		elif cmd == "readHW":
			chosen = DisplayMenu(GenMenuReadHW(chosen[1], chosen[2]))
		elif cmd == "delHW":
			chosen = DisplayMenu(GenMenuDelHW(chosen[1]))
		elif cmd == "updHW":
			DownloadHW(chosen[1], False, False)
			chosen = ["openHW", chosen[1]]
		elif cmd == "addnewHW":
			DownloadHW(chosen[1], False, True)
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
		elif cmd == "debugCode":
			DebugCode(chosen[1], chosen[2])
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

def getLanguageSetting(language, key):
	lkey = key + "_" + language.upper()
	if lkey in cfg:
		return cfg[lkey]
	else:
		return cfg[key]


colorama_init(autoreset=True)
colorama_colors = dict(Fore.__dict__.items())
SELECTED_COLOR = "WHITE"
selectColor(SELECTED_COLOR)

if not isFile("./Settings.txt"):
	osstr = "Windows" if platform.system() == "Windows" else "Linux"
	if isFile("./Settings.txt." + osstr):
		cp("./Settings.txt." + osstr, "./Settings.txt")
	else:
		print("Codev did not find the file Settings.txt")
		exit(0)

cfg = readConfigFile("./Settings.txt")
REPOSITORY_FOLDER = cfg.get("REPOSITORY_FOLDER", "./repository")
SERVER_URL = cfg["SERVER_URL"]
UPDATE_SOFTWARE = cfg.get("UPDATE_SOFTWARE", "1")
PDF_READER = cfg.get("PDF_READER", "<PDF_FILE>")
EXE_TIMELIMIT_FACTOR = int(cfg.get("EXE_TIMELIMIT_FACTOR", "10"))
MONOCHROMATIC = int(cfg.get("MONOCHROMATIC", "0"))

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

if checkConnection():
	minver = getURL(SERVER_URL + "/" + "MinVersion.txt")
	if minver != "" and not isVersionAtLeast(minver):
		print("ATTENTION: Your Codev client software may not work with")
		print("the current server version. It is highly recommended")
		print("updating Codev before continuing.")
		printWait()

if len(sys.argv) > 1:
	if sys.argv[1] == "upload":
		rf = sys.argv[2]; hid = sys.argv[3]; eid = sys.argv[4]
		exfolder = "{0}/{1}/{2}".format(rf, hid, eid)
		files = ["Hint2.txt"]
		language = exercise.getLanguage(eid)
		files.append("Code.cpp" if language == "C++" else "Code.py")
		for f in files:
			keyf = "Key" + f
			if isFile(exfolder + "/" + keyf):
				writeFile(exfolder + "/" + f, obscure(readFile(exfolder + "/" + keyf)))
			else:
				print(keyf + " not found.")
	elif sys.argv[1] == "pass":
		rf = sys.argv[2]; hid = sys.argv[3]
		hwfolder = "{0}/{1}".format(rf, hid)
		if isFile(hwfolder + "/KeyPass.txt"):
			writeFile(hwfolder + "/Pass.txt", obscure(readFile(hwfolder + "/KeyPass.txt")))
		else:
			print("KeyPass.txt not found.")
	else:
		print("Codev could not recognize the given parameters.")
else:

	GenMenu()
