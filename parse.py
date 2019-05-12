#!/usr/bin/python
import sys
import re
import io
import itertools as IT
import xml.dom.minidom as xdm
from xml.etree import ElementTree as ET

PY2 = sys.version_info[0] == 2
StringIO = io.BytesIO if PY2 else io.StringIO


csplit=lambda test:\
    [p.replace("\"","") for p in re.split("( |\\\".*?\\\"|'.*?')", test) if p.strip()]

#lsta slow kluczowych
nss_fdict = dict()

def validateXML(content):
    try:
        tree = ET.fromstring(content)
    except ET.ParseError as err:
        lineno, column = err.position
        line = next(IT.islice(StringIO(content), lineno))
        caret = '{:=>{}}'.format('^', column)
        err.msg = '{}\n{}\n{}'.format(err, line, caret)
        raise
    return tree

def indifystring(s,d):
    c = min([ len( a ) - len( a.lstrip() ) for a in s[1:].rstrip().split("\n") ])
    if not c: return s
    return re.sub("(?m)^\s{"+str(c)+"}", "\t" * d,s)


def makeXmlPrettyAgain(uglyXml):
    return uglyXml
    xml = xdm.parseString(re.sub("(?m)^\s+","",uglyXml))
    return xml.toprettyxml()
#dekorator
def nssfunc(method):
    def m1(args):
        return method(csplit(args.\
            replace(">","&gt;").\
            replace("<","&lt;")
            ))

    nss_fdict[ method.__name__[1:] ] = m1
    return m1

#funkcje skryptu

def ns_simple(arg):
    yield """
        <simpleinstruction>
            <text>{0}</text>
            <comment></comment>
        </simpleinstruction>""".format(arg)

	
    try:
        yield ( 'var', arg[:arg.index(':=')].strip() )
    except: pass


@nssfunc
def _begin(args):
    yield """
        <!DOCTYPE nsscheme>
        <nsscheme type="sequence">
            <position>
                <x>4</x>
                <y>30</y>
            </position>
            <size>
                <width>240</width>
                <height>180</height>
            </size>
            <name>{1}</name>
            <comment></comment>
            <author>{0}</author>
            <pascalCode contains="yes"/>
            <checkSyntax enabled="yes"/>
    """.format(*args)
    yield ('{variables}')
    #yield ('ind',1)
    yield """
        <sequence>
    """

@nssfunc
def _set(args):
    yield """
        <simpleinstruction>
            <text>{0}:={1}</text>
            <comment></comment>
        </simpleinstruction>""".format(\
            args[0],
            args[1]+''.join(args[2:])\
        )
    yield ('var',args[0])

@nssfunc
def _while(args):
    yield """
        <iteration>
            <condition>
                <text>{0}</text>
                <comment></comment>
            </condition>
            <loop>
                <sequence>
    """.format(''.join(args))
    #yield ('ind',2)

@nssfunc
def _done(args):
    #yield ('ind',-2)
    yield """
                </sequence>
            </loop>
        </iteration>
    """

@nssfunc
def _get(args):
    yield """
        <inputinstruction>
            <text>{0}</text>
            <comment></comment>
        </inputinstruction>
    """.format(", ".join(args))
    for a in args:
        yield ("var",a)

@nssfunc
def _if(args):
    yield """
    <selection instructionsheight="289" conditionheight="56">
        <condition>
            <text>{0}</text>
            <comment></comment>
        </condition>
        <ontrue>
            <sequence>
    """.format(" ".join(args))
    yield ('if',1)

@nssfunc
def _else(args):
    #yield ('ind',-1)
    yield """
                </sequence>
            </ontrue>
        <onfalse>
            <sequence>
    """
    yield ("else",0)

@nssfunc
def _fi(args):
    #yield ('ind',-2)
    yield """
                </sequence>
            </on{0}>
        </selection>
    """
    yield ("fi",0)
    yield ("if",-1)

@nssfunc
def _echo(args):
    yield """
    <outputinstruction>
        <comment></comment>
        <text>{0}</text>
    </outputinstruction>
    """.format(", ".join(args))

@nssfunc
def _do(args):
    pass

eq = lambda x: lambda x,y = x: x==y

class nsstranslator:
    def __init__(self,a):
        self.rawcode = list()
        self.code = list()
        self.variables = set()
        self.instructions=list(map(\
            lambda x: \
                x.lstrip().split(" ",1) + ['',],\
            a.replace(";","\n").split("\n") \
        ))
        #self.printcmds()

    def genVariables(self):
        return "<variables>"+"\n".join(["""
            <variable>
                <name>{0}</name>
                <type><double/></type>
                <value>0</value>
            </variable>
          """.format(v) for v in self.variables ])+"\n</variables>"

    def generate(self):

        for stuff in self.instructions:
            try:
                function,args = stuff[:2]
                self.rawcode += list(nss_fdict[function](args))
            except:
                s=" ".join(stuff)
                if not re.sub("\s+","",s): continue
                self.rawcode +=	ns_simple(s)
            #print("function",function)

        self.rawcode +=("</sequence>\n</nsscheme>\n",)
        nif = ind = 0
        nelse = dict()
        for a in self.rawcode:
            try:
                thing, arg = a
                th = eq(thing) 
                if th("var") : self.variables.add(arg)
                if th("if") : nif += arg
                if th("else"): nelse[nif] = True
                if th("fi"):
                    if nelse.get(nif):
                        del nelse[nif]
                        self.code[-1] = self.code[-1].format("false")
                    else:
                        self.code[-1] = self.code[-1].format("true")
                continue
            except: pass
            #self.code.append(indifystring(a,ind))
            self.code.append(a)

        #definicja zmiennych
        self.code[self.code.index('{variables}')] = \
            self.genVariables()

        self.finalxml = re.sub("(?m)^\s+","","\n".join(self.code))
        i = 0
        #for x in self.finalxml.split("\n"):
        #    print(i,x)
        #    i+=1
        print(self.finalxml)
        validateXML(self.finalxml)
        #validateXML(open("schemat0.nss").read())

if __name__ == "__main__":
    f=open(sys.argv[1],'r')
    t=nsstranslator(f.read())
    t.generate()
