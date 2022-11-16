// Fetch members on page load
fetch("members")
  .then(function (response) {
    return response.json();
  })
  .then(function (data) {
    appendDataMembers(data);
  })
  .catch(function (err) {
    console.log("error: " + err);
  });

// Static elements
let mainContainer = document.getElementById("members");
let messagebar = document.getElementsByClassName("messagebar")[0];
let addButton = document.getElementById("addButton");

// Show no members message
if (mainContainer.innerHTML == "") {
  var div = document.createElement("div");
  div.innerHTML = "No key-value pairs added";
  mainContainer.appendChild(div);
}

// Display members
function appendDataMembers(data) {
  mainContainer.innerHTML = "";

  for (var i = 0; i < data.length; i++) {
    var div = document.createElement("div");
    div.innerHTML =
      "Key-value pair " + String(i + 1) + " : " + JSON.stringify(data[i]);
    mainContainer.appendChild(div);
  }
}

// Add key-value pair
function addMember() {
  var x = document.getElementById("frm1");
  try {
    var myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");

    var raw = JSON.stringify({
      key: x.elements[0].value,
      value: x.elements[1].value,
    });

    console.log(raw);

    var requestOptions = {
      method: "POST",
      headers: myHeaders,
      body: raw,
      redirect: "follow",
    };

    addButton.disabled = true;
    fetch("/members", requestOptions).then((response) => {
      addButton.disabled = false;
      if (response.ok) {
        displayMessagebar("info");
        messagebar.firstElementChild.innerHTML = "Member added successfully";
      } else {
        displayMessagebar("error");

        if (response.status == 500) {
          messagebar.firstElementChild.innerHTML =
            "The server encountered an unknown error.";
          return;
        }

        response.json().then((res) => {
          messagebar.firstElementChild.innerHTML = res.errors[0].message;
        });
      }
    });
  } catch (err) {
    console.error(`Error: ${err}`);
  }
}

// Refresh web-page
function refreshPage() {
  window.location.reload();
}

// Display messagebar
function displayMessagebar(messageClass) {
  messagebar.classList.add(messageClass);
  messagebar.style.opacity = 1;
}

// Hide messagebar with fadeout effect
function closeMessagebar() {
  let style = messagebar.style;
  style.opacity = 1;
  (function fade() {
    (style.opacity -= 0.1) < 0
      ? messagebar.classList.remove("info", "error")
      : setTimeout(fade, 25);
  })();
}
