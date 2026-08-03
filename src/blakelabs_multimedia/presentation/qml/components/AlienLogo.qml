import QtQuick
import BlakeLabsTheme 1.0

Item {
  id: root
  property color outlineColor: Theme.text
  property color eyeColor: Theme.accent
  property color monogramColor: Theme.text

  implicitWidth: 44
  implicitHeight: 44

  Canvas {
    id: canvas
    anchors.fill: parent
    antialiasing: true

    onWidthChanged: requestPaint()
    onHeightChanged: requestPaint()

    onPaint: {
      const ctx = getContext("2d")
      ctx.clearRect(0, 0, width, height)
      const scale = Math.min(width, height) / 100
      const offsetX = (width - 100 * scale) / 2
      const offsetY = (height - 100 * scale) / 2
      ctx.save()
      ctx.setTransform(scale, 0, 0, scale, offsetX, offsetY)
      ctx.lineCap = "round"
      ctx.lineJoin = "round"

      ctx.beginPath()
      ctx.moveTo(50, 7)
      ctx.bezierCurveTo(28, 8, 14, 20, 10, 40)
      ctx.bezierCurveTo(6, 61, 18, 81, 37, 91)
      ctx.bezierCurveTo(45, 96, 55, 96, 63, 91)
      ctx.bezierCurveTo(82, 81, 94, 61, 90, 40)
      ctx.bezierCurveTo(86, 20, 72, 8, 50, 7)
      ctx.strokeStyle = root.outlineColor
      ctx.lineWidth = 5
      ctx.stroke()

      ctx.fillStyle = root.eyeColor
      ctx.beginPath()
      ctx.moveTo(21, 39)
      ctx.lineTo(44, 33)
      ctx.lineTo(39, 48)
      ctx.lineTo(25, 47)
      ctx.closePath()
      ctx.fill()

      ctx.beginPath()
      ctx.moveTo(79, 39)
      ctx.lineTo(56, 33)
      ctx.lineTo(61, 48)
      ctx.lineTo(75, 47)
      ctx.closePath()
      ctx.fill()

      ctx.fillStyle = "#DDFBFF"
      ctx.beginPath()
      ctx.ellipse(31, 38, 2.4, 2.4)
      ctx.fill()
      ctx.beginPath()
      ctx.ellipse(69, 38, 2.4, 2.4)
      ctx.fill()

      ctx.strokeStyle = root.monogramColor
      ctx.lineWidth = 5
      ctx.beginPath()
      ctx.moveTo(36, 58)
      ctx.lineTo(36, 79)
      ctx.moveTo(36, 59)
      ctx.bezierCurveTo(52, 56, 53, 66, 40, 68)
      ctx.bezierCurveTo(55, 68, 55, 80, 36, 78)
      ctx.moveTo(57, 58)
      ctx.lineTo(57, 78)
      ctx.lineTo(72, 78)
      ctx.stroke()

      ctx.restore()
    }

    Connections {
      target: root
      function onOutlineColorChanged() { canvas.requestPaint() }
      function onEyeColorChanged() { canvas.requestPaint() }
      function onMonogramColorChanged() { canvas.requestPaint() }
    }
  }
}
