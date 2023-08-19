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

    teamSelectDiv.after(newDiv)

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
        "addSubtask": addSubtask,
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