# -*- coding: utf-8 -*-
"""耘耕牧业 OA 系统冒烟测试（不跟随重定向，验证真实状态码）。"""
import urllib.request, urllib.parse, urllib.error, http.cookiejar, re

BASE = "http://127.0.0.1:5000"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # 不跟随，让 302 以 HTTPError 形式暴露


def make_opener():
    cj = http.cookiejar.CookieJar()
    return urllib.request.build_opener(NoRedirect, urllib.request.HTTPCookieProcessor(cj))


def post(op, url, data):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(),
                                  method="POST",
                                  headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        r = op.open(req)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")


def get(op, url):
    try:
        r = op.open(url)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")


def ok(cond, name):
    print(("PASS " if cond else "FAIL ") + name)


# 1) 未登录访问 / 应被拦截（302 跳登录）
op = make_opener()
st, _ = get(op, BASE + "/")
ok(st == 302, "未登录访问/ -> 302跳转登录")

# 2) 登录页含标题
op = make_opener()
_, body = get(op, BASE + "/login")
ok("耘耕牧业 OA 系统" in body, "登录页标题渲染")
ok("企业办公自动化平台" in body, "登录页副标题渲染")

# 3) 管理员登录
st, _ = post(op, BASE + "/login", {"username": "admin", "password": "admin123"})
ok(st == 302, "管理员登录 -> 302")
st, body = get(op, BASE + "/")
ok(st == 200 and "工作台" in body, "工作台可访问(200)")
ok("通讯录人数" in body, "工作台统计卡片渲染")

# 4) 各模块
_, b = get(op, BASE + "/addressbook"); ok("张三" in b, "通讯录显示员工")
_, b = get(op, BASE + "/announcements"); ok("欢迎使用" in b, "公告列表渲染")
_, b = get(op, BASE + "/approvals"); ok("待审批" in b, "审批列表渲染")

# 5) 员工提交申请
emp = make_opener()
post(emp, BASE + "/login", {"username": "zhangsan", "password": "123456"})
st, _ = post(emp, BASE + "/approvals/new", {"type": "报销", "title": "差旅报销", "content": "出差车票报销200元"})
ok(st == 302, "员工提交审批 -> 302")

# 6) 管理员审批（取第一条待审批）
_, b = get(op, BASE + "/approvals")
ids = re.findall(r'/approvals/(\d+)/review', b)
ok(len(ids) > 0, "审批列表含可审批项")
if ids:
    st, _ = post(op, BASE + f"/approvals/{ids[0]}/review", {"status": "已通过", "remark": "同意报销"})
    ok(st == 302, "管理员审批 -> 302")

print("==== SMOKE DONE ====")
