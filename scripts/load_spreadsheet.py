#!/usr/bin/env python
#
#  Read and work with OLS Caritas 2014-2015 directory
#
import os, sys
import re
import csv
import argparse

# Configuration
school_year = "2016-17"

# Default inputs
directory_tmpl = "{year} directory.csv"
class_tmpl = "{year} classes.csv"

# Default outputs
class_roster_tmpl = "ols-classes-{year}.txt"
directory_by_class_tmpl = "ols-class-directory-{year}.txt"
directory_by_family_tmpl = "ols-family-directory-{year}.txt"
caritas_hours_spreadsheet_tmpl = "ols-family-hours-{year}.csv"
classmom_spreadsheet_tmpl = "contact-info-%s.csv"
mothers_tmpl = "mothers-{year}.csv"
vertical_response_spreadsheet_tmpl = "vertical-response-{year}.csv"

guys_first_sortkey = { 
    "Father": 0,
    "Brother": 1,
    "Grandfather": 2,
    "Uncle": 3,
    "Mother": 10,
    "Sister": 11,
    "Grandmother": 12,
    "Aunt": 13,
    "Guardian": 20 }

ladies_first_sortkey = { 
    "Mother": 0,
    "Sister": 1,
    "Grandmother": 2,
    "Aunt": 3,
    "Father": 10,
    "Brother": 11,
    "Grandfather": 12,
    "Uncle": 13,
    "Guardian": 20 }

# If True, private information will NOT be redacted.
no_hidden_fields = False

#######################################################################
# Helper functions
#######################################################################

def cleanup_zipcode(zipcode):
    try:
        return "%05d" % int(zipcode)
    except ValueError:
        return zipcode

def class_sortkey(classname):
    if classname.startswith("P"):
        return "00 " + classname
    elif classname.startswith("K"):
        return "01 " + classname
    else:
        return "02 " + classname

def is_couple(g1, g2):
    if g1.relation == "Father" and g2.relation == "Mother":
        return True
    elif g1.relation == "Mother" and g2.relation == "Father":
        return True
    elif g1.relation == "Grandfather" and g2.relation == "Grandmother":
        return True
    elif g1.relation == "Grandmother" and g2.relation == "Grandfather":
        return True
    elif g1.relation == "Uncle" and g2.relation == "Aunt":
        return True
    elif g1.relation == "Aunt" and g2.relation == "Uncle":
        return True
    else:
        return False

def group_key(persons):
    return "; ".join(sorted([p.key() for p in persons]))

grade_names = [
    ("Unknown", "??"),
    ("Pre-K 2.5", "PK2"),
    ("Pre-K 3", "PK3"),
    ("Pre-K 4", "PK4"),
    ("Kindergarten", "K"),
    ("First Grade", "1"),
    ("Second Grade", "2"),
    ("Third Grade", "3"),
    ("Fourth Grade", "4"),
    ("Fifth Grade", "5"),
    ("Sixth Grade", "6"),
    ("Seventh Grade", "7"),
    ("Eighth Grade", "8"),
]

gradelevel = {}
graderank = {}

for idx, item in enumerate(grade_names):
    name, level = item
    gradelevel[name] = level
    graderank[name] = "%02d" % idx

def redacted(field):
    """
    If the given value was marked "private", by enclosing it in
    square brackets, return the empty string.  Otherwise, return
    the value as is.
    """
    if not field or no_hidden_fields:
        return field
    if field.startswith("[") or field.endswith("]"):
        return ""
    else:
        return field

#######################################################################
# Classes
#######################################################################

class Student(object):
    def __init__(self, firstname, lastname, olsclass):
        self.firstname = firstname
        self.lastname = lastname
        self.olsclass = olsclass
        self.family = None
        self._id = None     # database id

    def key(self):
        return self.name(lastname_first=True)

    def name(self, lastname_first=False):
        if lastname_first:
            return self.lastname + ", " + self.firstname
        else:
            return self.firstname + " " + self.lastname

    def siblings(self):
        sibs = set(self.family.children)
        sibs.discard(self)
        return sibs

    def sortkey(self):
        return(class_sortkey(self.olsclass.key), self.firstname)

