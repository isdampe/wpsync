import os, sys, hashlib, json

class WpSync:

	def __init__(self, mode, wpBaseDir):
		self.mode = mode.lower()
		self.baseDir = wpBaseDir
		self.configBaseFp = os.path.expanduser("~/.wpsync")

		sha = hashlib.sha1()
		sha.update(self.baseDir.encode("utf-8"))
		self.sha = str(sha.hexdigest())[:8]

		self.config = {
			"baseDir": wpBaseDir,
			"baseUrl": "",
			"baseDb": "",
			"destDir": "",
			"destUrl": "",
			"destDb": "",
			"destServer": ""
		}

		if not mode in ["pull", "push"]:
			print("Fatal: Unknown mode %s" % mode)
			self.fatalUsage()

		if not self._wpExists():
			print("Fatal: wp-config.php could not be found in %s" % wpBaseDir)
			self.fatalUsage()

		self._autoConfigure()

	def fatalUsage(self):
		print("Usage: wpsync [mode] [path-to-wordpress]")
		print("mode: [pull | push]")
		sys.exit(1)

	def _wpExists(self):
		return os.path.isfile(("%s/wp-config.php") % (self.config["baseDir"]))

	def _autoConfigure(self):
		if not os.path.isfile("%s/%s" % (self.configBaseFp, self.sha)):
			self.manualConfig()
		else:
			if not self._loadConfigCache():
				self.manualConfig()
			else:
				if not self.confirmConfig():
					self.manualConfig()

	def _getFilledInput(self, prompt):
		buffer = ""
		while buffer == "":
			buffer = input(prompt + ": ")

		return buffer


	def manualConfig(self):
		self.config["baseUrl"] = self._getFilledInput("What is the current WordPress base url?")
		self.config["baseDb"] = self._getFilledInput("What is the current WordPress database name?")
		self.config["destDir"] = self._getFilledInput("What is the destination path for WordPress?")
		self.config["destUrl"] = self._getFilledInput("What is the destination WordPress base url?")
		self.config["destDb"] = self._getFilledInput("What is the destination WordPress database name?")
		self.config["destServer"] = self._getFilledInput("What is the destination server hostname?")
		if not self.confirmConfig():
			return self.manualConfig()

		self._writeConfigCache()

	def _loadConfigCache(self):
		r = ""
		with open("%s/%s" % (self.configBaseFp, self.sha)) as fh:
			r = fh.read()
			fh.close()

		if r == "":
			return False

		j = json.loads(r)
		if not j:
			return False

		self.config = j
		return True

	def _writeConfigCache(self):
		if not os.path.isdir(self.configBaseFp):
			os.mkdir(self.configBaseFp, 0o700)

		p = "%s/%s" % (self.configBaseFp, self.sha)
		with open(p, "w") as fh:
			fh.write(json.dumps(self.config))
			os.chmod(p, 0o600)
			fh.close()

	def confirmConfig(self):
		print("\n-- Configuration --")
		print("Base directory: %s" % self.config["baseDir"])
		print("Base WP URL: %s" % self.config["baseUrl"])
		print("Base database: %s" % self.config["baseDb"])
		print("Dest directory: %s" % self.config["destDir"])
		print("Dest WP URL: %s" % self.config["destUrl"])
		print("Dest database: %s" % self.config["destDb"])
		print("Dest server: %s" % self.config["destServer"])
		print("\n")
		ans = self._getFilledInput("Is this okay (Y/N)?").lower()
		if (ans == "y" or ans == "yes"):
			return True
		return False


if __name__ == "__main__":
	if (len(sys.argv) < 2):
		WpSync.fatalUsage(False)

	baseFp = os.path.dirname(os.path.realpath(__file__))
	if len(sys.argv) >= 3:
		baseFp = sys.argv[2]

	s = WpSync(sys.argv[1], baseFp)
