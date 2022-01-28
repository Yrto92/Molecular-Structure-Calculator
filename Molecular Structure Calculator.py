# -*- coding: utf-8 -*-
"""Untitled2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1yimR3XzeMpI1zW7WGw1u0DtSXqoOeoUY
"""

!pip install periodictable
!pip install mendeleev

import periodictable as pt
from mendeleev import element

periodic_table_list = list(pt.elements)[1:]

periodic_table_dict = {}
for i in periodic_table_list:
  symbol = str(i)
  oxistates = [o for o in element(symbol).oxistates if o] #we cant have None's as oxistates
  oxistates.sort(key = lambda o: (-abs(o), o))
  periodic_table_dict[symbol] = tuple(oxistates)

#manually handling special cases:

#is the first noble gas found to form true chemical compund
periodic_table_dict["Xe"] = (8, 6, 4, 2)

#special case for carbon, make oxistate 2 unfavorable
unfavor = "unfavor"
periodic_table_dict["C"] = (-4, 4)
periodic_table_dict[("C", unfavor)]= (2,)

############################################################################
############################################################################
class Atom:

  _id : int                        #this itom ID (unique number)
  _symbol : str                    #the atom symbol
  _bonds : int                     #the number of bonds that this atom can still create
  _bonds_list : list               #the list of the other bonded atoms
                    
  ############################################################################
  # simple initialization, where the bond_list is set to empty
  def __init__(self, id : int, symbol : str, bonds : int):
    self._id = id
    self._symbol = symbol
    self._bonds = bonds
    self._bonds_list = []

  ############################################################################
  # returns the unique id
  def id(self) -> int:
    return self._id

  ############################################################################
  # returns the chemical symbol
  def symbol(self) -> str:
    return self._symbol

  ############################################################################
  # returns the current number of available bonds
  def bonds(self) -> int:
    return self._bonds

  ############################################################################
  # returns the current number of available bonds
  def bonds_list(self) -> int:
    return self._bonds_list

  ############################################################################
  # returns the current number of available bonds
  def is_in_bonds_list(self, n : int) -> bool:
    return n in self._bonds_list

  ############################################################################
  # bond between this Atom and other uniqe id
  def bond(self, id : int, bonds : int):
    self._bonds_list.extend([id] * abs(bonds))
    self._bonds_list.sort()
    self._bonds += bonds

  ############################################################################
  # unbond between this Atom and other uniqe id
  def unbond(self, id : int, bonds : int):
    self._bonds_list = [i for i in self._bonds_list if i != id]
    self._bonds -= bonds

  ############################################################################
  # returns if the atom is bonded to other atom(s)
  def is_bonded(self) -> bool:
    return len(self._bonds_list) > 0

  ############################################################################
  #string representation of atom
  def __str__(self) -> str:
    bonds_list_str = "{" + ','.join([f"{link:2}" for link in self._bonds_list]) + "}"
    ion_str = f"<{self._bonds:+2}>" if self._bonds != 0 else ""
    return f"[{self._id:2}] {self._symbol:2} {ion_str:5} {bonds_list_str:13}"

import networkx as nx

