# THE WAY TO RUN THE NEWEST SCRIPT VERSION

#bash command to run it on Linux
#mi=`mktemp` && wget -nv https://raw.github.com/qutorial/mbeddr_python_installer/master/mbeddr_install.py -O $mi && python2.7 $mi; rm $mi;

#bash command to run it on Mac
#mi=`mktemp /tmp/mbeddr_install.py.XXXXX` && curl  https://raw.github.com/qutorial/mbeddr_python_installer/master/mbeddr_install.py -o $mi && python2.7 $mi; rm $mi;

import sys, os, subprocess, urllib2, platform, time, shutil, string
import os.path
from os.path import expanduser
from urllib2 import urlparse
import zipfile, tarfile

#Autocompletion, input
import readline, glob
import rlcompleter

# Checking Python

if sys.version_info < (2, 7):
    print "Your Python version is old. Please, install Python 2.7."
    print "http://www.python.org/download/"
    exit(1);

################### -- CONFIGURATION -- ###################

# MBEDDR CONFIGURATION
MbeddrRepo = """https://github.com/mbeddr/mbeddr.core.git"""
#TheBranch = "fortissStable"
TheBranch = "master"
BuildProperties = """# MPS installation
mps.home=MPSDir
# Folder where MPS stores it's cache
mps.platform.caches=MPSCaches
# Points to the root folder of the mbeddr.core repository
mbeddr.github.core.home=MbeddrDir
"""
def getMbeddrDestDir(dest):
  return os.path.join(dest, "mbeddr.github");

# MPS CONFIGURATION

EAPNum = "30"  
MPSSourceUrl = """http://download-ln.jetbrains.com/mps/31/"""
MPSWin = """MPS-3.1-EAP1-"""+EAPNum+""".exe"""
MPSMac = """MPS-3.1-EAP1-"""+EAPNum+"""-macos.dmg"""
MPSLin = """MPS-3.1-EAP1-"""+EAPNum+""".tar.gz"""
MPSZip = """MPS-3.1-EAP1-"""+EAPNum+""".zip"""
MPSArcDir = """MPS 3.1 EAP"""
MPSVolumesDir = """/Volumes/MPS 3.1 EAP/MPS 3.1 EAP.app"""
MPSDestDirLinux = "MPS31"
MPSDestDirMac = "MPS31.app"

MPSVMOptions="""-client
-Xss1024k
-ea
-Xmx2048m
-XX:MaxPermSize=2048m
-XX:NewSize=512m
-XX:+HeapDumpOnOutOfMemoryError
-Dfile.encoding=UTF-8
-Dapple.awt.graphics.UseQuartz=true
-Didea.paths.selector=MPS30
-Didea.config.path=IdeaConfig
-Didea.system.path=IdeaSystem"""
#-Didea.plugins.path=IdeaPlugins"""

MPSLibraryManager = """<?xml version="1.0" encoding="UTF-8"?>
<application>
  <component name="LibraryManager">
    <option name="libraries">
      <map>
        <entry key="mbeddr.core">
          <value>
            <Library>
              <option name="name" value="mbeddr.core" />
              <option name="path" value="${mbeddr.github.core.home}/code" />
            </Library>
          </value>
        </entry>
      </map>
    </option>
  </component>
</application>"""

MPSPathMacros = """<?xml version="1.0" encoding="UTF-8"?>
<application>
  <component name="PathMacrosImpl">
    <macro name="mbeddr.github.core.home" value="MbeddrDir" />
  </component>
</application>
"""

