import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import BlakeLabsTheme 1.0

Rectangle {
  id: root
  required property string jobId
  required property string name
  required property string status
  required property string statusLabel
  required property string detail
  required property string kind
  required property string duration
  required property string fileSize
  required property real progress
  required property string progressLabel
  required property string presetTitle
  required property string speed
  required property string eta
  required property bool canCancel
  required property bool canOpen
  signal cancelRequested(string jobId)
  signal openRequested(string jobId)

  implicitHeight: 112
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
      Layout.preferredWidth: 58
      Layout.preferredHeight: 58
      radius: 18
      color: root.status === "failed" ? "#2A1519" : Theme.surfaceRaised

      Text {
        anchors.centerIn: parent
        text: root.kind === "audio" ? "A" : (root.kind === "image" ? "I" : "V")
        color: root.status === "failed" ? Theme.danger : Theme.accent
        font.pixelSize: 16
        font.weight: Font.Bold
      }
    }

    ColumnLayout {
      Layout.fillWidth: true
      spacing: 6

      RowLayout {
        Layout.fillWidth: true
        spacing: 8

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
          color: root.status === "failed" ? Theme.danger
                 : root.status === "completed" ? Theme.success
                 : root.status === "processing" ? Theme.accent
                 : Theme.warning
          font.pixelSize: 10
          font.weight: Font.Bold
        }
      }

      Text {
        Layout.fillWidth: true
        text: root.detail
        color: Theme.textMuted
        font.pixelSize: 10
        elide: Text.ElideMiddle
      }

      RowLayout {
        Layout.fillWidth: true
        spacing: 10

        Rectangle {
          Layout.fillWidth: true
          Layout.preferredHeight: 5
          radius: 3
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
          text: root.progressLabel
          color: Theme.text
          font.pixelSize: 10
          font.weight: Font.Bold
        }
      }

      RowLayout {
        Layout.fillWidth: true
        spacing: 10

        Text {
          Layout.fillWidth: true
          text: root.presetTitle
                + (root.speed ? "  -  " + root.speed : "")
                + (root.eta ? "  -  " + root.eta : "")
                + "  -  " + root.duration + "  -  " + root.fileSize
          color: Theme.textMuted
          font.pixelSize: 9
          elide: Text.ElideRight
        }

        Button {
          visible: root.canCancel
          text: "Cancel"
          flat: true
          onClicked: root.cancelRequested(root.jobId)
          contentItem: Text {
            text: parent.text
            color: Theme.danger
            font.pixelSize: 10
            font.weight: Font.Bold
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
          }
        }

        Button {
          visible: root.canOpen
          text: "Open folder"
          flat: true
          onClicked: root.openRequested(root.jobId)
          contentItem: Text {
            text: parent.text
            color: Theme.accent
            font.pixelSize: 10
            font.weight: Font.Bold
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
          }
        }
      }
    }
  }
}