class Adult(object):
    def __init__(self, firstname, lastname, 
            email=None, homephone=None, cellphone=None):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.homephone = homephone
        self.cellphone = cellphone
        self.address = None
        self._id = None     # database id

    def key(self):
        return self.lastname + ", " + self.firstname

    def name(self, lastname_first=False):
        first, last = [redacted(f) for f in (self.firstname, self.lastname)]
        if not first and not last:
            return ""
        elif first and last:
            if lastname_first:
                return last + ", " + first
            else:
                return first + " " + last
        else:
            return first + last

class Staff(Adult):
    def __init__(self, firstname, lastname, role, 
            email=None, homephone=None, cellphone=None):
        Adult.__init__(self, firstname, lastname, email, homephone, cellphone)
        self.role = role
        self.olsclass = None

class Guardian(Adult):
    def __init__(self, firstname, lastname, relation, 
            email=None, homephone=None, cellphone=None):
        Adult.__init__(self, firstname, lastname, email, homephone, cellphone)
        if relation:
            self.relation = relation.capitalize()
        else:
            self.relation = "Guardian"
        self.family = None
        self._id = None     # database id

    def guys_first(self):
        return guys_first_sortkey[self.relation]

    def ladies_first(self):
        return ladies_first_sortkey[self.relation]

    def shortrelation(self):
        if self.relation == "Mother" or self.relation == "_mother":
            return "Mom"
        elif self.relation == "Father" or self.relation == "_father":
            return "Dad"
        else:
            return self.relation

class Address(object):
    def __init__(self, street, city, state, zipcode):
        self.street = street
        self.city = city
        self.state = state
        self.zipcode = cleanup_zipcode(zipcode)
        self.residents = []
        self._id = None     # database id

    def oneline(self):
        parts = []
        street, city, state, zipcode = [redacted(f) for f in (
            self.street, self.city, self.state, self.zipcode)]
        if street:
            parts.append(street)
        if city:
            parts.append(city)
        if state or zipcode:
            parts.append(" ".join((state, zipcode)))
        if parts:
            return ", ".join(parts)
        else:
            return ""

    def multiline(self):
        lines = []
        street, city, state, zipcode = [redacted(f) for f in (
            self.street, self.city, self.state, self.zipcode)]
        if street:
            lines.append(street)
        if city:
            if state or zipcode:
                lines.append(city + ", " + state + " " + zipcode)
            else:
                lines.append(city)
        if lines:
            return "\n".join(lines)
        else:
            return "(no address)"

    def address_line1(self):
        return self.street

    def address_line2(self):
        city, state, zipcode = [redacted(f) for f in (
            self.city, self.state, self.zipcode)]
        if city:
            if state or zipcode:
                return city + ", " + state + " " + zipcode
            else:
                return city
        else:
            return ""