MPSInfoPlist="""<!DOCTYPE plist PUBLIC '-//Apple Computer//DTD PLIST 1.0//EN' 'http://www.apple.com/DTDs/PropertyList-1.0.dtd'>
<plist version="1.0">
  <!--Generated by MPS-->
  <dict>
    <key>CFBundleName</key>
    <string>MPS</string>
    <key>CFBundleGetInfoString</key>
    <string>JetBrains MPS 3.1 EAP</string>
    <key>CFBundleShortVersionString</key>
    <string>3.1 EAP</string>
    <key>CFBundleVersion</key>
    <string>MPS-133.1407</string>
    <key>CFBundleExecutable</key>
    <string>mps</string>
    <key>CFBundleIconFile</key>
    <string>mps.icns</string>
    <key>CFBundleDevelopmentRegion</key>
    <string>English</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>NSHighResolutionCapable</key>
    <true />
    <key>CFBundleDocumentTypes</key>
    <array>
      <dict>
        <key>CFBundleTypeExtensions</key>
        <array>
          <string>mpr</string>
        </array>
        <key>CFBundleTypeIconFile</key>
        <string>mps.icns</string>
        <key>CFBundleTypeName</key>
        <string>JetBrains MPS Project</string>
        <key>CFBundleTypeRole</key>
        <string>Editor</string>
      </dict>
    </array>
    <key>CFBundleURLTypes</key>
    <array>
      <dict>
        <key>CFBundleTypeRole</key>
        <string>Editor</string>
        <key>CFBundleURLName</key>
        <string>Stacktrace</string>
        <key>CFBundleURLSchemes</key>
        <array />
      </dict>
    </array>
    <key>Java</key>
    <dict>
      <key>ClassPath</key>
      <string>$APP_PACKAGE/lib/branding.jar:$APP_PACKAGE/lib/mps-boot.jar:$APP_PACKAGE/lib/boot.jar:$APP_PACKAGE/lib/bootstrap.jar:$APP_PACKAGE/lib/util.jar:$APP_PACKAGE/lib/jdom.jar:$APP_PACKAGE/lib/log4j.jar:$APP_PACKAGE/lib/extensions.jar:$APP_PACKAGE/lib/trove4j.jar</string>
      <key>JVMVersion</key>
      <string>1.6+</string>
      <key>MainClass</key>
      <string>jetbrains.mps.Launcher</string>
      <key>Properties</key>
      <dict>
        <key>apple.laf.useScreenMenuBar</key>
        <string>true</string>
        <key>com.apple.mrj.application.live-resize</key>
        <string>false</string>         	
        <key>idea.system.path</key>
        <string>IdeaSystem</string>
        <key>idea.config.path</key>
        <string>IdeaConfig</string>
      </dict>
      <key>VMOptions</key>
      <string>-client -Xss1024k -ea -Xmx1100m -XX:MaxPermSize=256m -XX:NewSize=256m -XX:+HeapDumpOnOutOfMemoryError -Dfile.encoding=UTF-8 -Dapple.awt.graphics.UseQuartz=true -Didea.paths.selector=MPS31</string>
      <key>WorkingDirectory</key>
      <string>$APP_PACKAGE/bin</string>
    </dict>
  </dict>
</plist>"""

# CBMC CONFIGURATION
CBMCVersion="""4"""
CBMCSubVersion = """7"""
CBMC32BitLinuxUrl = """http://www.cprover.org/cbmc/download/cbmc-""" + CBMCVersion + "-" + CBMCSubVersion + """-linux-32.tgz"""
CBMC64BitLinuxUrl = """http://www.cprover.org/cbmc/download/cbmc-""" + CBMCVersion + "-" + CBMCSubVersion + """-linux-64.tgz"""
CBMCMacFileName = """cbmc-""" + CBMCVersion + "-" + CBMCSubVersion + """.pkg"""
CBMCMacUrl = """http://www.cprover.org/cbmc/download/""" + CBMCMacFileName;
CBMCInstallDir = "/usr/bin"


# JAVA CONFIGURATION
InstallJavaMessage= """Please, install a Java (R, TM) from Oracle. 
http://www.oracle.com/technetwork/java/javase/downloads/index.html"""

InstallJavaHintUbuntu = """\nOn Ubuntu this might work:
sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update
sudo apt-get install oracle-java7-installer
"""

# ANT CONFIGURATION
InstallAntMessage= """Please, install Apache Ant(TM).\n 

http://ant.apache.org/bindownload.cgi"""

InstallAntHintUbuntu = """\nOn Ubuntu this might work:
sudo apt-get install ant
"""


# GIT CONFIGURATION
InstallGitMessage= """Please, install Git.\n 

http://git-scm.com/downloads"""

InstallGitHintUbuntu = """\nOn Ubuntu this might work:
sudo apt-get install git
"""


