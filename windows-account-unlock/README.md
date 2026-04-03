# Windows Administrator 账户解锁工具

用于解锁被锁定的 Windows Administrator 账户、重置密码、清除登录失败计数器的 PowerShell 脚本。

## 📋 功能特性

✅ **查看账户状态** - 显示 Administrator 账户的当前状态  
✅ **重置密码** - 为 Administrator 账户设置新密码  
✅ **解锁账户** - 解除被锁定的账户  
✅ **清除失败计数** - 清除登录失败的计数器  
✅ **解除锁定限制** - 禁用登录次数限制  
✅ **查看登录策略** - 显示当前的账户锁定策略  
✅ **一键快速解锁** - 自动执行所有解锁操作  
✅ **交互菜单** - 友好的命令行菜单界面  

## 🔧 前置要求

### 系统要求
- Windows 7 / Windows Server 2008 及更高版本
- PowerShell 3.0 或更高版本
- **必须以管理员权限运行**

### 权限要求
脚本需要以下权限：
- 管理员权限（Administrator）
- 本地账户管理权限

## 📖 使用方法

### 方式 1：运行 PowerShell 脚本（推荐）

#### 第 1 步：打开 PowerShell（管理员模式）
- 右键点击 PowerShell → 选择"以管理员身份运行"
- 或者按 `Win + X` → 选择 "Windows PowerShell (管理员)"

#### 第 2 步：允许执行脚本
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 第 3 步：运行脚本
```powershell
cd c:\path\to\script
.\unlock_windows_account.ps1
```

#### 第 4 步：选择操作
脚本会显示菜单，选择对应的数字：
```
1. 查看账户状态
2. 重置密码
3. 解锁账户
4. 清除登录失败计数器
5. 解除登录次数限制
6. 查看登录策略
7. 一键快速解锁（推荐）
0. 退出
```

### 方式 2：命令行直接执行

如果你只需要执行特定操作，可以直接在 PowerShell（管理员模式）运行以下命令：

#### 查看账户状态
```powershell
net user Administrator
```

#### 重置密码
```powershell
net user Administrator "新密码"
```

#### 解锁账户
```powershell
Enable-LocalUser -Name "Administrator"
```

#### 清除登录失败计数器和激活账户
```powershell
net user Administrator /active:yes
```

#### 解除登录次数限制
```powershell
net accounts /lockoutthreshold:0
```

#### 查看当前登录策略
```powershell
net accounts
```

## 📊 常见场景

### 场景 1：账户被锁定，无法登录

1. 用其他管理员账户登录
2. 打开 PowerShell（管理员模式）
3. 运行脚本，选择 `7. 一键快速解锁`
4. 输入新密码
5. 用新密码重新登录 Administrator 账户

### 场景 2：只想查看账户状态

```powershell
.\unlock_windows_account.ps1
# 选择 1
```

### 场景 3：只想重置密码

```powershell
.\unlock_windows_account.ps1
# 选择 2
```

### 场景 4：账户显示"已禁用"

```powershell
.\unlock_windows_account.ps1
# 选择 3（解锁账户）
```

## 🔍 理解各个操作

### 账户锁定（Account Locked）
- **原因**：登录失败次数过多
- **解决**：运行 `net user Administrator /active:yes`

### 账户禁用（Account Disabled）
- **原因**：账户被手动禁用或系统禁用
- **解决**：运行 `Enable-LocalUser -Name "Administrator"`

### 登录阈值（Lockout Threshold）
- **含义**：允许登录失败的最大次数
- **默认值**：通常为 0（不限制）或 5
- **设置**：`net accounts /lockoutthreshold:数字`
  - 0 = 禁用账户锁定
  - 5 = 失败 5 次后锁定

### 登录锁定时长（Lockout Duration）
- **含义**：账户被锁定后多久自动解锁（单位：分钟）
- **查看**：`net accounts`
- **修改**：`net accounts /lockoutduration:分钟数`

## 📋 命令详解

### `net user Administrator`
显示 Administrator 账户的详细信息，包括：
- Account active（账户是否激活）
- Account expires（账户过期时间）
- Password required（是否需要密码）
- User may change password（用户是否可更改密码）

### `net accounts`
显示密码和账户锁定策略：
```
Force user logoff how long after time expires?: No
Minimum password age (days): 0
Maximum password age (days): 42
Minimum password length: 0
Length of password history maintained: 0
Lockout threshold: 0  ← 登录失败次数限制
Lockout observation window (minutes): 30
Lockout duration (minutes): 30
```

## ⚠️ 重要注意事项

1. **备份数据** - 操作前请备份重要数据
2. **管理员权限** - 必须以管理员身份运行
3. **密码安全** - 设置强密码，不要使用简单密码
4. **谨慎操作** - 禁用账户锁定可能降低安全性
5. **测试环境** - 在生产环境前先在测试环境验证

## 🔒 安全建议

1. **定期更改密码**
```powershell
net user Administrator "强密码123!@#"
```

2. **启用账户锁定**
```powershell
# 失败 5 次后锁定
net accounts /lockoutthreshold:5
# 锁定 30 分钟
net accounts /lockoutduration:30
```

3. **监视登录失败**
```powershell
# 查看安全日志
Get-WinEvent -LogName Security | Where-Object { $_.ID -eq 4625 } | Select-Object -First 10
```

4. **定期审计账户**
```powershell
Get-LocalUser | Select-Object Name, Enabled, LastLogon
```

## 🆘 故障排除

### 问题 1：脚本无法运行（执行策略错误）
**错误信息**：`cannot be loaded because running scripts is disabled`

**解决**：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 问题 2：访问被拒绝
**错误信息**：`Access Denied`

**解决**：
- 确保使用管理员身份运行 PowerShell
- 检查你的账户是否有足够权限

### 问题 3：账户仍然被锁定
**原因**：
- 密码策略仍在生效
- 需要重启计算机

**解决**：
```powershell
# 1. 运行脚本的第 7 个选项
# 2. 如果还是不行，重启计算机
Restart-Computer -Force
```

### 问题 4：命令 `Enable-LocalUser` 不工作
**原因**：PowerShell 版本太旧或在某些 Windows 版本上不可用

**替代方案**：
```powershell
# 使用 WMI 方法
([ADSI]"WinNT://./Administrator,user").psbase.invokeset("accountdisabled",$false)
```

## 📚 相关 Windows 命令

```powershell
# 显示所有本地用户
Get-LocalUser

# 显示用户组信息
Get-LocalGroupMember Administrators

# 创建新用户
New-LocalUser -Name "username" -Password (ConvertTo-SecureString "password" -AsPlainText -Force)

# 删除用户
Remove-LocalUser -Name "username"

# 更改用户权限
Add-LocalGroupMember -Group "Administrators" -Member "username"
```

## 📝 日志记录

脚本执行的所有操作都会显示在 PowerShell 窗口中。建议保存输出：

```powershell
# 运行脚本并保存日志
.\unlock_windows_account.ps1 | Tee-Object -FilePath "unlock_log.txt"
```

## 许可证

MIT

## 更新日志

### v1.0 (2026-04-03)
- 初始版本
- 支持账户状态查看
- 支持密码重置
- 支持账户解锁
- 支持清除失败计数
- 支持解除登录限制
- 支持交互式菜单
