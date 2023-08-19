let teamIdNum = 1

function addTeamSelect() {
    const teamSelects = document.getElementsByClassName("team-select")
    const teamSelectDiv = teamSelects[teamSelects.length - 1]
    const newDiv = teamSelectDiv.cloneNode(true)

    teamIdNum++
    newDiv.id = `team_select_${teamIdNum}`
    newDiv.firstElementChild.id = `team_${teamIdNum}`

    teamSelectDiv.after(newDiv)
}

function deleteTeamSelect(elem) {
    let teamSelectLength = document.getElementsByClassName("team-select").length
    if(teamSelectLength <= 1) {
        alert("협업 팀은 1개 이상 존재해야 합니다.")
        return
    }

    elem.parentNode.remove()
}

async function postTask() {
    csrftoken = getCookie("csrftoken")
    
    let subtaskList = []
    const formSelects = document.getElementsByClassName("form-select")
    for(let i=0; i<formSelects.length; i++) {
        subtaskList.push(formSelects[i].value)
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