# USER GUIDE CONFIGURATION
UserGuideURL = """https://github.com/qutorial/mbeddr_python_installer/blob/master/mbeddr-userguide.pdf?raw=true"""

# README CONFIGURATION
ReadMeURL = """https://github.com/qutorial/mbeddr_python_installer/blob/master/README.txt?raw=true"""



################### END OF CONFIGURATION ###################

# Detecting OS

LINUX32 = "Lin32"
LINUX64 = "Lin64"
MACOS = "Mac"
WINDOWS = "Win"
    
def getOS():
  s = platform.platform()
  if "Lin" in s:
    if platform.architecture()[0] == '64bit':
      return LINUX64
    else:
      return LINUX32;
  if "Darwin" in s:
    return MACOS
  if "Win" in s:
    return WINDOWS

def onLinux32():
  return LINUX32 == getOS();
    
def onLinux64():
  return LINUX64 == getOS();

def onLinux():
  return onLinux32() or onLinux64();
  
def onMac():
  return MACOS == getOS();

def onWindows():
  return WINDOWS == getOS();
    

def TEST_getOS():
  if onLinux() and not onMac() and not onWindows():
    return True;
  if not onLinux() and onMac() and not onWindows():
    return True;
  if not onLinux() and not onMac() and onWindows():
    return True;
  return False;

    
# Downloading file with progress

def getFileNameFromUrl(url):
  parsed = urlparse.urlsplit(url);
  path = parsed.path;
  return os.path.basename(path);

def TEST_getFileNameFromUrl():
  return getFileNameFromUrl(UserGuideURL) == "mbeddr-userguide.pdf"
  
def downloadFile(url, destdir):
  file_name = getFileNameFromUrl(url);
  u = urllib2.urlopen(url)
  resName = os.path.join(destdir, file_name)
  f = open(resName, 'wb')
  meta = u.info()
  file_size = int(meta.getheaders("Content-Length")[0])
  print "Downloading: %s Bytes: %s" % (file_name, file_size)

  file_size_dl = 0
  block_sz = 8192
  while True:
      buffer = u.read(block_sz)
      if not buffer:
	  break

      file_size_dl += len(buffer)
      f.write(buffer)
      status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
      status = status + chr(8)*(len(status)+1)
      print status,

  f.close()
  
  print "\n"
  
  return resName
  
  
# Autocomplete file names
def completeSimple(text, state):
    res = glob.glob(text+"*")+[None];
    return (res)[state];

def completeDirAware(text, state):
    res = completeSimple(text, state);
    
    if os.path.exists(res):
      if os.path.isdir(res):
	if not res.endswith(os.sep):
	  res = res + os.sep;
	  
    return res


def readFileName(promptMessage):
  if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
    complete = completeSimple
  else:
    readline.parse_and_bind("tab: complete")
    complete = completeDirAware

  readline.set_completer_delims(' \t\n;')
  readline.set_completer(complete)  
  return raw_input(promptMessage).strip()


def TEST_INTERACTIVE_readFileName():
  s = readFileName("File: ")
  print "Result: ", s
  
# Unarchiving Zips and Tars

def unzip(zipzip, dest):
  zfile = zipfile.ZipFile(zipzip)
  for name in zfile.namelist():
    (dirname, filename) = os.path.split(name)
    print "Decompressing " + filename + " on " + dirname
    if not os.path.exists(dirname):
      os.makedirs(dirname)
    zfile.extract(name, os.path.join(dest,dirname))

def untgz(arc, dest):
  tfile = tarfile.open(arc, 'r:gz');
  tfile.extractall(dest);
  
def unarchive(a, dest):
  if "zip" in a:
    unzip(a, dest);
  else:
    untgz(a, dest);

    
# GIT 

def checkGitVersion(git):
  if "git version" in git:
    return True;
  else:
    return "Unrecognized git version\n"    
   
def checkGit():  
  try:
    git = subprocess.check_output(["git", "--version"], stderr=subprocess.STDOUT)
    return checkGitVersion(git)
  except OSError:
    return InstallGitMessage;

def TEST_checkGit():
  return checkGit() == True or checkGit() == InstallGitMessage;
    