class Family(object):
    def __init__(self, private, street, city, state, zipcode, email=None):
        self.address = Address(street, city, state, zipcode)
        self.email = email
        self.private = private
        self.guardians = []
        self.children = []
        self._name = None
        self._sortkey = None
        self._id = None     # database id

    def key(self):
        return group_key(self.guardians)

    def sortkey(self):
        if not self._sortkey:
            self.children.sort(key=Student.sortkey)
            self._sortkey = group_key(self.children)
        return self._sortkey

    def name(self):
        if not self._name:
            names = []
            for p in self.children + self.guardians:
                names.extend(p.lastname.split("-"))
            parts = []
            used = set()
            for name in names:
                if not name in used:
                    parts.append(name)
                    used.add(name)
            self._name = "-".join(parts)
        return self._name

    def add_guardian(self, adult):
        self.guardians.append(adult)
        self.guardians_sorted = False

    def parent_names(self, if_none=""):
        guardians = [g for g in self.guardians if g.name() != ""
                and not g.name().startswith("_")]
        if len(guardians) == 0:
            return if_none
        if len(guardians) == 1:
            return guardians[0].name()
        if len(guardians) == 2:
            (g1, g2) = (guardians[0], guardians[1])
            if g1.lastname == g2.lastname and is_couple(g1, g2):
                return g1.firstname + " & " + g2.firstname + " " + g2.lastname
            else:
                return g1.name() + " & " + g2.name()
        return " & ".join([g.name() for g in guardians])

    def children_names(self):
        last_names = set([child.lastname for child in self.children])
        if len(last_names) == 1:
            names = [child.firstname for child in self.children] 
            names[-1] += " " + self.children_last_name()
        else:
            names = [child.name() for child in self.children]
        if len(names) > 1:
            final = " and ".join((names[-2], names[-1]))
            names = names[:-2] + [final]
        return ", ".join(names)

    def child_with_grade(self, index=0, lastname_first=False):
        try:
            child = self.children[index]
            return "%s (%s)" % (child.name(lastname_first), child.olsclass.grade)
        except IndexError:
            return ""

    def children_with_grades(self, lastname_first=False):
        return "\n".join(["%s (%s)" % (c.name(lastname_first), c.olsclass.grade) 
            for c in self.children])

    def children_first_names(self):
        names = [c.firstname for c in self.children]
        if len(names) > 1:
            final = " and ".join((names[-2], names[-1]))
            names = names[:-2] + [final]
        return ", ".join(names)

    def children_last_name(self):
        return self.children[0].lastname

    def children_grade_levels(self):
        grades = [c.olsclass.gradelevel for c in self.children]
        return ",".join(grades)

    def guardian_relation(self, index=0):
        try:
            guard = self.guardians[index]
            return guard.relation
        except IndexError:
            return "Other"

    def guardian_name(self, index=0, lastname_first=False):
        try:
            guard = self.guardians[index]
            if guard.firstname.startswith("_"):
                return ""
            return guard.name(lastname_first)
        except IndexError:
            return ""

    def guardian_email(self, index=0):
        try:
            guard = self.guardians[index]
            return guard.email
        except IndexError:
            return ""

    def guardian_homephone(self, index=0):
        try:
            guard = self.guardians[index]
            return guard.homephone
        except IndexError:
            return ""

    def guardian_cellphone(self, index=0):
        try:
            guard = self.guardians[index]
            return guard.cellphone
        except IndexError:
            return ""

    def oneline_address(self):
        return self.address.oneline()

    def multiline_address(self):
        return self.address.multiline()

    def address_line1(self):
        return self.address.address_line1()

    def address_line2(self):
        return self.address.address_line2()

    def phone_numbers(self, sep=None):
        guardians = sorted(self.guardians, key=Guardian.ladies_first)
        lines = []
        homephone = None
        for g in guardians:
            ghome, gcell = [redacted(f) for f in (g.homephone, g.cellphone)]
            if ghome:
                if not homephone:
                    homephone = ghome
                elif ghome != homephone:
                    lines.append(ghome + " (%s home)" % g.shortrelation())
            if gcell:
                lines.append(gcell + " (%s cell)" % g.shortrelation())
        if homephone:
            lines.insert(0, homephone)
        if sep is None:
            return lines
        if lines:
            return sep.join(lines)
        else:
            return "(no phone numbers)"

    def emails(self, sep=None):
        guardians = sorted(self.guardians, key=Guardian.ladies_first)
        lines = []
        if self.email:
            lines.append(self.email)
        for g in guardians:
            if g.email:
                lines.append(g.email + " (%s)" % g.shortrelation())
        if sep is None:
            return lines
        if lines:
            return "\n".join(lines)
        else:
            return "(no email addresses)"

    def primary_phone(self):
        guardians = sorted(self.guardians, key=Guardian.ladies_first)
        for g in guardians:
            if g.homephone:
                return g.homephone
            if g.cellphone:
                return g.cellphone

    def primary_email(self):
        guardians = sorted(self.guardians, key=Guardian.ladies_first)
        lines = []
        if self.email:
            return self.email
        for g in guardians:
            if g.email:
                return g.email

class OLSClass(object):
    def __init__(self, key, title, teacher=None, aide=None, classmom=None, roster=[]):
        self.key = key
        self.title = title
        self.grade = re.sub(r" - \S+$", "", title)
        self.gradelevel = gradelevel[self.grade]
        self.rank = graderank[self.grade]
        self.teacher = teacher
        self.aide = aide
        self.classmom = classmom
        self.roster = roster
        self._id = None     # database id

    def add_staff(self, person):
        if person.role == "Teacher":
            self.teacher = person
        elif person.role == "Aide":
            self.aide = person
        elif person.role == "Classmom":
            self.classmom = person
        else:
            return
        person.olsclass = self

