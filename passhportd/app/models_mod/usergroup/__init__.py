# -*-coding:Utf-8 -*-

# Compatibility 2.7-3.4
from __future__ import absolute_import
from __future__ import unicode_literals

from app import db

# Table to handle the self-referencing many-to-many relationship
# for the Usergroup class:
# First column holds the containers, the second the subgroups.
group_of_group = db.Table(
    "group_of_group",
    db.Column(
        "container_id",
        db.Integer,
        db.ForeignKey("usergroup.id"),
        primary_key=True),
    db.Column(
        "subgroup_id",
        db.Integer,
        db.ForeignKey("usergroup.id"),
        primary_key=True))


class Usergroup(db.Model):
    """Usergroup defines a group of users
    (can contain some usergroups too)
    """
    __tablename__ = "usergroup"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True, unique=True)
    comment = db.Column(db.String(500), index=True, unique=False)

    # Relations
    members = db.relationship("User", secondary="group_user")
    gmembers = db.relationship(
        "Usergroup",
        secondary=group_of_group,
        primaryjoin=id == group_of_group.c.container_id,
        secondaryjoin=id == group_of_group.c.subgroup_id,
        backref="containedin")

    def __repr__(self):
        """Return main data of the usergroup as a string"""
        output = []

        output.append("Name: {}".format(self.name))
        output.append("Comment: {}".format(self.comment))
        output.append("User list:")

        for user in self.members:
            output.append(user.show_name())

        output.append("Usergroup list: ")

        for usergroup in self.gmembers:
            output.append(usergroup.show_name())

        output.append(" ".join(self.all_user_list()))
        output.append(" ".join(self.all_usergroup_list()))

        return "\n".join(output)

    def show_name(self):
        """Return a string containing the usergroup's name"""
        return self.name

    # User management
    def is_member(self, user):
        """Return true if the given user is a member of the usergroup,
        false otherwise
        """
        return user in self.members

    def adduser(self, user):
        """Add a user to the relation table"""
        if not self.is_member(user):
            self.members.append(user)

        return self

    def rmuser(self, user):
        """Remove a user from the relation table"""
        if self.is_member(user):
            self.members.remove(user)

        return self

    def username_in_usergroup(self, username):
        """Return true if the given username belongs to a member
        of the usergroup
        """
        for user in self.members:
            if user.show_name() == username:
                return True

        return False

    def user_list(self):
        """Return users in the usergroup"""
        users = []
        for user in self.members:
            users.append(user.show_name())

        return users

    def all_user_list(self,parsed_groups = []):
        """Return all users in the usergroup and sub-usergroups"""
        users = self.user_list()
        # Recursive on groups: 
        # we list all users but we never parse a group twice
        # To avoid cirular issues.
        for group in self.gmembers:
            if group not in parsed_groups:
                parsed_groups.append(group)
                for user in group.all_user_list(parsed_groups):
                    if user not in users:
                        users.append(user)

        return users

    # Usergroup management
    def is_gmember(self, usergroup):
        """Return true if the given usergroup is a member
        of the usergroup, false otherwise
        """
        return usergroup in self.gmembers

    def addusergroup(self, usergroup):
        """Add a usergroup to the relation table"""
        if not self.is_gmember(usergroup):
            self.gmembers.append(usergroup)

        return self

    def rmusergroup(self, usergroup):
        """Remove a usergroup from the relation table"""
        if self.is_gmember(usergroup):
            self.gmembers.remove(usergroup)

        return self

    def subusergroupname_in_usergroup(self, subusergroupname):
        """Return true if the given subusergroupname belongs to a member
        of the usergroup, false otherwise
        """
        for subusergroup in self.gmembers:
            if subusergroup.show_name() == subusergroupname:
                return True

        return False

    def usergroup_list(self):
        """Return usergroups in the usergroup"""
        usergroups = []
        for usergroup in self.gmembers:
            usergroups.append(usergroup.show_name())

        return usergroups

    def all_usergroup_list(self, parsed_usergroups = []):
        """Return all users in the usergroup and sub-usergroups"""
        usergroups = self.usergroup_list() # ["G1","G2"]
        # Recursive on groups: 
        # we list all usergroups but we never parse a group twice
        # To avoid cirular issues.
        for subgroup in self.gmembers:
            if subgroup not in parsed_usergroups:
                parsed_usergroups.append(subgroup) # [G1,G2]
                for subsubgroup in subgroup.all_usergroup_list(parsed_usergroups):
                    if subsubgroup not in usergroups:
                        usergroups.append(subsubgroup)

        return usergroups

