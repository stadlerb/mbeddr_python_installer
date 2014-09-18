#!python3
# THE WAY TO RUN THE NEWEST SCRIPT VERSION

#bash command to run it on Linux
#mi=`mktemp` && wget -nv https://raw.github.com/qutorial/mbeddr_python_installer/master/mbeddr_install.py -O $mi && python2.7 $mi; rm $mi;

#bash command to run it on Mac
#mi=`mktemp /tmp/mbeddr_install.py.XXXXX` && curl  https://raw.github.com/qutorial/mbeddr_python_installer/master/mbeddr_install.py -o $mi && python2.7 $mi; rm $mi;

import sys, os, subprocess, platform, time, shutil, string, traceback
import os.path
from os.path import expanduser
import errno

from urllib.request import urlopen
from urllib.request import urlretrieve
from urllib.parse import urlparse

import zipfile, tarfile

#Autocompletion, input
import readline, glob


log = print;

DEBUG = False

class ShutDownSilently(Exception):
  pass
  
  
def debug(strr):
  if DEBUG:
    strs = [s.strip() for s in strr.splitlines()]
    for s in strs:
      print("D: " + s);

# Checking Python

if sys.version_info < (3, 0):
    log ( "Your Python version is not supported. Please, install Python 2.7." );
    log ( "http://www.python.org/download/" );
    exit(1);
    

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

################### -- CONFIGURATION -- ###################

# MBEDDR CONFIGURATION
MbeddrRepo = """https://github.com/mbeddr/mbeddr.core.git"""
#TheBranch = "fortiss_stable"
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

JAVA_XMX="-Xmx2048m"

MPSMac = """https://raw.githubusercontent.com/mbeddr/mbeddr.core/"""+TheBranch+"""/versions/MPSMac.txt"""
MPSLin = """https://raw.githubusercontent.com/mbeddr/mbeddr.core/"""+TheBranch+"""/versions/MPSLin.txt"""
MPSWin = """https://raw.githubusercontent.com/mbeddr/mbeddr.core/"""+TheBranch+"""/versions/MPSWin.txt"""

MPSArcDir="MPS" #This is just a part of the unarchived folder name

MPSDestDirLinux = "MPS31"

MPSDestDirWin = MPSDestDirLinux


MPSDestDirWinDefault = """/cygdrive/c/Program Files (x86)/JetBrains/MPS 3.1"""
WindowsUsualJavaLocation = """/cygdrive/c/Program Files/Java/jdk1.7.0_65"""
WindowsUsualAntLocation = """/cygdrive/c/apache-ant-1.9.4"""
CygwinDocsAndSettings = """/cygdrive/c/Documents and Settings/"""
WindowsMPSDesktopLinkName = """JetBrains MPS 3.1.lnk""";
WindowsMbeddrDesktopLinkName = """mbeddr.lnk""";
MPSBatName = """mps.bat"""

MPSVolumesDir = """/Volumes/""" #MPSVolumesDir = """/Volumes/MPS 3.1/MPS 3.1.app"""
MPSDestDirMac = "MPS31.app"

MPS_VM_OPTIONS = """-client                                                                                                                              
-Xss1024k                                                                                                                            
-ea                                                                                                                                  
""" + JAVA_XMX + """                                                                                                                            
-XX:MaxPermSize=256m                                                                                                                 
-XX:NewSize=256m                                                                                                                     
-XX:+HeapDumpOnOutOfMemoryError                                                                                                      
-Xverify:none                                                                                                                        
-Dfile.encoding=UTF-8                                                                                                                
-Dapple.awt.graphics.UseQuartz=true                                                                                                  
-Didea.paths.selector=MPS31
"""

def getMPSVmoptions():
  global MPS_VM_OPTIONS;
  return MPS_VM_OPTIONS;
  
def TEST_getMPSVmoptions():  
  global JAVA_XMX  
  if not "m" in JAVA_XMX:
    return False;
  if not JAVA_XMX in getMPSVmoptions():
    return False;
  return True;

MPS_BAT_WITH_ENV = r"""@echo off

:: JetBrains MPS startup script
:: Generated by MPS

set PATH=CYGWINBIN;CBMCBIN;%PATH%

set PROJECT_HOME=%~dp0

:: we try JDK_HOME, JAVA_HOME, PROJECT_HOME\jre in that specific order
IF EXIST "%JDK_HOME%" set JDK=%JDK_HOME%
IF NOT "%JDK%" == "" GOTO jdk
IF EXIST "%JAVA_HOME%" set JDK=%JAVA_HOME%
IF NOT "%JDK%" == "" GOTO jdk
IF EXIST "%PROJECT_HOME%jre" set JDK=%PROJECT_HOME%jre
IF NOT "%JDK%" == "" GOTO jdk

:jdk
IF EXIST "%JDK%" set JAVA=%JDK%\bin\java.exe
IF NOT EXIST "%JAVA%" set JAVA=%JDK%\jre\bin\java.exe
IF NOT EXIST "%JAVA%" set JAVA=java.exe

set MAIN_CLASS=jetbrains.mps.Launcher

IF NOT "%MPS_VM_OPTIONS%" == "" GOTO options
SET MPS_VM_OPTIONS=%PROJECT_HOME%bin\mps.exe.vmoptions
:: test 64bit support
SET JRE=%JDK%
IF EXIST "%JRE%\jre" SET JRE=%JDK%\jre
IF NOT EXIST "%JRE%\lib\amd64" GOTO options
SET MPS_VM_OPTIONS=%PROJECT_HOME%bin\mps64.exe.vmoptions
:options

set ACC=
FOR /F "delims=" %%i in ('TYPE "%MPS_VM_OPTIONS%"') DO call :parse_vmoptions "%%i"
set JVM_ARGS=%ACC%
:: 32 bit
::set ADDITIONAL_JVM_ARGS=-Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=5005
:: 64 bit
::set ADDITIONAL_JVM_ARGS=-Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=5005

set CLASSPATH=%PROJECT_HOME%lib\branding.jar
set CLASSPATH=%CLASSPATH%;%PROJECT_HOME%lib\mps-boot.jar
set CLASSPATH=%CLASSPATH%;%PROJECT_HOME%lib\boot.jar
set CLASSPATH=%CLASSPATH%;%PROJECT_HOME%lib\bootstrap.jar
set CLASSPATH=%CLASSPATH%;%PROJECT_HOME%lib\util.jar
set CLASSPATH=%CLASSPATH%;%PROJEreturn CT_HOME%lib\jdom.jar
set CLASSPATH=%CLASSPATH%;%PROJECT_HOME%lib\log4j.jar
set CLASSPATH=%CLASSPATH%;%PROJECT_HOME%lib\extensions.jar
set CLASSPATH=%CLASSPATH%;%PROJECT_HOME%lib\trove4j.jar

pushd bin
start "" "%JAVA%" %JVM_ARGS% %ADDITIONAL_JVM_ARGS% -classpath "%CLASSPATH%" %MAIN_CLASS% %*
popd

exit

:parse_vmoptions
if not defined ACC goto emptyacc
if "%SEPARATOR%" == "" goto noseparator
set ACC=%ACC%%SEPARATOR%%1
goto :eof

:noseparator
set ACC=%ACC% %1
goto :eof

:emptyacc
set ACC=%1
goto :eof
"""

