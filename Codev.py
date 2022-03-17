import os
import os.path
import requests
import platform
import shutil
import time
import subprocess

CONFIG_FILE = "Config.txt"
VERIFIED_FILE = "Verified.txt"

def getVersion():
	return "0.2"

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
		self.timelimit = int(exdata[1])
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
	f = open(filename, "r")
	strRead = f.read()
	f.close()
	return strRead


def writeFile(filename, content):
	filename = OSPath(filename)
	f = open(filename, "w")
	f.write(content)
	f.close()

def downloadFile(url, filename):
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


def printHeader():
	os.system('cls||clear')
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

def run(cmd, params=None, inputfile=""):
	if params==None:
		params = []
	cmd = OSPath(cmd)
	fullcmd = [cmd] + params
	if inputfile == "":
		infileObj = None
	else:
		infileObj = open(OSPath(inputfile), "r")
	p = subprocess.run(fullcmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=infileObj)
	return p.stdout.decode("utf-8") + p.stderr.decode("utf-8")

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

def EditCode(eid, hid):
	path = "{0}/{1}/{2}/Code.cpp".format(REPOSITORY_FOLDER, hid, eid)
	path = OSPath(path)
	run(EDITOR_CMD.replace("<CODE_FILE>", path))

def OpenFigure(fig, eid, hid):
	path = "{0}/{1}/{2}/Figure{3}.pdf".format(REPOSITORY_FOLDER, hid, eid, fig)
	path = OSPath(path)
	run(PDF_READER.replace("<PDF_FILE>", path))

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
	COMPILER_CMD_STR = OSPath(COMPILER_CMD).replace("<EXE_FILE>", OSPath(exeFile)).replace("<CODE_FILE>", OSPath(code))
	print(run(COMPILER_CMD_STR))
	print("Compilation done.")
	print("---")
	print("Running executable file...")
	starttime = time.time()
	output = run(exeFile, inputfile=inputTXT)
	endtime = time.time()
	elapsedTime = endtime - starttime
	print(output)
	writeFile(outputTXT, output.strip("\n"))
	print("Execution done in {:.1f} sec.".format(elapsedTime))
	print("----------------------")
	diffout = ""
	if output != "":
		print("Comparing results:")
		print("----------------------")
		diffout = run(DIFF_CMD.replace("<FILE1>", OSPath(outputTXT)).replace("<FILE2>", OSPath(solutionTXT)))
		print(diffout)
		writeFile(diffTXT, diffout)
		print("----------------------")
	verOkay = True
	if output != "" and diffout == DIFF_NO_TEXT:
		print("Correctness: Checked!")
	else:
		print("Correctness: Failed...")
		verOkay = False
	if elapsedTime <= ex.timelimit:
		print("Time Complexity: Checked!")
	else:
		print("Time Complexity: Failed...")
		verOkay = False
	if verOkay:
		writeFile(verifiedTXT, "Okay")
		print("Veredict: Correct!")
	else:
		print("Veredict: Wrong Answer...")
	print("----------------------")
	input("Press ENTER to continue...")

def RunCode(eid, hid):

	exeFile = "{0}/{1}/{2}/Code.exe".format(REPOSITORY_FOLDER, hid, eid)
	code = "{0}/{1}/{2}/Code.cpp".format(REPOSITORY_FOLDER, hid, eid)

	print("Running my solution:")
	print("----------------------")
	print("Starting compilation...")
	COMPILER_CMD_STR = OSPath(COMPILER_CMD).replace("<EXE_FILE>", OSPath(exeFile)).replace("<CODE_FILE>", OSPath(code))
	print(run(COMPILER_CMD_STR))
	print("Compilation done.")
	print("---")
	print("Running executable file...")
	print("(type the input; use {0} to finish)".format("Ctrl+D" if platform.system() != "Windows" else "Ctrl+Z"))
	output = run(exeFile)
	print("---")
	print("Execution done. Output:")
	print(output)
	print("----------------------")
	input("Press ENTER to continue...")


