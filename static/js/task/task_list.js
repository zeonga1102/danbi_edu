async function check_subtask(elem) {
    csrftoken = getCookie("csrftoken")
    
    let taskData = {
        subtaskId: elem.id.split("subtask_")[1],
        is_complete: elem.checked
    }

    const response = await fetch(`/task/subtask`, {
        method: 'PUT',
        headers: {
            'Content-type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            "X-CSRFToken": csrftoken
        },
        withCredentials: true,
        body: JSON.stringify(taskData)
    })
        .then(response => {
            if (response.status == 200) {
                window.location.reload()
            }

            if (response.status == 400) {
                alert(response.status)
            }
        });
}