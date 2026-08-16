from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), default='employee')  # admin / employee
    department = db.Column(db.String(50), default='')
    position = db.Column(db.String(50), default='')
    phone = db.Column(db.String(20), default='')
    email = db.Column(db.String(80), default='')

    def __repr__(self):
        return f'<User {self.name}>'


class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author = db.relationship('User', backref='announcements', foreign_keys='Announcement.author_id')

    def __repr__(self):
        return f'<Announcement {self.title}>'


class Approval(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)        # 请假/报销/出差/采购/其他
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='待审批')      # 待审批/已通过/已驳回
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    remark = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    applicant = db.relationship('User', backref='approvals', foreign_keys='Approval.applicant_id')
    reviewer = db.relationship('User', backref='reviews', foreign_keys='Approval.reviewer_id')

    def __repr__(self):
        return f'<Approval {self.title}>'
