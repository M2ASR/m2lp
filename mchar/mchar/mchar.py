#!python3.4

class Mchar():
	romancode = {} ; municode = {}

	def __init__(self, Lang):
		self.Lang = Lang
		if self.Code_init():
			print("The %s code-map-file is laoded successfuly.\n" % self.Lang)
		else:
			print("error0, failed to load %s charater codes.\n" % self.Lang)
	#def __init__()

	def open_file(self, file, wr="r"):
		pfile = None
		try: pfile = open(file , wr, encoding='utf-8')
		except:
			print("error0, failed to open file %s\n" % file)
		return pfile
	# def open_file()

	def Code_init(self):
		fdir = "./mchar/charmaps/" + self.Lang + ".code"
		codefile = self.open_file(fdir)
		if not codefile: return None
		line = codefile.readline().replace(" ", "")
		while line:
			(roman , codeID, mcod) = ("", "", "")
			try:roman , codeID, mcod = line.strip().split("=")
			except: pass
			if not codeID.isdigit():pass
			elif roman.isdigit() and len(chr(int(roman)))> 1: pass # if it is a code then should be one char
			elif len(roman)>2: pass # if it is a char ,then can be a double chars
			elif (roman and codeID and mcod):
				if (roman not in self.romancode):
					self.romancode[roman] = codeID
				else:
					print("error2-2, there are duplicated codes for romancode: [%s]=[%s] \n" % (roman,codeID))
					return None
				ucodes = mcod.split(",")
				for code in ucodes:
					if not code: continue
					if code.isdigit(): code = chr(int(code))
					if len(code) > 2: print("error2-2, something wrong wiht code: [%s]=[%s] is" %(code,roman))
					elif code not in self.municode: self.municode[code] = roman
					else:
						print("error2-3, there are duplicated codes for unicode:[%s]=[%s] \n" % (code, roman))
						return None
			line = codefile.readline()
		codefile.close()
		print("total [%d] codes, mapped into [%d] codes for [%s] Language\n" % (len(self.municode), len(self.romancode), self.Lang))
		return 1
	#def CondeInit()

	# returns pure alphabet numbers in sting , return 0 if not pure
	def All_alphs(self, string):
		ret = 0;
		for ch in string:
			cID = 0;
			if ch in self.romancode: cID = int(self.romancode[ch])
			if cID >=1 and cID <=self.alphabet_len: ret +=1
			else: return None
		return ret
	#def Alphabet()

	# returns alphabet numbers in sting , return 0 if not containnig any alphabet
	def Alph_number(self, string):
		ret = 0;
		for ch in string:
			cID = self.romancode[ch]
			if cID >=1 and cID <=self.alphabet_len:
				ret +=1
		return ret
	#def AlphNumber()

	# returns vowel number if pure vowels,
	def IsVowel(self, string):
		ret = 0
		for ch in string:
			if ch in self.Vowels:
				ret +=1
			else:
				return None
		return ret
	# def IsVowel()

		# transform other multi-codes into roman code for a line string
	def Code_flip(self, string, alpha_only = True, mlable = ""):
		string = string.strip(); strlen = len(string)
		if not strlen: return None
		i = 0 ; word = ""; ret = ""
		while i < strlen:
			if i < strlen -1 and string[i:i+2] in self.municode:# try if there are double to to one code flip
				word += self.municode[string[i:i+2]];i +=2 # in case double alphabets are exist
			else:
				ch = string[i]; i +=1
				if ch in self.municode:ch = self.municode[ch]
				if self.All_alphs(ch): word += (ch)
				else: # assume other languages, but: donot forget whitespace
					if alpha_only and ch != " ": ch = ""
					if word: ret = ret + mlable + word + ch
					else: ret = ret + ch
					word = ""
		if word: ret += word
		return ret
	# def CodeFlip()

	# returns vowel lacation list (of string) of a word
	# two assumption are specific: 1)only one or double vowels in a syllable
	# 2) no longer than 4 consequetive consonants
	def Vowel_location(self, string):
		ret = []; lenth = len(string)
		if lenth > 30: return None
		vow_repeat = 0; cons_repeat = 0
		for i in range(lenth):
			if self.IsVowel(string[i]):
				if not vow_repeat: ret.append(i)  # double vowels are one syllable
				if cons_repeat > 4: return None
				vow_repeat += 1; cons_repeat = 0  # assume only double vowels no triple
			else:
				if vow_repeat > 2: return None  # assume only double vowels no triple
				vow_repeat = 0; cons_repeat +=1
		return ret
	#def Vowel_location()

	# syllable template matching method
	# two assumption is specific: 1) loghest syllable <=5;  2)chars ahead of vowel is necessary in the template
	def _BABB(self,syll,syll_template):
		lenth = len(syll)
		if lenth > 5: return None # we assume that syllable is no longer than 5
		babb = "" ;
		for i in range(lenth):
			if self.IsVowel(syll[i]):
				babb += "A"
				if babb not in syll_template: return None
			else:
				if (babb + "B") in syll_template: babb += "B"
				elif(babb + "[B]") in syll_template: babb += "[B]"
				else: return None
		indx = syll_template.find(",")
		if indx >=0  and syll_template[0:indx] in babb: return True # the first item is the necessary part
		else: return False
	#def _BABB()

	def Syll_split(self, string, syll_template):
		vloc = self.Vowel_location(string)
		if not vloc: return None
		syll_num = len(vloc)
		if not syll_num or syll_num > 10 : return None
		elif syll_num ==1:
			if self._BABB(string, syll_template):
				ret = []; ret.append(string) ; return ret
			else: return None
		else:
			syll_num -=1
			for i in range(syll_num): # while i > 0:
				span = vloc[i+1] - vloc[i]
				if self.IsVowel(string[vloc[i]+1]): span -=1 # double vowels
				if span <= 1: return None
				else:
					edge = []
					if span > 5: return None
					elif span == 5: edge.append(vloc[i+1]-2) # ABBBBA
					else:
						edge.append(vloc[i+1]-1) # "BA" pattern has priority than "A","BBA"
						if span == 4: edge.append(vloc[i+1]-2)
						elif span <= 3: edge.append(vloc[i+1])
					ret = [] ;
					for k in edge:
						syll = string[:k]
						if self._BABB(syll, syll_template):
							substr = string[k:]
							subret = self.Syll_split(substr,syll_template)
							if subret:
								for sub_syll in subret:
									subsyl = syll + "+" + str(sub_syll)
									ret.append(subsyl)
							#return ret if ret else None
					return ret if ret else None
	# def Syllable()

	# accoustic dictionary general format like HTK format:
	def Adict_format(self, word): # the easy way: word.replace(""," ").strip(" ")
		ret = ""
		for ch in word:
			ret += ch + " "
		return ret.strip(" ")
	#def Adict_format()