IdeaPropertiesPriv= """#---------------------------------------------------------------------
# Uncomment this option if you want to customize path to MPS config folder
#---------------------------------------------------------------------
idea.config.path=IdeaConfig

#---------------------------------------------------------------------
# Uncomment this option if you want to customize path to MPS system folder
#---------------------------------------------------------------------
idea.system.path=IdeaSystem

#---------------------------------------------------------------------
# Uncomment this option if you want to customize path to user installed plugins folder
#---------------------------------------------------------------------
# idea.plugins.path=${user.home}/.MPS30/config/plugins

#---------------------------------------------------------------------
# Uncomment this option if you want to customize path to MPS logs folder. Make sure you're using forward slashes
#---------------------------------------------------------------------
# idea.log.path=${user.home}/.MPS30/system/log


#---------------------------------------------------------------------
# Maximum file size (kilobytes) MPS should provide intellisense for.
# The larger file is the slower its editor works and higher overall system memory requirements are
# if intellisense is enabled. Remove this property or set to very large number if you need
# intellisense for any files available regardless their size.
#---------------------------------------------------------------------
idea.max.intellisense.filesize=2500

# MPS copies library jars to prevent their locking. If copying is not desirable, specify "true"
idea.jars.nocopy=false

# Configure if a special launcher should be used when running processes from within MPS. Using Launcher enables "soft exit" and "thread dump" features
idea.no.launcher=false

# The VM option value to be used start the JVM in debug mode. Some environments define it in a different way (-XXdebug in Oracle VM)
idea.xdebug.key=-Xdebug

#-----------------------------------------------------------------------
# This option controls console cyclic buffer: keeps the console output size not higher than the specified buffer size (Kb). Older lines are deleted.
# In order to disable cycle buffer use idea.cycle.buffer.size=disabled
idea.cycle.buffer.size=1024

#----------------------------------------------------------------------
# Disabling this property may lead to visual glitches like blinking and fail to repaint
# on certain display adapter cards.
#----------------------------------------------------------------------
sun.java2d.noddraw=true

#----------------------------------------------------------------------
# Removing this property may lead to editor performance degradation under Windows.
#----------------------------------------------------------------------
sun.java2d.d3d=false

#----------------------------------------------------------------------
# Removing this property may lead to editor performance degradation under X-Windows.
#----------------------------------------------------------------------
sun.java2d.pmoffscreen=false
"""

def getTemplateForMPSProperties():
  return IdeaPropertiesPriv;

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

MPSInfoPlist= """<!DOCTYPE plist PUBLIC '-//Apple Computer//DTD PLIST 1.0//EN' 'http://www.apple.com/DTDs/PropertyList-1.0.dtd'>
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
        <key>CFBundleTypeName</key>#Not supported yet
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
      <string>-client -Xss1024k -ea """ + JAVA_XMX + """ -XX:MaxPermSize=256m -XX:NewSize=256m -XX:+HeapDumpOnOutOfMemoryError -Dfile.encoding=UTF-8 -Dapple.awt.graphics.UseQuartz=true -Didea.paths.selector=MPS31</string>
      <key>WorkingDirectory</key>
      <string>$APP_PACKAGE/bin</string>
    </dict>
  </dict>
</plist>"""

# CBMC CONFIGURATION
CBMCVersion="""4"""
CBMCSubVersion = """7"""

#Linux
CBMC32BitLinuxUrl = """http://www.cprover.org/cbmc/download/cbmc-""" + CBMCVersion + "-" + CBMCSubVersion + """-linux-32.tgz"""
CBMC64BitLinuxUrl = """http://www.cprover.org/cbmc/download/cbmc-""" + CBMCVersion + "-" + CBMCSubVersion + """-linux-64.tgz"""

#Mac
CBMCMacFileName = """cbmc-""" + CBMCVersion + "-" + CBMCSubVersion + """.pkg"""
CBMCMacUrl = """http://www.cprover.org/cbmc/download/""" + CBMCMacFileName;
CBMCInstallDirMac = "/usr/bin"

#Windows
CBMCWinFileName = """cbmc-""" + CBMCVersion + "-" + CBMCSubVersion + """-win.zip"""
CBMCWinUrl = """http://www.cprover.org/cbmc/download/""" + CBMCWinFileName;
CBMCInstallDirWin = "cbmc-"+CBMCVersion+"-"+CBMCSubVersion;
CBMCEndPathWin = os.path.join("/cygdrive/c/", CBMCInstallDirWin);

# JAVA CONFIGURATION
InstallJavaMessage= """Please, install a Java from Oracle. 
http://www.oracle.com/technetwork/java/javase/downloads/index.html"""

InstallJavaHintUbuntu = """\nOn Ubuntu this might work:
sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update
sudo apt-get install oracle-java7-installer

 * On Ubuntu 14.04 the last command requires sometimes several runs.

"""

OpenJdkHint = """ ** Please, note that Oracle Java (instead of IcedTea/OpenJDK) is recommended to run MPS!\n"""

# ANT CONFIGURATION
InstallAntMessage= """Please, install Apache Ant(TM).\n 

http://ant.apache.org/bindownload.cgi"""

