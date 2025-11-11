# eminmin_algorithm.py
import random
from collections import namedtuple

VM = namedtuple('VM', ['name', 'ip', 'cpu_cores', 'ram_gb'])
Task = namedtuple('Task', ['id', 'name', 'index', 'cpu_load'])

def calculate_estimated_makespan(assignments: dict, tasks_dict: dict, vms_dict: dict) -> float:
    """Menghitung makespan dari hasil penugasan."""
    vm_finish_time = {vm.name: 0.0 for vm in vms_dict.values()}
    for task_id, vm_name in assignments.items():
        task = tasks_dict[task_id]
        vm = vms_dict[vm_name]
        exec_time = task.cpu_load / vm.cpu_cores
        vm_finish_time[vm_name] += exec_time
    return max(vm_finish_time.values())

def enhanced_min_min(tasks: list[Task], vms: list[VM]) -> dict:
    """
    Enhanced Min-Min Scheduling Algorithm (EMin-Min)
    - Menggunakan load balancing improvement dari Min-Min klasik
    """
    print("Memulai Enhanced Min-Min Scheduling...")

    vms_dict = {vm.name: vm for vm in vms}
    tasks_dict = {task.id: task for task in tasks}

    unassigned_tasks = tasks.copy()
    ready_time = {vm.name: 0.0 for vm in vms}

    assignment = {}

    # Threshold: untuk memisahkan antara short dan long tasks
    avg_load = sum(t.cpu_load for t in tasks) / len(tasks)
    threshold_ratio = 0.5  # rasio tweak, bisa disesuaikan
    threshold = avg_load * threshold_ratio

    while unassigned_tasks:
        # Hitung completion time (CTij) untuk semua task-VM
        ct_matrix = {}
        for task in unassigned_tasks:
            ct_matrix[task.id] = {}
            for vm in vms:
                et = task.cpu_load / vm.cpu_cores
                ct = ready_time[vm.name] + et
                ct_matrix[task.id][vm.name] = ct

        # Tentukan task terbaik (dengan CTmin)
        task_min_ct = {}
        for task in unassigned_tasks:
            vm_best = min(ct_matrix[task.id], key=ct_matrix[task.id].get)
            ct_best = ct_matrix[task.id][vm_best]
            task_min_ct[task.id] = (vm_best, ct_best)

        # Enhanced part:
        # Pilih antara short-task-priority atau long-task-priority tergantung beban rata-rata
        short_tasks = [tid for tid, (vm, ct) in task_min_ct.items()
                       if tasks_dict[tid].cpu_load <= threshold]
        long_tasks = [tid for tid, (vm, ct) in task_min_ct.items()
                      if tasks_dict[tid].cpu_load > threshold]

        # Ambil task dengan CTmin tergantung kategori
        if short_tasks:
            # short tasks diberi prioritas lebih dulu
            selected_task_id = min(short_tasks, key=lambda tid: task_min_ct[tid][1])
        else:
            selected_task_id = min(task_min_ct.keys(), key=lambda tid: task_min_ct[tid][1])

        selected_vm, selected_ct = task_min_ct[selected_task_id]

        # Update hasil penugasan
        assignment[selected_task_id] = selected_vm
        selected_task = tasks_dict[selected_task_id]
        et = selected_task.cpu_load / vms_dict[selected_vm].cpu_cores
        ready_time[selected_vm] += et

        # Hapus dari daftar unassigned
        unassigned_tasks = [t for t in unassigned_tasks if t.id != selected_task_id]

    makespan = calculate_estimated_makespan(assignment, tasks_dict, vms_dict)
    print(f"Enhanced Min-Min selesai. Estimasi Makespan: {makespan:.2f}")

    return assignment