# MChar()

# /////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////
class Uyghurchar(Mchar):
	alphabet_len = 33 ; Lang = "Uyghur"; Vowels = "aAeioOuU"
	syll_template = "BA,BA[B][B],BAA[B],BBAB[B]" # first memeber of template must be necessary parts

	def __init__(self):
		Mchar.__init__(self,self.Lang)
	#def __init__()

		# [acronyms, special irregular, combined] word's acoustic dictionary
	def Ir_Acoustics(self, word):
		if not word: return None
		ret = ""
		for h in word.split("-"): # acronym or combined?
			if not h: continue
			if len(h) == 1: # acronym
				insert = "e"
				if self.IsVowel(h) or h == "N": insert = ""
				ret += h + insert
			elif (len(h)==2 and h[0]=="v"):  # acronym
				ret += h
			else:   # combined words
				return word.replace("-","")
		return ret
	# def Spe

	# Amza_process() will check the amza is correctly used
	def Amza_process(self, word):
		lenth = len(word)
		if word == "v" or lenth < 2: return None
		i = 0
		while i < lenth -1:
			if word[i] == "v" and not self.IsVowel(word[i+1]):
				print("word [%s] has possibly spelling mistakes\n" % word)
				return None
			i += 1
		return word
	#def Amza_process()

		# check is a word is an acronym
	def Is_acronym(self, word):
		if len(word) == 1 and self.All_alphs(word): return True # acronym
		ret = 0
		for ch in word.split("-"):
			lenth = len(ch)
			if lenth == 1 and not self.IsVowel(ch): ret += 1
			elif lenth ==2 and ch[0] == "v" and ch[1] in self.Vowels: ret +=1
			elif not ch: continue
			else: return None
		return ret
	#def Is_acronym()

	def Syllables(self, word, single = True):
		if(not word): return None
		if not self.Amza_process(word): return None
		syll_candidates = self.Syll_split(word, self.syll_template)
		if not syll_candidates:
			print("word [%s] cannot be segmented into syllables, possibly spelling mistakes" % word)
			return None
		else: # there are many posible results which can be filtered by other methods;
			if single: return syll_candidates[0] # we cannot guaranty it is the conventional syllables
			else: return syll_candidates
	# def Syllable()

		# produce acoustic dictionary for a word;
	def AcousticDict(self, word, form = True):
		rstr = self.Amza_process(word)
		if not rstr: rstr = word
		rstr1 = self.Ir_Acoustics(rstr)
		if not rstr1: rstr1 = rstr
		return self._Adict_format(rstr1,form)
	# def AcousticDict()

	def _Adict_format(self, word, form):
		ret = ""
		for ch in word:
			if ch == "v": ret += ch
			else: ret += ch + " "
		if form: return ret.rstrip(" ")
		else: return ret.replace(" ", "")

	# def _Adict_format()


	# def AcousticDict()

