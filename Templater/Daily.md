---
date: <% tp.date.now("YYYY-MM-DD", 0, tp.file.title, "YYYY-MM-DD") %>
week: <% tp.date.now("YYYY-[W]W", 0, tp.file.title, "YYYY-MM-DD") %>
year: <% tp.date.now("YYYY", 0, tp.file.title, "YYYY-MM-DD") %>
tags:
  - daily
type: notes
---

# helpers

- [[training-log]]
- [[nutrition-log]]
- [[training-progression-plan]]
- [[Portfel Akcji]]

## ideation

manual notebook / samsung-remainder -> 
	-> high priority -> google task -> google calendar optimization (time bookings if needed)
	-> low priority -> obsidian-templater-idea + obsidian-tasks

## 🎯 Focus (from last weekly review)
![[<% tp.date.now("YYYY-[W]W", -7, tp.file.title, "YYYY-MM-DD") %>#Next]]

## Dziennik


## Logs

<% tp.date.now("YYYY-MM-DD HH:mm") %> - file created


## ToDo
```tasks
not done
due after 2024-01-01
sort by priority
group by priority
group by function task.start.format("YYYY-MM-DD dddd")
```


## Files created today
```dataview
list
where file.cday = date(<% tp.file.title %>)
sort file.ctime desc
```
## Files modified today
```dataview
list
where file.mday = date(<% tp.file.title %>)
sort file.ctime desc
```