#######################################################################
# Functions
#######################################################################

def load_directory_data(csvfile):
    """
    Read student & family data from the CSV export of Maria's directory
    spreadsheet.  
    
    This function returns a list of dicts - one for each student - where
    the keys are just the column names from the spreadsheet. 
    """
    records = []    # a list of all records read in from the spreadsheet
    fieldnames = [] # the column names from the spreadsheet
    with open(csvfile, "r") as fp:
        dir_reader = csv.DictReader(fp, delimiter=",", quotechar='"')
        fieldnames = dir_reader.fieldnames  
        records = [row for row in dir_reader]
    return records

def load_class_data(csvfile):
    """
    Read information about the staff for each class from the CSV export
    of Maria's class spreadsheet.  
    
    This function returns a list of OLSClass objects (one for each class)
    and a list of the classnames, in the order they were recorded in the
    spreadsheet.
    """
    classes = {}            # class info, indexed by the class name
    classes_fieldnames = [] # the column names from the classes spreadsheet
    classnames = []         # class keys, in order listed in classes spreadsheet

    cls = OLSClass("", "Unknown")
    classnames.append("")
    classes[""] = cls

    with open(csvfile, "r") as fp:
        class_reader = csv.DictReader(fp, delimiter=",", quotechar='"')
        class_fieldnames = class_reader.fieldnames  
        for row in class_reader:
            if not row["class"]:
                continue
            key = row["class"]
            cls = OLSClass(key, row["class title"])
            classnames.append(key)
            classes[key] = cls
            if row["teacher"]:
                (firstname, lastname) = row["teacher"].split()
                teacher = Staff(firstname.strip(), lastname.strip(),
                        "Teacher", row["teacher e-mail"])
                cls.add_staff(teacher)
            if row["aide"]:
                (firstname, lastname) = row["aide"].split()
                aide = Staff(firstname.strip(), lastname.strip(),
                        "Aide")
                cls.add_staff(aide)
            if row["class mom"]:
                (firstname, lastname) = row["class mom"].split()
                classmom = Staff(firstname.strip(), lastname.strip(),
                        "Classmom", row["class mom e-mail"])
                cls.add_staff(classmom)
            print "%s - %s" % (cls.grade, cls.teacher.name())

    return (classes, classnames)

#######################################################################
# Reports
#######################################################################

def write_class_roster(outfile):
    """
    """
    lines = []
    lines.append("\nClasses")
    for classname in classnames:
        if len(class_roster[classname]) == 0:
            continue
        cls = classes[classname]
        if cls.teacher:
            lines.append("%s - %s" % (cls.grade, cls.teacher.name()))
        else:
            lines.append("%s - " % (cls.grade))
        if cls.aide:
            lines.append("Aide: " + cls.aide.name())
        if cls.classmom:
            lines.append("Class parent: " + cls.classmom.name())
        lines.append("")
        for student in class_roster[classname]:
            sibs = student.siblings()
            if sibs:
                lines.append("    " + student.name() + " *")
            else:
                lines.append("    " + student.name())
        lines.append("")
    lines.append("")
    with open(outfile, "w") as fp:
        fp.write("\n".join(lines))
    print "wrote", outfile

def lastname_sortkey(person):
    return person.lastname

