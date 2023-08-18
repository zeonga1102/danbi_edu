function getCookie(name) {
    if (!document.cookie) {
      return null
    }
  
    const xsrfCookies = document.cookie.split(";")
      .map(c => c.trim())
      .filter(c => c.startsWith(name + "="))
  
    if (xsrfCookies.length === 0) {
      return null
    }
    return decodeURIComponent(xsrfCookies[0].split("=")[1])
  }


async function logout() {
    csrftoken = getCookie("csrftoken")
    const response = await fetch ("/login", {
        headers: { "X-CSRFToken": csrftoken },
        method: "DELETE"
    })

    if(response.status == 200)
        window.location.replace("/")
    else
        alert(response.status)
}
