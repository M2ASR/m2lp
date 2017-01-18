#!python3.4

class Mchar():
	romancode = {} ; municode = {} ;

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
		codefile = self.open_file(self.Lang + ".code")
		if not codefile: return None
		line = codefile.readline().replace(" ", "")
		while line:
			(roman , codeID, mcod) = ("", "", "")
			try:roman , codeID, mcod = line.strip().split("=")
			except: pass
			if (roman and codeID and mcod):
				if (roman not in self.romancode) and len(roman) == 1:
					self.romancode[roman] = codeID
				else:
					print("error2-2, there are duplicated codes for romancode: [%s]=[%s] \n" % (roman,codeID))
					return None
				ucodes = mcod.split(",")
				for code in ucodes:
					if not code: next
					if code.isdigit(): code = chr(int(code))
					if len(code) > 2: print("error2-2, something wrong wiht code: [%s]=[%s] is" %(code,roman))
					elif code not in self.municode: self.municode[code] = roman
					else:
						print("error2-3, there are duplicated codes for unicode:[%s]=[%s] \n" % (code, roman))
						return None
			line = codefile.readline()
		codefile.close()
		print("total [%d] multi-codes, mapped into [%d] roman codes for [%s] Language\n" % (len(self.municode), len(self.romancode), self.Lang))
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
			if i < strlen -2 and string[i:i+2] in self.municode:
			 # try if there are double to to one code flip
				word += self.municode[string[i:i+2]] # we assume only double alphabets no double puncts
				i +=2
			else:
				ch = string[i]; i +=1
				if ch in self.municode:
					ch = self.municode[ch]
					if self.All_alphs(ch): word += ch
					else:
						if ch != " " and alpha_only: ch = ""
						if word: ret = ret + mlable + word + ch
						else: ret = ret + ch
						word = ""
				else: # assume other languages, but: donot forget whitespace
					if ch != " " and alpha_only: ch = ""
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
					edge = [vloc[i+1] - 1, vloc[i+1]] # "BA" pattern has priority than "A","BBA"
					if span == 4 or span ==5: edge.append(vloc[i+1]-2)
					elif span > 5: return None
					ret = [] ;
					for k in edge:
						syll = string[:k]
						if self._BABB(syll, syll_template):
							substr = string[k:]
							subret = self.Syll_split(substr,syll_template)
							if not subret: return None
							for sub_syll in subret:
								subsyl = syll + "+" + str(sub_syll)
								ret.append(subsyl)
							return ret if ret else None
						else: return None
	# def Syllable()

	# accoustic dictionary general format like HTK format:
	def Adict_format(self, word): # the easy way: word.replace(""," ").strip(" ")
		ret = ""
		for ch in word:
			ret += ch + " "
		return ret.strip(" ")
	#def Adict_format()

# MChar()

