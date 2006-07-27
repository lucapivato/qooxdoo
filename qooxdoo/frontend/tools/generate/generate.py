#!/usr/bin/env python

import sys, string, re, os, random, shutil, optparse
import config, tokenizer, loader, compile, docgenerator, tree, treegenerator





def filetool(filename, content="", encoding="utf-8"):
  # Splitting
  directory = os.path.dirname(filename)

  # Check/Create directory
  if not os.path.exists(directory):
    os.makedirs(directory)

  # Writing file
  outputFile = file(filename, "w")
  outputFile.write(content.encode(encoding))
  outputFile.flush()
  outputFile.close()





def getparser():
  parser = optparse.OptionParser("usage: %prog [options]")


  #################################################################################
  # GENERAL
  #################################################################################

  # From/To File
  parser.add_option("--from-file", dest="fromFile", metavar="FILENAME", help="Read options from FILENAME.")
  parser.add_option("--export-to-file", dest="exportToFile", metavar="FILENAME", help="Store options to FILENAME.")

  # Directories (Lists, Match using index)
  parser.add_option("--script-input", action="append", dest="scriptInput", metavar="DIRECTORY", default=[], help="Define a script input directory.")
  parser.add_option("--source-script-path", action="append", dest="sourceScriptPath", metavar="PATH", default=[], help="Define a script path for the source version.")
  parser.add_option("--resource-input", action="append", dest="resourceInput", metavar="DIRECTORY", default=[], help="Define a resource input directory.")
  parser.add_option("--resource-output", action="append", dest="resourceOutput", metavar="DIRECTORY", default=[], help="Define a resource output directory.")

  # Available Actions
  parser.add_option("--generate-compiled-script", action="store_true", dest="generateCompiledScript", default=False, help="Compile source files.")
  parser.add_option("--generate-source-script", action="store_true", dest="generateSourceScript", default=False, help="Generate source version.")
  parser.add_option("--generate-api-documentation", action="store_true", dest="generateApiDocumentation", default=False, help="Generate API documentation.")
  parser.add_option("--copy-resources", action="store_true", dest="copyResources", default=False, help="Copy resource files.")

  # Debug Actions
  parser.add_option("--store-tokens", action="store_true", dest="storeTokens", default=False, help="Store tokenized content of source files. (Debugging)")
  parser.add_option("--print-files", action="store_true", dest="printFiles", default=False, help="Output known files. (Debugging)")
  parser.add_option("--print-modules", action="store_true", dest="printModules", default=False, help="Output known modules. (Debugging)")
  parser.add_option("--print-include", action="store_true", dest="printList", default=False, help="Output sorted file list. (Debugging)")

  # Output files
  parser.add_option("--source-script-file", dest="sourceScriptFile", metavar="FILENAME", help="Name of output file from source build process.")
  parser.add_option("--compiled-script-file", dest="compiledScriptFile", metavar="FILENAME", help="Name of output file from compiler.")
  parser.add_option("--api-documentation-json-file", dest="apiDocumentationJsonFile", metavar="FILENAME", help="Name of JSON API file.")
  parser.add_option("--api-documentation-xml-file", dest="apiDocumentationXmlFile", metavar="FILENAME", help="Name of XML API file.")



  #################################################################################
  # OPTIONS
  #################################################################################

  # General options
  parser.add_option("--encoding", dest="encoding", default="utf-8", metavar="ENCODING", help="Defines the encoding used for output files.")
  parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=False, help="Quiet output mode.")
  parser.add_option("-v", "--verbose", action="store_true", dest="verbose", help="Verbose output mode.")

  # Options for source and compiled version
  parser.add_option("--define-runtime-setting", action="append", dest="defineRuntimeSetting", metavar="NAMESPACE.KEY:VALUE", default=[], help="Define a setting.")
  parser.add_option("--add-new-lines", action="store_true", dest="addNewLines", default=False, help="Keep newlines in compiled files.")

  # Options for compiled version
  parser.add_option("--add-file-ids", action="store_true", dest="addFileIds", default=False, help="Add file IDs to compiled output.")
  parser.add_option("--compress-strings", action="store_true", dest="compressStrings", default=False, help="Compress strings. (ALPHA)")

  # Options for resource copying
  parser.add_option("--override-resource-output", action="append", dest="overrideResourceOutput", metavar="CLASSNAME.ID:DIRECTORY", default=[], help="Define a resource input directory.")

  # Options for token storage
  parser.add_option("--token-output-directory", dest="tokenOutputDirectory", metavar="DIRECTORY", help="Define output directory for tokenized JavaScript files. (Debugging)")




  #################################################################################
  # INCLUDE/EXCLUDE
  #################################################################################

  # Include/Exclude
  parser.add_option("-i", "--include", action="append", dest="include", help="Include ID")
  parser.add_option("-e", "--exclude", action="append", dest="exclude", help="Exclude ID")

  # Include/Exclude options
  parser.add_option("--disable-include-dependencies", action="store_false", dest="enableIncludeDependencies", default=True, help="Enable include dependencies.")
  parser.add_option("--disable-exclude-dependencies", action="store_false", dest="enableExcludeDependencies", default=True, help="Enable exclude dependencies.")
  parser.add_option("--disable-auto-dependencies", action="store_false", dest="enableAutoDependencies", default=True, help="Disable detection of dependencies.")

  return parser






