import QtQuick
import QtQuick.Controls
import BlakeLabsTheme 1.0

Button {
  id: root
  implicitHeight: 46
  leftPadding: 20
  rightPadding: 20
  hoverEnabled: true

  background: Rectangle {
    radius: 14
    color: !root.enabled ? Theme.border
           : root.down ? Theme.accentStrong
           : root.hovered ? "#9BFFA9"
           : Theme.accent
    scale: root.down && root.enabled ? 0.98 : 1
    opacity: root.enabled ? 1 : 0.62

    Behavior on color { ColorAnimation { duration: 100 } }
    Behavior on scale { NumberAnimation { duration: 90 } }
  }

  contentItem: Text {
    text: root.text
    color: root.enabled ? Theme.background : Theme.textMuted
    font.pixelSize: 13
    font.weight: Font.Bold
    horizontalAlignment: Text.AlignHCenter
    verticalAlignment: Text.AlignVCenter
  }
}