# class Uyghurchar

# /////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////
class Kazakchar(Mchar):
	alphabet_len = 34; Lang = "Kazak"; Vowels = "eiaEAoOuUI"
	syll_template = "A,BA[B][B],A[B][B],BAA[B],BBAB[B]" # first memeber of template must be necessary parts
	Ir_ADict = {}

	def __init__(self):
		Mchar.__init__(self, self.Lang)
	#def __init__()

	# condition for being a memeber of acronym(for Kazak: lenth ==1),check if it is a legal sub-acronym
	def Is_acronym(self, word):
		if len(word) == 1 and self.All_alphs(word): return True # acronym
		else:
			ret = 0
			for ch in word.split("-"):
				lenth = len(ch)
				if lenth == 1 and self.All_alphs(ch): ret += 1
				elif not ch: continue
				else: return None
			return ret
	#def Is_acronym()

	#  build acoustic dictionary for acronym
	def Acronym_adict(self, word):
		if "-" not in word: return None
		ret = ""; count = 0;
		for h in word.split("-"): # acronym?
			if not h: continue
			elif len(h) == 1: # acronym
				insert = "e"; count +=1
				if self.IsVowel(h) or h == "N": insert = ""
				ret += h + insert
			else: return None # len(ch) > 1: # combined
		if count < 2: return None
		return ret
	#def Is_acronym()

	# combined-words build acoustic dict for combined words by "-" in between
	def Combined_words(self, comword):
		if "-" not in comword: return None
		ret = self.Acronym_adict(comword) # check if it is an acronym
		if ret: return ret
		for w in comword.split("-"): # combined words?
			if not w: continue # sometimes there is an empty ""
			else:
				ad = self.AcousticDict(w) # this returns sth,
				if ad: ret += ad if ret else ad  #if ret: ret += "-" + ad if ret else ad
				else:
					print("something wrong with the word: [%s]\n" %comword)
					return None
		return ret
	# def Combined_words()

	# change vowels in words start with amza "v"
	def Amza_process(self, word):
		if not word:return None
		elif "v" in word[1:]:
			print("there is a spelling mistakes in word:[%s]" %word)
			return False
		elif word[0] != "v" and  not ("k" in word or "g" in word or "E" in word): return False
		rstr = ""
		for ch in word:
			if ch == "a": ch = "A"
			elif ch == "o": ch = "O"
			elif ch == "e": ch = "i"
			elif ch == "u": ch = "U"
			else: pass
			rstr += ch
		return rstr
	# def AmzaVowelReplace()

	# [acronyms, special irregular, combined] word's acoustic dictionary
	def Ir_Acoustics(self, word):
		ret = self.Ir_ADict[word] if word in self.Ir_ADict else ""
		if ret: return ret
		else: ret = self.Combined_words(word)
		return ret
	# def Ir_Acoustics

 # "y" and "w" are semi vowels in Kazak, that must be replaced with vowels "I", "u", only when it is vowel.
	def SemiVowel(self, word):
		semi = list(word); prev = ""
		lenth = len(semi); i =0
		if lenth <2: return None
		while i < lenth:
			ch = word[i]; i += 1
			if i < lenth-1 and (word[i:i+2] =="yw" or word[i:i+2] == "wy"):
				ch = word[i:i+2]; i += 1
				nxt = word[i] if i < lenth else ""
				if not self.IsVowel(prev):
					if not self.IsVowel(nxt):
						semi[i-1] = "I" if semi[i-1] == "y" else "u"
					else:
						semi[i-2] = "I" if semi[i-2] == "y" else "u"
				elif not self.IsVowel(nxt):
					semi[i-1] = "I" if semi[i-1] == "y" else "u"
				prev = nxt; i += 1
			elif ch =="y" or ch =="w":
				nxt = word[i] if i < lenth else ""
				if not self.IsVowel(prev) and not self.IsVowel(nxt):
					semi[i-1] = "I" if semi[i-1] == "y" else "u"
				prev = nxt; i += 1
			else:
				prev = ch

		semi = "".join(semi)
		if not semi or semi == word: return None
		else: return semi
	# def SemiVowel()

		# produce acoustic dictionary for a word;
	def AcousticDict(self, word, form = True):
		if len(word) <=1 : return word
		rstr = self.Ir_Acoustics(word)
		if rstr: return self._Adict_format(rstr,form)

		rstr1 = self.SemiVowel(word)
		if not rstr1: rstr1 = word
		rstr2 = self.Amza_process(rstr1)
		if not rstr2: rstr2 = rstr1

		return self._Adict_format(rstr2, form)
	# def AcousticDict()

	def _Adict_format(self, word, form):
		rstr = word
		if rstr[0] == "v": rstr = rstr[1:]
		if form:
			return rstr.replace("", " ").strip(" ") #self.Adict_format(ret) # add whitespces between each char
		else: return rstr
	# def _Adict_format()

	def Syllables(self, word, single = True):
		if not word or "v" in word[1:]:
			print("word [%s] cannot be segmented into syllables, possibly spelling mistakes" % word)
			return None
		amza = "v" if word[0] == "v" else ""
		sound = self.SemiVowel(word)
		if sound: word = sound
		if amza: word = word[1:]
		syll_candidates = self.Syll_split(word, self.syll_template)
		if not syll_candidates:
			print("word [%s] cannot be segmented into syllables, possibly spelling mistakes" % word)
		else: # there are many posible results which can be filtered by other methods;
			if single: return amza + syll_candidates[0] # all possible candidates are in the list
			else: return syll_candidates
			#return syll_candidates
	# def Syllable()