def argparser(cmdlineargs):

  # Parse arguments
  (options, args) = getparser().parse_args(cmdlineargs)

  # Export to file
  if options.exportToFile != None:
    print
    print "  EXPORTING:"
    print "----------------------------------------------------------------------------"

    print " * Translating options..."

    optionString = "# Exported configuration from build.py\n\n"
    ignoreValue = True
    lastWasKey = False

    for arg in cmdlineargs:
      if arg == "--export-to-file":
        ignoreValue = True

      elif arg.startswith("--"):
        if lastWasKey:
          optionString += "\n"

        optionString += arg[2:]
        ignoreValue = False
        lastWasKey = True

      elif arg.startswith("-"):
        print "   * Couldn't export short argument: %s" % arg
        optionString += "\n# Ignored short argument %s\n" % arg
        ignoreValue = True

      elif not ignoreValue:
        optionString += " = %s\n" % arg
        ignoreValue = True
        lastWasKey = False



    print " * Export to file: %s" % options.exportToFile
    exportFile = file(options.exportToFile, "w")
    exportFile.write(optionString)
    exportFile.flush()
    exportFile.close()

    sys.exit(0)

  # Read from file
  elif options.fromFile != None:

    print
    print "  INITIALIZATION:"
    print "----------------------------------------------------------------------------"

    print "  * Reading configuration..."

    # Convert file content into arguments
    fileargs = {}
    fileargpos = 0
    fileargid = "default"
    currentfileargs = []
    fileargs[fileargid] = currentfileargs

    alternativeFormatBegin = re.compile("\s*\[\s*")
    alternativeFormatEnd = re.compile("\s*\]\s*=\s*")
    emptyLine = re.compile("^\s*$")

    for line in file(options.fromFile).read().split("\n"):
      line = line.strip()

      if emptyLine.match(line) or line.startswith("#") or line.startswith("//"):
        continue

      # Translating...
      line = alternativeFormatBegin.sub(" = ", line)
      line = alternativeFormatEnd.sub(":", line)

      # Splitting line
      line = line.split("=")

      # Extract key element
      key = line.pop(0).strip()

      # Separate packages
      if key == "package":
        fileargpos += 1
        fileargid = line[0].strip()

        print "    - Found package: %s" % fileargid

        currentfileargs = []
        fileargs[fileargid] = currentfileargs
        continue

      key = "--%s" % key

      if len(line) > 0:
        line = line[0].split(",")

        for elem in line:
          currentfileargs.append(key)
          currentfileargs.append(elem.strip())

      else:
        currentfileargs.append(key)

    # Parse
    defaultargs = fileargs["default"]

    if len(fileargs) > 1:
      (fileDb, moduleDb) = load(getparser().parse_args(defaultargs)[0])

      for filearg in fileargs:
        if filearg == "default":
          continue

        print
        print
        print "**************************** Next Package **********************************"
        print "PACKAGE: %s" % filearg

        combinedargs = []
        combinedargs.extend(defaultargs)
        combinedargs.extend(fileargs[filearg])

        options = getparser().parse_args(combinedargs)[0]
        execute(fileDb, moduleDb, options, filearg)

    else:
      options = getparser().parse_args(defaultargs)[0]
      (fileDb, moduleDb) = load(options)
      execute(fileDb, moduleDb, options)

  else:
    print
    print "  INITIALIZATION:"
    print "----------------------------------------------------------------------------"

    print "  * Processing arguments..."

    (fileDb, moduleDb) = load(options)
    execute(fileDb, moduleDb, options)







