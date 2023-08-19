let teamIdNum = 1

function addTeamSelect() {
    const teamSelectDiv = document.getElementById(`team_select_${teamIdNum}`)
    const newDiv = teamSelectDiv.cloneNode(true)

    teamIdNum++
    newDiv.id = `team_select_${teamIdNum}`
    newDiv.firstElementChild.id = `team_${teamIdNum}`

    teamSelectDiv.after(newDiv)
}

function deleteTeamSelect(elem) {
    if(teamIdNum <= 1) {
        alert("협업 팀은 1개 이상 존재해야 합니다.")
        return
    }

    elem.parentNode.remove()
    teamIdNum--
}

async function postTask() {
    csrftoken = getCookie("csrftoken")
    
    let subtaskList = []
    for(let i=1; i<=teamIdNum; i++) {
        subtaskList.push(document.getElementById(`team_${i}`).value)
    }

    let taskData = {
        title: document.getElementById("title").value,
        content: document.getElementById("content").value,
        subtask: subtaskList,
    }

    const response = await fetch(`/task/register`, {
        method: "POST",
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