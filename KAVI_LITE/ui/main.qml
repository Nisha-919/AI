import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    id: root
    width: 900
    height: 600
    visible: true
    title: "KAVI Lite"
    color: "#0b0f1a"

    ColumnLayout {
        anchors.fill: parent
        spacing: 16
        anchors.margins: 24

        Text {
            text: "KAVI Lite"
            color: "#8fe9ff"
            font.pixelSize: 28
            font.weight: Font.DemiBold
            horizontalAlignment: Text.AlignHCenter
            Layout.fillWidth: true
        }

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            Orb {
                id: orb
                anchors.centerIn: parent
                state: backend.state
            }
        }

        Subtitles {
            id: subtitles
            text: backend.subtitle
            Layout.fillWidth: true
            Layout.preferredHeight: 90
        }

        Text {
            text: "State: " + backend.state
            color: "#5be3ff"
            font.pixelSize: 14
            horizontalAlignment: Text.AlignHCenter
            Layout.fillWidth: true
        }
    }
}