def DelConfirmHW(hid):
	path = "{0}/{1}".format(REPOSITORY_FOLDER, hid)
	rm(path)
	repository.remove(hid)

def DelConfirmCode(eid, hid):
	path = "{0}/{1}/{2}/Code.cpp".format(REPOSITORY_FOLDER, hid, eid)
	rm(path)

def DownloadHW(hid, creating):
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

		for f in filesOverwrite:
			writeFile(exfolder + "/" + f, getURL(exurl + "/" + f))
		for f in filesKeepOriginal:
			fn = exfolder + "/" + f
			if not isFile(fn):
				writeFile(fn, removeCodev(getURL(exurl + "/" + f)))
		for f in filesRem:
			rm(exfolder + "/" + f)
		i = 1; f = "Figure{0}.pdf".format(i)
		while isFile(exfolder + "/" + f):
			rm(exfolder + "/" + f)
			i = i+1; f = "Figure{0}.pdf".format(i)
		i = 1; f = "Figure{0}.pdf".format(i)
		while downloadFile(exurl + "/" + f, exfolder + "/" + f):
			i = i+1; f = "Figure{0}.pdf".format(i)
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
	rep = repository("remote")
	rep.load()

	Opt = []
	i = 1
	Opt.append("New Homeworks:")
	Opt.append(None)
	if len(rep.hws) == 0:
		Opt.append("(no new homeworks have been found)")
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
	Opt.append(None)
	Opt.append(r"COMPILER_CMD = <value>")
	Opt.append(r"<value> should be a valid command line for compiling")
	Opt.append(r"the code; the substring <CODE_FILE> will be replaced with")
	Opt.append(r"the code filename, and <EXE_FILE> with the executable file")
	Opt.append(r"to be created.")
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
	Opt.append(None)
	Opt.append(r"PDF_READER = <value>")
	Opt.append(r"<value> should be a valid command line for executing a")
	Opt.append(r"pdf reader tool; the substrings <PDF_FILE>")
	Opt.append(r"will be replaced with the filename to be opened.")
	Opt.append(None)
	Opt.append(["b", "Go Back", ["hwList"]])
	return Opt

def UpdateSoftware():
	if UPDATE_SOFTWARE == "1":
		hwurl = SERVER_URL
		hwfolder = os.getcwd()
		files = ["Codev.py", "Settings.txt"]
		if isFile(hwfolder + "/" + "Settings.txt"):
			mv(hwfolder + "/" + "Settings.txt", hwfolder + "/" + "Settings.old")
		for f in files:
			writeFile(hwfolder + "/" + f, getURL(hwurl + "/" + f))
		if isFile(hwfolder + "/" + "Settings.old"):
			mv(hwfolder + "/" + "Settings.txt", hwfolder + "/" + "Settings.new")
			mv(hwfolder + "/" + "Settings.old", hwfolder + "/" + "Settings.txt")
		print()
		input("You must restart in order to run the new version... ")

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
		elif cmd == "delCode":
			chosen = DisplayMenu(GenMenuDelCode(chosen[1], chosen[2]))
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


cfg = readConfigFile("Settings.txt")

REPOSITORY_FOLDER = cfg.get("REPOSITORY_FOLDER", "./repository")
if not isDir(REPOSITORY_FOLDER):
	mkdir(REPOSITORY_FOLDER)
SERVER_URL = cfg["SERVER_URL"]
EDITOR_CMD = cfg["EDITOR_CMD"]
COMPILER_CMD = cfg["COMPILER_CMD"]
DIFF_CMD = cfg["DIFF_CMD"]
DIFF_NO_TEXT = cfg.get("DIFF_NO_TEXT", "")
UPDATE_SOFTWARE = cfg.get("UPDATE_SOFTWARE", "1")
PDF_READER = cfg.get("PDF_READER", "<PDF_FILE>")

GenMenu()