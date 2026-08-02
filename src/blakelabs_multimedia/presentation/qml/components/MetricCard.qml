import QtQuick
import QtQuick.Layouts
import BlakeLabsTheme 1.0

Rectangle {
  id: root
  property string value: "0"
  property string label: ""
  property string hint: ""
  implicitHeight: 112
  radius: Theme.radiusMedium
  color: Theme.surface
  border.width: 1
  border.color: Theme.border

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: 18
    spacing: 4

    Text {
      text: root.value
      color: Theme.text
      font.pixelSize: 28
      font.weight: Font.Bold
    }

    Text {
      text: root.label
      color: Theme.textMuted
      font.pixelSize: 12
      font.weight: Font.DemiBold
    }

    Text {
      Layout.fillWidth: true
      text: root.hint
      color: Theme.accent
      font.pixelSize: 10
      elide: Text.ElideRight
    }
  }
}
