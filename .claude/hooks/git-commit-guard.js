#!/usr/bin/env node
// PreToolUse hook:拦截 git commit。两个通行证标记文件(30 分钟内)都在才放行。

const fs = require('fs')
const path = require('path')

let input = ''
process.stdin.on('data', (chunk) => { input += chunk })
process.stdin.on('end', () => {
  let data
  try {
    data = JSON.parse(input || '{}')
  } catch {
    process.exit(0) // 解析不了就放行,不误伤
  }

  const command = (data.tool_input && data.tool_input.command) || ''

  // 只拦截 git commit,其他命令直接放行
  if (!/git\s+commit\b/.test(command)) {
    process.exit(0)
  }

  // 用自己的位置定位项目根(脚本在 <项目>/.claude/hooks/ 下,向上两级即项目根),不受 cwd 影响
  const projDir = path.join(__dirname, '..', '..')
  const checksDir = path.join(projDir, '.claude', 'checks')
  const markers = ['test-passed.marker', 'quality-passed.marker']
  const FRESH_MS = 30 * 60 * 1000
  const now = Date.now()

  const fresh = markers.every((m) => {
    try {
      const st = fs.statSync(path.join(checksDir, m))
      return now - st.mtimeMs < FRESH_MS
    } catch {
      return false
    }
  })

  if (fresh) process.exit(0)

  process.stderr.write(JSON.stringify({
    hookSpecificOutput: { permissionDecision: 'deny' },
    systemMessage: '已阻止 git commit:缺少「单元测试通过 + 质量检查通过」通行证。请说「提交」让 git-commit 先跑完检查,通过后会自动提交。'
  }) + '\n')
  process.exit(2)
})
