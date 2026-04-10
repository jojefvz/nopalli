def parse_new_dispatch_plan(form) -> list[dict]:
    containers = []
    i = 0
    while f'container_number_{i}' in form:
        container = {
            'number': form[f'container_number_{i}'],
            'size': form[f'container_size_{i}'],
        }
        containers.append(container)
        i += 1
    
    # Build stops list
    plan = []
    i = 0
    while f'task_priority_{i}' in form:
        matched_container = ''
        for c in containers:
            if f'task_container_{i}' in form and form[f'task_container_{i}'] == c['number']:
                matched_container = c
                print("MATCHED CONTAINER", matched_container)
                break
        
        stop = {
            'priority': form[f'task_priority_{i}'],
            'location_id': form[f'task_location_id_{i}'],
            'instruction': form[f'task_instruction_{i}'],
            'container': matched_container,
            'date': form[f'task_date_{i}'],
            'appointment': {
                'type': form.get(f'task_appointment_type_{i}', ''),
                'start_time': form.get(f'task_appt_start_time_{i}', ''),
                'end_time': form.get(f'task_appt_end_time_{i}', '')
            }
        }
        plan.append(stop)
        i += 1

    return plan