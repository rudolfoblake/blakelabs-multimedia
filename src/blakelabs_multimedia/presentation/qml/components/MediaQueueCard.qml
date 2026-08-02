import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import BlakeLabsTheme 1.0

Rectangle {
  id: root
  required property string name
  required property string status
  required property string statusLabel
  required property string detail
  required property string kind
  required property string duration
  required property string fileSize
  required property real progress

  implicitHeight: 92
  radius: Theme.radiusMedium
  color: mouseArea.containsMouse ? Theme.surfaceHover : Theme.surface
  border.width: 1
  border.color: root.status === "failed" ? Theme.danger : Theme.border

  Behavior on color { ColorAnimation { duration: 120 } }

  MouseArea {
    id: mouseArea
    anchors.fill: parent
    hoverEnabled: true
    acceptedButtons: Qt.NoButton
  }

  RowLayout {
    anchors.fill: parent
    anchors.margins: 16
    spacing: 14

    Rectangle {
      Layout.preferredWidth: 54
      Layout.preferredHeight: 54
      radius: 17
      color: root.status === "failed" ? "#2A1519" : Theme.surfaceRaised

      Text {
        anchors.centerIn: parent
        text: root.kind === "audio" ? "♫" : (root.kind === "image" ? "▧" : "▶")
        color: root.status === "failed" ? Theme.danger : Theme.accent
        font.pixelSize: 21
        font.weight: Font.Bold
      }
    }

    ColumnLayout {
      Layout.fillWidth: true
      spacing: 5

      RowLayout {
        Layout.fillWidth: true

        Text {
          Layout.fillWidth: true
          text: root.name
          color: Theme.text
          font.pixelSize: 14
          font.weight: Font.DemiBold
          elide: Text.ElideMiddle
        }

        Text {
          text: root.statusLabel
          color: root.status === "failed" ? Theme.danger : (root.status === "ready" ? Theme.success : Theme.warning)
          font.pixelSize: 11
          font.weight: Font.Bold
        }
      }

      Text {
        Layout.fillWidth: true
        text: root.detail
        color: Theme.textMuted
        font.pixelSize: 11
        elide: Text.ElideRight
      }

      RowLayout {
        Layout.fillWidth: true
        spacing: 12

        Rectangle {
          Layout.fillWidth: true
          Layout.preferredHeight: 4
          radius: 2
          color: Theme.border

          Rectangle {
            width: parent.width * Math.max(0, Math.min(1, root.progress))
            height: parent.height
            radius: parent.radius
            color: root.status === "failed" ? Theme.danger : Theme.accent
            Behavior on width { NumberAnimation { duration: 220; easing.type: Easing.OutCubic } }
          }
        }

        Text {
          text: root.duration + "  ·  " + root.fileSize
          color: Theme.textMuted
          font.pixelSize: 10
        }
      }
    }
  }
}