# JAVA 

def checkJavaVersion(java):
  vals = java.split() 
  a = [s for s in vals if "1.6" in s]
  b = [s for s in vals if "1.7" in s]
  c = [s for s in vals if "HotSpot" in s]
  if len(c) > 0:
    if len(a) + len(b) > 0:
      return True;
  answer = "Java version is not recognized\n"+InstallJavaMessage;
  if onLinux():
    answer = answer + InstallJavaHintUbuntu;
    
  return answer;
  
  
def checkJava():  
  try:
    java = subprocess.check_output(["java", "-version"], stderr=subprocess.STDOUT)
    return checkJavaVersion(java)
  except OSError:
    return InstallJavaMessage;

def TEST_checkJava():
  s = checkJava();
  return s == True or InstallJavaMessage in s;
  
# ANT
    
def checkAntVersion(ant):
  if "Apache Ant" in ant:
    return True;
  
  answer = "Unrecognized ant version\n"
  if onLinux():
    answer = answer + InstallAntHintUbuntu;
    
  return answer;
  
def checkAnt():
  try:
    ant = subprocess.check_output(["ant", "-version"], stderr=subprocess.STDOUT)
    return checkAntVersion(ant)
  except OSError:
    return InstallAntMessage;

def TEST_checkAnt():
  s =  checkAnt();
  return s == True or InstallAntHintUbuntu in s;
  
# Preparing a destination directory
    
def prepareDestDir(complainExists = True):
  home = os.path.join(expanduser("~"), "mbeddr")
  try:
    destdir = readFileName("Where would you like to install it["+home+"]: ")
  except EOFError:
    destdir = None
  
  if (destdir is None) or (len(destdir) == 0):    
    destdir = home;
 
  print("Selecting: " + destdir)
  
  try:    
    if os.path.exists(destdir):
      if complainExists == True:
	print "This directory already exists, please, use another one."
	return False;
    else:
      os.makedirs(destdir)
  except OSError:
    return False;
    
  return destdir;
  
  
# ------------------ INSTALLING CBMC ------------------

class CBMCInstallerBase:
  
  def getCBMCVersion(self):
    return CBMCVersion + "." + CBMCSubVersion
    
  def checkCBMCVersion(self, cbmc):
    if self.getCBMCVersion() in cbmc:
      return True;
    else:
      return "Unrecognized CBMC C Prover version\n"
       
  def checkCBMC(self):
    try:
      cbmc = subprocess.check_output(["cbmc", "--version"], stderr=subprocess.STDOUT)
      return self.checkCBMCVersion(cbmc)
    except OSError:
      return "No CBMC C Prover installed\n"

  def getCBMCIntro(self):
    return "mbeddr verification heavily relies on CBMC C Prover, which is copyrighted:\n"
   
  def getOnlyCBMCCopyright(self): 
    return """(C) 2001-2008, Daniel Kroening, ETH Zurich,\nEdmund Clarke, Computer Science Department, Carnegie Mellon University\n"""

  def getCBMCCopyright(self): 
    return self.getCBMCIntro() + self.getOnlyCBMCCopyright();
  
  def getCBMCFallbackLicense(self):
    return """(C) 2001-2008, Daniel Kroening, ETH Zurich,
Edmund Clarke, Computer Science Department, Carnegie Mellon University

All rights reserved. Redistribution and use in source and binary forms, with
or without modification, are permitted provided that the following
conditions are met:

  1. Redistributions of source code must retain the above copyright
     notice, this list of conditions and the following disclaimer.

  2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.

  3. All advertising materials mentioning features or use of this software
     must display the following acknowledgement:

     This product includes software developed by Daniel Kroening,
     ETH Zurich and Edmund Clarke, Computer Science Department,
     Carnegie Mellon University.

  4. Neither the name of the University nor the names of its contributors
     may be used to endorse or promote products derived from this software
     without specific prior written permission.

   
THIS SOFTWARE IS PROVIDED BY THE UNIVERSITIES AND CONTRIBUTORS `AS IS'' AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
DAMAGE.\n"""

  def getCBMCLicense(self):
    try:
      return urllib2.urlopen("http://www.cprover.org/cbmc/LICENSE").read();
    except urllib2.HTTPError, e:
      return self.getCBMCFallbackLicense()
    except urllib2.URLError, e:
      return self.getCBMCFallbackLicense()
    except httplib.HTTPException, e:
      return self.getCBMCFallbackLicense()
    except Exception:
      return self.getCBMCFallbackLicense()
    
  
  def installCBMC(self, dest):
    print self.getCBMCLicense();
    print self.getCBMCIntro();
    print "Above is the CBMC license, do you accept it [y/n]?"
    accept = str(raw_input()).strip();
    if "y" != accept:
      return False;
    
    dest = os.path.join(dest, "cbmc");
    if not os.path.exists(dest):
      os.makedirs(dest);
    
    fName = self.downloadCBMC(dest);
    if fName == False:
      return False;
        
    if self.setUpCBMC(dest, fName) != True:
      return False;    
    return True;
      
  def downloadCBMC(self, dest):
    print "Not implemented in CBMC Installer Base"
    return False
        
    
