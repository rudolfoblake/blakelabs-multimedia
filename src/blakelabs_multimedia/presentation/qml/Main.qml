import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import BlakeLabsTheme 1.0
import "components"

ApplicationWindow {
  id: window
  visible: true
  width: 1320
  height: 820
  minimumWidth: 760
  minimumHeight: 620
  title: "BlakeLabs Multimedia"
  color: Theme.background

  readonly property bool compactNavigation: width < 940
  readonly property bool narrowContent: width < 1120

  RowLayout {
    anchors.fill: parent
    spacing: 0

    Rectangle {
      Layout.fillHeight: true
      Layout.preferredWidth: window.compactNavigation ? 84 : 238
      color: "#0C100F"
      border.width: 1
      border.color: Theme.border

      ColumnLayout {
        anchors.fill: parent
        anchors.margins: 18
        spacing: 8

        BrandMark {
          Layout.fillWidth: true
          Layout.bottomMargin: 28
          compact: window.compactNavigation
        }

        SidebarItem {
          Layout.fillWidth: true
          symbol: "◇"
          text: "Workspace"
          compact: window.compactNavigation
          selected: true
        }

        SidebarItem {
          Layout.fillWidth: true
          symbol: "⇄"
          text: "Convert"
          compact: window.compactNavigation
        }

        SidebarItem {
          Layout.fillWidth: true
          symbol: "✂"
          text: "Quick tools"
          compact: window.compactNavigation
        }

        SidebarItem {
          Layout.fillWidth: true
          symbol: "≡"
          text: "Queue"
          compact: window.compactNavigation
        }

        Item { Layout.fillHeight: true }

        SidebarItem {
          Layout.fillWidth: true
          symbol: "⚙"
          text: "Settings"
          compact: window.compactNavigation
        }
      }
    }

    ScrollView {
      Layout.fillWidth: true
      Layout.fillHeight: true
      clip: true
      ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

      contentWidth: availableWidth

      ColumnLayout {
        width: parent.width
        spacing: 22

        Item { Layout.preferredHeight: 8 }

        RowLayout {
          Layout.fillWidth: true
          Layout.leftMargin: 30
          Layout.rightMargin: 30
          spacing: 16

          ColumnLayout {
            Layout.fillWidth: true
            spacing: 4

            Text {
              text: "Multimedia workspace"
              color: Theme.text
              font.pixelSize: 28
              font.weight: Font.Bold
            }

            Text {
              text: "One native workspace for conversion, repair and fast media operations."
              color: Theme.textMuted
              font.pixelSize: 13
            }
          }

          Rectangle {
            Layout.preferredWidth: 118
            Layout.preferredHeight: 36
            radius: 18
            color: Theme.surface
            border.width: 1
            border.color: Theme.border

            Row {
              anchors.centerIn: parent
              spacing: 8

              Rectangle {
                width: 7
                height: 7
                radius: 4
                color: Theme.accent
              }

              Text {
                text: "APP READY"
                color: Theme.textMuted
                font.pixelSize: 9
                font.weight: Font.Bold
                font.letterSpacing: 0.8
              }
            }
          }
        }

        GridLayout {
          Layout.fillWidth: true
          Layout.leftMargin: 30
          Layout.rightMargin: 30
          columns: window.narrowContent ? 1 : 2
          columnSpacing: 22
          rowSpacing: 22

          DropZone {
            Layout.fillWidth: true
            Layout.preferredHeight: window.narrowContent ? 245 : 286
            onFilesSelected: function(urls) { mediaController.addFiles(urls) }
          }

          ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 14

            RowLayout {
              Layout.fillWidth: true
              spacing: 14

              MetricCard {
                Layout.fillWidth: true
                value: mediaQueueModel.count
                label: "FILES IN SESSION"
                hint: "Local and private"
              }

              MetricCard {
                Layout.fillWidth: true
                value: "∞"
                label: "FORMAT ROUTES"
                hint: "Powered by FFmpeg"
              }
            }

            Rectangle {
              Layout.fillWidth: true
              Layout.fillHeight: true
              Layout.minimumHeight: 136
              radius: Theme.radiusMedium
              color: Theme.surface
              border.width: 1
              border.color: Theme.border

              ColumnLayout {
                anchors.fill: parent
                anchors.margins: 18
                spacing: 8

                Text {
                  text: "Built to stay responsive"
                  color: Theme.text
                  font.pixelSize: 15
                  font.weight: Font.Bold
                }

                Text {
                  Layout.fillWidth: true
                  text: "FFprobe and future FFmpeg jobs run as asynchronous processes. The interface keeps rendering, resizing and accepting input while media work continues."
                  color: Theme.textMuted
                  font.pixelSize: 12
                  lineHeight: 1.35
                  wrapMode: Text.WordWrap
                }

                Item { Layout.fillHeight: true }

                Text {
                  text: "PYTHON  ·  QT QUICK  ·  FFMPEG"
                  color: Theme.accent
                  font.pixelSize: 10
                  font.weight: Font.Bold
                  font.letterSpacing: 1.2
                }
              }
            }
          }
        }

        RowLayout {
          Layout.fillWidth: true
          Layout.leftMargin: 30
          Layout.rightMargin: 30

          Text {
            Layout.fillWidth: true
            text: "Session queue"
            color: Theme.text
            font.pixelSize: 18
            font.weight: Font.Bold
          }

          Text {
            text: mediaQueueModel.count === 0 ? "Waiting for media" : mediaQueueModel.count + " item(s)"
            color: Theme.textMuted
            font.pixelSize: 11
          }
        }

        ListView {
          id: queueList
          Layout.fillWidth: true
          Layout.leftMargin: 30
          Layout.rightMargin: 30
          Layout.preferredHeight: Math.max(160, contentHeight)
          interactive: false
          spacing: 10
          model: mediaQueueModel

          delegate: MediaQueueCard {
            width: queueList.width
            name: model.name
            status: model.status
            statusLabel: model.statusLabel
            detail: model.detail
            kind: model.kind
            duration: model.duration
            fileSize: model.fileSize
            progress: model.progress
          }

          footer: Item {
            width: queueList.width
            height: mediaQueueModel.count === 0 ? 150 : 8

            Column {
              visible: mediaQueueModel.count === 0
              anchors.centerIn: parent
              spacing: 8

              Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "No media queued"
                color: Theme.text
                font.pixelSize: 15
                font.weight: Font.DemiBold
              }

              Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "Drop files above. Analysis starts instantly and asynchronously."
                color: Theme.textMuted
                font.pixelSize: 11
              }
            }
          }
        }

        Item { Layout.preferredHeight: 26 }
      }
    }
  }
}
