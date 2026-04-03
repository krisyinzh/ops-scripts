# ============================================================
# Windows 账户解锁和密码重置工具
# 功能：解锁被锁定的 Windows 账户、重置密码、清除失败计数
# 需要：管理员权限运行
# ============================================================

# 检查是否以管理员权限运行
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "错误：此脚本需要管理员权限运行！" -ForegroundColor Red
    exit 1
}

# ============================================================
# 1. 查看 Administrator 账户状态
# ============================================================
function Show-AccountStatus {
    Write-Host "`n========== Administrator 账户状态 ==========" -ForegroundColor Green
    net user Administrator
}

# ============================================================
# 2. 重置密码
# ============================================================
function Reset-AdminPassword {
    param(
        [Parameter(Mandatory=$true)]
        [string]$NewPassword
    )
    
    Write-Host "`n========== 重置 Administrator 密码 ==========" -ForegroundColor Green
    try {
        net user Administrator "$NewPassword"
        Write-Host "✓ 密码重置成功！" -ForegroundColor Green
    } catch {
        Write-Host "✗ 密码重置失败：$_" -ForegroundColor Red
    }
}

# ============================================================
# 3. 解锁账户
# ============================================================
function Unlock-AdminAccount {
    Write-Host "`n========== 解锁 Administrator 账户 ==========" -ForegroundColor Green
    try {
        Enable-LocalUser -Name "Administrator"
        Write-Host "✓ 账户已解锁！" -ForegroundColor Green
    } catch {
        Write-Host "✗ 解锁失败：$_" -ForegroundColor Red
    }
}

# ============================================================
# 4. 清除登录失败计数器并激活账户
# ============================================================
function Clear-FailedLogon {
    Write-Host "`n========== 清除登录失败计数器 ==========" -ForegroundColor Green
    try {
        net user Administrator /active:yes
        Write-Host "✓ 登录失败计数器已清除，账户已激活！" -ForegroundColor Green
    } catch {
        Write-Host "✗ 清除失败：$_" -ForegroundColor Red
    }
}

# ============================================================
# 5. 解除登录次数限制
# ============================================================
function Disable-LoginLockout {
    Write-Host "`n========== 解除登录锁定阈值 ==========" -ForegroundColor Green
    try {
        net accounts /lockoutthreshold:0
        Write-Host "✓ 已禁用登录锁定阈值（不再限制登录失败次数）！" -ForegroundColor Green
    } catch {
        Write-Host "✗ 操作失败：$_" -ForegroundColor Red
    }
}

# ============================================================
# 6. 查看登录策略
# ============================================================
function Show-LoginPolicy {
    Write-Host "`n========== 当前登录策略 ==========" -ForegroundColor Green
    net accounts
}

# ============================================================
# 7. 一键快速解锁（执行所有操作）
# ============================================================
function Quick-Unlock {
    param(
        [Parameter(Mandatory=$true)]
        [string]$NewPassword
    )
    
    Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║     开始执行 Administrator 账户解锁     ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Cyan
    
    Show-AccountStatus
    Reset-AdminPassword $NewPassword
    Unlock-AdminAccount
    Clear-FailedLogon
    Disable-LoginLockout
    Show-LoginPolicy
    
    Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║      所有操作完成！账户已完全解锁       ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Green
}

# ============================================================
# 主菜单
# ============================================================
function Show-Menu {
    Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║    Windows Administrator 账户管理工具    ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host "1. 查看账户状态"
    Write-Host "2. 重置密码"
    Write-Host "3. 解锁账户"
    Write-Host "4. 清除登录失败计数器"
    Write-Host "5. 解除登录次数限制"
    Write-Host "6. 查看登录策略"
    Write-Host "7. 一键快速解锁（推荐）"
    Write-Host "0. 退出"
    Write-Host ""
}

# ============================================================
# 主程序
# ============================================================
$continueLoop = $true
while ($continueLoop) {
    Show-Menu
    $choice = Read-Host "请选择操作 (0-7)"
    
    switch ($choice) {
        "1" { Show-AccountStatus }
        "2" { 
            $password = Read-Host "请输入新密码" -AsSecureString
            $plainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToCoTaskMemUnicode($password))
            Reset-AdminPassword $plainPassword
        }
        "3" { Unlock-AdminAccount }
        "4" { Clear-FailedLogon }
        "5" { Disable-LoginLockout }
        "6" { Show-LoginPolicy }
        "7" {
            $password = Read-Host "请输入新密码（用于重置）" -AsSecureString
            $plainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToCoTaskMemUnicode($password))
            Quick-Unlock $plainPassword
            $continueLoop = $false
        }
        "0" { 
            Write-Host "退出程序！" -ForegroundColor Yellow
            $continueLoop = $false 
        }
        default { Write-Host "无效选择，请重试！" -ForegroundColor Red }
    }
}
