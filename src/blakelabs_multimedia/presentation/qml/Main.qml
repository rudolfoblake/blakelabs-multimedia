import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Layouts
import BlakeLabsTheme 1.0
import "components"

ApplicationWindow {
  id: window
  visible: true
  width: 1440
  height: 900
  minimumWidth: 780
  minimumHeight: 650
  title: "BlakeLabs Multimedia"
  color: Theme.background

  readonly property bool compactNavigation: width < 960
  readonly property bool singleColumn: width < 1120

  FolderDialog {
    id: outputFolderDialog
    title: "Choose output folder"
    onAccepted: mediaController.setOutputDirectory(selectedFolder)
  }

  RowLayout {
    anchors.fill: parent
    spacing: 0

    Rectangle {
      Layout.fillHeight: true
      Layout.preferredWidth: window.compactNavigation ? 82 : 232
      color: "#0B0F0D"
      border.width: 1
      border.color: Theme.border

      ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 8

        BrandMark {
          Layout.fillWidth: true
          Layout.bottomMargin: 24
          compact: window.compactNavigation
        }

        SidebarItem {
          Layout.fillWidth: true
          symbol: "W"
          text: "Workspace"
          compact: window.compactNavigation
          selected: true
        }
        SidebarItem {
          Layout.fillWidth: true
          symbol: "C"
          text: "Convert"
          compact: window.compactNavigation
        }
        SidebarItem {
          Layout.fillWidth: true
          symbol: "T"
          text: "Quick tools"
          compact: window.compactNavigation
        }
        SidebarItem {
          Layout.fillWidth: true
          symbol: "Q"
          text: "Queue"
          compact: window.compactNavigation
        }

        Item { Layout.fillHeight: true }

        Rectangle {
          Layout.fillWidth: true
          Layout.preferredHeight: window.compactNavigation ? 58 : 76
          radius: 16
          color: Theme.surface
          border.width: 1
          border.color: Theme.border

          Column {
            anchors.centerIn: parent
            spacing: 4
            Rectangle {
              anchors.horizontalCenter: parent.horizontalCenter
              width: 8
              height: 8
              radius: 4
              color: Theme.accent
            }
            Text {
              visible: !window.compactNavigation
              anchors.horizontalCenter: parent.horizontalCenter
              text: "LOCAL PROCESSING"
              color: Theme.textMuted
              font.pixelSize: 8
              font.weight: Font.Bold
              font.letterSpacing: 0.8
            }
          }
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
          Layout.leftMargin: 28
          Layout.rightMargin: 28
          spacing: 16

          ColumnLayout {
            Layout.fillWidth: true
            spacing: 4
            Text {
              text: "Multimedia, without the ritual sacrifice"
              color: Theme.text
              font.pixelSize: window.width < 900 ? 23 : 30
              font.weight: Font.Bold
            }
            Text {
              Layout.fillWidth: true
              text: "Convert audio and video locally with FFmpeg. Responsive UI, real progress, clean outputs."
              color: Theme.textMuted
              font.pixelSize: 12
              wrapMode: Text.WordWrap
            }
          }

          Rectangle {
            Layout.preferredWidth: 124
            Layout.preferredHeight: 38
            radius: 19
            color: Theme.surface
            border.width: 1
            border.color: Theme.border

            Row {
              anchors.centerIn: parent
              spacing: 8
              Rectangle { width: 7; height: 7; radius: 4; color: Theme.accent }
              Text {
                text: mediaQueueModel.activeCount > 0 ? "WORKING" : "READY"
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
          Layout.leftMargin: 28
          Layout.rightMargin: 28
          columns: window.singleColumn ? 1 : 2
          columnSpacing: 20
          rowSpacing: 20

          DropZone {
            Layout.fillWidth: true
            Layout.preferredHeight: window.singleColumn ? 255 : 390
            onFilesSelected: function(urls) { mediaController.addFiles(urls) }
          }

          Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: window.singleColumn ? 420 : 390
            radius: Theme.radiusLarge
            color: Theme.surface
            border.width: 1
            border.color: Theme.border

            ColumnLayout {
              anchors.fill: parent
              anchors.margins: 18
              spacing: 12

              RowLayout {
                Layout.fillWidth: true
                Text {
                  Layout.fillWidth: true
                  text: "Output recipe"
                  color: Theme.text
                  font.pixelSize: 18
                  font.weight: Font.Bold
                }
                Text {
                  text: "7 PRESETS"
                  color: Theme.accent
                  font.pixelSize: 9
                  font.weight: Font.Bold
                  font.letterSpacing: 1
                }
              }

              Text {
                Layout.fillWidth: true
                text: "Choose once, process every ready item. Incompatible files fail clearly instead of guessing."
                color: Theme.textMuted
                font.pixelSize: 11
                lineHeight: 1.3
                wrapMode: Text.WordWrap
              }

              ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

                ColumnLayout {
                  width: parent.width
                  spacing: 8

                  Repeater {
                    model: mediaController.presets
                    delegate: PresetCard {
                      Layout.fillWidth: true
                      presetId: modelData.id
                      title: modelData.title
                      description: modelData.description
                      extension: modelData.extension
                      group: modelData.group
                      selected: mediaController.selectedPresetId === modelData.id
                      onChosen: mediaController.selectPreset(modelData.id)
                    }
                  }
                }
              }
            }
          }
        }

        Rectangle {
          Layout.fillWidth: true
          Layout.leftMargin: 28
          Layout.rightMargin: 28
          Layout.preferredHeight: 86
          radius: Theme.radiusMedium
          color: Theme.surface
          border.width: 1
          border.color: Theme.border

          RowLayout {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 12

            Rectangle {
              Layout.preferredWidth: 42
              Layout.preferredHeight: 42
              radius: 14
              color: Theme.surfaceRaised
              Text { anchors.centerIn: parent; text: "OUT"; color: Theme.accent; font.pixelSize: 10; font.weight: Font.Bold }
            }

            ColumnLayout {
              Layout.fillWidth: true
              spacing: 3
              Text { text: "Output destination"; color: Theme.text; font.pixelSize: 12; font.weight: Font.Bold }
              Text {
                Layout.fillWidth: true
                text: mediaController.outputDirectoryLabel
                color: Theme.textMuted
                font.pixelSize: 10
                elide: Text.ElideMiddle
              }
            }

            Button {
              text: "Reset"
              flat: true
              visible: mediaController.outputDirectoryLabel !== "Same folder as source"
              onClicked: mediaController.resetOutputDirectory()
              contentItem: Text {
                text: parent.text
                color: Theme.textMuted
                font.pixelSize: 10
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
              }
            }

            Button {
              text: "Choose folder"
              flat: true
              onClicked: outputFolderDialog.open()
              contentItem: Text {
                text: parent.text
                color: Theme.accent
                font.pixelSize: 10
                font.weight: Font.Bold
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
              }
            }

            PrimaryButton {
              text: mediaQueueModel.readyCount > 0 ? "Process " + mediaQueueModel.readyCount + " ready" : "Add media first"
              enabled: mediaQueueModel.readyCount > 0
              onClicked: mediaController.startReady()
            }
          }
        }

        RowLayout {
          Layout.fillWidth: true
          Layout.leftMargin: 28
          Layout.rightMargin: 28

          ColumnLayout {
            Layout.fillWidth: true
            spacing: 2
            Text { text: "Session queue"; color: Theme.text; font.pixelSize: 19; font.weight: Font.Bold }
            Text {
              text: mediaQueueModel.activeCount > 0
                    ? mediaQueueModel.activeCount + " background operation(s)"
                    : "No blocking dialogs. Ever."
              color: Theme.textMuted
              font.pixelSize: 10
            }
          }

          Button {
            text: "Clear finished"
            flat: true
            onClicked: mediaController.clearFinished()
            contentItem: Text {
              text: parent.text
              color: Theme.textMuted
              font.pixelSize: 10
              horizontalAlignment: Text.AlignHCenter
              verticalAlignment: Text.AlignVCenter
            }
          }
        }

        ListView {
          id: queueList
          Layout.fillWidth: true
          Layout.leftMargin: 28
          Layout.rightMargin: 28
          Layout.preferredHeight: Math.max(170, contentHeight)
          interactive: false
          spacing: 10
          model: mediaQueueModel

          delegate: MediaQueueCard {
            width: queueList.width
            jobId: model.jobId
            name: model.name
            status: model.status
            statusLabel: model.statusLabel
            detail: model.detail
            kind: model.kind
            duration: model.duration
            fileSize: model.fileSize
            progress: model.progress
            progressLabel: model.progressLabel
            presetTitle: model.presetTitle
            speed: model.speed
            eta: model.eta
            canCancel: model.canCancel
            canOpen: model.canOpen
            onCancelRequested: function(id) { mediaController.cancelJob(id) }
            onOpenRequested: function(id) { mediaController.openOutputFolder(id) }
          }

          footer: Item {
            width: queueList.width
            height: mediaQueueModel.count === 0 ? 150 : 8
            Column {
              visible: mediaQueueModel.count === 0
              anchors.centerIn: parent
              spacing: 7
              Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "The queue is suspiciously calm"
                color: Theme.text
                font.pixelSize: 14
                font.weight: Font.DemiBold
              }
              Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "Drop media above. Analysis starts immediately."
                color: Theme.textMuted
                font.pixelSize: 10
              }
            }
          }
        }

        Item { Layout.preferredHeight: 28 }
      }
    }
  }
}