# class Kazakchar

# ///////////////////////////////////////////////////////////////////
class Kirghizchar(Mchar):
	alphabet_len = 34 ; Lang = "Kirghiz"; Vowels = "eiaEAoOuU"
	syll_template = "A,BA[B][B],A[B][B],BAA[B],BBAB[B]" # first memeber of template must be necessary parts
	Ir_ADict = {}

	def __init__(self):
		Mchar.__init__(self,self.Lang)
	#def __init__()


# class Kizghizchar


# ///////////////////////////////////////////////////////////////////
class Mongolchar(Mchar):
	alphabet_len = 34 ; Lang = "Mongol"; Vowels = "eiaEAoOuU"
	syll_template = "A,BA[B][B],A[B][B],BAA[B],BBAB[B]" # first memeber of template must be necessary parts
	Ir_ADict = {}

	def __init__(self):
		Mchar.__init__(self,self.Lang)
	#def __init__()


# class Mongolchar

# ///////////////////////////////////////////////////////////////////
class Tibetchar(Mchar):
	alphabet_len = 34 ; Lang = "Tibet"; Vowels = "eiaEAoOuU"
	syll_template = "A,BA[B][B],A[B][B],BAA[B],BBAB[B]" # first memeber of template must be necessary parts
	Ir_ADict = {}

	def __init__(self):
		Mchar.__init__(self,self.Lang)
	#def __init__()


# class Tibetchar