InstallAntHintUbuntu = """\nOn Ubuntu this might work:
sudo apt-get install ant
"""


# Install Git Messages
InstallGitMac= """Please, install Git from here:
    http://git-scm.com/downloads
"""

InstallGitUbuntu = """Please, run
    sudo apt-get install git
to install git on Ubuntu.
"""

InstallGitCygwin = """Please, start Cygwin Installer and select "git" package to install"""

def getInstallGitMessage():
  if onLinux():
    return InstallGitUbuntu;
  if onMac():
    return InstallGitMac;
  if onWindows():
    return InstallGitCygwin;
  return "Install git, please, visit http://git-scm.com/ for instructions.\n";
  


# USER GUIDE CONFIGURATION
UserGuideURL = """https://github.com/qutorial/mbeddr_python_installer/blob/master/UserGuide.pdf?raw=true"""

# README CONFIGURATION
ReadMeURL = """https://github.com/qutorial/mbeddr_python_installer/blob/master/README.txt?raw=true"""



################### END OF CONFIGURATION ###################

# Adding to Path

def addToPath(d):
  os.environ['PATH'] = os.environ['PATH'] + os.pathsep + d;

# Making files executable
def makeExecutable(f):
  os.system("chmod +x " + f);
  
def makeAllExesExecutable(folder):
  for f in os.listdir(folder):
    if str(f).lower().endswith(".exe"):
      debug ("Making executable: " + f );
      makeExecutable(os.path.join(folder, f));
  
  
# Downloading file with progress

def getFileNameFromUrl(url):
  parsed = urlparse(url);
  path = parsed.path;
  return os.path.basename(path);

def TEST_getFileNameFromUrl():
  return getFileNameFromUrl(UserGuideURL) == "UserGuide.pdf"
  

def formatDataSize(d):
  if d > 2 * 1024 * 1024:
    return "" + (d / (1024 * 1024)) + " MB"
  else:
    if d > 100 * 1024:
      return "" + (d / 1024 ) + " KB"
    else:
      return "" + d + " B"
  
def formatProgressStr(totalsize, readsofar):
  
  if totalsize <= 0:
    return "\rRead " + formatDataSize(readsofar);
  
  ts = totalsize;
  rsf = readsofar;
  
  if readsofar > totalsize:
    rsf = totalsize;
    
  percent = rsf * 100 / ts
  
  s = "\rProgress: %5.1f%% %*d bytes / %d bytes"  
  
  if ts > 2*1024*1024:
    s = "\rProgress: %5.1f%% %*d MB / %d MB"
    ts = ts / (1024*1024)
    rsf = rsf / (1024*1024)
  else:
    if ts > 100*1024:
      s = "\rProgress: %5.1f%% %*d KB / %d KB"
      ts = ts / 1024
      rsf = rsf / 1024
   
  s = s % (percent, len(str(ts)), rsf, ts)
  return s;
  
  
  
def downloadProgressHook(blocknum, blocksize, totalsize):
  readsofar = blocknum * blocksize
  s = formatProgressStr(totalsize, readsofar);
  sys.stderr.write(s)
  if readsofar >= totalsize: # near the end
      sys.stderr.write("\n")

def downloadFile(url, destdir):
  file_name = getFileNameFromUrl(url);
  resName = os.path.join(destdir, file_name)
  log ( "Downloading from " + url + " : " );
  urlretrieve(url, resName, downloadProgressHook);
  return resName
  
def httpGet(url):
  filename, headers = urlretrieve(url);
  f = open(filename, 'r');
  res = f.read()
  f.close();  
  return res;
  
# Autocomplete file names
class Completer:
  def completeSimple(text, state):      
      res = glob.glob(text+"*");
      return res[state];
      
  def completeDirAware(text, state):  
    res = Completer.completeSimple(text, state);    
    if os.path.exists(res):
      if os.path.isdir(res):
        if not res.endswith(os.sep):
          res = res + os.sep;   
    return res;

def readFileName(promptMessage):
  debug (" readFileName with " + promptMessage );  
  readline.parse_and_bind("tab: complete")  
  readline.set_completer_delims("\t\n");
  readline.set_completer(Completer.completeDirAware)  
  return input(promptMessage).strip()

def inputFileName(message, defres):  
  res = None;
  try:
    res = readFileName(message + " [" + defres + "]: ")
  except EOFError:
    res = None
  
  if (res is None) or (len(res) == 0):    
    res = defres;
  
  res = os.path.abspath(res);
  
  log ( "Selecting: " + res);
  
  return res;
  
def TEST_INTERACTIVE_readFileName():
  s = readFileName("File: ")
  log ( "Result: " + s )
    
# Unarchiving Zips and Tars

def unzip(zipzip, dest):
  zfile = zipfile.ZipFile(zipzip)
  for name in zfile.namelist():
    (dirname, filename) = os.path.split(name)
    dirname = os.path.join(dest, dirname);
    log ( "Decompressing " + filename + " to " + dirname )    
    if not os.path.exists(dirname):
      os.makedirs(dirname)
    zfile.extract(name, dirname)

def untgz(arc, dest):
  tfile = tarfile.open(arc, 'r:gz');
  tfile.extractall(dest);
  
def unarchive(a, dest):
  if "zip" in a:
    unzip(a, dest);
  else:
    untgz(a, dest);

    
# Get command output as a string
def strToArr(args):
  command = args;
  if isinstance(args, str):
    command = args.split();      
  return command;


def getOutput(args):
  command = strToArr(args);      
  try:
    return subprocess.check_output(command, stderr=subprocess.STDOUT).decode('ascii').strip();
  except subprocess.CalledProcessError as e:
    return e.output;
    
def getReturnCode(args):
  command = strToArr(args);   
  f = open(os.devnull, 'w')
  res = subprocess.call(command, stdout = f, stderr=subprocess.STDOUT);
  f.close();
  return res;
  
# Windows Cygwin path conversions
def cygwinPathToWin(p):
  return getOutput(["cygpath", "-w", p]);

def convertPathToNative(p):
  if onWindows():
    return cygwinPathToWin(p);
  else:
    return p;

    
# GIT 