############################################################################
############################################################################
class ChemisteryFormulae:

    _periodic_table_dict : dict
    _formulae            : str
    _symbols             : list
    _atoms               : list
    _n_symbols           : int

    _verbose_count       : int
    #_verbose : function to either _debug_pass/_debug

    ############################################################################
    #use predefined periodic table dictionary and formulae, use debug to print console information
    def __init__(self, periodic_table_dict : dict, formulae : str, debug : int = 0):

      if not formulae:
        raise Exception("Formulae was not given")

      if not periodic_table_dict:
        raise Exception("Elements dictionary was not given")

      self._formulae = formulae
      self._periodic_table_dict = periodic_table_dict
      self._atoms = []
      self._verbose_count = 0
      self._verbose = self._debug_pass
      
      if debug > 0:
        self._verbose_count = debug
        self._verbose = self._debug
      
      #convert the formulae to a sequence of atoms
      self._symbols = self._split(formulae)
      self._n_symbols = len(self._symbols)  #saving it to save time
      
      #build the molecule from the atoms, using only preffered carbon oxistates
      if not self._moleculize():
        raise Exception("Unable to form a molecule")

    ############################################################################
    def _debug(self, n, caption, atom_a : Atom = None, atom_b : Atom = None):

      if self._verbose_count > 0:

        self._verbose_count -= 1

        atom_a_str = str(atom_a) if atom_a else ""
        atom_b_str = str(atom_b) if atom_b else ""
        print("debug:" + "    " * n + f"{atom_a_str:20}  {atom_b_str:20}" + "; " + caption)

    ############################################################################
    def _debug_pass(self, n, caption, atom_a : Atom = None, atom_b : Atom = None):
      pass

    ############################################################################
    # split the formulae string to symbol tokens based on the dictionary
    def _split(self, formulae : str) -> list: 

      #deal with parenthesis
      while '(' in formulae and ')' in formulae:
        right = formulae.index(')')
        left = formulae[:right].rindex('(')

        if left >= right:
          raise Exception("Bad formulae parenthesis")

        parenthesis = formulae[left + 1 : right]

        #find how many times the parenthesis should duplicate
        digits = None
        right += 1
        while right < len(formulae) and formulae[right].isdigit():

          if not digits:
            digits = formulae[right]
          else:
            digits += formulae[right]
          
          right += 1
        
        if not digits:
          digits = "1"

        #duplicate the parenthesis
        formulae = formulae[:left] + parenthesis * int(digits) + formulae[right:]
        #print(f"formulae: {formulae}")

      #build sets of symbols
      two_character_element_set = set(element_key for element_key in self._periodic_table_dict.keys() if len(element_key) == 2 and isinstance(element_key, str))
      one_character_element_set = set(element_key for element_key in self._periodic_table_dict.keys() if len(element_key) == 1 and isinstance(element_key, str))

      #split formulae into tokens:
      atoms = []      
      while formulae:

        atom = None
  
        #two character symbol?
        if len(formulae) >= 2:  
          if formulae[:2] in two_character_element_set:
            atom = formulae[:2]
            formulae = formulae[2:]

        #one character symbol?
        if atom is None: #if it's not two characters, maybe it's one?
          if formulae[0] in one_character_element_set:
            atom = formulae[:1]
            formulae = formulae[1:]

        #did not find a symbol
        if atom is None:
          raise Exception("could not find elements in the beggining of formulae:" + formulae)

        #do we have digits?
        digits = None
        while formulae and formulae[0].isdigit():
          if not digits:
            digits = formulae[0]
          else:
            digits += formulae[0]
          formulae = formulae[1:]
        
        if not digits:
          digits = "1"

        #add the symbol to the list
        atoms.extend([atom] * int(digits))

      if len(atoms) <= 0:
        raise Exception("did not find any elements in the formulae")

      return atoms

    ############################################################################
    # recursive function that builds the molecule
    # n, the index in the symbols_list to add
    def _moleculize(self, n : int = 0) -> bool:

      #find available bonds:
      open_atoms = [atom.id() for atom in self._atoms if atom.bonds() != 0]

      ##########################################################################
      #no more atoms to add?
      if n >= self._n_symbols:
                
        if len(open_atoms) <= 0:  #no open bonds?
          #if we have a single molecule with no left bonds, we are ok!
          return n == len(self._expand_molecule(0))  

        self._verbose(n, "enter all options")  

        #try to bond all open options:
        for a in open_atoms:
          for b in open_atoms:

            if a >= b:
              continue

            if self._bond(n, a, b):
              return True

        self._verbose(n, "left  all options")  

        return False
    
      ##########################################################################
      #add a new atom (n < self._n_symbols)
      symbol_n = self._symbols[n]

      #get the bonding options
      symbol_n_bonds = self._periodic_table_dict[symbol_n]

      ##########################################################################
      #no open bonds?
      if len(open_atoms) <= 0:

        if n > 0:  #the first atom is always free
          return False

        #try favorable bonds first
        if self._atom(n + 1, symbol_n, symbol_n_bonds):
          return True

        #try unfavorable bonds second
        if not ((symbol_n, unfavor) in self._periodic_table_dict):
          return False

        symbol_n_bonds = self._periodic_table_dict[(symbol_n, unfavor)]

        if self._atom(n + 1, symbol_n, symbol_n_bonds):
          return True

        return False        

      ##########################################################################
      #try a single bond, future implementation may try to bond more than a single bond
      for bonds_n in symbol_n_bonds:
        
        for a in reversed(open_atoms):

          bonds_a = self._atoms[a].bonds()

          #can connect?   (have different bond signs)            
          if bonds_a * bonds_n >= 0:
            continue
          
          #add the new atom
          atom_n = Atom(len(self._atoms), symbol_n, bonds_n)
          self._atoms.append(atom_n)

          if self._bond(n + 1, a, atom_n.id()):
            return True

          self._atoms.pop()

      ##########################################################################
      #finally, add an unbonded atom, maybe it'll bond at the end
      if self._atom(n + 1, symbol_n, symbol_n_bonds):
        return True

      ##########################################################################
      #do we have oxistated that we totaly unfavor?
      if not ((symbol_n, unfavor) in self._periodic_table_dict):
        return False

      symbol_n_bonds = self._periodic_table_dict[(symbol_n, unfavor)]

      for bonds_n in symbol_n_bonds:
                
        for a in reversed(open_atoms):

          bonds_a = self._atoms[a].bonds()

          #can connect?   (have different bond signs)            
          if bonds_a * bonds_n >= 0:
            continue
          
          #add the new atom
          atom_n = Atom(len(self._atoms), symbol_n, bonds_n)
          self._atoms.append(atom_n)

          if self._bond(n + 1, a, atom_n.id()):
            return True

          self._atoms.pop()

      ##########################################################################
      if self._atom(n + 1, symbol_n, symbol_n_bonds):
        return True

      return False

    ############################################################################
    # adds a 'free' atom to the molecule
    def _atom(self, n : int, symbol : str, symbol_bonds : list) -> bool:

      id = len(self._atoms)

      for bonds in symbol_bonds:
        
        self._atoms.append(Atom(id, symbol, bonds))
        self._verbose(n, "add free", self._atoms[id])

        #recursively call myself for next option
        if self._moleculize(n):   
          return True

        self._verbose(n, "rem free", self._atoms[id])
        self._atoms.pop()

      return False

    ############################################################################
    # bonds between two atoms in the molecule
    def _bond(self, n : int, a : int, b : int) -> bool:

      #already bonded?
      if self._atoms[b].is_in_bonds_list(a) or self._atoms[a].is_in_bonds_list(b):
        self._verbose(n, "rejected, already bonded", self._atoms[b])
        return False

      bonds_a = self._atoms[a].bonds()
      bonds_b = self._atoms[b].bonds()

      #can connect?  (have different bond signs, and they are not zero)            
      if bonds_a * bonds_b >= 0:
        self._verbose(n, "rejected, same bond direction", self._atoms[b], self._atoms[a])
        return False

      #limit the actual number of bonds with what's available
      bonds = min([abs(bonds_a), abs(bonds_b)])

      #try all bonds between (+1, bonds) or (-1, bonds)
      for new_bonds in range(1, bonds + 1):   #to favor stronger bonds: (bonds, 0, -1)
        
        signed_new_bonds = new_bonds if bonds_a < 0 else -new_bonds  #set the correct sign of 'bonds'

        #bond the two atoms
        self._atoms[a].bond(b, +signed_new_bonds)
        self._atoms[b].bond(a, -signed_new_bonds)
        self._verbose(n, f"bonded {b}", self._atoms[b], self._atoms[a])
        
        if n < self._n_symbols and self._is_seperate_molecule(b): #did we create a seperated molecule from less atoms?   
          self._verbose(n, "rejected, detected complete molecule", self._atoms[b], self._atoms[a])               
        
        elif self._moleculize(n): #recursively call _moleculize for next option
          return True

        #unbond the two atoms
        self._atoms[a].unbond(b, +signed_new_bonds)
        self._atoms[b].unbond(a, -signed_new_bonds)
        self._verbose(n, "unbonded", self._atoms[b], self._atoms[a])

      return False

    ############################################################################
    # returns a set will all the atoms that are linked to 'n' atom
    def _expand_molecule(self, n : int) -> set:

      molecule = set()
      atoms = set([n])

      while atoms:

        new_atoms = set()

        for n in atoms:     
          new_atoms = new_atoms | set(self._atoms[n].bonds_list())

        molecule = molecule | atoms
        atoms = new_atoms - molecule
        

      return molecule

    ############################################################################
    #return whether the 'molecule' from atom 'n' links has no more bonds
    def _is_seperate_molecule(self, n : int) -> bool:

      molecule = self._expand_molecule(n)
      for n in molecule:
          if self._atoms[n].bonds() != 0:
            return False

      return True

    ############################################################################
    def __str__(self):
      return '\n'.join([f"{atom}" for i, atom in enumerate(self._atoms)])

    ############################################################################
    def draw(self):
      
      M = nx.MultiGraph()    

      # running through elements to bond the different atoms
      for s, atom_s in enumerate(self._atoms):

        for b, atom_b in enumerate(self._atoms):

          if s >= b:  #just need to add the edge once
            continue

          #single, double, triple (or higher) bond?
          strength = atom_s.bonds_list().count(b)
 
          if strength > 0:
            M.add_edges_from( [(s, b)] * strength)


      pos     = nx.spring_layout(M)
      labels  = {atom.id(): atom.symbol() for atom in self._atoms}
      nx.draw_networkx_nodes(M, pos, node_size = 1200)
      nx.draw_networkx_labels(M, pos, labels, font_size = 22, font_color = "whitesmoke")

      ax = plt.gca()
      for e in M.edges:
        ax.annotate("",
                xy = pos[e[0]], xycoords = 'data',
                xytext = pos[e[1]], textcoords = 'data',
                arrowprops = dict(arrowstyle = "-", color = "0.5",
                                shrinkA = 5, shrinkB =5 ,
                                patchA = None, patchB = None,
                                connectionstyle = "arc3,rad=rrr".replace('rrr', str(0.3 * e[2])
                                ),
                                ),
                )

try:
  molecule = ChemisteryFormulae(periodic_table_dict, "CWQH3")
  print(molecule)
  
except Exception as e:
  print(e)

import matplotlib.pyplot as plt

try:

  user_input = input('Please insert your molecule formulae to receive its Lewis Model: ')
  molecule = ChemisteryFormulae(periodic_table_dict, user_input)

  #molecule = ChemisteryFormulae(periodic_table_dict, "(CH2)6")    #circular
  #molecule = ChemisteryFormulae(periodic_table_dict, "CH3CHCH2")  #double bond
  #molecule = ChemisteryFormulae(periodic_table_dict, "CH3CH2OH")  #ethanol
  
  #sets a 'good' phisical size for the image output
  plt.rcParams["figure.figsize"] = (12, 12)

  molecule.draw()
  #print(molecule)

  plt.axis("off")
  plt.show()

except Exception as e:
  print(e)