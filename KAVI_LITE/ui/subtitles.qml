import QtQuick 2.15

Item {
    id: root
    property string text: ""

    Rectangle {
        anchors.fill: parent
        radius: 12
        color: "#111827"
        border.color: "#1f2937"
        border.width: 1
    }

    Text {
        text: root.text
        anchors.centerIn: parent
        width: parent.width - 32
        wrapMode: Text.Wrap
        horizontalAlignment: Text.AlignHCenter
        color: "#c7f7ff"
        font.pixelSize: 16
    }
}
