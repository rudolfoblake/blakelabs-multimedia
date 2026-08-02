import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Layouts
import BlakeLabsTheme 1.0
import "components"

ApplicationWindow {
  id: window
  visible: true
  width: 1280
  height: 820
  minimumWidth: 760
  minimumHeight: 620
  title: "BlakeLabs Multimedia"
  color: Theme.background

  readonly property bool compact: width < 980

  FolderDialog {
    id: outputFolderDialog
    title: "Choose output folder"
    onAccepted: mediaController.setOutputDirectory(selectedFolder)
  }

  header: Rectangle {
    implicitHeight: 72
    color: "#0B0F0D"
    border.width: 1
    border.color: Theme.border

    RowLayout {
      anchors.fill: parent
      anchors.leftMargin: 24
      anchors.rightMargin: 24
      spacing: 16

      BrandMark {
        Layout.alignment: Qt.AlignVCenter
      }

      Item { Layout.fillWidth: true }

      Rectangle {
        Layout.preferredWidth: statusRow.implicitWidth + 24
        Layout.preferredHeight: 34
        radius: 17
        color: Theme.surface
        border.width: 1
        border.color: Theme.border

        Row {
          id: statusRow
          anchors.centerIn: parent
          spacing: 8

          Rectangle {
            anchors.verticalCenter: parent.verticalCenter
            width: 7
            height: 7
            radius: 4
            color: mediaQueueModel.activeCount > 0 ? Theme.warning : Theme.accent
          }

          Text {
            text: mediaQueueModel.activeCount > 0
                  ? mediaQueueModel.activeCount + " active"
                  : "Ready"
            color: Theme.textMuted
            font.pixelSize: 10
            font.weight: Font.DemiBold
          }
        }
      }

      Button {
        text: "Diagnostics"
        flat: true
        onClicked: mediaController.openDiagnosticsFolder()

        contentItem: Text {
          text: parent.text
          color: Theme.textMuted
          font.pixelSize: 10
          font.weight: Font.DemiBold
          horizontalAlignment: Text.AlignHCenter
          verticalAlignment: Text.AlignVCenter
        }
      }
    }
  }

  ScrollView {
    id: page
    anchors.fill: parent
    clip: true
    contentWidth: availableWidth
    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

    Item {
      width: page.availableWidth
      implicitHeight: content.implicitHeight + 48

      ColumnLayout {
        id: content
        anchors.top: parent.top
        anchors.topMargin: 24
        anchors.horizontalCenter: parent.horizontalCenter
        width: Math.min(Math.max(0, parent.width - 48), 1240)
        spacing: 20

        ColumnLayout {
          Layout.fillWidth: true
          spacing: 5

          Text {
            Layout.fillWidth: true
            text: "Convert audio and video"
            color: Theme.text
            font.pixelSize: window.compact ? 24 : 30
            font.weight: Font.Bold
            wrapMode: Text.WordWrap
          }

          Text {
            Layout.fillWidth: true
            text: "Choose files, select an output format and start the queue. Processing stays on this computer."
            color: Theme.textMuted
            font.pixelSize: 12
            wrapMode: Text.WordWrap
          }
        }

        GridLayout {
          Layout.fillWidth: true
          columns: window.compact ? 1 : 2
          columnSpacing: 18
          rowSpacing: 18

          DropZone {
            Layout.fillWidth: true
            Layout.preferredHeight: 310
            onFilesSelected: function(urls) { mediaController.addFiles(urls) }
          }

          Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 310
            radius: Theme.radiusLarge
            color: Theme.surface
            border.width: 1
            border.color: Theme.border

            ColumnLayout {
              anchors.fill: parent
              anchors.margins: 20
              spacing: 12

              ColumnLayout {
                Layout.fillWidth: true
                spacing: 4

                Text {
                  text: "Output format"
                  color: Theme.text
                  font.pixelSize: 18
                  font.weight: Font.Bold
                }

                Text {
                  Layout.fillWidth: true
                  text: "The selected preset is applied to every compatible ready file."
                  color: Theme.textMuted
                  font.pixelSize: 11
                  wrapMode: Text.WordWrap
                }
              }

              ComboBox {
                id: presetBox
                Layout.fillWidth: true
                Layout.preferredHeight: 46
                model: mediaController.presets
                textRole: "title"
                valueRole: "id"
                onActivated: mediaController.selectPreset(currentValue)

                function synchronizeSelection() {
                  for (let index = 0; index < count; index++) {
                    if (valueAt(index) === mediaController.selectedPresetId) {
                      currentIndex = index
                      return
                    }
                  }
                }

                Component.onCompleted: synchronizeSelection()

                Connections {
                  target: mediaController
                  function onSelectedPresetChanged() { presetBox.synchronizeSelection() }
                }
              }

              Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                radius: Theme.radiusMedium
                color: Theme.surfaceRaised
                border.width: 1
                border.color: Theme.border

                RowLayout {
                  anchors.fill: parent
                  anchors.margins: 16
                  spacing: 14

                  Rectangle {
                    Layout.preferredWidth: 52
                    Layout.preferredHeight: 52
                    radius: 16
                    color: "#14261B"

                    Text {
                      anchors.centerIn: parent
                      text: mediaController.selectedPresetExtension
                      color: Theme.accent
                      font.pixelSize: 11
                      font.weight: Font.Bold
                    }
                  }

                  ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 4

                    Text {
                      Layout.fillWidth: true
                      text: mediaController.selectedPresetTitle
                      color: Theme.text
                      font.pixelSize: 14
                      font.weight: Font.Bold
                      elide: Text.ElideRight
                    }

                    Text {
                      Layout.fillWidth: true
                      text: mediaController.selectedPresetDescription
                      color: Theme.textMuted
                      font.pixelSize: 11
                      lineHeight: 1.25
                      wrapMode: Text.WordWrap
                    }
                  }
                }
              }
            }
          }
        }

        Rectangle {
          Layout.fillWidth: true
          Layout.preferredHeight: window.compact ? 172 : 92
          radius: Theme.radiusMedium
          color: Theme.surface
          border.width: 1
          border.color: Theme.border

          GridLayout {
            anchors.fill: parent
            anchors.margins: 16
            columns: window.compact ? 1 : 3
            columnSpacing: 16
            rowSpacing: 10

            ColumnLayout {
              Layout.fillWidth: true
              spacing: 3

              Text {
                text: "Save converted files to"
                color: Theme.text
                font.pixelSize: 12
                font.weight: Font.Bold
              }

              Text {
                Layout.fillWidth: true
                text: mediaController.outputDirectoryLabel
                color: Theme.textMuted
                font.pixelSize: 10
                elide: Text.ElideMiddle
              }
            }

            RowLayout {
              Layout.alignment: window.compact ? Qt.AlignLeft : Qt.AlignHCenter
              spacing: 4

              Button {
                text: "Use source folder"
                flat: true
                enabled: mediaController.outputDirectoryLabel !== "Same folder as source"
                onClicked: mediaController.resetOutputDirectory()

                contentItem: Text {
                  text: parent.text
                  color: parent.enabled ? Theme.textMuted : Theme.border
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
            }

            PrimaryButton {
              Layout.fillWidth: window.compact
              Layout.preferredWidth: window.compact ? -1 : 188
              text: mediaQueueModel.readyCount > 0
                    ? "Convert " + mediaQueueModel.readyCount + " file(s)"
                    : "Add files to continue"
              enabled: mediaQueueModel.readyCount > 0
              onClicked: mediaController.startReady()
            }
          }
        }

        Rectangle {
          Layout.fillWidth: true
          implicitHeight: queueContent.implicitHeight + 32
          radius: Theme.radiusLarge
          color: Theme.surface
          border.width: 1
          border.color: Theme.border

          ColumnLayout {
            id: queueContent
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: 16
            spacing: 12

            RowLayout {
              Layout.fillWidth: true

              ColumnLayout {
                Layout.fillWidth: true
                spacing: 2

                Text {
                  text: "Queue"
                  color: Theme.text
                  font.pixelSize: 18
                  font.weight: Font.Bold
                }

                Text {
                  text: mediaQueueModel.count === 0
                        ? "No files added"
                        : mediaQueueModel.count + " file(s) in this session"
                  color: Theme.textMuted
                  font.pixelSize: 10
                }
              }

              Button {
                text: "Clear finished"
                flat: true
                enabled: mediaQueueModel.count > 0
                onClicked: mediaController.clearFinished()

                contentItem: Text {
                  text: parent.text
                  color: parent.enabled ? Theme.textMuted : Theme.border
                  font.pixelSize: 10
                  horizontalAlignment: Text.AlignHCenter
                  verticalAlignment: Text.AlignVCenter
                }
              }
            }

            Rectangle {
              Layout.fillWidth: true
              Layout.preferredHeight: 118
              visible: mediaQueueModel.count === 0
              radius: Theme.radiusMedium
              color: Theme.surfaceRaised
              border.width: 1
              border.color: Theme.border

              Column {
                anchors.centerIn: parent
                spacing: 6

                Text {
                  anchors.horizontalCenter: parent.horizontalCenter
                  text: "Your files will appear here"
                  color: Theme.text
                  font.pixelSize: 13
                  font.weight: Font.DemiBold
                }

                Text {
                  anchors.horizontalCenter: parent.horizontalCenter
                  text: "Add an audio or video file to begin."
                  color: Theme.textMuted
                  font.pixelSize: 10
                }
              }
            }

            ColumnLayout {
              Layout.fillWidth: true
              visible: mediaQueueModel.count > 0
              spacing: 10

              Repeater {
                model: mediaQueueModel

                delegate: MediaQueueCard {
                  Layout.fillWidth: true
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
              }
            }
          }
        }
      }
    }
  }
}
