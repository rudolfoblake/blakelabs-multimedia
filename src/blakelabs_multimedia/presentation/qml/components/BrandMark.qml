import QtQuick
import QtQuick.Layouts
import BlakeLabsTheme 1.0

RowLayout {
  id: root
  property bool compact: false
  spacing: 12

  Rectangle {
    Layout.preferredWidth: 42
    Layout.preferredHeight: 42
    radius: 13
    color: Theme.surfaceRaised
    border.width: 1
    border.color: Theme.borderStrong

    AlienLogo {
      anchors.fill: parent
      anchors.margins: 6
    }
  }

  ColumnLayout {
    visible: !root.compact
    spacing: -1

    Text {
      text: "BLAKE LABS"
      color: Theme.text
      font.pixelSize: 13
      font.weight: Font.Bold
      font.letterSpacing: 1.8
    }

    Text {
      text: "MULTIMEDIA"
      color: Theme.accent
      font.pixelSize: 9
      font.weight: Font.DemiBold
      font.letterSpacing: 2.4
    }
  }
}