def write_classmom_spreadsheets(outfile_template):
    """
    """
    for classname in classnames:
        if len(class_roster[classname]) == 0:
            continue
        cls = classes[classname]
        if cls.grade.startswith('Pre'):
            class_label = cls.grade + '-' + cls.teacher.lastname[0]
        else:
            class_label = cls.grade
        outfile = outfile_template % class_label
        outfile = outfile.replace("Pre-K", "PreK")
        outfile = outfile.replace(" ", "")
            
        with open(outfile, "w") as fp:
            wtr = csv.writer(fp)
            header = ["Child", "Parent1", "Email1", "Cell1", "Phone1",
                    "Parent2", "Email2", "Cell2", "Phone2",
                    ""]
            wtr.writerow(header)
            for student in class_roster[classname]:
                family = student.family
                if student.family.private:
                    family.guardians.sort(key=Guardian.ladies_first)
                    row = [student.name(),
                           family.guardian_name(0),
                           "",
                           "",
                           "",
                           family.guardian_name(1),
                           "",
                           "",
                           "",
                           "" ]
                else:
                    family.guardians.sort(key=Guardian.ladies_first)
                    row = [student.name(),
                           family.guardian_name(0),
                           family.guardian_email(0),
                           family.guardian_cellphone(0),
                           family.guardian_homephone(0),
                           family.guardian_name(1),
                           family.guardian_email(1),
                           family.guardian_cellphone(1),
                           family.guardian_homephone(1),
                           "" ]
                wtr.writerow(row)
        print "wrote", outfile

def write_directory_by_class(outfile):
    """
    """
    lines = []
    for classname in classnames:
        if len(class_roster[classname]) == 0:
            continue
        cls = classes[classname]
        lines.append("- " * 16)
        if cls.teacher:
            lines.append("%s - %s" % (cls.grade, cls.teacher.name()))
        else:
            lines.append("%s" % (cls.grade))
        lines.append("- " * 16)
        if cls.classmom:
            lines.append("Class parent: " + cls.classmom.name())
        if cls.aide:
            lines.append("Aide: " + cls.aide.name())
        lines.append("")
        for student in class_roster[classname]:
            if student.family.private:
                continue
            lines.append(student.name(lastname_first=True))
            lines.append(student.family.parent_names("(no parent names)"))
            lines.append(student.family.multiline_address())
            lines.append(student.family.phone_numbers(sep="\n"))
            lines.append(student.family.emails(sep="\n"))
            lines.append("")
    lines.append("")
    with open(outfile, "w") as fp:
        fp.write("\n".join(lines))
    print "wrote", outfile

def write_directory_by_family(outfile):
    """
    """
    lines = []

    for family in sorted(families.values(), key=Family.sortkey):
        family.children.sort(key=Student.sortkey, reverse=True) # oldest first
        if family.private:
            continue
        lines.append(family.children_with_grades(lastname_first=True))
        lines.append(family.parent_names("(no parent names)"))
        if family.private:
            lines.append("(contact information withheld)")
        else:
            lines.append(family.multiline_address())
            lines.append(family.phone_numbers(sep="\n"))
            lines.append(family.emails(sep="\n"))
        lines.append("")
    lines.append("")
    with open(outfile, "w") as fp:
        fp.write("\n".join(lines))
    print "wrote", outfile

def write_mothers_spreadsheet(outfile):
    """
    """
    with open(outfile, "w") as fp:
        wtr = csv.writer(fp)
        header = ["Guardian", "Children"]
        wtr.writerow(header)
        for family in sorted(families.values(), key=Family.sortkey):
            family.children.sort(key=Student.sortkey, reverse=True) # oldest first
            family.guardians.sort(key=Guardian.ladies_first)
            if family.guardians:
                g = family.guardians[0]
                if g.lastname != family.children_last_name():
                    row = [g.name(), 
                           family.children_names()]
                    wtr.writerow(row)
            else:
                print "!! no guardians for", family.children_last_name()
    print "wrote", outfile

def write_family_spreadsheet(outfile):
    """
    """
    with open(outfile, "w") as fp:
        wtr = csv.writer(fp)
        header = ["Family", "Parents", "Children", "Grades", 
                "Student1", "Student2", "Student3",
                "Address", "Address2",
                "Relation1", "Email1", "Cell1", "Phone1",
                "Relation2", "Email2", "Cell2", "Phone2",
                ""]
        wtr.writerow(header)
        for family in sorted(families.values(), key=Family.sortkey):
            family.children.sort(key=Student.sortkey, reverse=True) # oldest first
            family.guardians.sort(key=Guardian.ladies_first)
            row = [family.children_last_name(),
                   family.parent_names(),
                   family.children_names(),
                   family.children_grade_levels(), 
                   family.child_with_grade(0), 
                   family.child_with_grade(1), 
                   family.child_with_grade(2), 
                   family.address_line1(),
                   family.address_line2(),
                   family.guardian_relation(0),
                   family.guardian_email(0),
                   family.guardian_cellphone(0),
                   family.guardian_homephone(0),
                   family.guardian_relation(1),
                   family.guardian_email(1),
                   family.guardian_cellphone(1),
                   family.guardian_homephone(1),
                   "" ]
            wtr.writerow(row)
    print "wrote", outfile