def checkGitVersion(git):
  if "git version" in git:
    return True;
  else:
    return "Unrecognized git version\n"    
   
def checkGit():  
  try:
    git = getOutput(["git", "--version"]);
    return checkGitVersion(git)
  except OSError:
    return getInstallGitMessage();

def TEST_checkGit():
  return checkGit() == True or checkGit() == getInstallGitMessage();
    
# JAVA 

def checkJavaVersion(java):
  vals = java.split() 
  a = [s for s in vals if "1.6" in s]
  b1 = [s for s in vals if "1.7" in s]
  b2 = [s for s in vals if "1.8" in s]
  c = [s for s in vals if "HotSpot" in s]
  if len(c) > 0:
    if len(a) + len(b1) + len(b2) > 0:
      return True;
  answer = "No supported Java version detected\n" + InstallJavaMessage;
  if onLinux():
    answer = answer + InstallJavaHintUbuntu;    
    a = [s for s in vals if "IcedTea" in s]
    a += [s for s in vals if "OpenJDK" in s]
    if len(a) > 0:
      answer = answer + OpenJdkHint;    
  return answer;


JDKWINDOWS = None

def locateAndExecuteJavaWindows():
    
  log ( "Note: In Cygwin a path like /cygdrive/c/ stands for C:\ in Windows " );
  jdkpath = inputFileName("Please, point to Oracle JDK folder", WindowsUsualJavaLocation);
  
  javaexe = os.path.join(jdkpath, "bin", "java.exe")
  
  if os.path.exists( javaexe ):
    
    global JDKWINDOWS
    JDKWINDOWS = jdkpath
    
    debug ( "Setting JAVA_HOME to " + JDKWINDOWS )
    os.environ['JAVA_HOME'] = JDKWINDOWS;
    pathToJavaBin = os.path.join(JDKWINDOWS, "bin");
    addToPath(pathToJavaBin);
    
    global MPS_BAT_WITH_ENV        
    MPS_BAT_WITH_ENV = MPS_BAT_WITH_ENV.replace("CYGWINBIN", convertPathToNative("/usr/bin"));
    
    
    return getOutput([javaexe, "-version"])    
    
  else:
    log ( "No JDK located at " + jdkpath );
    return "";
  
def locateAndExecuteJava():
  if onWindows():
    return locateAndExecuteJavaWindows();
  else:
    return getOutput(["java", "-version"]);
  
def checkJava():  
  try:
    java = locateAndExecuteJava()
    return checkJavaVersion(java)
  except OSError:
    answer = InstallJavaMessage;
    if onLinux():
      answer += InstallJavaHintUbuntu;
    return answer;

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
  


ANTWINDOWS = None
ANTWINDOWSEXE = None

def locateAndExecuteAntWindows():
    
  log ( "Note: In Cygwin a path like /cygdrive/c/ stands for C:\ in Windows " );
  antpath = inputFileName("Please, point to Apache Ant folder", WindowsUsualAntLocation);
  
  antexe = os.path.join(antpath, "bin", "ant")
  
  if os.path.exists( antexe ):
    
    global ANTWINDOWS    
    ANTWINDOWS = antpath   
    
    debug ( "Setting ANT_HOME to " + ANTWINDOWS )
    os.environ['ANT_HOME'] = ANTWINDOWS;
    pathToAntBin = os.path.join(ANTWINDOWS, "bin");
    addToPath(pathToAntBin);
    
    global ANTWINDOWSEXE
    ANTWINDOWSEXE = antexe    
    
    return getOutput(["ant", "-version"])
    
    
  else:
    log ( "No Apache Ant located at " + antpath );
    return "";
  
def locateAndExecuteAnt():
  if onWindows():
    return locateAndExecuteAntWindows();
  else:
    return getOutput(["ant", "-version"]);
    
def checkAnt():
  try:
    ant = locateAndExecuteAnt()
    return checkAntVersion(ant)
  except OSError:
    answer = InstallAntMessage;
    if onLinux():
      answer += InstallAntHintUbuntu
    return answer;

def TEST_checkAnt():
  s =  checkAnt();
  return s == True or InstallAntHintUbuntu in s;
  
# Preparing a destination directory

def getUserHomeDirectory():
  return expanduser("~");

def prepareDestDir(complainExists = True):
  home = os.path.join(getUserHomeDirectory(), "mbeddr")
  
  destdir = inputFileName("Where would you like to install mbeddr", home);  
    
  try:    
    if os.path.exists(destdir):
      if complainExists == True:
        log ( "This directory already exists, please, use another one." )
        return False;
    else:
      os.makedirs(destdir)
  except OSError:
    return False;
    
  return destdir;
  
  
# ------------------ INSTALLING CBMC ------------------

def replaceCbmcbinInBat(targetPath):
  global MPS_BAT_WITH_ENV    
  MPS_BAT_WITH_ENV = MPS_BAT_WITH_ENV.replace("CBMCBIN", convertPathToNative(targetPath));

def locateAndExecuteCBMC():
  if onWindows():
    global CBMCEndPathWin
    if os.path.exists(CBMCEndPathWin):
      cbmcExe = os.path.join(CBMCEndPathWin, "cbmc.exe");
      if os.path.exists(cbmcExe):        
        debug ( "Located Existing CBMC at: " + CBMCEndPathWin );
        makeAllExesExecutable(CBMCEndPathWin);
        replaceCbmcbinInBat(CBMCEndPathWin);
        return getOutput([cbmcExe, "--version"]);  
  
  #if stuff above did not work for windows - last attempt and solution for Unix
  return getOutput(["cbmc", "--version"]);
  
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
      cbmc = locateAndExecuteCBMC();      
      debug ( "Locate returns " + cbmc );
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
      return urlopen("http://www.cprover.org/cbmc/LICENSE").read().decode("utf-8").strip();
    except Exception:
      return self.getCBMCFallbackLicense()
    
  
  def installCBMC(self, dest):
    
    strs = [s.strip() for s in self.getCBMCLicense().splitlines()]    
    for s in strs:
      log ( s );
      
    log ( self.getCBMCIntro() );
    log ( "Above is the CBMC license, do you accept it [y/n]?" )
    accept = str(input()).strip();
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
    log ( "Not implemented in CBMC Installer Base" )
    return False
        
    
