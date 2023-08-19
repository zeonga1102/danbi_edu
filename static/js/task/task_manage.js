let teamIdNum = 0
let maxIdNum = 0

let addSubtask = {}
let editSubtask = {}
let deleteSubtask = []

window.onload = function () {
    const teamSelects = document.getElementsByClassName("team-select")
    const teamSelectDiv = teamSelects[teamSelects.length - 1]
    maxIdNum = parseInt(teamSelectDiv.id.split("team_select_")[1])
    teamIdNum = maxIdNum
}

function addTeamSelect() {
    const teamSelects = document.getElementsByClassName("team-select")
    const teamSelectDiv = teamSelects[teamSelects.length - 1]
    const newDiv = teamSelectDiv.cloneNode(true)

    teamIdNum++
    newDiv.id = `team_select_${teamIdNum}`
    newDiv.firstElementChild.id = `team_${teamIdNum}`
    newDiv.firstElementChild.options[0].selected = true
    newDiv.firstElementChild.removeAttribute("disabled")

    teamSelectDiv.after(newDiv)
    if(newDiv.lastElementChild.className == "form-select") {
        const btnDelete = `<svg onclick="deleteTeamSelect(this)" class="team-delete" xmlns="http://www.w3.org/2000/svg" width="25" height="25" fill="currentColor" class="bi bi-x-square" viewBox="0 0 16 16">
                                <path d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"/>
                                <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>
                            </svg>`
        newDiv.innerHTML = newDiv.innerHTML + btnDelete
    }

    addSubtask[teamIdNum] = newDiv.firstElementChild.value
}

function changeTeam(elem) {
    let curId = parseInt(elem.id.split("team_")[1])
    if(curId > maxIdNum) {
        addSubtask[curId] = elem.value
    }
    else {
        editSubtask[curId] = elem.value
    }
}

function deleteTeamSelect(elem) {
    let teamSelectLength = document.getElementsByClassName("team-select").length
    if(teamSelectLength <= 1) {
        alert("협업 팀은 1개 이상 존재해야 합니다.")
        return
    }

    let curId = parseInt(elem.parentNode.id.split("team_select_")[1])
    if(curId > maxIdNum) {
        delete addSubtask[curId]
    }
    else {
        deleteSubtask.push(curId)
        delete editSubtask[curId]
    }

    elem.parentNode.remove()
}

async function putTask() {
    csrftoken = getCookie("csrftoken")

    urlSearch = new URLSearchParams(location.search)
    task_id = urlSearch.get("task")

    let taskData = {
        id: task_id,
        title: document.getElementById("title").value,
        content: document.getElementById("content").value,
        "addSubtask": Object.values(addSubtask),
        "editSubtask": editSubtask,
        "deleteSubtask": deleteSubtask
    }

    const response = await fetch(`/task/manage`, {
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
                window.location.href = "/task/list"
            }

            if (response.status == 400) {
                alert(response.status)
            }
        })
}