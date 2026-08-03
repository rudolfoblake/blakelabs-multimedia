import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import BlakeLabsTheme 1.0

Rectangle {
  id: root
  property bool compact: false
  property bool expanded: false

  readonly property var videoCrfValues: [0, 18, 20, 22, 24, 28]
  readonly property var videoBitrateValues: [0, 2500, 5000, 8000, 12000, 20000]
  readonly property var videoWidthValues: [0, 3840, 1920, 1280, 854]
  readonly property var videoSpeedValues: ["", "ultrafast", "fast", "medium", "slow", "veryslow"]
  readonly property var audioBitrateValues: [0, 96, 128, 160, 192, 256, 320]
  readonly property var sampleRateValues: [0, 44100, 48000, 96000]
  readonly property var channelValues: [0, 1, 2]

  implicitHeight: advancedContent.implicitHeight + 32
  radius: Theme.radiusMedium
  color: Theme.surface
  border.width: 1
  border.color: root.expanded ? Theme.borderStrong : Theme.border

  function findIndex(values, value) {
    const index = values.indexOf(value)
    return index < 0 ? 0 : index
  }

  function synchronize() {
    videoCrfBox.currentIndex = findIndex(videoCrfValues, mediaController.videoCrf)
    videoBitrateBox.currentIndex = findIndex(videoBitrateValues, mediaController.videoBitrate)
    videoWidthBox.currentIndex = findIndex(videoWidthValues, mediaController.videoMaxWidth)
    videoSpeedBox.currentIndex = findIndex(videoSpeedValues, mediaController.videoEncoderPreset)
    audioBitrateBox.currentIndex = findIndex(audioBitrateValues, mediaController.audioBitrate)
    sampleRateBox.currentIndex = findIndex(sampleRateValues, mediaController.audioSampleRate)
    channelsBox.currentIndex = findIndex(channelValues, mediaController.audioChannels)
  }

  ColumnLayout {
    id: advancedContent
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.top: parent.top
    anchors.margins: 16
    spacing: 14

    RowLayout {
      Layout.fillWidth: true
      spacing: 12

      Rectangle {
        Layout.preferredWidth: 34
        Layout.preferredHeight: 34
        radius: 10
        color: Theme.accentSoft
        border.width: 1
        border.color: Theme.borderStrong

        Text {
          anchors.centerIn: parent
          text: "≡"
          color: Theme.accent
          font.pixelSize: 18
          font.weight: Font.Bold
        }
      }

      ColumnLayout {
        Layout.fillWidth: true
        spacing: 2

        Text {
          text: "Advanced settings"
          color: Theme.text
          font.pixelSize: 14
          font.weight: Font.Bold
        }

        Text {
          Layout.fillWidth: true
          text: mediaController.advancedSummary
          color: Theme.textMuted
          font.pixelSize: 10
          elide: Text.ElideRight
        }
      }

      Button {
        visible: root.expanded
        text: "Reset"
        flat: true
        onClicked: mediaController.resetAdvancedOptions()

        contentItem: Text {
          text: parent.text
          color: Theme.textMuted
          font.pixelSize: 10
          font.weight: Font.DemiBold
          horizontalAlignment: Text.AlignHCenter
          verticalAlignment: Text.AlignVCenter
        }
      }

      Button {
        text: root.expanded ? "Hide" : "Customize"
        flat: true
        onClicked: root.expanded = !root.expanded

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

    Rectangle {
      Layout.fillWidth: true
      Layout.preferredHeight: 1
      visible: root.expanded
      color: Theme.border
    }

    ColumnLayout {
      Layout.fillWidth: true
      visible: root.expanded && mediaController.selectedPresetSupportsVideo
      spacing: 10

      RowLayout {
        Layout.fillWidth: true

        Text {
          text: "VIDEO"
          color: Theme.accent
          font.pixelSize: 10
          font.weight: Font.Bold
          font.letterSpacing: 1.6
        }

        Item { Layout.fillWidth: true }

        Text {
          text: "Choose CRF or a fixed bitrate — setting one clears the other."
          color: Theme.textMuted
          font.pixelSize: 9
          visible: !root.compact
        }
      }

      GridLayout {
        Layout.fillWidth: true
        columns: root.compact ? 1 : 4
        columnSpacing: 12
        rowSpacing: 10

        ColumnLayout {
          Layout.fillWidth: true
          spacing: 5

          Text {
            text: "Quality (CRF)"
            color: Theme.textMuted
            font.pixelSize: 10
          }

          ComboBox {
            id: videoCrfBox
            Layout.fillWidth: true
            model: ["Preset default", "18 · Visually lossless", "20 · High", "22 · Balanced", "24 · Compact", "28 · Small"]
            onActivated: mediaController.setVideoCrf(root.videoCrfValues[currentIndex])
          }
        }

        ColumnLayout {
          Layout.fillWidth: true
          spacing: 5

          Text {
            text: "Video bitrate"
            color: Theme.textMuted
            font.pixelSize: 10
          }

          ComboBox {
            id: videoBitrateBox
            Layout.fillWidth: true
            model: ["Preset default", "2.5 Mbps", "5 Mbps", "8 Mbps", "12 Mbps", "20 Mbps"]
            onActivated: mediaController.setVideoBitrate(root.videoBitrateValues[currentIndex])
          }
        }

        ColumnLayout {
          Layout.fillWidth: true
          spacing: 5

          Text {
            text: "Maximum resolution"
            color: Theme.textMuted
            font.pixelSize: 10
          }

          ComboBox {
            id: videoWidthBox
            Layout.fillWidth: true
            model: ["Source / preset", "4K · 3840", "1080p · 1920", "720p · 1280", "480p · 854"]
            onActivated: mediaController.setVideoMaxWidth(root.videoWidthValues[currentIndex])
          }
        }

        ColumnLayout {
          Layout.fillWidth: true
          spacing: 5

          Text {
            text: "Encoder speed"
            color: Theme.textMuted
            font.pixelSize: 10
          }

          ComboBox {
            id: videoSpeedBox
            Layout.fillWidth: true
            model: ["Preset default", "Ultra fast", "Fast", "Medium", "Slow", "Very slow"]
            onActivated: mediaController.setVideoEncoderPreset(root.videoSpeedValues[currentIndex])
          }
        }
      }
    }

    Rectangle {
      Layout.fillWidth: true
      Layout.preferredHeight: 1
      visible: root.expanded
               && mediaController.selectedPresetSupportsVideo
               && mediaController.selectedPresetSupportsAudio
      color: Theme.border
    }

    ColumnLayout {
      Layout.fillWidth: true
      visible: root.expanded && mediaController.selectedPresetSupportsAudio
      spacing: 10

      RowLayout {
        Layout.fillWidth: true

        Text {
          text: "AUDIO"
          color: Theme.accent
          font.pixelSize: 10
          font.weight: Font.Bold
          font.letterSpacing: 1.6
        }

        Item { Layout.fillWidth: true }

        Text {
          visible: mediaController.selectedPresetIsLossless
          text: "Bitrate does not apply to lossless output."
          color: Theme.textMuted
          font.pixelSize: 9
        }
      }

      GridLayout {
        Layout.fillWidth: true
        columns: root.compact ? 1 : 3
        columnSpacing: 12
        rowSpacing: 10

        ColumnLayout {
          Layout.fillWidth: true
          spacing: 5

          Text {
            text: "Audio bitrate"
            color: Theme.textMuted
            font.pixelSize: 10
          }

          ComboBox {
            id: audioBitrateBox
            Layout.fillWidth: true
            enabled: !mediaController.selectedPresetIsLossless
            model: ["Preset default", "96 kbps", "128 kbps", "160 kbps", "192 kbps", "256 kbps", "320 kbps"]
            onActivated: mediaController.setAudioBitrate(root.audioBitrateValues[currentIndex])
          }
        }

        ColumnLayout {
          Layout.fillWidth: true
          spacing: 5

          Text {
            text: "Sample rate"
            color: Theme.textMuted
            font.pixelSize: 10
          }

          ComboBox {
            id: sampleRateBox
            Layout.fillWidth: true
            model: ["Preset default", "44.1 kHz", "48 kHz", "96 kHz"]
            onActivated: mediaController.setAudioSampleRate(root.sampleRateValues[currentIndex])
          }
        }

        ColumnLayout {
          Layout.fillWidth: true
          spacing: 5

          Text {
            text: "Channels"
            color: Theme.textMuted
            font.pixelSize: 10
          }

          ComboBox {
            id: channelsBox
            Layout.fillWidth: true
            model: ["Preset default", "Mono", "Stereo"]
            onActivated: mediaController.setAudioChannels(root.channelValues[currentIndex])
          }
        }
      }

      GridLayout {
        Layout.fillWidth: true
        columns: root.compact ? 1 : 2
        columnSpacing: 16

        CheckBox {
          text: "Normalize loudness to -16 LUFS"
          checked: mediaController.normalizeAudio
          onToggled: mediaController.setNormalizeAudio(checked)
        }

        CheckBox {
          text: "Preserve source metadata"
          checked: mediaController.preserveMetadata
          onToggled: mediaController.setPreserveMetadata(checked)
        }
      }
    }

    Text {
      Layout.fillWidth: true
      visible: root.expanded && mediaController.selectedPresetGroup === "quick-tool"
      text: "Animated GIF uses a purpose-built video filter. Advanced audio and video overrides are disabled for this tool."
      color: Theme.textMuted
      font.pixelSize: 10
      wrapMode: Text.WordWrap
    }
  }

  Component.onCompleted: synchronize()

  Connections {
    target: mediaController
    function onAdvancedOptionsChanged() { root.synchronize() }
    function onSelectedPresetChanged() { root.synchronize() }
  }
}
