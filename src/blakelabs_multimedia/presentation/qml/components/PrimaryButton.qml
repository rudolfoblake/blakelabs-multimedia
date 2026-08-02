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
    color: root.down ? Theme.accentStrong : (root.hovered ? "#9BFFA9" : Theme.accent)
    scale: root.down ? 0.98 : 1

    Behavior on color { ColorAnimation { duration: 100 } }
    Behavior on scale { NumberAnimation { duration: 90 } }
  }

  contentItem: Text {
    text: root.text
    color: Theme.background
    font.pixelSize: 14
    font.weight: Font.Bold
    horizontalAlignment: Text.AlignHCenter
    verticalAlignment: Text.AlignVCenter
  }
}
