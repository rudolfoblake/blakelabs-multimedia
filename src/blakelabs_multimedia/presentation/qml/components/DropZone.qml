import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Layouts
import BlakeLabsTheme 1.0

Rectangle {
  id: root
  signal filesSelected(var urls)
  property bool active: dropArea.containsDrag
  implicitHeight: 260
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
    title: "Choose audio, video or image files"
    fileMode: FileDialog.OpenFiles
    onAccepted: root.filesSelected(selectedFiles)
  }

  ColumnLayout {
    anchors.centerIn: parent
    width: Math.min(parent.width - 48, 430)
    spacing: 14

    Rectangle {
      Layout.alignment: Qt.AlignHCenter
      Layout.preferredWidth: 64
      Layout.preferredHeight: 64
      radius: 22
      color: root.active ? Theme.accent : Theme.surfaceRaised

      Text {
        anchors.centerIn: parent
        text: root.active ? "↓" : "+"
        color: root.active ? Theme.background : Theme.accent
        font.pixelSize: 30
        font.weight: Font.Light
      }
    }

    Text {
      Layout.fillWidth: true
      text: root.active ? "Drop to analyze" : "Bring any media into the lab"
      color: Theme.text
      font.pixelSize: 22
      font.weight: Font.Bold
      horizontalAlignment: Text.AlignHCenter
      wrapMode: Text.WordWrap
    }

    Text {
      Layout.fillWidth: true
      text: "Video, audio and images. Metadata is analyzed in the background without freezing the interface."
      color: Theme.textMuted
      font.pixelSize: 13
      lineHeight: 1.35
      horizontalAlignment: Text.AlignHCenter
      wrapMode: Text.WordWrap
    }

    PrimaryButton {
      Layout.alignment: Qt.AlignHCenter
      text: "Choose files"
      onClicked: fileDialog.open()
    }
  }
}