class CBMCInstallerForLinux(CBMCInstallerBase):
  def downloadCBMC(self, dest):
    fName = False
    url=""    
    if onLinux32():
      url = CBMC32BitLinuxUrl;
    if onLinux64:
      url = CBMC64BitLinuxUrl;    
    print "Downloading CBMC: " + url;
    try:
      fName = downloadFile(url, dest);
    except Exception:      
      return False;      
    return fName;
    
  def getCBMCInstallPath(self):  
    return "/usr/bin/cbmc";  
    
  def setUpCBMC(self, dest, fname):
    unarchive(fname, dest);
    print "\nTo finish the CBMC installation, you might be asked for the root/administrator password.\n"
    print "Password: "
    proc = subprocess.Popen(["sudo","-p", "", "ln", "-s", "--force", os.path.join(dest, "cbmc"), self.getCBMCInstallPath()], stdin=subprocess.PIPE)
    proc.wait()
    print "Finished installing"
    return True;
    
class CBMCInstallerForMac(CBMCInstallerBase):
  def downloadCBMC(self, dest):
    fName = False
    url = CBMCMacUrl;
    print "Downloading CBMC: " + url;
    try:
      fName = downloadFile(url, dest);
    except Exception:      
      return False;      
    return fName;
    
  def setUpCBMC(self, dest, fname):
    print "\nPlease, proceed installing CBMC..."
    proc = subprocess.Popen(["open", fname], stdin=subprocess.PIPE)    
    print "Continuing installation...\n"
    return True;

def getCBMCInstaller():
  if onLinux():
    return CBMCInstallerForLinux();
  if onMac():
    return CBMCInstallerForMac();
  return None;

def TEST_getCBMCInstaller():
  installer = getCBMCInstaller();
  return "Mellon" in installer.getCBMCLicense()
  
def TEST_checkCBMC():
  installer = getCBMCInstaller();
  s = installer.checkCBMC();
  return s == True or "CBMC" in s;
    
def installCBMC(dest):
  print "Detecting CBMC"
  cbmcInstaller = getCBMCInstaller();
  if cbmcInstaller == None:
    print "Problem configurring CBMC, analyses might not work!"
  else:    
    j = cbmcInstaller.checkCBMC()
    if j != True:
      print j
      if cbmcInstaller.installCBMC(dest) != True:
	print "Failed to install CBMC!\n"
	exit(1);
      else:
	print "CBMC installed!\n"
    else:
      print """You have CBMC already installed."""
      print cbmcInstaller.getCBMCCopyright();
    
    
def TEST_INTERACTIVE_installCBMC():
  dest = prepareDestDir();
  print "Testing CBMC installer";
  installCBMC(dest);
  
# ------------------ END INSTALLING CBMC ------------------
    

    
    
# ------------------ INSTALLING MPS ------------------


def getMPSFileName():
  if onLinux():
    return MPSLin
  if onMac():
    return MPSMac
  if onWindows():
    return MPSWin
  return "";

def getMPSUrl():
  return MPSSourceUrl + getMPSFileName();
  
def TEST_getMPSUrl():
  return getMPSFileName() in getFileNameFromUrl(getMPSUrl());
  
