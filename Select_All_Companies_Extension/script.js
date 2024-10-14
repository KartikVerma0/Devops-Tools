document.addEventListener('DOMContentLoaded', function () {
  const selectAllButton = document.getElementById("selectall");
  if (selectAllButton) {
    selectAllButton.addEventListener("click", () => {
      // Query the active tab and inject the script
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        chrome.scripting.executeScript({
          target: { tabId: tabs[0].id },
          func: selectAllPermissions // This function will run in the context of the current tab
        });
      });
    });
  }
});

// The function to be executed in the context of the webpage
function selectAllPermissions() {
  document.querySelectorAll("em[mattooltip='Permission to edit']").forEach((ele) => ele.click());
}

