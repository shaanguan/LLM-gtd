# Document Sync Protocol — DingTalk

> Detailed operational protocol for DingTalk document sync.
> This is a reference file — consult during document sync operations.
> For the summary, see CLAUDE.md §4.

## Scheduling Document Block Layout (6 blocks, index 0–5)

- **block 0**: blockquote disclaimer "AI-generated" — **don't touch**
- **block 1**: h1 + 40×40 gif "submit requests below" — **don't touch** (image dims sensitive)
- **block 2**: request submission table — **read-only** (colleagues' input channel)
- **block 3**: h1 + 40×40 gif "below is the schedule" — **don't touch**
- **block 4**: schedule table — **agent writes here** via `update_document_block` with jsonml
- **block 5**: footer blockquote (timestamp can be updated)

## Update Procedure

1. `list_document_blocks` to get current blockId (don't hardcode, query each time)
2. Build full schedule jsonml (with `colsWidth / styleId / tblLook / tblW` + every `tr/tc`)
3. `update_document_block` blockId=schedule, format=jsonml
4. Same for footer timestamp
5. **Never** use `insert_document_block` at an existing position — duplicates with unreachable old table

## Rate-Limit Guard

- Between ≥3 consecutive `update_document_block` calls → `sleep 2-3s`
- On 5xx / rate limit → wait 5s, retry once → if still failing, skip and alert user
- `list_document_blocks` doesn't count — call as often as needed
- Total DingTalk API calls per cron ≤ 8

## Status Color Scheme (jsonml span `color` + `bold`)

| Status | Hex | Auto-derivation |
|---|---|---|
| Today's review | #fa8c16 | `due = today` |
| In progress | #1677ff | `due = tomorrow` and active |
| Pending | #8c8c8c | `due > tomorrow` or unstarted |
| Overdue | #f5222d | `due < today` |
| Completed | #52c41a | User confirmed done |

## Schedule Table Columns

Task | Project | Requester | Due | Status

- "Requester" is required
- 5 columns, consistent ordering

## Content Selection Rule

Show only:
- Items with explicit external request
- Items with independent review/delivery milestone

Exclude:
- Subtasks
- Internal coordination (alignment / discussion)
- Legacy cleanup
- Process actions
- "If users want everything they can open the Dashboard" — be selective

## Hard Limits (Non-negotiable)

- Only blocks 4 and 5 are writable; **never touch 0/1/2/3**
- Block 2 (request table) is sacred — colleagues' input channel
- **No markdown overwrite** of the whole document — kills 40×40 gif metadata
- **No `insert_document_block`** for new tables — old tables without blockIds become un-deletable
- Always confirm document ID matches title before any write
- jsonml image `width / height` must be a number, not a string

## Daily-Rollover Protocol (First Touch of Day)

1. Run `date` for today
2. `list_document_blocks` for both docs
3. Migrate yesterday's "Today's X" into daily doc's history table
4. Regenerate today's view (MIT + schedule + tomorrow preview) from current vault NA
5. Realign every relative phrase against today

## Lessons Learned

1. **Document overwritten** — didn't verify title before overwrite; lost attachments permanently
2. **Image sizes lost** — used markdown-overwrite mode; 40×40 gifs reset to default
3. **Duplicate table** — `insert_document_block` created unreachable old table
