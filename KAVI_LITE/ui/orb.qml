import QtQuick 2.15
import QtQuick.Effects 1.15

Item {
    id: root
    property string state: "Idle"
    width: 260
    height: 260

    property color orbColor: state === "Thinking" ? "#b06bff" :
                             state === "Listening" ? "#42ffd7" :
                             state === "Speaking" ? "#7ef9ff" : "#4b8bff"

    Rectangle {
        id: orb
        width: 160
        height: 160
        radius: width / 2
        anchors.centerIn: parent
        color: orbColor
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#ffffff" }
            GradientStop { position: 1.0; color: orbColor }
        }
    }

    MultiEffect {
        anchors.fill: orb
        source: orb
        glowEnabled: true
        glowColor: orbColor
        glowRadius: state === "Speaking" ? 40 : 20
        glowOpacity: state === "Speaking" ? 0.9 : 0.5
    }

    NumberAnimation {
        target: orb
        property: "scale"
        from: 0.95
        to: 1.08
        duration: 800
        running: state === "Listening"
        loops: Animation.Infinite
        easing.type: Easing.InOutQuad
    }

    RotationAnimator {
        target: orb
        from: 0
        to: 360
        duration: 1400
        running: state === "Thinking"
        loops: Animation.Infinite
    }

    Behavior on orbColor {
        ColorAnimation { duration: 200 }
    }
}
