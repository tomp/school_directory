from django.db import models

class Student(models.Model):
    firstname = models.CharField(max_length=64)
    lastname = models.CharField(max_length=64)
    olsclass = models.ForeignKey('OLSClass')
    family = models.ForeignKey('Family')

    def __unicode__(self):
        return self.name()

    def name(self, lastname_first=False):
        if lastname_first:
            return self.lastname + ", " + self.firstname
        else:
            return self.firstname + " " + self.lastname

    class Meta:
        ordering = ('lastname', 'firstname')

class Adult(models.Model):
    firstname = models.CharField(max_length=64)
    lastname = models.CharField(max_length=64)
    email = models.CharField(max_length=64, blank=True, null=True)
    homephone = models.CharField(max_length=32, blank=True, null=True)
    cellphone = models.CharField(max_length=32, blank=True, null=True)

    def __unicode__(self):
        return self.name()

    def name(self, lastname_first=False):
        if lastname_first:
            return self.lastname + ", " + self.firstname
        else:
            return self.firstname + " " + self.lastname

    def contact_info(self):
        info = []
        if self.cellphone:
            info.append(('cell', self.cellphone))
        if self.homephone:
            info.append(('home', self.homephone))
        if self.email:
            info.append(('email', self.email))
        return info

    class Meta:
        ordering = ('lastname', 'firstname')

class Guardian(models.Model):
    MOTHER = "Mother"
    FATHER = "Father"
    SISTER = "Sister"
    BROTHER = "Brother"
    AUNT = "Aunt"
    UNCLE = "Uncle"
    GRANDMOTHER = "Grandmother"
    GRANDFATHER = "Grandfather"
    GUARDIAN = "Guardian"

    RELATION_CHOICES = (
        (MOTHER, 'Mother'),
        (FATHER, 'Father'),
        (AUNT, 'Aunt'),
        (UNCLE, 'Uncle'),
        (GRANDMOTHER, 'Grandmother'),
        (GRANDFATHER, 'Grandfather'),
        (SISTER, 'Sister'),
        (BROTHER, 'Brother'),
        (GUARDIAN, 'Guardian'),
    )

    person = models.OneToOneField('Adult')
    relation = models.CharField(max_length=32, choices=RELATION_CHOICES)
    family = models.ForeignKey('Family')

    def shortrelation(self):
        if self.relation == "Mother" or self.relation == "_mother":
            return "Mom"
        elif self.relation == "Father" or self.relation == "_father":
            return "Dad"
        else:
            return self.relation

    def __unicode__(self):
        return "{} {}".format(self.person.firstname, self.person.lastname)

    class Meta:
        ordering = ('person',)

class Address(models.Model):
    street = models.CharField(max_length=64)
    city = models.CharField(max_length=64)
    state = models.CharField(max_length=16)
    zipcode = models.CharField(max_length=16)

    def multiline(self):
        lines = []
        if self.street:
            lines.append(self.street)
        if self.city:
            if self.state or self.zipcode:
                lines.append(self.city + ", " + self.state + " " + self.zipcode)
            else:
                lines.append(self.city)
        if not lines:
            return ["(no address)"]
        return lines

    def __unicode__(self):
        return "{} {}".format(self.street, self.city)

    class Meta:
        ordering = ('-city', 'street',)

class Family(models.Model):
    name = models.CharField(max_length=64, blank=True)
    address = models.ForeignKey('Address', related_name="+", blank=True, null=True)
    email = models.CharField(max_length=64, blank=True, null=True)
    private = models.BooleanField()

    def parent_names(self, if_none=""):
        # guardians = [g.person for g in self.guardian_set.all()]
        guardians = [g for g in self.guardian_set.all() if g.person.name() != ""
                and not g.person.name().startswith("_")]
        if len(guardians) == 0:
            return if_none
        if len(guardians) == 1:
            return guardians[0].person.name()
        if len(guardians) == 2:
            (g1, g2) = (guardians[0], guardians[1])
            if g1.person.lastname == g2.person.lastname and is_couple(g1, g2):
                return g1.person.firstname + " & " + g2.person.firstname + " " + g2.person.lastname
            else:
                return g1.person.name() + " & " + g2.person.name()
        return " & ".join([g.person.name() for g in guardians])

    def phone_numbers(self):
        info = []
        guardians = self.guardian_set.all()
        homephone = None
        for g in guardians:
            ghome, gcell = (g.person.homephone, g.person.cellphone)
            if ghome:
                if not homephone:
                    homephone_info ={'label':"%s home" % g.shortrelation(),
                        'value':ghome}
                    homephone = ghome
                elif ghome != homephone:
                    info.append({'label':"%s home" % g.shortrelation(),
                        'value':ghome})
            if gcell:
                    info.append({'label':"%s cell" % g.shortrelation(),
                        'value':gcell})
        if homephone:
            info.insert(0, homephone_info)
        return info

    def emails(self):
        info = []
        guardians = self.guardian_set.all()
        for g in guardians:
            if g.person.email:
                info.append({'label':"%s email" % g.shortrelation(),
                    'value':g.person.email})
        return info

    def __unicode__(self):
        if self.name:
            return self.name
        else:
            return "Family {}".format(self.id)

    class Meta:
        verbose_name_plural = "Families"
        ordering = ('name',)

class OLSClass(models.Model):
    title = models.CharField(max_length=64)
    grade = models.CharField(max_length=16)
    gradelevel = models.CharField(max_length=16)
    rank = models.CharField(max_length=8, default="")
    teacher = models.OneToOneField('Adult', related_name="+", blank=True, null=True)
    aide = models.ForeignKey('Adult', related_name="+", blank=True, null=True)
    classmom = models.ForeignKey('Adult', related_name="+", blank=True, null=True)

    order_field = '-rank'

    def tag(self):
        return "class-{}".format(self.id)

    def teacher_name(self):
        if self.teacher is not None:
            return self.teacher.name()
        else:
            return ""

    def aide_name(self):
        if self.aide is not None:
            return self.aide.name()
        else:
            return ""

    def classmom_name(self):
        if self.classmom is not None:
            return self.classmom.name()
        else:
            return ""

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = "OLS Class"
        verbose_name_plural = "OLS Classes"
        ordering = ('-rank',)

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
