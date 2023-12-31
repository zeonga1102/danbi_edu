async function checkSubtask(elem) {
    csrftoken = getCookie("csrftoken")
    
    let taskData = {
        subtaskId: parseInt(elem.id.split("subtask_")[1]),
        isComplete: elem.checked
    }

    const response = await fetch(`/task/subtask`, {
        method: "PUT",
        headers: {
            "Content-type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
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
        })
}


function editTask(elem) {
    const task_id = elem.id.split("btn_edit_")[1]
    window.location.href = `/task/manage?task=${task_id}`
}


async function deleteTask(elem) {
    csrftoken = getCookie("csrftoken")

    const task_id = elem.id.split("btn_delete_")[1]
    const response = await fetch(`/task/manage?task=${task_id}`, {
        method: "DELETE",
        headers: {
            "Content-type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": csrftoken
        },
        withCredentials: true,
    })
        .then(response => {
            if (response.status == 200) {
                window.location.reload()
            }

            if (response.status == 400) {
                alert(response.status)
            }
        })
}