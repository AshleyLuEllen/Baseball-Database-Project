from sqlalchemy import case, func
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    favTeam = db.Column(db.String(3))
    favYear = db.Column(db.SmallInteger)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def set_favTeam(self, team):
        self.favTeam = team

    def set_favYear(self, year):
        self.favYear = year

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class People(db.Model):
    __tablename__ = 'people'
    playerID = db.Column(db.String(9), primary_key=True)
    nameFirst = db.Column(db.String(255))
    nameLast = db.Column(db.String(255))
    birthMonth = db.Column(db.Integer)
    birthDay = db.Column(db.Integer)
    birthCountry = db.Column(db.String(255))
    birthState = db.Column(db.String(255))
    birthCity = db.Column(db.String(255))
    bats = db.Column(db.String(255))
    throws = db.Column(db.String(255))


class Appearances(db.Model):
    __tablename__ = 'appearances'
    id = db.Column(db.Integer, primary_key=True)
    playerID = db.Column(db.String(9), db.ForeignKey("people.playerID"))
    yearID = db.Column(db.SmallInteger)
    teamID = db.Column(db.String(3))
    G_p = db.Column(db.SmallInteger)
    G_c = db.Column(db.SmallInteger)
    G_1b = db.Column(db.SmallInteger)
    G_2b = db.Column(db.SmallInteger)
    G_3b = db.Column(db.SmallInteger)
    G_ss = db.Column(db.SmallInteger)
    G_lf = db.Column(db.SmallInteger)
    G_cf = db.Column(db.SmallInteger)
    G_rf = db.Column(db.SmallInteger)
    G_of = db.Column(db.SmallInteger)
    G_dh = db.Column(db.SmallInteger)
    G_ph = db.Column(db.SmallInteger)
    G_pr = db.Column(db.SmallInteger)

    @hybrid_property
    def positions_played(self):
        rtn = []
        if (self.G_p or 0) > 0:
            rtn.append('P')
        if (self.G_c or 0) > 0:
            rtn.append('C')
        if (self.G_1b or 0) > 0:
            rtn.append('1B')
        if (self.G_2b or 0) > 0:
            rtn.append('2B')
        if (self.G_3b or 0) > 0:
            rtn.append('3B')
        if (self.G_ss or 0) > 0:
            rtn.append('SS')
        if (self.G_lf or 0) > 0:
            rtn.append('LF')
        if (self.G_cf or 0) > 0:
            rtn.append('CF')
        if (self.G_rf or 0) > 0:
            rtn.append('RF')
        if (self.G_of or 0) > 0:
            rtn.append('OF')
        if (self.G_dh or 0) > 0:
            rtn.append('DH')
        if (self.G_ph or 0) > 0:
            rtn.append('PH')
        if (self.G_pr or 0) > 0:
            rtn.append('PR')
        return ', '.join(rtn)

    @positions_played.expression
    def positions_played(cls):
        rtn = []
        if func.coalesce(cls.G_p, 0) > 0:
            rtn.append('P')
        if func.coalesce(cls.G_c, 0) > 0:
            rtn.append('C')
        if func.coalesce(cls.G_1b, 0) > 0:
            rtn.append('1B')
        if func.coalesce(cls.G_2b, 0) > 0:
            rtn.append('2B')
        if func.coalesce(cls.G_3b, 0) > 0:
            rtn.append('3B')
        if func.coalesce(cls.G_ss, 0) > 0:
            rtn.append('SS')
        if func.coalesce(cls.G_lf, 0) > 0:
            rtn.append('LF')
        if func.coalesce(cls.G_cf, 0) > 0:
            rtn.append('CF')
        if func.coalesce(cls.G_rf, 0) > 0:
            rtn.append('RF')
        if func.coalesce(cls.G_of, 0) > 0:
            rtn.append('OF')
        if func.coalesce(cls.G_dh, 0) > 0:
            rtn.append('DH')
        if func.coalesce(cls.G_ph, 0) > 0:
            rtn.append('PH')
        if func.coalesce(cls.G_pr, 0) > 0:
            rtn.append('PR')
        return ', '.join(rtn)