def write_mailmerge_spreadsheet(outfile):
    """
    """
    with open(outfile, "w") as fp:
        wtr = csv.writer(fp)
        header = ["Email", "Relation", "Family", "Parents", "Children", "Grades", 
                "Student1", "Student2", "Student3",
                "Address",
                "Relation1", "Email1", "Cell1", "Phone1",
                "Relation2", "Email2", "Cell2", "Phone2",
                ""]
        wtr.writerow(header)
        for family in sorted(families.values(), key=Family.sortkey):
            family.children.sort(key=Student.sortkey, reverse=True) # oldest first
            family.guardians.sort(key=Guardian.ladies_first)
            for g in family.guardians: 
                if g.email:
                    row = [g.email, 
                           g.relation, 
                           family.children_last_name(),
                           family.parent_names(),
                           family.children_names(),
                           family.children_grade_levels(), 
                           family.child_with_grade(0), 
                           family.child_with_grade(1), 
                           family.child_with_grade(2), 
                           family.oneline_address(),
                           family.guardian_relation(0),
                           family.guardian_email(0),
                           family.guardian_cellphone(0),
                           family.guardian_homephone(0),
                           family.guardian_relation(1),
                           family.guardian_email(1),
                           family.guardian_cellphone(1),
                           family.guardian_homephone(1),
                           "" ]
                    wtr.writerow(row)
    print "wrote", outfile

#######################################################################
# Main code
#######################################################################

def parse_args(args):
    """
    Parse the commandline options.
    A namespace object is returned.
    """
    parser = argparse.ArgumentParser(
            "Create OLS school directory files from student and class data.")
    parser.add_argument("--student-file", dest="directory_file", 
            help="A CSV file containing student information")
    parser.add_argument("--class-file", dest="class_file",
            help="A CSV file containing class information")
    parser.add_argument("--year", dest="year", default=school_year,
            help="Populate database for Django app; don't create outputs")
    parser.add_argument("--django", dest="django", action="store_true",
            help="Populate database for Django app; don't create outputs")
    parser.add_argument("--dry-run", dest="dryrun", action="store_true",
            help="Process data, but don't create outputs.")
    parser.add_argument("--no-hidden", dest="nohidden", action="store_true",
            help="Don't redact private information")
    opt = parser.parse_args()

    if not opt.directory_file:
        opt.directory_file = directory_tmpl.format(year=opt.year)
    if not opt.class_file:
        opt.class_file = class_tmpl.format(year=opt.year)

    return opt

