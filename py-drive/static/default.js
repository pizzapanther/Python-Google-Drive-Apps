var pickerView = new google.picker.View(google.picker.ViewId.DOCS);
pickerView.setMimeTypes('text/plain');
var pickerView2 = new google.picker.View(google.picker.ViewId.RECENTLY_PICKED);
var pickerView3 = new google.picker.View(google.picker.ViewId.FOLDERS);

function open_file_dialog () {
  picker = new google.picker.PickerBuilder().
    setAppId(CLIENT_ID).
    addView(pickerView).
    addView(pickerView2).
    addView(pickerView3).
    setCallback(pickerCallback).
    enableFeature(google.picker.Feature.MULTISELECT_ENABLED).
    build();
  picker.setVisible(true);
}

function pickerCallback (data) {
  if (data.action == google.picker.Action.PICKED) {
    file_opener(data.docs[0].id);
  }
}

function file_opener (file_id) {
  $.ajax({
    type: 'POST',
    url: '/shatner',
    data: {'file_id': file_id, 'task': 'open'},
    success: load_file,
    error: function () { alert('Error opening file.'); }
  });
}

var CURRENT_ID;
function load_file (data, textStatus, jqXHR) {
  $('#textedit').val(data.file.content);
  $("#filename").html(data.file.title);
  CURRENT_ID = data.file.id;
}

function save_file () {
  var name = $("#filename").html();
  var content = $('#textedit').val();
  
  $.ajax({
    type: 'POST',
    url: '/shatner',
    data: {
      file_id: CURRENT_ID,
      task: 'save',
      content: content,
      name: name
    },
    success: function (data) {
      alert('Save was successful');
    },
    error: function () { alert('Error saving file ' + name); }
  });
}