def main():
  if len(sys.argv[1:]) == 0:
    basename = os.path.basename(sys.argv[0])
    print "usage: %s [options]" % basename
    print "Try '%s -h' or '%s --help' to show the help message." % (basename, basename)
    sys.exit(1)

  argparser(sys.argv[1:])






def load(options):

  ######################################################################
  #  SOURCE LOADER
  ######################################################################

  print
  print "  SOURCE LOADER:"
  print "----------------------------------------------------------------------------"

  print "  * Normalizing directory information..."

  if options.scriptInput == None or len(options.scriptInput) == 0:
    basename = os.path.basename(sys.argv[0])
    print "You must define at least one source directory!"
    print "usage: %s [options]" % basename
    print "Try '%s -h' or '%s --help' to show the help message." % (basename, basename)
    sys.exit(1)
  else:
    # Normalizing directories
    i=0
    for directory in options.scriptInput:
      options.scriptInput[i] = os.path.normpath(options.scriptInput[i])
      i+=1

  print "  * Loading JavaScript files..."

  (fileDb, moduleDb) = loader.indexScriptInput(options)

  print "  * Found %s JavaScript files" % len(fileDb)

  if options.printFiles:
    print
    print "  OUTPUT OF KNOWN FILES:"
    print "----------------------------------------------------------------------------"
    print "  * These are all known files:"
    for fileEntry in fileDb:
      print "    - %s (%s)" % (fileEntry, fileDb[fileEntry]["path"])

  if options.printModules:
    print
    print "  OUTPUT OF KNOWN MODULES:"
    print "----------------------------------------------------------------------------"
    print "  * These are all known modules:"
    for moduleEntry in moduleDb:
      print "    * %s" % moduleEntry
      for fileEntry in moduleDb[moduleEntry]:
        print "      - %s" % fileEntry






  ######################################################################
  #  DETECTION OF AUTO DEPENDENCIES
  ######################################################################

  if options.enableAutoDependencies:
    print
    print "  DETECTION OF AUTO DEPENDENCIES:"
    print "----------------------------------------------------------------------------"

    print "  * Collecting IDs..."

    knownIds = []

    for fileEntry in fileDb:
      knownIds.append(fileEntry)

    print "  * Detecting dependencies..."

    for fileEntry in fileDb:
      if options.verbose:
        print "    * %s" % fileEntry

      fileTokens = fileDb[fileEntry]["tokens"]
      fileDeps = []

      assembledName = ""

      for token in fileTokens:
        if token["type"] == "name" or token["type"] == "builtin":
          if assembledName == "":
            assembledName = token["source"]
          else:
            assembledName += ".%s" % token["source"]

          if assembledName in knownIds:
            if assembledName != fileEntry and not assembledName in fileDeps:
              fileDeps.append(assembledName)

            assembledName = ""

        elif not (token["type"] == "token" and token["source"] == "."):
          if assembledName != "":
            assembledName = ""

          if token["type"] == "string" and token["source"] in knownIds and token["source"] != fileEntry and not token["source"] in fileDeps:
            fileDeps.append(token["source"])

      # Updating lists...
      optionalDeps = fileDb[fileEntry]["optionalDeps"]
      loadtimeDeps = fileDb[fileEntry]["loadDeps"]
      runtimeDeps = fileDb[fileEntry]["runtimeDeps"]

      # Removing optional deps from list
      for dep in optionalDeps:
        if dep in fileDeps:
          fileDeps.remove(dep)

      # Checking loadtime dependencies
      for dep in loadtimeDeps:
        if not dep in fileDeps:
          print "    * Wrong load dependency %s in %s!" % (dep, fileEntry)

      # Checking runtime dependencies
      for dep in runtimeDeps:
        if not dep in fileDeps:
          print "    * Wrong runtime dependency %s in %s!" % (dep, fileEntry)

      # Adding new content to runtime dependencies
      for dep in fileDeps:
        if not dep in runtimeDeps and not dep in loadtimeDeps:
          if options.verbose:
            print "    * Add dependency: %s" % dep

          runtimeDeps.append(dep)



  return fileDb, moduleDb







