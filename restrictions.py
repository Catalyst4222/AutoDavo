# Added self to stuff to make things work -Cata
# Also, discord.Permissions are probably a good idea


class RestrictLevel(object):  # TODO make things properties and classmethods -Cata
    """A basic bitflag object containing the bitwise restriction level for a command/group"""

    def init_flag(self, code=0):  # Initialise with all bit flags already defined
        self.flags = code

    def init_bools(
        self,
        davoOnly,
        invis,
        adminOnly,
        modOnly,
        needrole1=False,
        needrole2=False,
        needrole3=False,
        needrole4=False,
    ):
        # Plugin made change -Cata
        self.flags = 0
        self.flags |= davoOnly * 0b10000000
        self.flags |= invis * 0b01000000
        self.flags |= adminOnly * 0b00100000
        self.flags |= modOnly * 0b00010000
        self.flags |= needrole1 * 0b00001000
        self.flags |= needrole2 * 0b00000100
        self.flags |= needrole3 * 0b00000010
        self.flags |= needrole4 * 0b00000001

    def __init__(self, *args):
        self.flags: int = 0

        if len(args) == 0:
            self.init_flag()
        elif len(args) == 1:
            self.init_flag(args[0])
        else:
            self.init_bools(*args)

    def isDavoOnly(self):
        return self.flags & 0b10000000 > 0

    def isInvis(self):
        return self.flags & 0b01000000 > 0

    def isAdminOnly(self):
        return self.flags & 0b00100000 > 0

    def isModOnly(self):
        return self.flags & 0b00010000 > 0

    def needsRole1(self):
        return self.flags & 0b00001000 > 0

    def needsRole2(self):
        return self.flags & 0b00000100 > 0

    def needsRole3(self):
        return self.flags & 0b00000010 > 0

    def needsRole4(self):
        return self.flags & 0b00000001 > 0


# Define the most useful restriction types
RES_EMPTY = RestrictLevel(
    0
)  # No restrictions, command can be seen & executed by anyone
RES_MODS = RestrictLevel(0b00010000)  # Command execution restricted to mods only
RES_ADMINS = RestrictLevel(0b00100000)  # Command execution restricted to admins only
RES_DAVO_ONLY = RestrictLevel(0b11000000)  # Command execution restricted to Davo only
