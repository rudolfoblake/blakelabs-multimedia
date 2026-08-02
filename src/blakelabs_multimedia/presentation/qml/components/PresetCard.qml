import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import BlakeLabsTheme 1.0

Rectangle {
  id: root
  required property string presetId
  required property string title
  required property string description
  required property string extension
  required property string group
  property bool selected: false
  signal chosen()

  implicitHeight: 104
  radius: Theme.radiusMedium
  color: selected ? "#14261B" : (mouse.containsMouse ? Theme.surfaceHover : Theme.surfaceRaised)
  border.width: selected ? 2 : 1
  border.color: selected ? Theme.accent : Theme.border

  Behavior on color { ColorAnimation { duration: 120 } }
  Behavior on border.color { ColorAnimation { duration: 120 } }

  MouseArea {
    id: mouse
    anchors.fill: parent
    hoverEnabled: true
    cursorShape: Qt.PointingHandCursor
    onClicked: root.chosen()
  }

  RowLayout {
    anchors.fill: parent
    anchors.margins: 14
    spacing: 12

    Rectangle {
      Layout.preferredWidth: 42
      Layout.preferredHeight: 42
      radius: 14
      color: root.selected ? Theme.accent : Theme.surface

      Text {
        anchors.centerIn: parent
        text: root.group === "audio" ? "A" : (root.group === "quick-tool" ? "Q" : "V")
        color: root.selected ? Theme.background : Theme.accent
        font.pixelSize: 15
        font.weight: Font.Bold
      }
    }

    ColumnLayout {
      Layout.fillWidth: true
      spacing: 4

      RowLayout {
        Layout.fillWidth: true

        Text {
          Layout.fillWidth: true
          text: root.title
          color: Theme.text
          font.pixelSize: 13
          font.weight: Font.Bold
          elide: Text.ElideRight
        }

        Rectangle {
          Layout.preferredWidth: 46
          Layout.preferredHeight: 22
          radius: 11
          color: root.selected ? Theme.accent : Theme.surface

          Text {
            anchors.centerIn: parent
            text: root.extension
            color: root.selected ? Theme.background : Theme.textMuted
            font.pixelSize: 9
            font.weight: Font.Bold
            font.letterSpacing: 0.5
          }
        }
      }

      Text {
        Layout.fillWidth: true
        text: root.description
        color: Theme.textMuted
        font.pixelSize: 10
        lineHeight: 1.25
        wrapMode: Text.WordWrap
        maximumLineCount: 2
        elide: Text.ElideRight
      }
    }
  }
}
