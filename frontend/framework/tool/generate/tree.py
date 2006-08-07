#!/usr/bin/env python

class NodeAccessException (Exception):
  def __init__ (self, msg, node):
    Exception.__init__(self, msg)
    self.node = node


class Node:
  def __init__ (self, type):
    self.type = type

  def hasAttributes(self):
    return hasattr(self, "attributes")

  def set(self, key, value):
    """Sets an attribute"""
    if not isinstance(value, basestring):
      raise NodeAccessException("'value' is no string: " + str(value), self)
    if not self.hasAttributes():
      self.attributes = {}
    self.attributes[key] = value
    return self

  def get(self, key, mandatory = True):
    value = None
    if hasattr(self, "attributes") and key in self.attributes:
      value = self.attributes[key]

    if value != None:
      return value
    elif mandatory:
      raise NodeAccessException("Node " + self.type + " has no attribute " + key, self)

  def remove(self, key):
    del self.attributes[key]
    if len(self.attributes) == 0:
      del self.attributes

  def hasChildren(self):
    return hasattr(self, "children")

  def addChild(self, childNode, index = None):
    if childNode:
      if not self.hasChildren():
        self.children = []
      if index != None:
        self.children.insert(index, childNode)
      else:
        self.children.append(childNode)
      childNode.parent = self
    return self

  def removeChild(self, childNode):
    if self.hasChildren():
      self.children.remove(childNode)
      childNode.parent = None
      if len(self.children) == 0:
        del self.children

  def getChild(self, type, mandatory = True):
    if self.hasChildren():
      for child in self.children:
        if child.type == type:
          return child
    if mandatory:
      raise NodeAccessException("Node " + self.type + " has no child with type " + type, self)

  def getChildByAttribute(self, key, value, mandatory = True):
    if self.hasChildren():
      for child in self.children:
        if child.get(key) == value:
          return child

    if mandatory:
      raise NodeAccessException("Node " + self.type + " has no child with attribute " + key + " = " + value, self)

  def getFirstChild(self, mandatory = True):
    if self.hasChildren():
      return self.children[0]

    if mandatory:
      raise NodeAccessException("Node " + self.type + " has no children", self)

  def addListChild(self, listName, childNode):
    listNode = self.getChild(listName, False)
    if not listNode:
      listNode = Node(listName)
      self.addChild(listNode)
    listNode.addChild(childNode)

  def getListChildByAttribute(self, listName, key, value, mandatory = True):
    listNode = self.getChild(listName, False)
    if listNode:
      return listNode.getChildByAttribute(key, value, mandatory)

    if mandatory:
      raise NodeAccessException("Node " + self.type + " has no child " + listName, self)

  def getFirstListChild(self, listName, mandatory = True):
    listNode = self.getChild(listName, False)
    if listNode:
      return listNode.getFirstChild(mandatory)

    if mandatory:
      raise NodeAccessException("Node " + self.type + " has no child " + listName, self)



def nodeToXmlString(node, prefix = "", childPrefix = "  ", newLine="\n"):
  hasText = False
  asString = prefix + "<" + node.type
  if node.hasAttributes():
    for key in node.attributes:
      if key == "text":
        hasText = True
      else:
        asString += " " + key + "=\"" + escapeXmlChars(node.attributes[key], True) + "\""

  if not node.hasChildren() and not hasText:
    asString += "/>" + newLine
  else:
    asString += ">"

    if hasText:
      if node.hasChildren():
        asString += newLine + prefix + "  "
      asString += "<text>" + escapeXmlChars(node.attributes["text"], False) + "</text>"

    if node.hasChildren():
      asString += newLine
      prefix = prefix + childPrefix
      for child in node.children:
        asString += nodeToXmlString(child, prefix, childPrefix, newLine)
      asString += prefix

    asString += "</" + node.type + ">" + newLine

  return asString



def nodeToJsonString(node, prefix = "", childPrefix = "  ", newLine="\n"):
  asString = prefix + '{type:"' + escapeJsonChars(node.type) + '"'

  if node.hasAttributes():
    asString += ',attributes:{'
    firstAttribute = True
    for key in node.attributes:
      if not firstAttribute:
        asString += ','
      asString += '"' + key + '":"' + escapeJsonChars(node.attributes[key]) + '"'
      firstAttribute = False
    asString += '}'

  if node.hasChildren():
    asString += ',children:[' + newLine

    firstChild = True
    prefix = prefix + childPrefix
    for child in node.children:
      asString += nodeToJsonString(child, prefix, childPrefix, newLine) + ',' + newLine
      firstChild = False

    # NOTE We remove the ',\n' of the last child
    if newLine == "":
      asString = asString[:-1] + prefix + ']'
    else:
      asString = asString[:-2] + newLine + prefix + ']'

  asString += '}'

  return asString



def escapeXmlChars(text, inAttribute):
  text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
  if inAttribute:
    text = text.replace("\"", "&quot;")
  return text



def escapeJsonChars(text):
  return text.replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
