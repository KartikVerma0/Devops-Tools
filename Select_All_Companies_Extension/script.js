document.addEventListener('DOMContentLoaded', function () {
  const selectAllButtonEdit = document.getElementById("selectalledit");
  if (selectAllButtonEdit) {
    selectAllButtonEdit.addEventListener("click", () => {
      // Query the active tab and inject the script
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        chrome.scripting.executeScript({
          target: { tabId: tabs[0].id },
          func: selectAllPermissionsEdit // This function will run in the context of the current tab
        });
      });
    });
  }

  const selectAllButtonRead = document.getElementById("selectallread");
  if (selectAllButtonRead) {
    selectAllButtonRead.addEventListener("click", () => {
      // Query the active tab and inject the script
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        chrome.scripting.executeScript({
          target: { tabId: tabs[0].id },
          func: selectAllPermissionsRead // This function will run in the context of the current tab
        });
      });
    });
  }
});

// The function to be executed in the context of the webpage
function selectAllPermissionsEdit() {
  document.querySelectorAll("em[mattooltip='Permission to edit']").forEach((ele) => ele.click());
}

function selectAllPermissionsRead(){
  document.querySelectorAll("mat-checkbox").forEach((ele)=>{ele.children[0].children[0].children[0].click()})
}