def downloadMPSOSDep(dest):
  url = getMPSUrl();
  fName = os.path.join(dest, getMPSFileName());  
  if os.path.exists(fName):
    print "\nAn archive with MPS has already been downloaded to: " + fName + "\nDelete it manually, if the installation fails to use it!"
    return fName;
  else:
    return downloadFile(url, dest);



class MPSInstallerBase:
  archive = None
  mpsPath = None
  def downloadMPS(self, dest):
    self.archive = downloadMPSOSDep(dest);
    return self.archive;
    
  def setUpMPSHook(self, dest):
    print "Not implemented for this platform in MPSInstallerBase"
    return None   
    
  def setUpMPS(self, dest):
    self.setUpMPSHook(dest); 
    self.removeArchive();
    
  def getMPSPath(self):
    return self.mpsPath;
    
  def getMPSEndPath(self, dest):
    print "Not implemented for this platform in MPSInstallerBase";
    return None
  
  def removeArchive(self):
    print "Deleting downloaded MPS archive"
    os.remove(self.archive);  
    
    
class MPSInstallerForLinux(MPSInstallerBase):    
  def getMPSEndPath(self, dest):
    return os.path.join(dest, MPSDestDirLinux);
    
  def setUpMPSHook(self, dest):
    MPSDir = self.getMPSEndPath(dest);
    if os.path.exists(MPSDir):
      print "Can not install MPS, the folder " + MPSDir + " already exists, please delete it first or specify a new one."
      return False;    
    print "Extracting..."
    unarchive(self.archive, dest);        
    print "Renaming MPS folder"    
    os.rename(os.path.join(dest, MPSArcDir), MPSDir)
    self.mpsPath = MPSDir;

def ejectImageMac(imagePath):
  lines = os.popen("hdiutil info").readlines()
  shouldEject = False;
  for line in lines:
    if line.startswith("image-path"):
      shouldEject = False;
      path = line.split(":")[1].lstrip().rstrip()
      if path == imagePath:
	shouldEject = True;
    elif line.startswith("/dev/") and shouldEject is True:
      os.popen("hdiutil eject %s" % line.split()[0])
      shouldEject = False;
    elif line.startswith("###"):
      shouldEject = False;
      
   
class MPSInstallerForMac(MPSInstallerBase):
  def getMPSEndPath(self, dest):
    return os.path.join(dest, MPSDestDirMac);
  
  def setUpMPSHook(self, dest):    
    proc = subprocess.Popen(["hdiutil", "attach", "-quiet", self.archive], stdin=subprocess.PIPE)
    proc.wait();
    if not os.path.exists(MPSVolumesDir):
      print "Waiting for the image to mount..."
      time.sleep(5);
      if not os.path.exists(MPSVolumesDir):
	print "Image not mounted, installation fails!"
	exit(1);	      
    
    
    self.mpsPath = self.getMPSEndPath(dest);
    print "Copying MPS...";
    print "Please, do not eject the MPS drive..."
    shutil.copytree(MPSVolumesDir, self.mpsPath);
    print "Ready!"
    print "Ejecting the MPS image now..."    
    ejectImageMac(self.archive);
    
  
def getMPSInstaller():
  if onLinux():
    return MPSInstallerForLinux();
  if onMac():
    return MPSInstallerForMac();
  return None;

def TEST_getMPSInstaller():
  installer = getMPSInstaller();
  return "MPS" in installer.getMPSEndPath("");
    
def TEST_INTERACTIVE_INSTALL_MPS():
  dest = prepareDestDir();
  print "Testing MPS installer";
  installer = getMPSInstaller();
  installer.downloadMPS(dest);  
  installer.setUpMPS(dest);
  print "MPS Installed to: " + installer.getMPSPath();
  
     
# ------------------ END INSTALLING MPS ------------------


# ------------------ CONFIGURING MPS WITH MBEDDR ------------------


# MAC PART
def replaceConfigAndSystemPaths(template, ConfigPath, SysPath):
  opts = template;
  opts = opts.replace("IdeaConfig", ConfigPath);
  opts = opts.replace("IdeaSystem", SysPath);
  return opts;

