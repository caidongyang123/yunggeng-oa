from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from models import db, User, Announcement, Approval

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yunggeng-oa-secret-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///oa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


COMPANY = '耘耕牧业'
APPROVAL_TYPES = ['请假', '报销', '出差', '采购', '其他']


@app.context_processor
def inject_globals():
    return dict(company=COMPANY, approval_types=APPROVAL_TYPES,
                now=datetime.utcnow().strftime('%Y-%m-%d'))


def create_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password=generate_password_hash('admin123'),
                         name='系统管理员', role='admin', department='总经办',
                         position='系统管理员', phone='13800000000', email='admin@ygmy.com')
            db.session.add(admin)
            demo = [
                ('zhangsan', '张三', '财务部', '会计', '13900000001', 'zhangsan@ygmy.com'),
                ('lisi', '李四', '人事部', '人事专员', '13900000002', 'lisi@ygmy.com'),
                ('wangwu', '王五', '生产部', '养殖技术员', '13900000003', 'wangwu@ygmy.com'),
                ('zhaoliu', '赵六', '销售部', '销售经理', '13900000004', 'zhaoliu@ygmy.com'),
                ('sunqi', '孙七', '行政部', '行政主管', '13900000005', 'sunqi@ygmy.com'),
            ]
            for u, n, d, pos, ph, e in demo:
                db.session.add(User(username=u, password=generate_password_hash('123456'),
                                    name=n, role='employee', department=d,
                                    position=pos, phone=ph, email=e))
            db.session.add(Announcement(
                title='欢迎使用耘耕牧业 OA 系统',
                content='本系统用于公司内部的审批流程、公告通知与通讯录管理。\n如有使用问题，请联系行政部。',
                author_id=1))
            db.session.add(Announcement(
                title='关于养殖场防疫检查的通知',
                content='本周五将进行全场防疫检查，请生产部与行政部提前做好准备，确保各项记录齐全。',
                author_id=1))
            db.session.add(Approval(type='请假', title='事假 1 天',
                                    content='家中有事，申请事假 1 天，望批准。',
                                    applicant_id=2, status='待审批'))
            db.session.commit()


@app.route('/')
@login_required
def index():
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).limit(5).all()
    announcement_count = Announcement.query.count()
    my_approvals = Approval.query.filter_by(applicant_id=current_user.id).all()
    my_pending = [a for a in my_approvals if a.status == '待审批']
    pending = Approval.query.filter_by(status='待审批').all() if current_user.role == 'admin' else []
    employees = User.query.count()
    return render_template('dashboard.html', announcements=announcements,
                           announcement_count=announcement_count,
                           my_approvals=my_approvals, my_pending=my_pending,
                           pending=pending, employees=employees)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        flash('用户名或密码错误')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/announcements')
@login_required
def announcements():
    items = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('announcements.html', items=items)


@app.route('/announcements/new', methods=['GET', 'POST'])
@login_required
def announcement_new():
    if current_user.role != 'admin':
        flash('只有管理员可以发布公告')
        return redirect(url_for('announcements'))
    if request.method == 'POST':
        db.session.add(Announcement(title=request.form['title'],
                                    content=request.form['content'],
                                    author_id=current_user.id))
        db.session.commit()
        flash('公告已发布')
        return redirect(url_for('announcements'))
    return render_template('announcement_new.html')


@app.route('/addressbook')
@login_required
def addressbook():
    users = User.query.order_by(User.department, User.name).all()
    return render_template('addressbook.html', users=users)


@app.route('/approvals')
@login_required
def approvals():
    if current_user.role == 'admin':
        items = Approval.query.order_by(Approval.created_at.desc()).all()
    else:
        items = Approval.query.filter_by(applicant_id=current_user.id).order_by(Approval.created_at.desc()).all()
    return render_template('approvals.html', items=items)


@app.route('/approvals/new', methods=['GET', 'POST'])
@login_required
def approval_new():
    if request.method == 'POST':
        db.session.add(Approval(type=request.form['type'], title=request.form['title'],
                                content=request.form['content'], applicant_id=current_user.id))
        db.session.commit()
        flash('申请已提交，等待审批')
        return redirect(url_for('approvals'))
    return render_template('approval_new.html')


@app.route('/approvals/<int:aid>/review', methods=['GET', 'POST'])
@login_required
def approval_review(aid):
    if current_user.role != 'admin':
        flash('只有管理员可以审批')
        return redirect(url_for('approvals'))
    a = Approval.query.get_or_404(aid)
    if request.method == 'POST':
        a.status = request.form['status']
        a.remark = request.form.get('remark', '')
        a.reviewer_id = current_user.id
        a.updated_at = datetime.utcnow()
        db.session.commit()
        flash('审批已完成')
        return redirect(url_for('approvals'))
    return render_template('approval_detail.html', a=a)


@app.route('/healthz')
def healthz():
    return 'ok', 200


with app.app_context():
    create_db()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)