class CBMCInstallerForLinux(CBMCInstallerBase):
  def downloadCBMC(self, dest):
    fName = False
    url=""    
    if onLinux32():
      url = CBMC32BitLinuxUrl;
    if onLinux64():
      url = CBMC64BitLinuxUrl;    
    log ( "Downloading CBMC: " + url );
    try:
      fName = downloadFile(url, dest);
    except Exception:      
      return False;      
    return fName;
    
  def getCBMCInstallPath(self):  
    return "/usr/bin/cbmc";  
    
  def setUpCBMC(self, dest, fname):
    unarchive(fname, dest);
    log ( "\nTo finish the CBMC installation, you might be asked for the root/administrator password.\n" )
    log ( "Password: " )
    proc = subprocess.Popen(["sudo","-p", "", "ln", "-s", "--force", os.path.join(dest, "cbmc"), self.getCBMCInstallPath()], stdin=subprocess.PIPE)
    proc.wait()
    log ( "Finished installing" )
    return True;
    
class CBMCInstallerForMac(CBMCInstallerBase):
  def downloadCBMC(self, dest):
    fName = False
    url = CBMCMacUrl;
    log ( "Downloading CBMC: " + url )
    try:
      fName = downloadFile(url, dest);
    except Exception:      
      return False;      
    return fName;
    
  def setUpCBMC(self, dest, fname):
    log ( "\nPlease, proceed installing CBMC..." )
    proc = subprocess.Popen(["open", fname], stdin=subprocess.PIPE)    
    log ( "Continuing installation...\n" )
    return True;


 
    
#This is a stub
class CBMCInstallerForWin(CBMCInstallerBase):
  def downloadCBMC(self, dest):
    fName = False
    url = CBMCWinUrl;     
    log ( "Downloading CBMC: " + url );
    try:
      fName = downloadFile(url, dest);
    except Exception:      
      return False;      
    return fName;
    
  def setUpCBMC(self, dest, fname):
    res = os.path.join(dest, CBMCInstallDirWin);
    os.makedirs(res);    
    unarchive(fname, res);
    
    targetPath = CBMCEndPathWin;
    
    if os.path.exists(targetPath):
      log ( "CBMC was installed before but does not work. Remove manually " + targetPath + " and start over, please." );
      return False;
      
    os.system("mv " + res + " " + targetPath);
    
    replaceCbmcbinInBat(targetPath);
    makeAllExesExecutable(targetPath);
    
    return True;
    
    
    
    
def getCBMCInstaller():
  if onLinux():
    return CBMCInstallerForLinux();
  if onMac():
    return CBMCInstallerForMac();
  if onWindows():
    return CBMCInstallerForWin();

def TEST_getCBMCInstaller():
  installer = getCBMCInstaller();
  return "Mellon" in str ( installer.getCBMCLicense() )
  
def TEST_checkCBMC():
  installer = getCBMCInstaller();
  s = installer.checkCBMC();
  return s == True or "CBMC" in s;
    
def installCBMC(dest):
  log ( "Detecting CBMC" )
  cbmcInstaller = getCBMCInstaller();
  if cbmcInstaller == None:
    log ( "Problem configurring CBMC, analyses might not work!" )
  else:    
    j = cbmcInstaller.checkCBMC()
    if j != True:
      log ( j )
      if cbmcInstaller.installCBMC(dest) != True:
        log ( "Failed to install CBMC!\n" )
        exit(1);
      else:
        log (  "CBMC installed!\n" );
    else:
      log (  """You have CBMC already installed.""" );
      log (  cbmcInstaller.getCBMCCopyright() );
    
    
def TEST_INTERACTIVE_installCBMC():
  dest = prepareDestDir();
  log (  "Testing CBMC installer" );
  installCBMC(dest);

# ------------------ END INSTALLING CBMC ------------------
    

    
    
# ------------------ INSTALLING MPS ------------------




def getMPSDownloadUrl():
  if onLinux():
    return MPSLin
  if onMac():
    return MPSMac
  if onWindows():
    return MPSWin
  return "";

THE_MPS_URL = None;
def getMPSUrl():
  global THE_MPS_URL
  if THE_MPS_URL == None:
    THE_MPS_URL = str ( httpGet(getMPSDownloadUrl()) ).strip();
  return THE_MPS_URL;
  
def getMPSFileName():
  return getFileNameFromUrl(getMPSUrl());

def TEST_getMPSUrl():
  return getMPSFileName() in getFileNameFromUrl(getMPSUrl());

def getMPSArchiveInUserHome():
  return os.path.join(getUserHomeDirectory(), getMPSFileName());

def downloadMPSOSDep(dest):
  url = getMPSUrl();
  
  #Cached installation
  fName = getMPSArchiveInUserHome();
  if os.path.exists(fName):
    log (  "\nUsing cached archive with MPS: " + fName + "\nDelete it manually, if the installation fails to use it!" );
    return fName;
  
  fName = os.path.join(dest, getMPSFileName());    
  if os.path.exists(fName):
    log (  "\nAn archive with MPS has already been downloaded to: " + fName + "\nDelete it manually, if the installation fails to use it!" );
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
    MPSDir = self.getMPSEndPath(dest);
    if os.path.exists(MPSDir):
      log (  "Can not install MPS, the folder " + MPSDir + " already exists, please delete it first or specify a new one." );
      return False;    
    log (  "Extracting..." );
    unarchive(self.archive, dest);        
    log (  "Renaming MPS folder"     );
    MPSArcDirLocal=MPSArcDir;
    dirs = [ f for f in os.listdir(dest) if os.path.isdir(os.path.join(dest, f)) and MPSArcDirLocal in f ];
    MPSArcDirLocal = dirs[0];
    os.rename(os.path.join(dest, MPSArcDirLocal), MPSDir)
    self.mpsPath = MPSDir;

    
  def setUpMPS(self, dest):
    self.setUpMPSHook(dest); 
    self.removeArchive();
    
  def getMPSPath(self):
    return self.mpsPath;
    
  def getMPSEndPath(self, dest):
    return os.path.join(dest, self.getMPSDir());
  
  def removeArchive(self):
    if self.archive == getMPSArchiveInUserHome():
      log ( "Skipping removal of the archive from the home folder" );
      return;
    
    log (  "Deleting downloaded MPS archive..." );
    os.remove(self.archive);  
    
  def getMPSDir(self):
    log ( "Not implemented for this platform in MPSInstallerBase" );
    return None;
    
