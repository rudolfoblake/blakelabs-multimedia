import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Layouts
import BlakeLabsTheme 1.0

Rectangle {
  id: root
  signal filesSelected(var urls)
  property bool active: dropArea.containsDrag

  implicitHeight: 292
  radius: Theme.radiusLarge
  color: active ? Theme.accentSoft : Theme.surface
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
    spacing: 11

    Rectangle {
      Layout.alignment: Qt.AlignHCenter
      Layout.preferredWidth: 62
      Layout.preferredHeight: 62
      radius: 18
      color: Theme.surfaceRaised
      border.width: 1
      border.color: root.active ? Theme.accent : Theme.borderStrong

      AlienLogo {
        anchors.fill: parent
        anchors.margins: 10
        visible: !root.active
      }

      Text {
        anchors.centerIn: parent
        visible: root.active
        text: "↓"
        color: Theme.accent
        font.pixelSize: 28
        font.weight: Font.Light
      }
    }

    Text {
      Layout.fillWidth: true
      text: root.active ? "Drop files to add them" : "Add audio or video"
      color: Theme.text
      font.pixelSize: 20
      font.weight: Font.Bold
      horizontalAlignment: Text.AlignHCenter
      wrapMode: Text.WordWrap
    }

    Text {
      Layout.fillWidth: true
      text: "Analyzed and converted locally. Nothing is uploaded."
      color: Theme.textMuted
      font.pixelSize: 11
      horizontalAlignment: Text.AlignHCenter
      wrapMode: Text.WordWrap
    }

    Text {
      Layout.fillWidth: true
      text: "MP3 · WAV · FLAC · M4A · MP4 · MKV · MOV · WebM"
      color: Theme.textMuted
      opacity: 0.72
      font.pixelSize: 9
      font.letterSpacing: 0.5
      horizontalAlignment: Text.AlignHCenter
      wrapMode: Text.WordWrap
    }

    PrimaryButton {
      Layout.alignment: Qt.AlignHCenter
      Layout.topMargin: 5
      text: "Choose files"
      onClicked: fileDialog.open()
    }
  }
}
