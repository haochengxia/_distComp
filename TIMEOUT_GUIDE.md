# DistComp Timeout Mechanism User Guide

## Overview

DistComp now supports task-level timeout mechanisms to prevent tasks from running indefinitely, improving system stability and resource utilization.

## Features

1. **Task-level timeout control**: Each task can set independent timeout duration
2. **Default timeout protection**: Tasks without specified timeout use system default timeout
3. **Automatic process cleanup**: Timeout tasks are automatically terminated and resources cleaned up
4. **Backward compatibility**: Supports old task formats
5. **Flexible configuration**: Timeout-related parameters can be adjusted via configuration file

## Configuration Parameters

Add the following configuration items in `conf.json`:

```json
{
    "default_task_timeout_seconds": 3600,    // Default task timeout (seconds)
    "task_timeout_check_interval": 30        // Timeout check interval (seconds)
}
```

## Task Format

### Old Format (Backward Compatible)
```
task_type:priority:min_dram:min_cpu:task_params
```

### New Format (Supports Timeout)
```
task_type:priority:min_dram:min_cpu:timeout_seconds:task_params
```

### Parameter Description
- `task_type`: Task type (shell, python, demo)
- `priority`: Priority (higher number means higher priority)
- `min_dram`: Minimum memory requirement (GB)
- `min_cpu`: Minimum CPU core requirement
- `timeout_seconds`: Timeout duration (seconds), 0 means no limit
- `task_params`: Task parameters

## Usage Examples

### 1. Tasks Using Default Timeout
```
shell:5:8:2:echo "Hello World"
```

### 2. Tasks with Custom Timeout
```
shell:5:8:2:1800:echo "30-minute timeout task"
shell:3:4:1:300:echo "5-minute timeout task"
shell:4:16:4:7200:echo "2-hour timeout task"
```

### 3. Tasks Without Timeout Limit
```
shell:2:2:1:0:echo "Task without timeout limit"
```

## Timeout Handling Mechanism

### 1. Task Execution Timeout
- When task execution time exceeds the set timeout, the system automatically terminates the task
- Uses `subprocess.TimeoutExpired` exception to handle timeouts
- Timeout tasks are marked as failed and error information is recorded

### 2. Process Cleanup
- All child processes of timeout tasks are forcibly terminated
- Uses `psutil` to ensure complete process tree cleanup
- Releases related memory and CPU resources

### 3. Status Updates
- Timeout tasks are moved from `in_progress_tasks` to `failed_tasks`
- Records timeout reasons and failure information
- Supports task retry mechanism

## Monitoring and Logging

### 1. Timeout Monitoring Thread
- Independent monitoring thread periodically checks task timeouts
- Configurable check interval (default 30 seconds)
- Automatically handles timeout tasks

### 2. Logging
- Timeout events record detailed log information
- Includes task ID, timeout duration, processing results, etc.
- Facilitates problem troubleshooting and performance analysis

### 3. Status Queries
```bash
# Check failed tasks (including timeout tasks)
python3 redisManager.py --task checkTask --failed true

# View task failure reasons
python3 redisManager.py --task checkTask --failed true --print_result true
```

## Best Practices

### 1. Timeout Duration Settings
- Set reasonable timeout duration based on task type and complexity
- Consider system resources and task priority
- Set different timeout strategies for different types of tasks

### 2. Monitoring Configuration
- Adjust timeout check interval based on task execution time
- Avoid overly frequent checks affecting performance
- Ensure timely and effective timeout handling

### 3. Error Handling
- Monitor timeout task failure rates
- Analyze timeout reasons and optimize tasks
- Consider whether timeout duration or task parameters need adjustment

## Troubleshooting

### 1. Frequent Task Timeouts
- Check if task complexity is reasonable
- Consider increasing timeout duration or optimizing tasks
- Check if system resources are sufficient

### 2. Incomplete Process Cleanup
- Check `psutil` permissions
- Ensure process termination logic is correct
- View related error logs

### 3. Performance Impact
- Adjust timeout check interval
- Monitor system resource usage
- Optimize timeout handling logic

## Upgrade Instructions

### Upgrading from Old Version
1. Update configuration file, add timeout-related parameters
2. Restart worker nodes to load new configuration
3. Existing task formats remain compatible
4. Gradually migrate to new task formats

### Compatibility
- Fully backward compatible with old task formats
- Existing tasks can be used without modification
- New features are optional and don't affect existing deployments