# //////////////////////////////////////////////////////
class Mcount():
	charDict = {} ; wordDict = {}
	acronDict = {} ; unkDict= {}
	morph_lable = "_"

	def __init__(self ,lang):
		if lang == "Uyghur": self.charObj = Uyghurchar()
		elif lang == "Kazak": self.charObj = Kazakchar()
		elif lang == "Kighiz": self.charObj = Kirghizchar()

		if not self.charObj: print("error0, there is a problem while creating %schar object\n" %lang)
		#try: self.TokenVocab(srfile)
		#except:print("warning, there is a problem while opening file:[%s]\n" %srfile)
	#def __init__()

	# count chars of all kinds;
	def _char_vocab(self, string):
		for ch in string:
			if not ch or ch == " " or ch == "\n": next
			if ch in self.charDict: self.charDict[ch] +=1
			else:self.charDict[ch] = 1
			if(ch not in self.charObj.romancode and ch not in self.charObj.municode):
				if ch in self.unkDict: self.unkDict[ch] += 1
				else: self.unkDict[ch] = 1
	# def _char_vocab()

		# count words of all kinds;
	def _word_vocab(self, string):
		ret = 0
		for ch in string.strip().split(","):
			if ch:
				if ch in self.wordDict: self.wordDict[ch] +=1
				else:self.wordDict[ch] = 1
				ret += 1
		return ret
	# def _word_vocab()

	def _acron_vocab(self, string):
		ret = 0
		for ch in string.split(","):
			if "-" in ch: # acronym
				if ch in self.acronDict: self.acronDict[ch] +=1
				else:self.acronDict[ch] = 1
			elif ch: self._word_vocab(ch)
			ret += 1
		return ret
	# def _acron_vocab()

	# extract all tokens, vocabs, chars, char vocabs, acronyms also combined with "-"
	def Token_Vocab(self , txfile):
		sfile = self.charObj.open_file(txfile)
		if not sfile: return None
		linecount = 0; charcount = 0; tokencount = 0 ; acronym = ""
		line = sfile.readline()
		while line:
			linecount += 1; word = "";
			for ch in line:
				self._char_vocab(ch); charcount += 1
				if self.charObj.All_alphs(ch): word += ch # we assume that char length is 1 only
				elif word:
					if len(word) == 1 and (word not in self.morph_lable): # condition for being an acronym
						if acronym: acronym = acronym + "-" + word
						else: acronym = word
					else:
						if self._word_vocab(word): tokencount += 1
						if self._acron_vocab(acronym):tokencount += 1;
						acronym = ""
					word = ""
			line = sfile.readline()
		sfile.close()
		charvocab = len(self.charDict); wordvocab = len(self.wordDict); acronvocab = len(self.acronDict); unkvocab = len(self.unkDict)
		print("\n statisics of file [%s]: \n" % txfile)
		print("%s different chars occured %s times\n" % (charvocab, charcount))
		print("%s different words occured %s times\n" % (wordvocab, tokencount))
		print("there are %s acronyms in file\n" % acronvocab)
		print("there are %s unknown chars in file\n" % unkvocab)
	#def TokenVocab()

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

	# export word vocabs to txfile
	def Particle_export(self, trfile, unit = "word", filter_X = 0):
		unitDict = self.wordDict  # default is word
		if unit == "char": unitDict = self.charDict
		elif unit == "unk_char": unitDict = self.unkDict
		elif unit == "acronym": unitDict = self.acronDict
		elif unit == "word" or unit == "syllable" or unit =="adict": pass
		else:
			print("the (unit) argument must be one of strings:[word,char,unk_char,acronym,syllable,adict]\n")
			return None
		tfile = self.charObj.open_file(trfile , wr="w")
		if not tfile: return None
		total= len(unitDict) ;count = 0
		for k in sorted(unitDict, key = unitDict.get, reverse = True):
			val = unitDict[k]
			if val >= filter_X:
				line = "%s=%s\n" % (k, val)
				if unit == "char" or unit == "unk_char":
					line = "%s=%d=%s\n" % (k,ord(k),val)
				elif unit == "syllable":  # syllable export
					syll = self.charObj.Syllables(k)
					if syll:
						line = "%s=%s\n" % (k, syll)
						count += 1
					else: line = "%s=%s\n" % (k, "")
				elif unit == "adict":  # dictionary export
					adict = self.charObj.AcouticDict(k)
					if adict:
						line = "%s    %s\n" % (k, adict)
						count += 1
				tfile.write(line)
		tfile.close()
		print("[%d] units are chosen from [%d] units\n" %(count, total) )
	# def Export_counts()



# class Mcount()