def execute(fileDb, moduleDb, options, pkgid=""):

  additionalOutput = []


  ######################################################################
  #  SORT OF INCLUDE LIST
  ######################################################################

  print
  print "  SORT OF INCLUDE LIST:"
  print "----------------------------------------------------------------------------"

  if options.verbose:
    print "  * Include: %s" % options.include
    print "  * Exclude: %s" % options.exclude

  print "  * Sorting files..."

  sortedIncludeList = loader.getSortedList(options, fileDb, moduleDb)

  if options.printList:
    print
    print "  PRINT OF INCLUDE ORDER:"
    print "----------------------------------------------------------------------------"
    print "  * The files will be included in this order:"
    for key in sortedIncludeList:
      print "    - %s" % key







  ######################################################################
  #  STRING COMPRESSION (ALPHA!)
  ######################################################################

  if options.compressStrings:
    print
    print "  STRING COMPRESSION (ALPHA!):"
    print "----------------------------------------------------------------------------"

    print "  * Searching for string instances..."

    compressedStrings = {}

    for fileId in sortedIncludeList:
      if options.verbose:
        print "    - %s" % fileId

      for token in fileDb[fileId]["tokens"]:
        if token["type"] != "string":
          continue

        if token["detail"] == "doublequotes":
          compressSource = "\"%s\"" % token["source"]
        else:
          compressSource = "'%s'" % token["source"]

        if not compressedStrings.has_key(compressSource):
          compressedStrings[compressSource] = 1
        else:
          compressedStrings[compressSource] += 1


    if options.verbose:
      print "  * Sorting strings..."

    compressedList = []

    for compressSource in compressedStrings:
      compressedList.append({ "source" : compressSource, "usages" : compressedStrings[compressSource] })

    pos = 0
    while pos < len(compressedList):
      item = compressedList[pos]
      if item["usages"] <= 1:
        compressedList.remove(item)

      else:
        pos += 1

    compressedList.sort(lambda x, y: y["usages"]-x["usages"])

    print "  * Found %s string instances" % len(compressedList)

    if options.verbose:
      print "  * Building replacement map..."

    compressMap = {}
    compressCounter = 0
    compressJavaScript = "QXS%s=[" % pkgid

    for item in compressedList:
      if compressCounter != 0:
        compressJavaScript += ","

      compressMap[item["source"]] = compressCounter
      compressCounter += 1
      compressJavaScript += item["source"]

    compressJavaScript += "];"

    additionalOutput.append(compressJavaScript)

    print "  * Updating tokens..."

    for fileId in sortedIncludeList:
      if options.verbose:
        print "    - %s" % fileId

      for token in fileDb[fileId]["tokens"]:
        if token["type"] != "string":
          continue

        if token["detail"] == "doublequotes":
          compressSource = "\"%s\"" % token["source"]
        else:
          compressSource = "'%s'" % token["source"]

        if compressSource in compressMap:
          token["source"] = "QXS%s[%s]" % (pkgid, compressMap[compressSource])
          token["detail"] = "compressed"





  ######################################################################
  #  TOKEN STORAGE
  ######################################################################

  if options.storeTokens:
    print
    print "  TOKEN STORAGE:"
    print "----------------------------------------------------------------------------"

    if options.tokenOutputDirectory == None:
      print "    * You must define the token directory!"
      sys.exit(1)

    else:
      options.tokenOutputDirectory = os.path.normpath(options.tokenOutputDirectory)

      # Normalizing directory
      if not os.path.exists(options.tokenOutputDirectory):
        os.makedirs(options.tokenOutputDirectory)

    print "  * Storing tokens..."

    for fileId in sortedIncludeList:
      if options.verbose:
        print "    - %s" % fileId

      tokenString = tokenizer.convertTokensToString(fileDb[fileId]["tokens"])
      tokenSize = len(tokenString) / 1000.0

      if options.verbose:
        print "    * writing tokens to file (%s KB)..." % tokenSize

      tokenFileName = os.path.join(options.tokenOutputDirectory, fileId + config.TOKENEXT)

      tokenFile = file(tokenFileName, "w")
      tokenFile.write(tokenString)
      tokenFile.flush()
      tokenFile.close()




  ######################################################################
  #  GENERATION OF API
  ######################################################################

  if options.generateApiDocumentation:
    print
    print "  GENERATION OF API:"
    print "----------------------------------------------------------------------------"

    if options.apiOutputDirectory == None:
      print "    * You must define the API output directory!"
      sys.exit(1)

    else:
      options.apiOutputDirectory = os.path.normpath(options.apiOutputDirectory)

      # Normalizing directory
      if not os.path.exists(options.apiOutputDirectory):
        os.makedirs(options.apiOutputDirectory)

    docTree = None

    print "  * Generating API tree..."

    for fileId in fileDb:
      if options.verbose:
        print "  - %s" % fieId

      docTree = docgenerator.createDoc(fileDb[fileId]["tree"], docTree)

    if docTree:
      print "  * Finalising tree..."
      docgenerator.postWorkPackage(docTree, docTree)

    if options.xmlApiOutputFilename:
      print "  * Writing XML API file..."

      xmlContent = "<?xml version=\"1.0\" encoding=\"" + options.encoding + "\"?>\n\n"
      xmlContent += tree.nodeToXmlString(docTree)

      filetool(options.apiOutputDirectory, options.xmlApiOutputFilename, xmlContent, options.encoding)

    if options.jsonApiOutputFilename:
      print "  * Writing JSON API file..."

      jsonContent = tree.nodeToJsonString(docTree)

      filetool(options.apiOutputDirectory, options.jsonApiOutputFilename, jsonContent, options.encoding)





  ######################################################################
  #  CREATE COPY OF RESOURCES
  ######################################################################

  if options.copyResources:

    print
    print "  CREATE COPY OF RESOURCES:"
    print "----------------------------------------------------------------------------"

    print "  * Preparing target configuration..."

    overrideList = []

    for overrideEntry in options.overrideResourceOutput:
      # Parse
      # fileId.resourceId:destinationDirectory
      targetSplit = overrideEntry.split(":")
      targetStart = targetSplit.pop(0)
      targetStartSplit = targetStart.split(".")

      # Store
      overrideData = {}
      overrideData["destinationDirectory"] = ":".join(targetSplit)
      overrideData["resourceId"] = targetStartSplit.pop()
      overrideData["fileId"] = ".".join(targetStartSplit)

      # Append
      overrideList.append(overrideData)

    print "  * Syncing..."

    for fileId in sortedIncludeList:
      filePath = fileDb[fileId]["path"]
      fileResources = fileDb[fileId]["resources"]

      if len(fileResources) > 0:
        print "    - Found %i resources in %s" % (len(fileResources), fileId)

        for fileResource in fileResources:
          fileResourceSplit = fileResource.split(":")

          resourceId = fileResourceSplit.pop(0)
          relativeDirectory = ":".join(fileResourceSplit)

          sourceDirectory = os.path.join(fileDb[fileId]["resourceInput"], relativeDirectory)
          destinationDirectory = os.path.join(fileDb[fileId]["resourceOutput"], relativeDirectory)

          # Searching for overrides
          for overrideData in overrideList:
            if overrideData["fileId"] == fileId and overrideData["resourceId"] == resourceId:
              destinationDirectory = overrideData["destinationDirectory"]

          print "      - Copy %s => %s" % (sourceDirectory, destinationDirectory)

          try:
            os.listdir(sourceDirectory)
          except OSError:
            print "        - Source-Directory isn't readable!"
            continue

          for root, dirs, files in os.walk(sourceDirectory):

            # Filter ignored directories
            for ignoredDir in config.DIRIGNORE:
              if ignoredDir in dirs:
                dirs.remove(ignoredDir)

            # Searching for items (resource files)
            for itemName in files:

              # Generate absolute source file path
              itemSourcePath = os.path.join(root, itemName)

              # Extract relative path and directory
              itemRelPath = itemSourcePath.replace(sourceDirectory + os.sep, "")
              itemRelDir = os.path.dirname(itemRelPath)

              # Generate destination directory and file path
              itemDestDir = os.path.join(destinationDirectory, itemRelDir)
              itemDestPath = os.path.join(itemDestDir, itemName)

              # Check/Create destination directory
              if not os.path.exists(itemDestDir):
                os.makedirs(itemDestDir)

              # Copy file
              if options.verbose:
                print "      - Copying: %s => %s" % (itemSourcePath, itemDestPath)

              shutil.copyfile(itemSourcePath, itemDestPath)






  ######################################################################
  #  GENERATION OF SETTINGS
  ######################################################################

  if options.generateSourceScript or options.generateCompiledScript:
    print
    print "  GENERATION OF SETTINGS:"
    print "----------------------------------------------------------------------------"

    print "  * Processing input data..."

    TypeFloat = re.compile("^([0-9\-]+\.[0-9]+)$")
    TypeNumber = re.compile("^([0-9\-])$")

    settingsStr = ""

    # If you change this, change this in qx.Settings and qx.OO, too.
    settingsStr += 'if(typeof qx==="undefined"){var qx={_UNDEFINED:"undefined",_LOADSTART:(new Date).valueOf()};}'

    if options.addNewLines:
      settingsStr += "\n"

    # If you change this, change this in qx.Settings, too.
    settingsStr += 'if(typeof qx.Settings===qx._UNDEFINED){qx.Settings={_userSettings:{},_defaultSettings:{}};}'

    if options.addNewLines:
      settingsStr += "\n"

    for setting in options.setting:
      settingSplit = setting.split(":")
      settingKey = settingSplit.pop(0)
      settingValue = ":".join(settingSplit)

      settingKeySplit = settingKey.split(".")
      settingKeyName = settingKeySplit.pop()
      settingKeySpace = ".".join(settingKeySplit)

      checkStr = 'if(typeof qx.Settings._userSettings["%s"]===qx._UNDEFINED){qx.Settings._userSettings["%s"]={};}' % (settingKeySpace, settingKeySpace)
      if not checkStr in settingsStr:
        settingsStr += checkStr

        if options.addNewLines:
          settingsStr += "\n"

      settingsStr += 'qx.Settings._userSettings["%s"]["%s"]=' % (settingKeySpace, settingKeyName)

      if settingValue == "false" or settingValue == "true" or TypeFloat.match(settingValue) or TypeNumber.match(settingValue):
        settingsStr += '%s' % settingValue

      else:
        settingsStr += '"%s"' % settingValue.replace("\"", "\\\"")

      settingsStr += ";"

      if options.addNewLines:
        settingsStr += "\n"

      print settingsStr









  ######################################################################
  #  GENERATION OF SOURCE VERSION
  ######################################################################

  if options.generateSourceScript:
    print
    print "  GENERATION OF SOURCE SCRIPT:"
    print "----------------------------------------------------------------------------"

    if options.sourceOutputDirectory == None:
      print "    * You must define the source output directory!"
      sys.exit(1)

    else:
      options.sourceOutputDirectory = os.path.normpath(options.sourceOutputDirectory)

    print "  * Generating includer..."

    sourceOutput = settingsStr

    if sourceOutput != "" and options.addNewLines:
      settingsStr += "\n"

    if options.addNewLines:
      for fileId in sortedIncludeList:
        sourceOutput += 'document.write(\'<script type="text/javascript" src="%s%s"></script>\');\n' % (os.path.join(fileDb[fileId]["webSourcePath"], fileId.replace(".", os.sep)), config.JSEXT)

    else:
      includeCode = ""
      for fileId in sortedIncludeList:
        includeCode += '<script type="text/javascript" src="%s%s"></script>' % (os.path.join(fileDb[fileId]["webSourcePath"], fileId.replace(".", os.sep)), config.JSEXT)
      sourceOutput += "document.write('%s');" % includeCode

    print "  * Saving includer output as %s..." % options.sourceOutputFilename
    filetool(options.sourceOutputDirectory, options.sourceOutputFilename, sourceOutput, options.encoding)






  ######################################################################
  #  GENERATION OF COMPILED VERSION
  ######################################################################

  if options.generateCompiledScript:
    print
    print "  GENERATION OF COMPILED SCRIPT:"
    print "----------------------------------------------------------------------------"

    compiledOutput = settingsStr + "".join(additionalOutput)

    print "  * Compiling tokens..."

    if options.compiledScriptFile == None:
      print "    * You must define the compiled script file!"
      sys.exit(1)

    else:
      options.compiledScriptFile = os.path.normpath(options.compiledScriptFile)

    for fileId in sortedIncludeList:
      if options.verbose:
        print "    - %s" % fileId

      compiledFileContent = compile.compile(fileDb[fileId]["tokens"], options.addNewLines)

      if options.addFileIds:
        compiledOutput += "/* ID: " + fileId + " */\n" + compiledFileContent + "\n"
      else:
        compiledOutput += compiledFileContent

    print "  * Saving compiled output as %s..." % options.compiledScriptFile
    filetool(options.compiledScriptFile, compiledOutput, options.encoding)







######################################################################
#  MAIN LOOP
######################################################################

if __name__ == '__main__':
  try:
    main()

  except KeyboardInterrupt:
    print "  * Keyboard Interrupt"
    sys.exit(1)
