function deleteNote(noteId) {
  fetch("/delete-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    window.location.href = "/";
  });
}

function deleteEvent(eventId) {
  fetch("/delete-event", {
    method: "POST",
    body: JSON.stringify({ eventId: eventId }),
  }).then((_res) => {
    window.location.href = "/create-event";
  });
}

function deleteData(eventId, itemName) {
  fetch("/delete-item", {
    method: "POST",
    body: JSON.stringify({ eventId: eventId, itemName: itemName }),
  }).then((_res) => {
    window.location.href = "/create-event";
  });
}

function addItem(eventId, itemName) {
  fetch("/add-item", {
    method: "POST",
    body: JSON.stringify({ eventId: eventId, itemName: itemName }),
  }).then((_res) => {
    window.location.href = "/create-event";
  });
}