def getFileNameToWriteInfoPlistTo(MPSDir):
  return os.path.join(MPSDir, "Contents", "Info.plist");
    
def getTemplateForMPSInfoPlist():
  return MPSInfoPlist;


def rewriteFile(path, content):
  f = open( path , 'w');    
  f.write(content);
  f.close();  
  
def configureInfoPlist(MPSDir, ConfigPath, SysPath):
  infoPlistPath = getFileNameToWriteInfoPlistTo(MPSDir);
  infoPlistContent = replaceConfigAndSystemPaths(getTemplateForMPSInfoPlist(), ConfigPath, SysPath);
  rewriteFile(infoPlistPath, infoPlistContent);

# END OF MAC PART

def getFileNameToWritePropertiesTo(MPSDir):
  return os.path.join(MPSDir, "bin", "mps.vmoptions");
    
def getTemplateForMPSProperties():
  return MPSVMOptions;
  
def writeMPSProperties (MPSDir, ConfigPath, SysPath):
# print "Write mps props is called with mpsdir ", MPSDir, " and  ConfigPath ", ConfigPath, " and SysPath ", SysPath;
  optsPath = getFileNameToWritePropertiesTo(MPSDir)	
  optsContent = replaceConfigAndSystemPaths(getTemplateForMPSProperties(), ConfigPath, SysPath);
  rewriteFile(optsPath, optsContent);
  
  
def configureMPSWithMbeddr(MPSDir, MbeddrDir):
#  print "configure is called with MPS dir ", MPSDir, " and MbeddrDir ", MbeddrDir;
  ConfigPath = os.path.join(MPSDir, "IdeaConfig");
  if not os.path.exists(ConfigPath):
    os.makedirs(ConfigPath);
      
  SysPath = os.path.join(MPSDir, "IdeaSystem");    
  if not os.path.exists(SysPath):
    os.makedirs(SysPath);
  
  OptionsPath = os.path.join(ConfigPath, "options");
  if not os.path.exists(OptionsPath):
    os.makedirs(OptionsPath);
  
  rewriteFile(os.path.join(OptionsPath, "libraryManager.xml"), MPSLibraryManager);
  
  rewriteFile(os.path.join(OptionsPath, "path.macros.xml"), MPSPathMacros.replace("MbeddrDir", MbeddrDir));
  
  writeMPSProperties(MPSDir, ConfigPath, SysPath);
  
  if onMac():
    configureInfoPlist(MPSDir, ConfigPath, SysPath);
    
def testConfigureMPSWithMbeddr():
  dest = prepareDestDir(False);
  MbeddrDir = getMbeddrDestDir(dest);
  mpsInstaller = getMPSInstaller();
  MPSDir = mpsInstaller.getMPSEndPath(dest);  
  configureMPSWithMbeddr(MPSDir, MbeddrDir);
 
# ------------------ END CONFIGURING MPS WITH MBEDDR ------------------

    
def cloneMbeddr(dest, MbeddrDir):
  if not os.path.exists(MbeddrDir):
      os.makedirs(MbeddrDir);
  os.chdir(MbeddrDir);
  os.system("git clone " + MbeddrRepo+ " .");
  print "Checking out " + TheBranch + " branch..."  
  os.system("git --git-dir="+ os.path.join(MbeddrDir, ".git") + " reset --hard");
  os.system("git --git-dir="+ os.path.join(MbeddrDir, ".git") + " checkout " + TheBranch);
    
  

def configureMbeddr(MPSDir, MbeddrDir):
  BuildPropsPath = os.path.join(MbeddrDir, "code", "languages", "build.properties");
  f = open(BuildPropsPath, 'w');
  f.write(BuildProperties.replace("MPSDir", MPSDir).replace("MPSCaches", os.path.join(MPSDir, "CachesMbeddr")).replace(
 "MbeddrDir", MbeddrDir));
  f.close();

def buildMbeddr(MbeddrDir):
  BuildPath = os.path.join(MbeddrDir, "code", "languages");
  os.chdir(BuildPath);
  os.system(os.path.join(BuildPath, "buildLanguages.sh"));
  
  
