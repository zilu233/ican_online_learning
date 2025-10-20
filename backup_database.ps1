# ============================================
# MySQL 数据库备份脚本 (PowerShell)
# ============================================

# 配置信息
$MYSQL_USER = "root"
$MYSQL_PASSWORD = "123456"
$DATABASE_NAME = "onlinejudgesystem"
$BACKUP_DIR = ".\backup"

# 生成时间戳
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$BACKUP_FILE = "backup_${TIMESTAMP}.sql"

# 创建备份目录（如果不存在）
if (-not (Test-Path $BACKUP_DIR)) {
    New-Item -ItemType Directory -Path $BACKUP_DIR | Out-Null
    Write-Host "创建备份目录: $BACKUP_DIR" -ForegroundColor Green
}

$BACKUP_PATH = Join-Path $BACKUP_DIR $BACKUP_FILE

# 显示备份信息
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MySQL 数据库备份" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "数据库: $DATABASE_NAME"
Write-Host "备份文件: $BACKUP_PATH"
Write-Host "时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""
Write-Host "正在备份..." -ForegroundColor Yellow

# 执行备份
$mysqldumpCmd = "mysqldump -u $MYSQL_USER -p$MYSQL_PASSWORD $DATABASE_NAME"
Invoke-Expression "$mysqldumpCmd" | Out-File -FilePath $BACKUP_PATH -Encoding UTF8

# 检查结果
if (Test-Path $BACKUP_PATH) {
    $fileSize = [math]::Round((Get-Item $BACKUP_PATH).Length / 1KB, 2)
    Write-Host ""
    Write-Host "备份成功！" -ForegroundColor Green
    Write-Host "文件大小: $fileSize KB"
    Write-Host "保存位置: $BACKUP_PATH" -ForegroundColor Green
    Write-Host ""
    
    # 列出备份文件
    Write-Host "最近的备份文件:" -ForegroundColor Cyan
    Get-ChildItem $BACKUP_DIR -Filter "backup_*.sql" | Sort-Object LastWriteTime -Descending | Select-Object -First 5 | Format-Table Name, Length, LastWriteTime -AutoSize
} else {
    Write-Host "备份失败" -ForegroundColor Red
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