class MPSInstallerForLinux(MPSInstallerBase):    
  def getMPSDir(self):
    return MPSDestDirLinux;    
    
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
      
      
def failNoImage():
  log (  "Image not mounted, installation fails!" );
  exit(1);
   
class MPSInstallerForMac(MPSInstallerBase):
  def getMPSDir(self):
    return MPSDestDirMac;
  
  def setUpMPSHook(self, dest):    
    proc = subprocess.Popen(["hdiutil", "attach", "-quiet", self.archive], stdin=subprocess.PIPE)
    proc.wait();
    
    log (  "Waiting for the image to mount..." );
    time.sleep(5);
    
    
    MPSVolumesDirLocal = MPSVolumesDir;
    
    dirs = [ f for f in os.listdir(MPSVolumesDirLocal) if "MPS" in f ]
    if len(dirs) == 0:
      failNoImage();
      
    
    MPSVolumesDirLocal = os.path.join(MPSVolumesDirLocal, dirs[0]);
        
    dirs = [ f for f in os.listdir(MPSVolumesDirLocal) if "MPS" in f ]
    if len(dirs) == 0:
      failNoImage();
      
    MPSVolumesDirLocal = os.path.join(MPSVolumesDirLocal, dirs[0]);
    
    if not os.path.exists(MPSVolumesDirLocal):
      failNoImage();
    
    self.mpsPath = self.getMPSEndPath(dest);
    log (  "Copying MPS..." );
    log (  "Please, do not eject the MPS drive..." );
    shutil.copytree(MPSVolumesDirLocal, self.mpsPath);
    log (  "Ready!" );
    log (  "Ejecting the MPS image now..."     );
    ejectImageMac(self.archive);
    
class MPSInstallerForWin(MPSInstallerBase):
  def getMPSDir(self):
    return MPSDestDirWin;
    
  def setUpMPSHook(self, dest):
    log ( "Running the installer..." );
    
    log ( " * Please, specify this directory in MPS Installer:\n\t" + convertPathToNative(self.getMPSEndPath(dest)) + "\n" ); 
    log ( "Note the message above and press Enter key to continue..." );
    input();    
    
    makeExecutable(self.archive);
    currdir = os.getcwd();    
    os.chdir(os.path.dirname(self.archive));    
    comm = "explorer.exe " + getFileNameFromUrl(self.archive);
    os.system( comm );    
    os.chdir(currdir);        
    
    self.mpsPath = self.getMPSEndPath(dest);
    
    linkPath = os.path.join(CygwinDocsAndSettings, getOutput("whoami"), "Desktop", WindowsMPSDesktopLinkName);
    mbeddrLinkPath = os.path.join(CygwinDocsAndSettings, getOutput("whoami"), "Desktop", WindowsMbeddrDesktopLinkName);
    
    i = 0;
    
    log ( "Waiting untill MPS is installed..." );
    log ( " * The installer window can be in the background, switch to it, please!" );
    while not os.path.exists(linkPath):
      i = i + 1;
      time.sleep(1);
      if i > 300 :
        log ( "Can not detect MPS installed" );
        exit (1);
    
    os.system("mv \"" + linkPath + "\" \"" + mbeddrLinkPath+"\"");
    
    i = 0;
    
    while True:
      fp = None
      
      i = i + 1;
      time.sleep(1);
      
      if i > 300:
        log ( "Can not finish the installation of MPS..." );
        exit (1);
      
      try:
        fp = open(self.archive, "w")
      except IOError as e:        
        continue;
      
      fp.close();
      break;
      
    log ( "Finished installing MPS!\n" );  
    
           
def getMPSInstaller():
  if onLinux():
    return MPSInstallerForLinux();
  if onMac():
    return MPSInstallerForMac();
  if onWindows():
    return MPSInstallerForWin();
  return None;

def TEST_getMPSInstaller():
  installer = getMPSInstaller();
  return "MPS" in installer.getMPSEndPath("");
    
def TEST_INTERACTIVE_INSTALL_MPS():
  dest = prepareDestDir();
  log (  "Testing MPS installer" );
  installer = getMPSInstaller();
  installer.downloadMPS(dest);  
  installer.setUpMPS(dest);
  log (  "MPS Installed to: " + installer.getMPSPath() );
  
     
# ------------------ END INSTALLING MPS ------------------


  

# ------------------ CONFIGURRING MPS WITH MBEDDR ------------------

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
  
  debug ( "Writing Info Plist to " + infoPlistPath + " :\n " + infoPlistContent );
  
  rewriteFile(infoPlistPath, infoPlistContent);

# END OF MAC PART

def getIdeaPropertiesFile(MPSDir):
  return os.path.join(MPSDir, "bin", "idea.properties");
    
  
def writeIdeaProperties (MPSDir, ConfigPath, SysPath):  
  optsPath = getIdeaPropertiesFile(MPSDir)
  
  optsContent = "";
  if onWindows():
    optsContent = replaceConfigAndSystemPaths(getTemplateForMPSProperties(), "\"../IdeaConfig\"", "\"../IdeaSystem\"");
  else:
    optsContent = replaceConfigAndSystemPaths(getTemplateForMPSProperties(), ConfigPath, SysPath);
  
  debug ( "Writing Idea Properties to " + optsPath + " :\n " + optsContent );
  
  rewriteFile(optsPath, optsContent);

  