def main(args):
    global families, students, class_roster
    global classes, classnames
    global no_hidden_fields

    opt = parse_args(args)

    no_hidden_fields = opt.nohidden

    records = load_directory_data(opt.directory_file)
    (classes, classnames) = load_class_data(opt.class_file)

    # Loop over the records, creating Student, Guardian, and Family objects
    # to hold the data in a manageable form
    #
    families = {}  # each family, indexed by its unique "family key"
    students = []  # a list of all students

    class_roster = {}
    for classname in classnames:
        class_roster[classname] = []

    for rec in records:
        # Verify classnames and build class rosters
        classname = rec["Grade Level"]
        if not classname in classes:
            print "ERROR: %s %s class %s not in classes DB" % (
                    rec["First Name"], rec["Last Name"], classname)
        if not classname in class_roster:
            class_roster[classname] = []
        olsclass = classes.get(classname, "")

        # Create a Student object for this record
        student = Student(rec["First Name"], rec["Last Name"], olsclass)

        # Add this student to the list of all students
        students.append(student)

        # Add this student to their class
        class_roster[classname].append(student)

        # Create Guardian objects for this child's parents
        guardians = []
        if rec["Father"] or rec["Ftr Email"]:
            try:
                if rec["Father"]:
                    (lastname, firstname) = rec["Father"].split(",")
                else:
                    (lastname, firstname) = (student.lastname, "_father")
                father = Guardian(firstname.strip(), lastname.strip(), "Father",
                        rec["Ftr Email"], rec["Father Home Phone"], 
                        rec["Father cell phone"])
                guardians.append(father)
            except Exception as err:
                if not "deceased" in rec["Father"].lower():
                    print "ERROR: '%s' - %s" % (rec["Father"], err)
        if rec["Mother"] or rec["Mtr Email"]:
            try:
                if rec["Mother"]:
                    (lastname, firstname) = rec["Mother"].split(",")
                else:
                    (lastname, firstname) = (student.lastname, "_mother")
                mother = Guardian(firstname.strip(), lastname.strip(), "Mother", 
                        rec["Mtr Email"], rec["Mother Home Phone"], 
                        rec["Mother cell phone"])
                guardians.append(mother)
            except Exception as err:
                if not "deceased" in rec["Mother"].lower():
                    print "ERROR: '%s' - %s" % (rec["Mother"], err)
        if rec["Guardian"] or rec["Guardian Email"]:
            try:
                if rec["Guardian"]:
                    (lastname, firstname) = rec["Guardian"].split(",")
                else:
                    (lastname, firstname) = (student.lastname, "_guardian")
                relation = rec["Guardian Relation"]
                guardian = Guardian(firstname.strip(), lastname.strip(), relation,
                        rec["Guardian Email"], rec["Guardian Home Phone"], 
                        rec["Guardian cell phone"])
                guardians.append(guardian)
            except Exception as err:
                print "ERROR: '%s' - %s" % (rec["Guardian"], err)

        if not guardians:
            print "** No guardian names or emails for %s" % student.name()

        # Get the Family object for this family (or create a new one)
        fkey = group_key(guardians)
        if fkey in families:
            family = families[fkey]
        else:
            private = (rec.get("NO DIRECTORY", "") == "TRUE") 
            family = Family(private, rec["Street"], rec["City"], rec["State"],
                    rec["Zip"])
            family.guardians =  guardians
            for person in guardians:
                person.family = family
            families[fkey] = family

        # Add this student to their family
        family.children.append(student)
        student.family = family

    # Produce the directory
    #
    # classnames = sorted(class_roster.keys(), key=class_sortkey)
    for classname in classnames:
        class_roster[classname].sort(key=lastname_sortkey)

    print
    print "There are", len(students), "students in", len(families), "families"

    if opt.dryrun:
        return
    
    if opt.django:
        populate_database()
    else:
        write_output_files(opt)


def write_output_files(opt):
    # Outputs
    class_roster_file = class_roster_tmpl.format(year=opt.year)
    directory_by_class_file = directory_by_class_tmpl.format(year=opt.year)
    directory_by_family_file = directory_by_family_tmpl.format(year=opt.year)
    caritas_hours_spreadsheet_file = caritas_hours_spreadsheet_tmpl.format(year=opt.year)
    classmom_spreadsheet_file = classmom_spreadsheet_tmpl.format(year=opt.year)
    mothers_file = mothers_tmpl.format(year=opt.year)
    vertical_response_spreadsheet_file = vertical_response_spreadsheet_tmpl.format(year=opt.year)

    write_class_roster(class_roster_file)
    write_directory_by_class(directory_by_class_file)
    write_directory_by_family(directory_by_family_file)
    write_family_spreadsheet(caritas_hours_spreadsheet_file)
    write_mothers_spreadsheet(mothers_file)
    write_classmom_spreadsheets(classmom_spreadsheet_file)
    write_mailmerge_spreadsheet(vertical_response_spreadsheet_file)

def populate_database():
    global models

    import django
    django.setup()
    from contacts import models

    models.Student.objects.all().delete()
    models.Adult.objects.all().delete()
    models.Guardian.objects.all().delete()
    models.Family.objects.all().delete()
    models.Address.objects.all().delete()
    models.OLSClass.objects.all().delete()

    for olsclass in classes.values():
        olsclass_obj = get_or_create_olsclass(olsclass)

    for family in families.values():
        family_obj = get_or_create_family(family)
        for guardian in family.guardians:
            guardian_obj = get_or_create_guardian(guardian)
        for child in family.children:
            student_obj = get_or_create_student(child)