# /////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////
class Uyghurchar(Mchar):
	alphabet_len = 33 ; Lang = "Uyghur"; Vowels = "aAeioOuU"
	syll_template = "BA,BA[B][B],BAA[B],BBAB[B]" # first memeber of template must be necessary parts

	def __init__(self):
		Mchar.__init__(self,self.Lang)
	#def __init__()

		# [acronyms, special irregular, combined] word's acoustic dictionary
	def Ir_Acoutics(self, word):
		if not word: return None
		ret = ""
		for h in word.split("-"): # acronym or combined?
			if not h: next
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
		i = word.find("v")
		while i < lenth-1:
			if not self.IsVowel(word[i+1]):
				print("word [%s] has possibly spelling mistakes\n" % word)
				return None
			i = word.find("v")
		return True
	#def Amza_process()

	def Syllables(self, word):
		if(not word): return None
		if not self.Amza_process(word): return None
		syll_candidates = self.Syll_split(word, self.syll_template)
		if not syll_candidates:
			print("word [%s] cannot be segmented into syllables, possibly spelling mistakes" % word)
		else: # there are many posible results which can be filtered by other methods;
			return syll_candidates[0] # we cannot guaranty it is the conventional syllables
	# def Syllable()

	def AcouticDict(self, word):
		if not self.AmzaProcess(word): return None
		rstr = self.Ir_Acoutics(word)
		if not rstr: rstr = word # this should not happen
		ret = rstr.replace("", " ").strip()
		ret = ret.replace("v ", "v")
		return ret


		# add whitespces between each char
	# def AcouticDict()

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

	# change vowels in words start with amza "v" return 0 if illigal word
	def Amza_process(self, word):
		if  not word or "v" in word[1:]: return False
		elif word[0] != "v":
			if "k" not in word or "g" not in word or "E" not in word:
				return False
		else:
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
	def Ir_Acoutics(self, word):
		ret = self.Ir_ADict[word] if word in self.Ir_ADict else ""
		if ret: return ret
		for h in word.split("-"): # acronym or combined?
			if not h: next
			if len(h) == 1: # acronym
					insert = "e"
					if self.IsVowel(h) or h == "N": insert = ""
					ret += h + insert
			else: # len(ch) > 1: # combined
					combn = self.Ir_ADict[h] if h in self.Ir_ADict else h
					ret += combn
		return ret
	# def Spe

	def SemiVowel(self, word,):
		semi = list(word); prev = ""
		lenth = len(semi); i =0
		if lenth <2: return None
		while i < lenth:
			ch = word[i] ; i += 1
			if ch =="y" or ch =="w":
					if not self.IsVowel(prev):
						nxt = word[i] if i < lenth-1 else ""
						if nxt =="y" or nxt=="w": # special place
								yw = "I" if nxt == "y" else "u"
								semi[i] = yw
						elif not self.IsVowel(nxt):
								yw = "I" if ch == "y" else "u"
								semi[i-1] = yw
						prev = nxt;  i += 1
					else: prev = ch
			else: prev = ch


		semi = "".join(semi)
		if not semi or semi == word: return None
		else: return semi
	# def SemiVowel()

		# produce acoustic dictionary for a word without spell checking;
	def AcouticDict(self, word):
		rstr = self.Ir_Acoutics(word)
		if not rstr: rstr = word # this should not happen
		rstr = self.Amza_process(word)
		if not rstr: rstr = word

		rstr = self.SemiVowel(rstr)
		if not rstr: rstr = word
		if "v" == rstr[0]: rstr = rstr[1:]
		return rstr.replace("", " ").strip(" ") #self.Adict_format(ret) # add whitespces between each char
	# def AcouticDict()

	def Syllables(self, word):
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
			return amza + syll_candidates[0] # we cannot guaranty it is the conventional syllables
	# def Syllable()

# class Kazakchar

# ///////////////////////////////////////////////////////////////////
class Kirghizchar(Mchar):
	alphabet_len = 34 ; Lang = "Kazak"; Vowels = "eiaEAoOuU"
	syll_template = "A,BA[B][B],A[B][B],BAA[B],BBAB[B]" # first memeber of template must be necessary parts
	Ir_ADict = {}

	def __init__(self):
		Mchar.__init__(self,self.Lang)
	#def __init__()


# class Kizghizchar


if __name__ =="__main__":
	mm = Mcount("Kazak")
	#mm.Code_transform("kazaktext-200k.txt","")
	mm.Token_Vocab("kazaktext-200k.txt_roman_word")
	mm.Particle_export("kazaktext-200k.txt_roman_adict", unit = "adict")
	#mm.Export_units("kazaktext-200k.txt_roman_char", unit = "char")
	#mm.Export_units("kazaktext-200k.txt_roman_unk_char", unit = "unk_char")
	#mm.Export_units("kazaktext-200k.txt_roman_acronym", unit = "acronym")
	#ss= mm.charObj.Syllables("vbyazy")
	#print(ss)