# ///////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////
class Mcount():
	charDict = {} ; wordDict = {}
	acronDict = {} ; unkDict= {}
	morph_lable = ["_","-"]

	def __init__(self ,lang=""):
		if lang == "Uyghur": self.charObj = Uyghurchar()
		elif lang == "Kazak": self.charObj = Kazakchar()
		elif lang == "Kighiz": self.charObj = Kirghizchar()
		elif lang == "Mongol": self.charObj = Mongolchar()
		elif lang == "Tibet": self.charObj = Tibetchar()
		else: print("error! please select a language.\n")

		if not self.charObj: print("error0, there is a problem while creating %schar object\n" %lang)
	#def __init__()

		# codetransform will transfrom all unicodes into roman codes
	def Code_transform(self, srfile, trfile, alpha_only = True, mlable = ""):
		if not trfile:
			trfile = srfile + "_roman"
		sfile = self.charObj.open_file(srfile)
		tfile = self.charObj.open_file(trfile, wr="w")
		if not sfile or not tfile: return None
		linecount = 0;
		line = sfile.readline()
		while line:
			linecount += 1;
			tline = self.charObj.Code_flip(line, alpha_only = True, mlable = "")
			tfile.write("%s\n" % tline)
			line = sfile.readline()
		sfile.close; tfile.close()
	# CodeTransfrom()

	# count chars of all kinds,but return the number of alphabet numbers;
	def _char_vocab(self, string):
		ret = 0
		for ch in string:
			if not ch or ch == " " or ch == "\n": continue
			elif  self.charObj.All_alphs(ch): ret +=1
			if ch in self.charDict: self.charDict[ch] +=1
			else:self.charDict[ch] = 1
			if not (ch in self.charObj.romancode or ch in self.charObj.municode):
				if ch in self.unkDict: self.unkDict[ch] += 1
				else: self.unkDict[ch] = 1
		return ret
	# def _char_vocab()

	# count words and acronym words;
	def _acron_word(self, string, both = True):
		ret = 0
		for ch in string.split(","):
			if "-" in ch: # acronym
				if ch in self.acronDict: self.acronDict[ch] +=1
				else:self.acronDict[ch] = 1
				ret += 1
				if both:
					if ch in self.wordDict: self.wordDict[ch] +=1
					else:self.wordDict[ch] = 1
			elif ch:
				if ch in self.wordDict: self.wordDict[ch] +=1
				else:self.wordDict[ch] = 1
				ret += 1
		return ret
	# def _acron_vocab()

	def Spelling(self, word, single = True):
		if not word: return None
		syll = self.charObj.Syllables(word, single)
		if syll: return syll
		else: return None

	# imput a line and export (yield) one word at a time other chars are omitted
	# this is a generator function;
	def Line_process(self , txtline, mlable = morph_lable):
		line = txtline.strip() + "  " # we need last iteration to finish line
		if not line: return None
		word = ""; acronym = ""
		for ch in line:
			if self.charObj.All_alphs(ch) or (ch in mlable):
				 word += ch # we assume that alphabet length is 1 only
			else:
				if self.charObj.Is_acronym(word) : # condition for being an acronym
					acronym = word if not acronym else acronym + "-" + word
					word = ""
				else:
					if acronym: yield acronym; acronym = "" # maybe acron or not
					if word: yield word ; word = ""
			self._char_vocab(ch)
	# Line_process()

	# extract all tokens, vocabs, chars, char vocabs, acronyms also combined with "-"
	def Token_Vocab(self , txfile):
		sfile = self.charObj.open_file(txfile)
		if not sfile: return None
		self.charDict.clear();  self.unkDict.clear(); self.wordDict.clear();self.acronDict.clear()
		linecount = 0; tokencount = 0
		line = sfile.readline()
		while line:
			linecount += 1
			for word in self.Line_process(line):
				tokencount += self._acron_word(word)
			line = sfile.readline()
		sfile.close()
		charvocab = len(self.charDict); wordvocab = len(self.wordDict); acronvocab = len(self.acronDict); unkvocab = len(self.unkDict)
		print("\n statisics of file [%s]: \n" % txfile)
		print("there are %d different chars.\n" % charvocab)
		print("%d different words occured %d times\n" % (wordvocab, tokencount))
		print("there are %d different acronyms.\n" % acronvocab)
		print("there are %d unknown chars.\n" % unkvocab)
	#def TokenVocab()

	# export [word, char, acronym,unk_char,syllable] vocabs to txfile
	def Particle_export(self, trfile , unit = "word", filter_X = 0):
		trfile = trfile + "_" + unit
		unitDict = self.wordDict  # default is word
		if unit == "char": unitDict = self.charDict
		elif unit == "unk_char": unitDict = self.unkDict
		elif unit == "acronym": unitDict = self.acronDict
		elif unit == "word" or unit == "syllable": pass
		else:
			print("the (unit) argument must be one of strings:[word,char,unk_char,acronym,syllable]\n")
			return None
		tfile = self.charObj.open_file(trfile , wr="w")
		if not tfile: return None
		total= len(unitDict) ;count = 0
		for k in sorted(unitDict, key = unitDict.get, reverse = True):
			val = unitDict[k]; line = ""
			if val >= filter_X:
				if unit == "word" or unit == "acronym":
					line = "%s=%d\n" % (k, val); count +=1
				elif unit == "char" or unit == "unk_char":
					line = "%s=%d=%d\n" % (k,ord(k),val);count +=1
				elif unit == "syllable":  # syllable export
					syll = self.charObj.Syllables(k)
					if syll:
						# pass
						line = "%s=%s\n" % (k, syll);count += 1
					else:
						line = "%s=%d; syllable failure\n" % (k,val); count +=1

				if line: tfile.write(line)
		tfile.close()
		print("[%d] units from [%d] units are exported.\n" %(count, total) )
	# def Export_counts()

	# export [pronounce, syllables,or others] as same format of source file
	def File_export(self, srfile, trfile = "", form = "file", filter_X = 0):
		sfile = self.charObj.open_file(srfile)
		if not trfile: trfile = srfile + "_" + form
		tfile = self.charObj.open_file(trfile , wr="w")
		if not sfile or not tfile: return None
		linecount = 0;
		line = sfile.readline();
		while line :
			linecount += 1;  tline = ""
			for w in self.Line_process(line):
				if not w: continue
				word = ""
				if  form == "syllable":
					word = self.charObj.Syllables(w)[0]
				elif form == "form": # this line can be used for various format compilations
					word =  w
				elif form == "adict_file": # this line can be used for various format compilations
					word =  self.charObj.AcousticDict(w, form = False)
				elif form == "adict":
					word =w + "	" +  self.charObj.AcousticDict(w, form = True)
				else:
					print("the (unit) argument must be one of strings:[file,syllable,adict]\n")
				tline += word  if word else w ; tline += " "
			tfile.write("%s\n" % tline.rstrip(" "))
			line = sfile.readline()
		sfile.close; tfile.close()
		print("[%d] lines are processed.\n" %linecount)