def configureMPSWithMbeddr(MPSDir, MbeddrDir):
#  print "configure is called with MPS dir ", MPSDir, " and MbeddrDir ", MbeddrDir;
  ConfigPath = os.path.join(MPSDir, "IdeaConfig");
  if not os.path.exists(ConfigPath):
    os.makedirs(ConfigPath);

  debug ( "Idea Configuration will be in " + ConfigPath );
  
  SysPath = os.path.join(MPSDir, "IdeaSystem");    
  if not os.path.exists(SysPath):
    os.makedirs(SysPath);
  
  debug ( "Idea System will be in " + SysPath );
  
  OptionsPath = os.path.join(ConfigPath, "options");
  if not os.path.exists(OptionsPath):
    os.makedirs(OptionsPath);
 
  debug ( "Options will be in " + OptionsPath );
  
  rewriteFile(os.path.join(OptionsPath, "libraryManager.xml"), MPSLibraryManager);
  
  thePathMacros = MPSPathMacros.replace("MbeddrDir", convertPathToNative(MbeddrDir));
  
  debug ( " Path macros to be written : " + thePathMacros );
  
  rewriteFile(os.path.join(OptionsPath, "path.macros.xml"), thePathMacros);
  
  writeIdeaProperties(MPSDir, ConfigPath, SysPath);
  
  if onLinux():
    debug ( "Setting mps.vmoptions" );
    rewriteFile(os.path.join(MPSDir, "bin", "mps.vmoptions"), getMPSVmoptions());
    rewriteFile(os.path.join(MPSDir, "bin", "mps64.vmoptions"), getMPSVmoptions());
  
  if onMac():
    debug ( "Configurring Info.Plist on Mac");
    configureInfoPlist(MPSDir, ConfigPath, SysPath);
  
  if onWindows():
    debug ( "Configurring mps.bat on Windows" );    
    global MPS_BAT_WITH_ENV
    rewriteFile(os.path.join(MPSDir, MPSBatName), MPS_BAT_WITH_ENV);
    debug ( "Setting mps.vmoptions" );
    rewriteFile(os.path.join(MPSDir, "bin", "mps.exe.vmoptions"), getMPSVmoptions());
    rewriteFile(os.path.join(MPSDir, "bin", "mps64.exe.vmoptions"), getMPSVmoptions());
    
    
def testConfigureMPSWithMbeddr():
  dest = prepareDestDir(False);
  MbeddrDir = getMbeddrDestDir(dest);
  mpsInstaller = getMPSInstaller();
  MPSDir = mpsInstaller.getMPSEndPath(dest);
  
  log ( "Testing MPS Configuration with " + MPSDir + " and " + MbeddrDir );
  
  configureMPSWithMbeddr(MPSDir, MbeddrDir);
  
# ------------------ END CONFIGURING MPS WITH MBEDDR ------------------

def printPathVariable():
  os.system("""echo PATH for git is set to: $PATH""");
    
def cloneMbeddr(MbeddrDir, branch):  
  if not os.path.exists(MbeddrDir):
      os.makedirs(MbeddrDir);
  os.chdir(MbeddrDir);
  
  theOldPath = os.environ['PATH'];
  
  if onWindows():    
    os.environ['PATH'] = "/usr/bin"+ os.pathsep + "/bin";  
  
  os.system("git clone --recursive -b " + branch + " " + MbeddrRepo+ " .");  
  
  if onWindows():
    os.environ['PATH'] = theOldPath;

def TEST_INTERACTIVE_cloneMbeddr():
  mdir = readFileName("Where to clone mbeddr?");
  branch = TheBranch;
  cloneMbeddr(mdir, branch);
 
#Path to Native with Forward Slashes
def p2nfs(p):
  return convertPathToNative(p).replace("\\", "/");
  

def getBuildProperties(MPSDir, MbeddrDir):  
  caches = os.path.join(MPSDir, "CachesMbeddr");  
  if onWindows():
    return BuildProperties.replace("MPSDir", p2nfs(MPSDir)).replace("MPSCaches", p2nfs(caches)).replace("MbeddrDir", p2nfs(MbeddrDir));
  else:
    return BuildProperties.replace("MPSDir", MPSDir).replace("MPSCaches", caches).replace("MbeddrDir", MbeddrDir)
  
def configureMbeddr(MPSDir, MbeddrDir):    
  BuildPropsPath = os.path.join(MbeddrDir, "code", "languages", "build.properties");
  rewriteFile(BuildPropsPath, getBuildProperties(MPSDir, MbeddrDir))


def buildMbeddr(MbeddrDir):
  BuildPath = os.path.join(MbeddrDir, "code", "languages");
  os.chdir(BuildPath);
  scriptname = "offlineBuildLanguages.sh";  
  scriptname = os.path.join(BuildPath, scriptname);  
  os.system(scriptname);
  

  
  
# ---------- DOWNLOADING USER GUIDE ------------

def downloadTheUserGuide(dest):
  try:
    downloadFile(UserGuideURL, dest);
  except:
    log (  "Can not download the user guide." );
  

    
# ---------- END OF : DOWNLOADING USER GUIDE ------------



# ---------- DOWNLOADING README ------------

def downloadTheReadMe(dest):
  try:
    downloadFile(ReadMeURL, dest);
  except:
    log (  "Can not download the README.txt." );

# ---------- END OF : DOWNLOADING README ------------


  
# ---------- FINAL GREETINGS ------------
  
  
def greetingsLinux(MPSDir, MbeddrDir, dest):
  log (  """\nTo start working: Run\n"""+os.path.join(MPSDir, "mps.sh")+"""\nand go through the tutorial project from:""" );

def greetingsMac(MPSDir, MbeddrDir, dest):
  log (  "\nTo start working: Run MPS (located in " + dest + ") and go through the tutorial project from:" );


