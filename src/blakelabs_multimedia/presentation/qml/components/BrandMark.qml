import QtQuick
import QtQuick.Layouts
import BlakeLabsTheme 1.0

RowLayout {
  id: root
  property bool compact: false
  spacing: 12

  Rectangle {
    Layout.preferredWidth: 38
    Layout.preferredHeight: 38
    radius: 12
    color: Theme.accent

    Text {
      anchors.centerIn: parent
      text: "B"
      color: Theme.background
      font.pixelSize: 20
      font.weight: Font.Black
    }
  }

  ColumnLayout {
    visible: !root.compact
    spacing: -2

    Text {
      text: "BLAKE LABS"
      color: Theme.text
      font.pixelSize: 14
      font.weight: Font.Bold
      font.letterSpacing: 1.4
    }

    Text {
      text: "MULTIMEDIA"
      color: Theme.accent
      font.pixelSize: 10
      font.weight: Font.DemiBold
      font.letterSpacing: 2.2
    }
  }
}
