# <问题简述> Loop 改进记录

> 记录路径：`spec/reports/loop-improvements/<yyyymmdd>-<问题简述>-loop改进记录.md`
> Status：Draft | In Progress | Verified | Synced | Deferred | Rejected
> 创建日期：YYYY-MM-DD
> 负责人：用户 | Agent | 用户 + Agent

## 1. 来源反馈

- 来源反馈单：`spec/reports/harness-feedback/<yyyymmdd>-<问题简述>-上游反馈单.md`
- 关联试点项目：已脱敏 | 不适用
- 问题分类：SKILL_CONTRACT | TEMPLATE_GAP | VALIDATOR_GAP | EVIDENCE_GAP | CONTEXT_LOADING | RULE_TOO_HEAVY | CROSS_PROJECT_REPEAT | 其他
- 是否进入上游改进：是 | 否 | 待确认

## 2. 用户决策

- 用户目标：
- 用户确认的边界：
- 不允许修改的范围：
- 需要用户再次确认的事项：无 | <说明>

## 3. 问题归因

- 现象摘要：
- 根因判断：
- 项目私有因素：无 | 有，说明
- 上游通用因素：无 | 有，说明
- 证据成熟度：L1 | L2 | L3

## 4. 修改清单

| 类型 | 路径 | 动作 | 状态 |
| --- | --- | --- | --- |
| skill | `skills/<skill>/SKILL.md` | 新增/修改/暂缓 | pending/done/deferred |
| template | `skills/<skill>/assets/templates/<template>.md` | 新增/修改/暂缓 | pending/done/deferred |
| validator | `scripts/validators/<script>.py` | 新增/修改/暂缓 | pending/done/deferred |
| docs | `docs/<doc>.md` | 新增/修改/暂缓 | pending/done/deferred |

## 5. 验证记录

| 验证命令 | 结果 | 说明 |
| --- | --- | --- |
| `python scripts/validate_all.py --root .` | 通过/失败/未执行 |  |
| `<其他命令>` | 通过/失败/未执行 |  |

## 6. 全局同步

- 是否涉及全局 skills：否 | 是
- 同步路径：不适用 | `C:\Users\chuang_ying_h\.agents\skills`
- 同步文件：无 | <文件列表>
- 哈希比对：不适用 | 通过 | 失败

## 7. 关闭结论

- 当前状态：Draft | In Progress | Verified | Synced | Deferred | Rejected
- 是否关闭：是 | 否
- 剩余风险：
- 待观察项：