def get_or_create_olsclass(olsclass):
    """
    Return a models.OLSClass object corresponding to the given
    OLSClass object.  If the given OLSClass has no database id, it will
    added to the database; otherwise, the existing item is fetched.
    """
    if olsclass is None:
        return None
    elif olsclass._id is not None:
        olsclass_obj = models.OLSClass.objects.filter(pk=olsclass._id)[0]
    else:
        teacher_obj = get_or_create_adult(olsclass.teacher)
        aide_obj = get_or_create_adult(olsclass.aide)
        classmom_obj = get_or_create_adult(olsclass.classmom)

        olsclass_obj = models.OLSClass(title=olsclass.title, grade=olsclass.grade,
                gradelevel=olsclass.gradelevel, teacher=teacher_obj,
                aide=aide_obj, classmom=classmom_obj, rank=olsclass.rank)
        olsclass_obj.save()
        olsclass._id = olsclass_obj.id
    return olsclass_obj

def get_or_create_family(family):
    """
    Return a models.Family object corresponding to the given
    Family object.  If the given Family has no database id, it will
    added to the database; otherwise, the existing item is fetched.
    """
    if family is None:
        return None
    elif family._id is not None:
        family_obj = models.Family.objects.filter(pk=family._id)[0]
    else:
        address_obj = get_or_create_address(family.address)
        family_obj = models.Family(name=family.name(), email=family.email,
                address=address_obj, private=family.private)
        family_obj.save()
        family._id = family_obj.id
    return family_obj

def get_or_create_address(address):
    """
    Return a models.Address object corresponding to the given
    Address object.  If the given Address has no database id, it will
    added to the database; otherwise, the existing item is fetched.
    """
    if address is None or address.oneline() == "":
        return None
    elif address._id is not None:
        address_obj = models.Address.objects.filter(pk=address._id)[0]
    else:
        address_obj = models.Address(street=address.street,
                city=address.city, state=address.state,
                zipcode=address.zipcode)
        address_obj.save()
        address._id = address_obj.id
    return address_obj

def get_or_create_guardian(guardian):
    """
    Return a models.Guardian object corresponding to the given
    Guardian object.  If the given Guardian has no database id, it will
    added to the database; otherwise, the existing item is fetched.
    """
    if guardian is None:
        return None
    elif guardian._id is not None:
        guardian_obj = models.Guardian.objects.filter(pk=guardian._id)[0]
    else:
        adult_obj = get_or_create_adult(guardian)
        family_obj = get_or_create_family(guardian.family)
        guardian_obj = models.Guardian(person=adult_obj,
                relation=guardian.relation, family=family_obj)
        guardian_obj.save()
        guardian._id = guardian_obj.id
    return guardian_obj

def get_or_create_adult(adult):
    """
    Return a models.Adult object corresponding to the given
    Adult object.  If the given Adult has no database id, it will
    added to the database; otherwise, the existing item is fetched.
    """
    if adult is None:
        return None
    elif adult._id is not None:
        adult_obj = models.Adult.objects.filter(pk=adult._id)[0]
    else:
        adult_obj = models.Adult(firstname=adult.firstname,
                lastname =adult.lastname, email=adult.email,
                homephone=adult.homephone, cellphone=adult.cellphone)
        adult_obj.save()
        adult._id = adult_obj.id
    return adult_obj

def get_or_create_student(student):
    """
    Return a models.Student object corresponding to the given
    Student object.  If the given Student has no database id, it will
    added to the database; otherwise, the existing item is fetched.
    """
    if student is None:
        return None
    elif student._id is not None:
        student_obj = models.Student.objects.filter(pk=student._id)[0]
    else:
        family_obj = get_or_create_family(student.family)
        olsclass_obj = get_or_create_olsclass(student.olsclass)
        student_obj = models.Student(firstname=student.firstname,
                lastname =student.lastname, family=family_obj,
                olsclass=olsclass_obj)
        student_obj.save()
        student._id = student_obj.id
    return student_obj

if __name__ == '__main__':
    import pdb
    try:
        main(sys.argv[1:])
    except Exception:
        # pdb.post_mortem()
        raise