# class Mcount()

# ///////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////

def recipe1(mm, mfile): # recipe1 will transform unitcode-file into a roman-code-file
	mm.Code_transform(mfile,"")

# recipe2 will export various particles from roman-text-file
# Token_Vocab() will gather all the particle statistics. then you can export whatever you need.
def recipe2(mm,mfile):
	mm.Token_Vocab(mfile)
	mm.Particle_export(mfile, unit = "word", filter_X = 0)
	mm.Particle_export(mfile, unit = "unk_char")
	mm.Particle_export(mfile, unit = "syllable")
	mm.Particle_export(mfile, unit = "acronym")

def recipe3(mm,mfile):
	mm.File_export(mfile,form = "form" )
	mm.File_export(mfile + "_form",form = "adict_file" )
	mm.File_export(mfile + "_word",form = "adict" )


# recipe4 is segmenting a word into syllables....
def recipe4(mm):
	word = "vavila"
	syll = mm.Spelling(word,single = False)
	print("%s=" %word)
	if not syll:
		print("spelling mistakes found by syllable cheking\n")
		return None
	for sl in syll:
		print("%s; " %sl)
	print("\n")

if __name__ =="__main__":
	mm = Mcount(lang = "Uyghur")
	mfile = "./tmp/uyghur-2k.txt_roman"
	#mfile = "./tmp/kazak-4k.txt"
#	recipe1(mm, mfile)
	#mfile += "_roman"
	recipe2(mm,mfile)
	recipe3(mm,mfile)
	#recipe4(mm)



