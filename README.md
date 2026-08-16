# 耘耕牧业 OA 系统

基于 **Python + Flask** 的企业办公自动化系统，包含：

- 📢 **公告通知**：管理员发布，全员查看
- 👥 **通讯录**：员工信息（部门 / 职务 / 电话 / 邮箱）
- ✅ **审批流程**：员工提交申请（请假 / 报销 / 出差 / 采购 / 其他），管理员审批
- 🔐 **登录与权限**：管理员 / 员工两种角色

界面采用农业绿主题，响应式布局，开箱即用。

## 技术栈

- Flask 3.x（Web 框架）
- Flask-SQLAlchemy（ORM）
- Flask-Login（登录会话）
- SQLite（零配置数据库）
- 原生 HTML / CSS（无前端构建步骤）

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动（首次启动会自动建库并写入演示数据）
python app.py

# 3. 浏览器访问
http://127.0.0.1:5000
```

## 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 员工 | zhangsan | 123456 |
| 员工 | lisi | 123456 |

> 员工示例账号还有 wangwu / zhaoliu / sunqi，密码均为 `123456`。

## 功能说明

### 工作台
登录后展示公告数、通讯录人数、我的申请数、待办审批数，以及最新公告与我的审批概览。

### 公告通知
- 管理员：可发布新公告
- 全员：查看全部公告

### 通讯录
展示全部员工卡片，含部门、职务、电话、邮箱。

### 审批流程
- 员工：提交申请 → 状态变为「待审批」
- 管理员：在列表点击「去审批」→ 通过 / 驳回，可填写审批意见
- 申请人可在「我的审批」中查看审批结果与意见

## 目录结构

```
yunggeng-oa/
├── app.py              # 应用入口与路由
├── models.py           # 数据库模型
├── requirements.txt    # 依赖
├── static/style.css    # 样式
├── templates/          # 页面模板
└── oa.db               # 运行时自动生成的数据库（已加入 .gitignore）
```

## 部署到 GitHub

```bash
git init
git add .
git commit -m "init: 耘耕牧业 OA 系统"
gh repo create yunggeng-oa --public --source=. --push
```

如需公网访问，可部署到任意支持 Python 的平台（如 Render / Railway / 阿里云函数计算），
将 `oa.db` 改为云数据库（PostgreSQL）即可。
