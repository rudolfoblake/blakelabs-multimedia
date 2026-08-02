import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Layouts
import BlakeLabsTheme 1.0

Rectangle {
  id: root
  signal filesSelected(var urls)
  property bool active: dropArea.containsDrag

  implicitHeight: 300
  radius: Theme.radiusLarge
  color: active ? "#13231A" : Theme.surface
  border.width: active ? 2 : 1
  border.color: active ? Theme.accent : Theme.border

  Behavior on color { ColorAnimation { duration: 140 } }
  Behavior on border.color { ColorAnimation { duration: 140 } }

  DropArea {
    id: dropArea
    anchors.fill: parent
    keys: ["text/uri-list"]
    onDropped: function(drop) {
      if (drop.hasUrls) {
        root.filesSelected(drop.urls)
        drop.acceptProposedAction()
      }
    }
  }

  FileDialog {
    id: fileDialog
    title: "Choose audio or video files"
    fileMode: FileDialog.OpenFiles
    nameFilters: [
      "Audio and video (*.mp3 *.wav *.flac *.m4a *.aac *.ogg *.opus *.mp4 *.mkv *.mov *.avi *.webm *.wmv)",
      "All files (*)"
    ]
    onAccepted: root.filesSelected(selectedFiles)
  }

  ColumnLayout {
    anchors.centerIn: parent
    width: Math.min(parent.width - 48, 460)
    spacing: 12

    Rectangle {
      Layout.alignment: Qt.AlignHCenter
      Layout.preferredWidth: 60
      Layout.preferredHeight: 60
      radius: 18
      color: root.active ? Theme.accent : Theme.surfaceRaised

      Text {
        anchors.centerIn: parent
        text: root.active ? "↓" : "+"
        color: root.active ? Theme.background : Theme.accent
        font.pixelSize: 28
        font.weight: Font.Light
      }
    }

    Text {
      Layout.fillWidth: true
      text: root.active ? "Drop files here" : "Add audio or video"
      color: Theme.text
      font.pixelSize: 21
      font.weight: Font.Bold
      horizontalAlignment: Text.AlignHCenter
      wrapMode: Text.WordWrap
    }

    Text {
      Layout.fillWidth: true
      text: "Files are analyzed locally. Nothing is uploaded."
      color: Theme.textMuted
      font.pixelSize: 12
      horizontalAlignment: Text.AlignHCenter
      wrapMode: Text.WordWrap
    }

    Text {
      Layout.fillWidth: true
      text: "MP3, WAV, FLAC, M4A, MP4, MKV, MOV and WebM"
      color: Theme.textMuted
      opacity: 0.72
      font.pixelSize: 10
      horizontalAlignment: Text.AlignHCenter
      wrapMode: Text.WordWrap
    }

    PrimaryButton {
      Layout.alignment: Qt.AlignHCenter
      Layout.topMargin: 4
      text: "Choose files"
      onClicked: fileDialog.open()
    }
  }
}
