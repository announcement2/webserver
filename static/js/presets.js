function announce_preset(preset) {
    announce_button = document.getElementById("announce_button");
    announcement_message = document.getElementById("announcement_message");
    announcement_message.innerHTML = preset;
    announce_button.click();
}
