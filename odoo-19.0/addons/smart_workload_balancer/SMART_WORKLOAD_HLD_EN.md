# Smart Workload Balancer - User Stories and High-Level Design (English)

## 1. As-Is Process Summary

The current Odoo project management flow is mainly manual:
1. A Project Manager creates or updates tasks.
2. Task assignment is done manually without a structured workload rule.
3. Team overload and overdue workload are not visible in a unified dashboard.
4. There is no automatic recommendation of the best assignees for each task.
5. No daily metric refresh exists to support workload-based decision making.

This means the current process depends heavily on human judgment, which can cause:
- uneven workload distribution,
- overload for some employees,
- delayed task completion,
- lack of visibility for managers.

## 2. Proposed To-Be Solution

The Smart Workload Balancer feature introduces an intelligent assignment support system inside Odoo Project Management.

It provides:
- assignment rules per project,
- workload score calculation,
- overload and high-workload warnings,
- automatic task assignee suggestions,
- employee workload dashboard,
- daily metric refresh via cron.

## 3. User Stories

### Epic: Smart Task Assignment and Workload Monitoring

1. As a Project Manager, I want to define assignment thresholds for each project, so that workload rules are consistent and reusable.
2. As a Project Manager, I want the system to recommend the best assignees for a task, so that assignment is faster and more balanced.
3. As a Project Manager, I want to see overload warnings on tasks, so that I can avoid assigning new work to overloaded employees.
4. As a Project Manager, I want to override the recommendation and record the reason, so that I can still make business decisions when needed.
5. As a Manager, I want to monitor employee workload through a dashboard, so that I can identify overload and high-load staff quickly.
6. As a System, I want workload metrics to refresh automatically every day, so that the recommendation data is always up to date.

## 4. Functional Scope

### 4.1 Core Models

- project.assignment.rule
  - Stores project-specific assignment rules.
  - Fields: project_id, max_task_threshold, max_overtime_threshold, max_overdue_threshold, skill_weight, workload_weight, active, note.

- project.workload.metric
  - Stores employee workload indicators per project.
  - Fields: employee_id, user_id, project_id, active_tasks_count, overdue_tasks_count, completed_tasks_count, total_timesheet_hours, overtime_hours, workload_score, workload_status, last_updated.

- project.task (inherited)
  - Adds recommendation support and warning display for task assignment.
  - Fields: recommended_assignee_ids, override_reason, show_override_reason, workload_warning.

### 4.2 Main Functional Flows

1. Project Manager configures assignment rules.
2. Task form displays the recommendation button.
3. System evaluates all candidate employees.
4. System filters overloaded users and ranks candidates by workload score.
5. System proposes up to three assignees.
6. Task displays warnings and allows override with reason.
7. Daily cron refreshes workload metrics.

## 5. Backend Design

### 5.1 Architecture

The module is built as a standard Odoo addon under:
- addons/smart_workload_balancer/models
- addons/smart_workload_balancer/views
- addons/smart_workload_balancer/security
- addons/smart_workload_balancer/data

### 5.2 Model Responsibilities

#### project.assignment.rule
Responsibilities:
- hold project rules,
- validate weight totals (= 100%),
- support project-level assignment policy.

#### project.workload.metric
Responsibilities:
- calculate workload from tasks and timesheets,
- classify status as available / normal / high / overload,
- provide dashboard and analytics data.

#### project.task
Responsibilities:
- trigger recommendation logic,
- display overload warnings,
- store override reason when PM chooses outside the recommendation list.

### 5.3 Business Logic Flow

1. Candidate users are collected from the project members / followers.
2. Each candidate is matched to an employee record.
3. Workload metrics are loaded or created if missing.
4. Users exceeding task or overtime thresholds are excluded.
5. Remaining users are sorted by workload score.
6. Top three are displayed and saved as recommended assignees.
7. Notification / chatter message is posted to the task.

### 5.4 Cron / Automation

- A daily cron updates all workload metrics.
- It recomputes task counts, overdue counts, overtime hours, and workload score.

## 6. High-Level Design (HLD)

### 6.1 Presentation Layer
- Odoo Project task form
- Workload dashboard (kanban/list/graph/form)
- Assignment rule menu
- Employee workload metrics menu

### 6.2 Application Layer
- Model logic in Python:
  - recommendation engine
  - workload metric computation
  - overload warning logic
  - override reason handling

### 6.3 Data Layer
- Odoo ORM models
- Existing Odoo database tables for project.task, project.project, hr.employee, account.analytic.line
- New records in project.assignment.rule and project.workload.metric

### 6.4 Security Layer
- Project Manager: full access to rules and workload metrics
- Project User: read access to personal workload metrics

## 7. English Translation Plan for Odoo UI

The UI and supporting documentation are now aligned to English terminology. The following labels are the approved English names used across the module:

| UI / Documentation Term | English Label |
|---|---|
| Smart Workload Balancer | Smart Workload Balancer |
| Task Assignment Rule | Task Assignment Rule |
| Project | Project |
| Max Tasks per Employee | Max Tasks per Employee |
| Max Overtime Hours | Max Overtime Hours |
| Max Overdue Tasks | Max Overdue Tasks |
| Skill Weight (%) | Skill Weight (%) |
| Workload Weight (%) | Workload Weight (%) |
| Note | Note |
| Suggest Assignees | Suggest Assignees |
| Recommended by System | Recommended by System |
| Reason for Override | Reason for Override |
| Confirm and Save Reason | Confirm and Save Reason |
| Employee Workload Metrics | Employee Workload Metrics |
| Workload Dashboard | Workload Dashboard |
| Active Tasks | Active Tasks |
| Overdue Tasks | Overdue Tasks |
| Completed Tasks | Completed Tasks |
| Total Worked Hours | Total Worked Hours |
| Overtime Hours | Overtime Hours |
| Workload Score | Workload Score |
| Status | Status |
| Last Updated | Last Updated |

## 8. Recommended Next Implementation Steps

1. Standardize all menu labels and field strings to English.
2. Keep the computation logic in the current models.
3. Add richer scoring rules using skill level, availability, and due date priority.
4. Add notifications for PM and assignees in the task chatter.
5. Add reporting views for weekly/monthly workload trends.
