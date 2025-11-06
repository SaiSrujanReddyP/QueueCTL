for this we need to tell that get only works with key and not other things


queuectl> config get backoff-base 2
Usage: queuectl.py config get [OPTIONS] KEY
Try 'queuectl.py config get --help' for help.
+- Error ---------------------------------------------------------------------+
| Got unexpected extra argument (2)                                           |
+-----------------------------------------------------------------------------+

EOF works

banner need to make a small change

clear works 

config works

queuectl> dashboard
Starting web dashboard...
This will start the dashboard in the background.
Access it at: http://localhost:8080
Dashboard started! Check http://localhost:8080
queuectl> Starting web dashboard at http://localhost:8080
Web dashboard started at http://localhost:8080
Press Ctrl+C to stop the dashboard
 need to check dashboard but it needs to stop this and go back to the interactive shell only not directly outside


 Starting Interactive Shell...
Type 'help' for command help, 'exit' to quit


Welcome to QueueCTL Interactive Shell!
Type 'help' for available commands or 'exit' to quit.
You can run any queuectl command without the 'python queuectl.py' prefix.

this might be a bit misleading need to tell that


queuectl> dlq
DLQ commands:
  dlq list           - List jobs in DLQ
  dlq retry <job_id> - Retry a job from DLQ
queuectl> dlq list
No jobs in Dead Letter Queue
queuectl> dlq retry 

here in dlq when telling to retry it needs to list a option to show the commands to check the job id 


enqueue doesnt work for different commands 

queuectl> enqueue   
Error: Job JSON required
Example: enqueue {"id":"test","command":"echo hello"}
queuectl> enqueue {"id":"test","command":"mkdir folder"}
Usage: queuectl.py enqueue [OPTIONS] JOB_JSON
Try 'queuectl.py enqueue --help' for help.
+- Error ---------------------------------------------------------------------+
| Got unexpected extra argument (folder})                                     |
+-----------------------------------------------------------------------------+
queuectl> 

exit works 

need to check this demo 


queuectl> demo
Running Enhanced Demo...
Adding job: demo_hello (priority: 1)
OK Job enqueued: demo_hello
  Command: echo Hello from QueueCTL!
  Max retries: 3
Adding job: demo_date (priority: 0)
OK Job enqueued: demo_date
  Command: date /t
  Max retries: 3
Adding job: demo_time (priority: -1)
OK Job enqueued: demo_time
  Command: time /t
  Max retries: 3
Adding job: demo_scheduled (priority: 0)
OK Job enqueued: demo_scheduled
  Command: echo Scheduled job!
  Max retries: 3
Adding job: demo_fail (priority: 0)
OK Job enqueued: demo_fail
  Command: nonexistent_command
  Max retries: 2

Enhanced demo jobs added!
• High priority job will run first
• Scheduled job will run in 30 seconds
• Failed job will demonstrate retry logic
Start workers with: worker start --count 2

need to tell it to create something comprehensive for the user to understand 


queuectl> priority
Error: Command required
Example: priority echo urgent task
queuectl> priority echo urgent task
Creating high priority job: priority_1762665903
OK Job enqueued: priority_1762665903
  Command: echo urgent task
  Max retries: 3
queuectl> list
+-----------------------------------------------------------------------------+
| ID              | State     | Command         | Attempts | Created          |
|-----------------+-----------+-----------------+----------+------------------|
| priority_17626… | pending   | echo urgent     |   0/3    | 2025-11-09       |
|                 |           | task            |          | 05:25:03         |
| demo_fail       | pending   | nonexistent_co… |   0/2    | 2025-11-09       |
|                 |           |                 |          | 05:02:22         |
| demo_scheduled  | scheduled | echo Scheduled  |   0/3    | 2025-11-09       |
|                 |           | job!            |          | 05:02:22         |
| demo_time       | pending   | time /t         |   0/3    | 2025-11-09       |
|                 |           |                 |          | 05:02:21         |
| demo_date       | pending   | date /t         |   0/3    | 2025-11-09       |
|                 |           |                 |          | 05:02:21         |
| demo_hello      | pending   | echo Hello from |   0/3    | 2025-11-09       |
|                 |           | QueueCTL!       |          | 05:02:20         |
| workflow-test-… | pending   | echo workflow   |   0/3    | 2025-11-09       |
|                 |           | test            |          | 04:50:31         |
| persistence-te… | pending   | echo            |   0/3    | 2025-11-09       |
|                 |           | persistence     |          | 04:50:29         |
|                 |           | test            |          |                  |
| test-job        | pending   | echo test       |   0/3    | 2025-11-09       |
|                 |           |                 |          | 04:49:27         |
| test1           | pending   | echo Hello      |   0/3    | 2025-11-09       |
|                 |           | World           |          | 04:41:17         |
| timeout         | completed | echo test       |   0/3    | 2025-11-08       |
|                 |           |                 |          | 16:22:25         |
| priority        | completed | echo test       |   0/3    | 2025-11-08       |
|                 |           |                 |          | 16:22:24         |
| test            | completed | echo hello      |   0/3    | 2025-11-08       |
|                 |           |                 |          | 16:22:23         |
| persist-test    | completed | echo test       |   0/3    | 2025-11-08       |
|                 |           |                 |          | 16:21:21         |
+-----------------------------------------------------------------------------+




I want you to give proper readme with these 📘 README Expectations

Your README.md should cover:

Setup Instructions — How to run locally

Usage Examples — CLI commands with example outputs

Architecture Overview — Job lifecycle, data persistence, worker logic

Assumptions & Trade-offs — Decisions made, any simplifications

Testing Instructions — How to verify functionality and also I need you to give commands to open the 