# ---------- DOWNLOADING USER GUIDE ------------

def downloadTheUserGuide(dest):
  downloadFile(UserGuideURL, dest);

# ---------- END OF : DOWNLOADING USER GUIDE ------------



# ---------- DOWNLOADING README ------------

def downloadTheReadMe(dest):
  downloadFile(ReadMeURL, dest);

# ---------- END OF : DOWNLOADING README ------------


  
# ---------- FINAL GREETINGS ------------
  
  
def greetingsLinux(MPSDir, MbeddrDir, dest):
  print """\nTo start working: Run\n"""+os.path.join(MPSDir, "mps.sh")+"""\nand go through the tutorial project from:"""

def greetingsMac(MPSDir, MbeddrDir, dest):
  print "\nTo start working: Run MPS (located in " + dest + ") and go through the tutorial project from:"


def greetings(MPSDir, MbeddrDir, dest):
  if onLinux():
    greetingsLinux(MPSDir, MbeddrDir, dest);
  if onMac():
    greetingsMac(MPSDir, MbeddrDir, dest);
  
  print os.path.join(MbeddrDir, "code", "application"),""" folder.\n"""  
  print """\nVisit mbeddr.com to learn what's new!\n"""  
  print """ * A user guide PDF has been downloaded to the destination folder!"""
  print """ * See the README.txt file for the further instructions and basic troubleshooting.""" 
  
  print "\nWelcome to mbeddr. C the difference C the future.\n";
  print "-----------------------------------------------------------\n"
  print """This installer for mbeddr advanced users has been built by molotnikov (at) fortiss (dot) org.\n
Please, let me know, if it does not work for you!"""

  
# ---------- END OF :  FINAL GREETINGS ------------

  
def main():  
  print("Welcome!")
  print("You are about to install the last stable version of mbeddr.")

  print "Detecting Git"  
  j = checkGit()
  if j != True:
    print j;
    return 1; 
  
  print "Detecting Java"  
  j = checkJava()
  if j != True:
    print j;
    return 1;  
  
  print "Detecting Ant"
  j = checkAnt()
  if j != True:
    print j;
    return 1;  
  
  print "Preparing destination directory";  
  dest = prepareDestDir();
  if dest == False:
    print "Problem creating destination directory";
    return 1;
  
  
  
  #Installing CBMC
  installCBMC(dest);
    
  
  
  #Installing MPS
  mpsInstaller = getMPSInstaller();
  mpsInstaller.downloadMPS(dest);  
  mpsInstaller.setUpMPS(dest);
  MPSDir = mpsInstaller.getMPSPath();
  
    
  MbeddrDir = getMbeddrDestDir(dest);
  if os.path.exists(MbeddrDir):
    print "Can not install mbeddr, the folder " + MbeddrDir + " already exists, please delete it first or specify a new one.\n"
    print "Don't forget to save your changes if made to mbeddr!"
    exit(1);
    
  print "Cloning mbeddr..."
  cloneMbeddr(dest, MbeddrDir);
  
  print "Setting up MPS to work with mbeddr..."
  configureMPSWithMbeddr(MPSDir, MbeddrDir);
  
  print "Setting up mbeddr..."
  configureMbeddr(MPSDir, MbeddrDir);
  
  print "Building mbeddr..."
  buildMbeddr(MbeddrDir);
  
  print "Downloading the user guide..."
  downloadTheUserGuide(dest);
  
  print "Downloading the README.txt..."
  downloadTheReadMe(dest);
  
  
  greetings(MPSDir, MbeddrDir, dest);


def RUN_TESTS():
  print "URL Parsing: ", TEST_getFileNameFromUrl();
  print "OS Detection: ", TEST_getOS();
  print "Git Detection: ", TEST_checkGit();
  print "Java Detection: ", TEST_checkJava();
  print "Ant Detection: ", TEST_checkAnt();
  print "CBMC Installer Init: ", TEST_getCBMCInstaller();
  print "CBMC Detection: ", TEST_checkCBMC();
  print "MPS URL: ", TEST_getMPSUrl();
  print "MPS Installer Init: ", TEST_getMPSInstaller();
  
#RUN_TESTS();
#exit(1);
  
main();