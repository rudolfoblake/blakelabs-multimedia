import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import BlakeLabsTheme 1.0

Button {
  id: root
  property string symbol: ""
  property bool compact: false
  property bool selected: false
  implicitHeight: 48
  hoverEnabled: true
  padding: 0

  background: Rectangle {
    radius: Theme.radiusSmall
    color: root.selected ? Theme.surfaceHover : (root.hovered ? Theme.surfaceRaised : "transparent")
    border.width: root.selected ? 1 : 0
    border.color: root.selected ? Theme.border : "transparent"

    Behavior on color {
      ColorAnimation { duration: 120 }
    }
  }

  contentItem: RowLayout {
    spacing: 12

    Text {
      Layout.preferredWidth: root.compact ? 48 : 32
      horizontalAlignment: Text.AlignHCenter
      text: root.symbol
      color: root.selected ? Theme.accent : Theme.textMuted
      font.pixelSize: 18
      font.weight: Font.DemiBold
    }

    Text {
      visible: !root.compact
      Layout.fillWidth: true
      text: root.text
      color: root.selected ? Theme.text : Theme.textMuted
      font.pixelSize: 14
      font.weight: root.selected ? Font.DemiBold : Font.Medium
      elide: Text.ElideRight
    }
  }
}