class Batting(db.Model):
    __tablename__ = 'batting'
    id = db.Column(db.Integer, primary_key=True)
    playerID = db.Column(db.String(9), db.ForeignKey("people.playerID"))
    yearID = db.Column(db.SmallInteger)
    teamID = db.Column(db.String(3))
    person = db.relationship("People")
    appearance = db.relationship('Appearances', foreign_keys=[playerID, teamID, yearID])
    __table_args__ = (
        db.ForeignKeyConstraint([playerID, teamID, yearID],
                                [Appearances.playerID, Appearances.teamID, Appearances.yearID]),
    )
    H = db.Column(db.SmallInteger)
    HR = db.Column(db.SmallInteger)
    AB = db.Column(db.SmallInteger)
    BB = db.Column(db.SmallInteger)
    HBP = db.Column(db.SmallInteger)
    SF = db.Column(db.SmallInteger)
    SH = db.Column(db.SmallInteger)
    B2 = db.Column('2B', db.SmallInteger)
    B3 = db.Column('3B', db.SmallInteger)

    @hybrid_property
    def plate_appearance(self):
        return self.AB + self.BB + (self.HBP or 0) + (self.SF or 0) + (self.SH or 0)

    @plate_appearance.expression
    def plate_appearance(cls):
        return cls.AB + cls.BB + func.coalesce(cls.HBP, 0) + func.coalesce(cls.SF, 0) + func.coalesce(cls.SH, 0)

    @hybrid_property
    def batting_avg(self):
        return self.H / self.AB if self.AB > 0 else 0

    @batting_avg.expression
    def batting_avg(cls):
        return case([(cls.AB, cls.H / cls.AB)], else_=0)

    @hybrid_property
    def onbase_percent(self):
        return (self.H + self.BB + (self.HBP or 0)) / (self.AB + self.BB + (self.HBP or 0) + (self.SF or 0)) if (self.AB + self.BB + (self.HBP or 0) + (self.SF or 0)) > 0 else 0

    @onbase_percent.expression
    def onbase_percent(cls):
        return case([(cls.H + cls.BB + func.coalesce(cls.HBP, 0)) / (cls.AB + cls.BB + func.coalesce(cls.HBP, 0) + func.coalesce(cls.SF, 0))], else_=0)

    @hybrid_property
    def slug_percent(self):
        return (self.H + self.B2 + 2 * self.B3 + 3 * self.HR) / self.AB if self.AB > 0 else 0

    @slug_percent.expression
    def slug_percent(cls):
        return case([(cls.H + cls.B2 + 2 * cls.B3 + 3 * cls.HR) / cls.AB], else_=0)


# pitchers with statistics (innings pitched, wins, losses, saves, era)
class Pitching(db.Model):
    __tablename__ = 'pitching'
    id = db.Column(db.Integer, primary_key=True)
    playerID = db.Column(db.String(9), db.ForeignKey("people.playerID"))
    yearID = db.Column(db.SmallInteger)
    teamID = db.Column(db.String(3))
    person = db.relationship("People")
    W = db.Column(db.SmallInteger)
    L = db.Column(db.SmallInteger)
    IPouts = db.Column(db.Integer)
    SV = db.Column(db.SmallInteger)
    ERA = db.Column(db.Float)

    @hybrid_property
    def innings_pitched(self):
        return self.IPouts / 3

    @innings_pitched.expression
    def innings_pitched(cls):
        return cls.IPouts / 3


#
class Managers(db.Model):
    __tablename__ = 'managers'
    id = db.Column(db.Integer, primary_key=True)
    playerID = db.Column(db.String(9), db.ForeignKey("people.playerID"))
    yearID = db.Column(db.SmallInteger)
    teamID = db.Column(db.String(3))
    person = db.relationship("People")


class Teams(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    yearID = db.Column(db.SmallInteger)
    lgID = db.Column(db.String(2))
    teamID = db.Column(db.String(3))
    teamRank = db.Column(db.SmallInteger)
    franchID = db.Column(db.String(3))
    name = db.Column(db.String(50))
    DivWin = db.Column(db.String(1))
    WCWin = db.Column(db.String(1))
    WSWin = db.Column(db.String(1))
    LgWin = db.Column(db.String(1))


class Seriespost(db.Model):
    __tablename__ = 'seriespost'
    ID = db.Column(db.Integer, primary_key=True)
    yearID = db.Column(db.SmallInteger)
    round = db.Column(db.String(5))
    teamIDwinner = db.Column(db.String(3))
    teamIDloser = db.Column(db.String(3))
    wins = db.Column(db.SmallInteger)
    losses = db.Column(db.SmallInteger)
    ties = db.Column(db.SmallInteger)