asciiArt = """
                                                      dKKl                                :O00.         ,KK0.           
                 .  .                                 OMMd                                dMMM.         :MMM'           
            .:d0WM':MNOd:.                            0MMd                                dMMM.         :MMM'           
         cOWMMMMMM':MMMMMMWOd  .oxO0XX0Odc:xOKX0ko.   0MMNOOOOd;      ;dO0KOkl'     .cxOO0NMMM.   .cxOOOXMMM'  ldOKXXXX:
         0MMMMMMMM':MMMMMMMMM. lMMMo,,:OMMM0c,,xMMW;  0MMO,,:kWMX,  ,XMWd:,lXMMx  .OMMKl;,OMMW.  cKXOo:,lKXN. .MMMO;,:: 
        .MMMMMMMMM';MNXX000Ok. cWMM'   'MMMl   .MMMd  0MMd    kMMW. XMMd..''kWXX' cxxl    ,xxo  :xxO.   'xxx. .ddd'     
        .XNWMMMMMM'.kdoxkO00K. 'xxx.   .O00:   .MMMd  0MWo    c00k..xkkdolcc:',,..XNMd    dMMM. KMM0    :MMM' 'MMM,     
        .xxxxxxdxc :MMMMMMMMM. lMMM'   .KOO,   .xxx;  dxo,   .xO0x  0MMO          KMMK.   dMMM. dMMW'   :MMM' 'MMMl     
        .MMMMMMMMW.:MMMMMMMMM. lMMM'   'MMMl   .MMMd .MMMKooxXMNd.  .kNMXkddkOXo  .kWMNkooKMMM.  oNMNkdoOMMM. 'MMMl     
        .KWMMMMMMM':MMMMMMMW0. .lll.   .lll'    lll,  ':oxxxdc,        ,lxxxxoc.     ,cdxxxo:'     ,lxxxxoc,  .lll'     
          .;oONMMM':MMWKxc'                                                                                             
               .:o..:'                    engineering the future of embedded software
"""
  
  
def greetings(MPSDir, MbeddrDir, dest):
#  log ( asciiArt );
  if onLinux():
    greetingsLinux(MPSDir, MbeddrDir, dest);
  if onMac():
    greetingsMac(MPSDir, MbeddrDir, dest);
  
  log (  os.path.join(MbeddrDir, "code", "application"),""" folder.\n"""   );
  log (  """\nVisit mbeddr.com to learn what's new!\n"""   );
  log (  """ * A user guide PDF has been downloaded to the destination folder!""" );
  log (  """ * See the README.txt file for the further instructions and basic troubleshooting."""  );
  
  log (  "\nWelcome to mbeddr. C the difference C the future.\n" );
  log (  "-----------------------------------------------------------\n" );
  log (  """This installer for mbeddr advanced users has been built by molotnikov (at) fortiss (dot) org.
  
If the installer did not work for you, please, let us know by posting an issue here:
https://github.com/qutorial/mbeddr_python_installer
""" );

def printErrorMessage():
  log (  """The installation went wrong, unfortunately.

Please, report an issue on the installer's GitHub page:
https://github.com/qutorial/mbeddr_python_installer

Please, include in your letter a detailed description, what exactly you have been doing before facing
difficulties, what did not work for you? Which environment did you have, in particular, which operating system?
Please, include the error messages appearing above on the console.

This installer is created by Zaur Molotnikov ( molotnikov at fortiss dot org ).
Please, write an email on this address, if you experience troubles using the installer or mbeddr.""" );
  
# ---------- END OF :  FINAL GREETINGS ------------

def checkRights():
  if onWindows():
    rc = getReturnCode("at");
    if rc != 0:
      log ( "\nPlease, run Cygwin Terminal as an Administrator!" );
      raise ShutDownSilently();
  
def main():  

  log ( "\nWelcome to mbeddr installer for advanced users and developers!\n" );
  
  checkRights();

  log (  "Detecting Git"   );
  j = checkGit()
  if j != True:
    log (  j );
    return 1; 
  
  log (  "Detecting Java"   );
  j = checkJava()
  if j != True:
    log (  j );
    return 1;  
  
  log (  "Detecting Ant" );
  j = checkAnt()
  if j != True:
    log (  j );
    return 1;  
  
  log (  "Preparing destination directory"   );
  dest = prepareDestDir();
  if dest == False:
    log (  "Problem creating destination directory" );
    return 1;
    
  
  #Installing CBMC
  log (  "Installing CBMC" );
  installCBMC(dest);
      
  
  #Installing MPS
  log (  "Installing MPS..." );
  mpsInstaller = getMPSInstaller();
  mpsInstaller.downloadMPS(dest);  
  mpsInstaller.setUpMPS(dest);
  MPSDir = mpsInstaller.getMPSPath();
  
    
  log (  "Installing mbeddr" );
  MbeddrDir = getMbeddrDestDir(dest);
  if os.path.exists(MbeddrDir):
    log (  "Can not install mbeddr, the folder " + MbeddrDir + " already exists, please delete it first or specify a new one.\n" );
    log (  "Don't forget to save your changes if made to mbeddr!" );
    exit(1);
    
  log (  "Cloning mbeddr..." );
  cloneMbeddr(MbeddrDir, TheBranch);
  
  log (  "Setting up MPS to work with mbeddr..." );
  configureMPSWithMbeddr(MPSDir, MbeddrDir);
  
  log (  "Setting up mbeddr..." );
  configureMbeddr(MPSDir, MbeddrDir);
     
  log (  "Downloading the user guide..." );
  downloadTheUserGuide(dest);
 
  log (  "Downloading the README.txt..." );
  downloadTheReadMe(dest);
  
  log (  "Building mbeddr..." );
  buildMbeddr(MbeddrDir);
  
  greetings(MPSDir, MbeddrDir, dest);

def RUN_TESTS():
  log (  "URL Parsing:\t\t", TEST_getFileNameFromUrl() );
  log (  "OS Detection:\t\t", TEST_getOS() );
  log (  "Git Detection:\t\t", TEST_checkGit() );
  log (  "Java Detection:\t\t", TEST_checkJava() );
  log (  "Ant Detection:\t\t", TEST_checkAnt() );
  log (  "CBMC Installer:\t\t", TEST_getCBMCInstaller() );
  log (  "CBMC Detection:\t\t", TEST_checkCBMC() );
  log (  "MPS URL:\t\t", TEST_getMPSUrl() );
  log (  "MPS Installer:\t\t", TEST_getMPSInstaller() );
  log (  "MPS VM Options:\t\t", TEST_getMPSVmoptions() );
  
  
#RUN_TESTS();
#exit(1);

def reportException(exc_type, exc_value, exc_traceback):
  log (  "\nException:" )
  traceback.print_exception(exc_type, exc_value, exc_traceback)
  log (  "\n" )
  printErrorMessage()

try:
  main();
except:
  
  exc_type, exc_value, exc_traceback = sys.exc_info()
    
  if exc_type == ShutDownSilently:
    pass;
  else:
    reportException(exc_type, exc_value, exc_traceback);
     