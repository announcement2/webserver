var socket = io();

socket.on("connect", () => {
    console.log("Socket.IO Connected");
})

socket.emit("joinRoom");``

socket.on("joinedRoom", (room) => {
    window.current_room = room;
})

function isInArray(array_, text) {
    return array_.indexOf(text.toLowerCase()) > -1;
}

function removeAnnouncement(announcement_uuid) {
    announcement = document.getElementById(announcement_uuid);
    announcement.remove();
    delete announcements[announcement_uuid];
}

socket.on("announcement", (data) => {
    recent_announcements = document.getElementById("recent-announcements");
    announcement_li = document.createElement("li");
    announcement_li.innerText = data["message"] + " - " + data["name"] + " - now";
    announcement_li.setAttribute("id", data["uuid"])
    recent_announcements.appendChild(announcement_li);
    addAnnouncementToObj(data["uuid"], data["name"], data["message"], "now")
})

socket.on("clearAnnouncements", () => {
    recent_announcements = document.getElementById("recent-announcements");
    recent_announcements.innerHTML = "";
})

socket.on("announcementTimeUpdate", (data) => {
    recent_announcements = document.getElementById("recent-announcements");
    for (let i = 0; i < recent_announcements.children.length; i++) {
        child = recent_announcements.children[i];
        if (isInArray(Object.keys(data), child.id)) {
            announcement_data = announcements[child.id];
            child.innerText = announcement_data["message"] + " - " + announcement_data["name"] + " - " + data[child.id];
            addAnnouncementToObj(child.id, announcement_data["name"], announcement_data["message"], data[child.id]);
        }
    }
})

function updateAnnouncementTimes() {
    socket.emit("updateAnnouncementTimes", {"data": Object.keys(announcements), "room": window.current_room});
}

setInterval(updateAnnouncementTimes, 1000);
