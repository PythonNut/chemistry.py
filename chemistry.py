import abc
import collections
import string

class Element(metaclass=abc.ABCMeta):
    pass

class Atom(object):
    def __init__(self, options):
        props = {
            "number"            : int,
            "symbol"            : str,
            "name"              : str,
            "mass"              : float,
            "exact_mass"        : float,
            "ionization"        : float,
            "electron_affinity" : float,
            "electronegativity" : float,
            "radius_vdw"        : float,
            "radius_covalent"   : float,
            "boiling_point"     : float,
            "melting_point"     : float,
            "block"             : str,
            "period"            : int,
            "group"             : str,
            "family"            : str,
            "electron_config"   : str
        }
        
        for prop in options:
            if prop not in props:
                raise AttributeError("Unknown property " + str(prop))
        
        for prop in props:
            if prop in options:
                setattr(self, prop, props[prop](options[prop]))
            else:
                setattr(self, prop, None)
                
        # more properties to come
    
    def __repr__(self):
        return self.symbol

    __str__ = __repr__
    
Element.register(Atom)

class Lookup(object):
    number = {}
    name   = {}
    symbol = {}
    
    @classmethod
    def lookup(self, item):
        if item in self.number:
            return self.number[item]
        elif item in self.name:
            return self.name[item]
        elif item in self.symbol:
            return self.symbol[item]
        
        raise ValueError("No such element "+str(item))


def build_table():
    import xml.etree.cElementTree as ET

    tree = ET.ElementTree(file="bodr-10/elements/elements.xml")
    root = tree.getroot()

    keymap = {
        "bo:atomicNumber"             : ("number",            "text"),
        "bo:symbol"                   : ("symbol",            "value"),
        "bo:name"                     : ("name",              "value"),
        "bo:mass"                     : ("mass",              "text"),
        "bo:exactMass"                : ("exact_mass",        "text"),
        "bo:radiusCovalent"           : ("radius_covalent",   "text"),
        "bo:radiusVDW"                : ("radius_vdw",        "text"),
        "bo:ionization"               : ("ionization",        "text"),
        "bo:electronAffinity"         : ("electron_affinity", "text"),
        "bo:electronegativityPauling" : ("electronegativity", "text"),
        "bo:boilingpoint"             : ("boiling_point",     "text"),
        "bo:meltingpoint"             : ("melting_point",     "text"),
        "bo:group"                    : ("group",             "text"),
        "bo:periodTableBlock"         : ("block",             "text"),
        "bo:period"                   : ("period",            "text"),
        "bo:family"                   : ("family",            "text"),
        "bo:electronicConfiguration"  : ("electron_config",   "text"),
    }

    for element in root[2:]:
        properties = {}
        for property in element:
            key = property.attrib["dictRef"]
            if key not in keymap:
                continue
            key = keymap[key]
            if key[1] == "text":
                properties[key[0]] = property.text
            else:
                properties[key[0]] = property.attrib[key[1]]

        atom = Atom(properties)
        globals()[properties["symbol"]] = atom
        Lookup.number[properties["number"]] = atom
        Lookup.name[properties["name"]] = atom
        Lookup.symbol[properties["symbol"]] = atom

build_table()

class Formula(object):
    def __init__(self, symbols, count=1, charge=0):
        # print("push "+symbols)
        self.count   = count
        self.charge  = charge
        self.symbols = []
        
        if isinstance(symbols, str):
            current_symbol = []
            openparens = 0
            detectparen = False
            multiplier = ""
            for char in symbols+"Q":
                if char == "(":
                    # print("opening")
                    detectparen = True
                    openparens += 1
                    if current_symbol != []:
                        # print("D" + str(current_symbol))
                        if multiplier == "":
                            self.symbols.append(Lookup.lookup("".join(current_symbol)))
                        else:
                            multiplier = int(multiplier)
                            sym = Formula("".join(current_symbol), multiplier)
                            self.symbols.append(sym)
                           
                    current_symbol = []
                    multiplier = ""
                    continue

                elif char == ")":
                    # print("closing")
                    openparens -= 1
                    continue
                    
                # print("A"+char)
                if char in string.digits and openparens == 0:
                    # print("digit")
                    multiplier += char
                   
                elif openparens == 0:
                    # print("B")
                    if detectparen:
                        # print("C" + str(current_symbol))
                        if multiplier == "":
                            multiplier = 1
                        self.symbols.append(Formula("".join(current_symbol),multiplier))
                        current_symbol = [char]
                        detectparen = False
                        multiplier == ""

                    elif current_symbol != []:
                        # print("D" + str(current_symbol))
                        if multiplier == "":
                            self.symbols.append(Lookup.lookup("".join(current_symbol)))
                        else:
                            multiplier = int(multiplier)
                            sym = Formula("".join(current_symbol), multiplier)
                            self.symbols.append(sym)

                    current_symbol = [char]
                    multiplier = ""

                elif char in string.ascii_letters+string.digits:
                    current_symbol.append(char)
                        
            # print("pop")
                        
        elif isinstance(symbols, collections.Iterable):
            for symbol in symbols:
                if isinstance(symbol, (Element,Formula)):
                    self.symbols.append(symbol)
                else:
                    self.symbols.append(Lookup.lookup(symbol))
    
    def __str__(self):
        string = []
        for symbol in self.symbols:
            string.append(str(symbol))
        
        if self.count != 1:
            if len(self.symbols) > 1:
                string = ["("] + string + [")"]
            string += [str(self.count)]
            
        if self.charge != 0:
            if self.charge < 0:
                string += ["(" + str(self.charge) + "-)"]
            else:
                string += ["(" + str(self.charge) + "+)"]
            
        return "".join(string)
        
    __repr__ = __str__
        
